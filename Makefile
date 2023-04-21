clean:
	docker-compose -f docker-compose.yml down --remove-orphans --volumes

start_cluster:
	docker-compose -f docker-compose.yml up -d
	/src/scripts/wait_for_airflow_web.sh && tail -f /dev/null

integration_test: clean start_cluster
	pytest -vvv -s --log-cli-level=DEBUG tests/integration

run_test_runner_in_manual_mode: start_cluster

manual_testing: clean run_test_runner_in_manual_mode
