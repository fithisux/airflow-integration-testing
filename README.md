# Airflow Integration Tests

This project demonstrates how we can use docker-compose with pytest to run an integration test suite for Airflow DAGs.

## Background

This is based on a heavily modified version of this useful article
[Airflow Integration Testing using Docker Compose](https://selectfrom.dev/airflow-integration-testing-d7bfa510f8f0)

also I have thrown in the mix parts of the circle of ideas outlined here:

[My Medium article](https://medium.com/@fithis2001/remarks-on-setting-up-celery-flower-rabbitmq-for-airflow-d8553267110e)

The list of changes follow

1. We use the official docker compose
2. We add the Mongo db with proper health checks and volumes
3. We add a jupyter notebook for experimenting with Mongo
4. Integration testing is done outside of the image
5. The sample dag also creates documents in the collection

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

## TODO

Revise makefile
Testcontainers
Proper health check of whole deployment

### Running integration tests automatically

Start the deployment

```sh
docker-compose up
```

Now time to create our user. Connect to mongo

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

to get the token. Just change port 8888 to 8891 and you are good to go.

Now from Airflow [http://localhost:8080](http://localhost:8080) activate you `sample` dag.
Every 2 minutes it create a document but also for specific documents it marks them as processed. Consult the integration test.


Ru your test now.
```sh
make integration_test
```