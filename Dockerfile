FROM apache/airflow:2.6.0-python3.10
ADD requirements-docker.txt .
RUN pip install -r requirements-docker.txt