"""Serenity Quant Research API.

    uvicorn app.main:app --reload --port 8000

In development the Vite dev server proxies /api here. In production the built
web app (web/dist) is served by this same process when the folder exists.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .routers import chain, companies, nodes
from .seed import ensure_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_database(config.DB_PATH, config.SEED_DIR)
    yield


app = FastAPI(title="Serenity Quant Research", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(nodes.router)
app.include_router(chain.router)
app.include_router(companies.router)


@app.get("/api/health", tags=["meta"])
def health():
    return {"ok": True, "db": str(config.DB_PATH)}


# ---- serve the built web app, if present (single-process deployment) --------
if config.WEB_DIST.exists():
    app.mount("/assets", StaticFiles(directory=config.WEB_DIST / "assets"), name="assets")
    _index = config.WEB_DIST / "index.html"

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        candidate = config.WEB_DIST / path
        if path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_index)
