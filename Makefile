all: venv

venv:
	python3 -m venv venv
	venv/bin/pip install black isort

format:
	venv/bin/isort . --skip venv --profile black
	venv/bin/black . --exclude venv

.PHONY: all venv format
