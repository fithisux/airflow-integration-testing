import os
import pymongo
import pytest
import requests
from pymongo import MongoClient
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from tests.integration.airflow_api import AirflowAPI

@pytest.fixture
def wait_for_airflow() -> requests.Session:
    api_url = f"http://localhost:8080/health"
    return assert_container_is_ready(api_url)


@pytest.fixture
def airflow_api():
    return AirflowAPI()


@pytest.fixture
def document_store_mongo_collection(mongo_database):
    return mongo_database.mytest_collection


@pytest.fixture
def mongo_database():
    mongo_client = MongoClient('mongodb://newTestUser:Test123@localhost:27017/test?authSource=test')
    database = mongo_client.get_database()
    return database


def assert_container_is_ready(readiness_check_url) -> requests.Session:
    request_session = requests.Session()
    retries = Retry(
        total=20,
        backoff_factor=0.2,
        status_forcelist=[404, 500, 502, 503, 504],
    )
    request_session.mount("http://", HTTPAdapter(max_retries=retries))
    assert request_session.get(readiness_check_url)
    return request_session


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

