import os
import pymongo
import pytest
from pymongo import MongoClient


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

