.PHONY: install infra-up infra-down schema test lint

install:
	python3.14 -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"

infra-up:
	docker compose up -d clickhouse mlflow

infra-down:
	docker compose down

schema:
	.venv/bin/recsys schema apply

test:
	.venv/bin/python -m pytest -q

lint:
	.venv/bin/python -m ruff check .

