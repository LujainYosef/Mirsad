from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, settings
from app.routes import chat, investigate

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("mirsad")

app = FastAPI(title=settings.APP_TITLE, docs_url="/api/docs", redoc_url=None)

app.include_router(investigate.router)
app.include_router(chat.router)

STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "model": settings.OPENROUTER_MODEL,
        "api_key_configured": bool(settings.OPENROUTER_API_KEY),
    }


@app.on_event("startup")
async def on_startup():
    if not settings.OPENROUTER_API_KEY:
        logger.warning(
            "OPENROUTER_API_KEY is not set. Set it in .env (local) or in Render's "
            "Environment settings (production) before submitting an investigation."
        )
