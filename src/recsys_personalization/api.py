from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from recsys_personalization.personalization import ParquetPersonalizationStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = PROJECT_ROOT / "data/raw/recsys2025/challenge_dataset"

app = FastAPI(title="RecSys 2025 Personalized Retail Demo")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@lru_cache
def store() -> ParquetPersonalizationStore:
    return ParquetPersonalizationStore(DATA_DIR)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "dataset_present": DATA_DIR.exists()}


@app.get("/personas")
def personas(limit: int = Query(16, ge=1, le=50)) -> dict:
    return {"personas": store().validation_personas(limit=limit)}


@app.get("/profile/{client_id}")
def profile(client_id: int) -> dict:
    user_profile = store().user_profile(client_id)
    return {"profile": store().profile_payload(user_profile)}


@app.get("/search")
def search(
    client_id: int,
    q: str = "",
    limit: int = Query(12, ge=1, le=50),
) -> dict:
    return store().search(client_id=client_id, query=q, limit=limit)

