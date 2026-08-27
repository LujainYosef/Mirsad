"""
Central configuration for Mirsad.

All secrets/config come from environment variables. Locally, python-dotenv
loads them from a `.env` file (never committed to git). On Render, the same
variable names are set in the service's Environment settings.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development. In production (Render) this file
# won't exist, which is fine — real env vars are already present.
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    # --- LLM / OpenRouter ---
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5")
    OPENROUTER_BASE_URL: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions"
    )
    OPENROUTER_TIMEOUT_SECONDS: float = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "90"))
    OPENROUTER_MAX_RETRIES: int = int(os.getenv("OPENROUTER_MAX_RETRIES", "2"))
    # Optional, used by OpenRouter for analytics / rankings — safe to leave blank.
    APP_PUBLIC_URL: str = os.getenv("APP_PUBLIC_URL", "http://localhost:8000")
    APP_TITLE: str = os.getenv("APP_TITLE", "Mirsad")

    # --- Server ---
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = _get_bool("DEBUG", False)

    # --- Upload limits ---
    MAX_UPLOAD_MB: float = float(os.getenv("MAX_UPLOAD_MB", "10"))
    MAX_UPLOAD_BYTES: int = int(MAX_UPLOAD_MB * 1024 * 1024)
    MAX_FILES_PER_REQUEST: int = int(os.getenv("MAX_FILES_PER_REQUEST", "5"))
    ALLOWED_EXTENSIONS: set[str] = {
        ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif",
        ".txt", ".log", ".csv", ".json", ".eml",
    }
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

    # --- Evidence bounds (protects against huge/adversarial input) ---
    MAX_TEXT_EVIDENCE_CHARS: int = int(os.getenv("MAX_TEXT_EVIDENCE_CHARS", "60000"))
    MAX_PDF_CHARS: int = int(os.getenv("MAX_PDF_CHARS", "40000"))
    MAX_CHAT_HISTORY_TURNS: int = int(os.getenv("MAX_CHAT_HISTORY_TURNS", "12"))

    # --- Case store ---
    CASE_TTL_SECONDS: int = int(os.getenv("CASE_TTL_SECONDS", str(60 * 60 * 6)))  # 6h


settings = Settings()
