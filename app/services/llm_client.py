"""
Thin, server-side client for the OpenRouter Chat Completions API.

Security notes (see PRD section 11 / Agents.md section 16):
- The API key is read only from environment configuration and is NEVER sent
  to the browser or logged.
- Requests use a bounded timeout and a small number of retries.
- Evidence content is not written to persistent logs here.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger("mirsad.llm")


class LLMError(Exception):
    """Raised when the OpenRouter call fails or returns an unusable response."""


def _headers() -> dict:
    if not settings.OPENROUTER_API_KEY:
        raise LLMError(
            "OPENROUTER_API_KEY is not configured on the server. "
            "Set it in your .env file (local) or in Render's Environment settings (production)."
        )
    return {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional but recommended by OpenRouter for attribution/rankings.
        "HTTP-Referer": settings.APP_PUBLIC_URL,
        "X-Title": settings.APP_TITLE,
    }


async def chat_completion(
    messages: list[dict],
    *,
    temperature: float = 0.2,
    max_tokens: int = 4000,
) -> str:
    """
    Calls OpenRouter's chat completions endpoint and returns the assistant's
    text content. Retries a bounded number of times on transient failures.
    """
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_error: Exception | None = None
    for attempt in range(settings.OPENROUTER_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.OPENROUTER_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    settings.OPENROUTER_BASE_URL, headers=_headers(), json=payload
                )
            if response.status_code == 401:
                raise LLMError("OpenRouter rejected the API key (401). Check OPENROUTER_API_KEY.")
            if response.status_code == 429:
                last_error = LLMError("OpenRouter rate limit reached (429).")
                await asyncio.sleep(1.5 * (attempt + 1))
                continue
            if response.status_code >= 500:
                last_error = LLMError(f"OpenRouter server error ({response.status_code}).")
                await asyncio.sleep(1.0 * (attempt + 1))
                continue
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                raise LLMError("OpenRouter returned no choices.")
            content = choices[0].get("message", {}).get("content", "")
            if not content or not content.strip():
                raise LLMError("OpenRouter returned an empty response.")
            return content
        except httpx.TimeoutException as exc:
            last_error = LLMError("Request to OpenRouter timed out.")
            logger.warning("OpenRouter timeout on attempt %s: %s", attempt + 1, exc)
        except httpx.HTTPError as exc:
            last_error = LLMError(f"Network error contacting OpenRouter: {exc}")
            logger.warning("OpenRouter HTTP error on attempt %s: %s", attempt + 1, exc)

    raise last_error or LLMError("Unknown error contacting OpenRouter.")
