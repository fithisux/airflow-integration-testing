clean:
	docker-compose -f docker-compose.yaml down --remove-orphans --volumes

start_cluster:
	docker-compose -f docker-compose.yaml up -d
	/src/scripts/wait_for_airflow_web.sh && tail -f /dev/null

integration_test:
	pytest -vvv -s --log-cli-level=DEBUG tests/integration
