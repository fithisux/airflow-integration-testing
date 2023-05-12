import time
import uuid

import airflow_client
from airflow_client.client.api import dag_api, dag_run_api
from airflow_client.client.model.dag import DAG
from airflow_client.client.model.dag_run import DAGRun


def run_dag(dag_id: str):
    configuration = airflow_client.client.Configuration(host="http://localhost:8080/api/v1", username="airflow", password="airflow")
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
