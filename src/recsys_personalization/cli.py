from pathlib import Path

import typer

from recsys_personalization.clickhouse import apply_schema
from recsys_personalization.download import download_dataset

app = typer.Typer(help="RecSys 2025 behavioral personalization CLI")
schema_app = typer.Typer(help="ClickHouse schema commands")
app.add_typer(schema_app, name="schema")


@schema_app.command("apply")
def apply_schema_command(sql_path: Path = Path("sql/clickhouse_schema.sql")) -> None:
    apply_schema(sql_path)
    typer.echo(f"Applied schema from {sql_path}")


@app.command()
def download(destination: Path = Path("data/raw/recsys2025"), raw: bool = False) -> None:
    archive_path = download_dataset(destination, raw=raw)
    typer.echo(f"Downloaded dataset archive to {archive_path}")


if __name__ == "__main__":
    app()

