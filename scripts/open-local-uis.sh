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
CLICKHOUSE_UI_URL="${CLICKHOUSE_UI_URL:-http://localhost:${CLICKHOUSE_PORT}/play?theme=dark}"

echo "MLflow UI:      ${MLFLOW_URL}"
echo "ClickHouse UI:  ${CLICKHOUSE_UI_URL}"

if command -v open >/dev/null 2>&1; then
  open "${MLFLOW_URL}"
  open "${CLICKHOUSE_UI_URL}"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${MLFLOW_URL}" >/dev/null 2>&1 &
  xdg-open "${CLICKHOUSE_UI_URL}" >/dev/null 2>&1 &
else
  echo "No browser opener found. Open the URLs above manually."
fi
