"""Cloudflare Turnstile captcha verification."""

import httpx
from fastapi import HTTPException, Request

from src.config import settings
from src.logging_config import get_logger

logger = get_logger("captcha")

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


async def verify_turnstile(request: Request) -> None:
    """Verify Cloudflare Turnstile token from request header.

    Skipped in development when TURNSTILE_ENABLED is False.
    """
    if not settings.turnstile_enabled:
        return

    token = request.headers.get("X-Turnstile-Token")
    if not token:
        raise HTTPException(status_code=403, detail="Captcha token required")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            TURNSTILE_VERIFY_URL,
            data={
                "secret": settings.turnstile_secret_key,
                "response": token,
                "remoteip": request.client.host if request.client else None,
            },
        )

    result = response.json()
    if not result.get("success"):
        logger.warning("Turnstile verification failed", extra={"errors": result.get("error-codes", [])})
        raise HTTPException(status_code=403, detail="Captcha verification failed")
