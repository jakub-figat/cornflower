format:
	docker-compose run --rm backend bash -c "isort . && black ."

unit-test:
	coverage run --source=cornflower -m pytest tests/unit/

coverage-report:
	coverage html
