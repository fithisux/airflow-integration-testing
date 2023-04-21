from datetime import timedelta

import pendulum
from airflow.models.dag import dag

from operators.process_document_operator import ProcessDocumentOperator

DAG_ID = "sample"
DOCUMENT_STORE_CONNECTION_ID = "mongo_store"
DEFAULT_ARGS = {
    "depends_on_past": False,
    "start_date": pendulum.datetime(2021, 1, 1, tz="Asia/Singapore"),
}

@dag(
    dag_id=DAG_ID,
    default_args=DEFAULT_ARGS,
    catchup=False,
    schedule_interval=timedelta(minutes = 2),
    is_paused_upon_creation=True,
    description="Just a sample DAG",
)
def create_sample_dag():
    ProcessDocumentOperator(
        task_id="process_document",
        document_store_connection_id = DOCUMENT_STORE_CONNECTION_ID,
    )


globals()[DAG_ID] = create_sample_dag()
