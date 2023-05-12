# Airflow Integration Tests

This project demonstrates how we can use docker-compose with pytest to run an integration test suite for Airflow DAGs.

## Background

This is based on a heavily modified version of this useful article
[Airflow Integration Testing using Docker Compose](https://selectfrom.dev/airflow-integration-testing-d7bfa510f8f0)

also I have thrown in the mix parts of the circle of ideas outlined here:

[My Medium article](https://medium.com/@fithis2001/remarks-on-setting-up-celery-flower-rabbitmq-for-airflow-d8553267110e)

The list of changes follow

1. We use the [official docker compose](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#fetching-docker-compose-yaml) 
2. We add the Mongo db with proper health checks and volumes
3. We add a jupyter notebook for experimenting with Mongo
4. Integration testing is done outside of the image
5. The sample dag also creates documents in the collection, currently commented out
6. Testcontainers execution, no need to run docker compose manually!!!
7. Replace custom triggering code with official airflow client calls in a more robust way. 

## Highlights

We add an environment variable in docker compose according to [Connections](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)
for the mongo hook

```yaml
AIRFLOW_CONN_MONGO_STORE: 'mongodb://myTester:tester123@mongodb:27017/test?authSource=test'
```

which is referred by `mongo_store`. We also add a variable for the document collection

```yaml
AIRFLOW_VAR_DOCUMENT_COLLECTION: 'mytest_collection'
```

called `mytest_collection`.

### Running integration tests automatically

Create a virtual environment (tested with 3.11.3) and use `requirements-dev.txt`. Integration testing cannot be 
simpler than a

```sh
make integration_test
```

It starts a modified deployment, creates a test user, it runs the test, it deletes the user and kills the deployment.
All automatic through [testcontainers-python](https://github.com/testcontainers/testcontainers-python/).

It is actually an automation of `test_sample_dag.py` (in the original article) as `test_automatically_saple_dag.py`.


### Running deployment manually

Start the deployment

```sh
docker-compose up
```

If you are interested in making stateful, bring back the commented out volumes for postgres and mongo.


Now time to create our user (see docker file for the user). Connect to mongo

```sh
docker exec -it airflow-integration-testing-mongodb-1 mongosh -u root -p example
```

Use the following admin command in mongo to create the user, taken from [here](https://www.mongodb.com/docs/manual/tutorial/create-users/)

```javascript
use test
db.createUser(
  {
    user: "myTester",
    pwd:  passwordPrompt(),   // or cleartext password
    roles: [ { role: "readWrite", db: "test" },
             { role: "read", db: "reporting" } ]
  }
)
```

Set as password `tester123`. Exit and you can verify it works if you can connect with

```sh
docker exec -it airflow-integration-testing-mongodb-1 mongosh --port 27017 -u "myTester" --authenticationDatabase "test" -p
```

You can also use the notebook of jupyter. Run

```sh 
docker logs airflow-integration-testing-datascience-notebook-1
```

to get the token/url. Just change port 8888 to 8891 and you are good to go.

Now from Airflow [http://localhost:8080](http://localhost:8080) activate you `sample` dag.

Read the corresponding operator. In summary every 2 minutes it checks if a document exists with `{"source": 'some_source'}`
and marks it as processed. For debugging purposes there is a commented out section that actually creates a document.