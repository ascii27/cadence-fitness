"""Jester outbound HTTP client."""
from __future__ import annotations

import httpx

from ..config import Settings


class JesterNotConfigured(Exception):
    pass


async def send_event(settings: Settings, event_type: str, payload: dict) -> None:
    """POST one event to Jester. Raises on non-2xx or transport error."""
    if not settings.jester_base_url or not settings.jester_write_key:
        raise JesterNotConfigured("JESTER_BASE_URL / JESTER_WRITE_KEY not set")
    url = f"{settings.jester_base_url.rstrip('/')}/api/item/{event_type}"
    headers = {
        "Authorization": f"Bearer {settings.jester_write_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
