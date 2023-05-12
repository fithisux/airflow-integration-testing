import os
import time
import uuid

import airflow_client
import pymongo
import pytest
from airflow_client.client.api import dag_api, dag_run_api
from airflow_client.client.model.dag import DAG
from airflow_client.client.model.dag_run import DAGRun
from pymongo import MongoClient


def run_dag(dag_id: str):
    configuration = airflow_client.client.Configuration(host="http://localhost:8080/api/v1", username="airflow",
                                                        password="airflow")
    with airflow_client.client.ApiClient(configuration) as api_client:
        print("[blue]Unpause a DAG")
        dag_api_instance = dag_api.DAGApi(api_client)
        try:
            dag = DAG(
                is_paused=False,
            )
            _ = dag_api_instance.patch_dag(dag_id, dag, update_mask=["is_paused"])
        except airflow_client.client.exceptions.OpenApiException as e:
            print("[red]Exception when calling DAGAPI->patch_dag: %s\n" % e)
        else:
            print("[green] Unpausing DAG is successful")

        print("[blue]Triggering a DAG run")
        dag_run_api_instance = dag_run_api.DAGRunApi(api_client)
        try:
            # Create a DAGRun object (no dag_id should be specified because it is read-only property of DAGRun)
            # dag_run id is generated randomly to allow multiple executions of the script
            dag_run_id = "some_test_run_" + uuid.uuid4().hex
            dag_run = DAGRun(dag_run_id=dag_run_id)
            _ = dag_run_api_instance.post_dag_run(dag_id, dag_run)
        except airflow_client.client.exceptions.OpenApiException as e:
            print("[red]Exception when calling DAGRunAPI->post_dag_run: %s\n" % e)
        else:
            print("[green]Posting DAG Run successful")

        print("[blue]Status of a DAG run")
        try:
            is_not_success = True
            while is_not_success:
                api_response = dag_run_api_instance.get_dag_run(dag_id, dag_run_id)
                print(api_response.state)
                if str(api_response.state) == "success":
                    is_not_success = False
                else:
                    time.sleep(1)

        except airflow_client.client.exceptions.OpenApiException as e:
            print("[red]Exception when calling DAGRunAPI->get_dag_run: %s\n" % e)
        else:
            print("[green]Getting DAG Run successful")


@pytest.fixture
def document_store_mongo_collection(mongo_database):
    return mongo_database.mytest_collection


@pytest.fixture
def mongo_database():
    mongo_client = MongoClient('mongodb://newTestUser:Test123@localhost:27017/test?authSource=test')
    database = mongo_client.get_database()
    return database


class TempComposeFile(object):
    def __init__(self):
        self.lines = []
        with open("docker-compose.yaml") as f:
            for line in f:
                if "AIRFLOW_CONN_MONGO_STORE" in line:
                    self.lines.append(
                        "    AIRFLOW_CONN_MONGO_STORE: 'mongodb://newTestUser:Test123@mongodb:27017/test?authSource=test'\n")
                else:
                    self.lines.append(line)
    def __enter__(self):
        with open('other_compose.yaml', 'w') as f:
            f.writelines(self.lines)
    def __exit__(self, sometype, value, traceback):
        os.unlink('other_compose.yaml')


class TempTestingUser(object):
    def __init__(self):
        client = pymongo.MongoClient('mongodb://root:example@127.0.0.1:27017/admin?authSource=admin')
        self.db = client['test']
        mycol = self.db["sometouch"]
        mycol.update_one({'hello': 'world'}, {'$set': {'hello': 'world'}}, upsert=True) #initial "touch" to create database
    def __enter__(self):
        try:
            self.db.command('createUser', 'newTestUser', pwd='Test123', roles=[{'role': 'readWrite', 'db': 'test'}, {'role': "read", 'db': "reporting"}])
        except pymongo.errors.OperationFailure as e:
            if e.code == 51003:  # Duplicate user error code pymongo.errors.OperationFailure: User "jdoe@mydatabase" already exists, full error: {'ok': 0.0, 'errmsg': 'User "jdoe@mydatabase" already exists', 'code': 51003, 'codeName': 'Location51003'}
                print(f"User newTestUser exists")
    def __exit__(self, sometype, value, traceback):
        try:
            self.db.command('dropUser', 'newTestUser')
        except pymongo.errors.OperationFailure as e:
            if e.code == 11:  # Duplicate user error code pymongo.errors.OperationFailure: User "jdoe@mydatabase" already exists, full error: {'ok': 0.0, 'errmsg': 'User "jdoe@mydatabase" already exists', 'code': 51003, 'codeName': 'Location51003'}
                print(f"User newTestUser not found")

