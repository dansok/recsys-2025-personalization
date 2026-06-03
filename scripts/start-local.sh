#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-8124}"
MLFLOW_PORT="${MLFLOW_PORT:-5002}"
MLFLOW_URL="${MLFLOW_URL:-http://localhost:${MLFLOW_PORT}}"
CLICKHOUSE_HTTP_URL="${CLICKHOUSE_HTTP_URL:-http://localhost:${CLICKHOUSE_PORT}}"
CLICKHOUSE_UI_URL="${CLICKHOUSE_UI_URL:-${CLICKHOUSE_HTTP_URL}/play?theme=dark}"
OPEN_UI="${OPEN_UI:-1}"

http_ready() {
  curl -fsS "$1" >/dev/null 2>&1
}

wait_for_http() {
  local name="$1"
  local url="$2"
  local attempts="${3:-60}"

  printf "Waiting for %s" "${name}"
  for _ in $(seq 1 "${attempts}"); do
    if http_ready "${url}"; then
      echo " ready"
      return 0
    fi
    printf "."
    sleep 1
  done

  echo
  echo "${name} did not become ready at ${url}"
  return 1
}

services=()
if http_ready "${CLICKHOUSE_HTTP_URL}/ping"; then
  echo "ClickHouse already available at ${CLICKHOUSE_HTTP_URL}"
else
  services+=(clickhouse)
fi

if http_ready "${MLFLOW_URL}/health"; then
  echo "MLflow already available at ${MLFLOW_URL}"
else
  services+=(mlflow)
fi

if ((${#services[@]} > 0)); then
  docker compose up -d "${services[@]}"
fi

wait_for_http "ClickHouse" "${CLICKHOUSE_HTTP_URL}/ping" 60
wait_for_http "MLflow" "${MLFLOW_URL}/health" 60

echo
echo "Local services are running:"
echo "  MLflow UI:      ${MLFLOW_URL}"
echo "  ClickHouse UI:  ${CLICKHOUSE_UI_URL}"
echo "  ClickHouse API: ${CLICKHOUSE_HTTP_URL}"
echo
echo "Tip: run '.venv/bin/recsys schema apply' after first startup if the ClickHouse schema is not initialized."

if [[ "${OPEN_UI}" == "1" ]]; then
  ./scripts/open-local-uis.sh
fi
