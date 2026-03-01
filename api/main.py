"""FastAPI app for Montrixa Telegram Mini App."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import analytics, balance, categories, health, transactions

app = FastAPI(title="Montrixa Mini App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NoCacheStaticFiles(StaticFiles):
    """Static files with no-store headers to avoid stale Telegram WebView cache."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app.include_router(health.router)
app.include_router(categories.router)
app.include_router(balance.router)
app.include_router(analytics.router)
app.include_router(transactions.router)

# Serve Mini App static files (optional, for same-origin hosting)
_miniapp_dir = Path(__file__).resolve().parents[1] / "miniapp"
if _miniapp_dir.exists():
    app.mount("/", NoCacheStaticFiles(directory=str(_miniapp_dir), html=True), name="miniapp")
