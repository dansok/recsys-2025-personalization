from pathlib import Path

import clickhouse_connect
import polars as pl

from recsys_personalization.config import get_settings


def get_client():
    settings = get_settings()
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_database,
    )


def apply_schema(sql_path: Path) -> None:
    client = get_client()
    for statement in [stmt.strip() for stmt in sql_path.read_text().split(";") if stmt.strip()]:
        client.command(statement)


def insert_polars(table: str, frame: pl.DataFrame, batch_size: int = 100_000) -> None:
    if frame.is_empty():
        return
    client = get_client()
    for offset in range(0, frame.height, batch_size):
        batch = frame.slice(offset, batch_size)
        client.insert(table, batch.rows(), column_names=batch.columns)


def query_polars(sql: str, parameters: dict | None = None) -> pl.DataFrame:
    result = get_client().query(sql, parameters=parameters)
    return pl.DataFrame(result.result_rows, schema=result.column_names, orient="row")

