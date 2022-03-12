format:
	isort . && black .


unit-test:
	coverage run --source=cornflower -m pytest $(location)

coverage-report:
	coverage html