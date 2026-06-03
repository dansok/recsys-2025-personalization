from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8124
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "recsys2025"
    mlflow_tracking_uri: str = "http://localhost:5002"
    data_dir: Path = Path("data/raw/recsys2025")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

