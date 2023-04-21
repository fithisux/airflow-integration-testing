import logging
from datetime import datetime

from airflow.models import BaseOperator, Variable
from airflow.models.taskinstance import Context
from airflow.providers.mongo.hooks.mongo import MongoHook

DOCUMENT_STORE_COLLECTION_NAME = "document_collection"

class ProcessDocumentOperator(BaseOperator):
    def __init__(self, document_store_connection_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.document_store_connection_id = document_store_connection_id

    def execute(self, context: Context):
        mongo_hook = MongoHook(conn_id=self.document_store_connection_id)
        #source_name = context["dag_run"].conf["source_name"]

        tstamp_name = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        collection_name = str(Variable.get(DOCUMENT_STORE_COLLECTION_NAME))
        logging.info(f'collection_name is {collection_name}')
        mongo_hook.insert_one(
            mongo_collection=collection_name,
            doc={"source": tstamp_name},
        )
        mongo_hook.update_many(
            mongo_collection=collection_name,
            filter_doc={"source": 'some_source'},
            update_doc={"$set": {"processed": True}},
        )
