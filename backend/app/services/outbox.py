"""Outbox: durable event queue with a background drain worker.

Events are written to the outbox in the same transaction as the action that
produced them. A background task retries delivery to Jester with exponential
backoff, marking events `failed` (terminal) after MAX_ATTEMPTS.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..models import OutboxEvent, SessionLog, utcnow
from . import jester

log = logging.getLogger("cadence.outbox")

MAX_ATTEMPTS = 5
DRAIN_INTERVAL_SECONDS = 60
_BACKOFF_BASE_SECONDS = 30  # 30s, 60s, 120s, 240s, ...


def _backoff(attempts: int) -> timedelta:
    return timedelta(seconds=_BACKOFF_BASE_SECONDS * (2 ** max(0, attempts - 1)))


# ---- Payload builders ----
def workout_logged_payload(logentry: SessionLog) -> dict:
    return {
        "log_id": logentry.log_id,
        "session_type": logentry.session_type,
        "status": logentry.status,
        "session_date": logentry.session_date,
        "day_of_week": logentry.day_of_week,
        "label": logentry.label,
        "duration_minutes": logentry.duration_minutes,
        "rounds_completed": logentry.rounds_completed,
        "rating": logentry.rating,
        "readiness": logentry.readiness,
        "swap_reason": logentry.swap_reason,
        "routine_version": logentry.routine_version,
        "health_metrics": logentry.health_metrics or {
            "avg_hr_bpm": None,
            "max_hr_bpm": None,
            "active_energy_kcal": None,
            "hrv_ms": None,
        },
    }


def milestone_payload(streak_days: int, logentry: SessionLog) -> dict:
    return {
        "milestone_type": "streak",
        "streak_days": streak_days,
        "session_date": logentry.session_date,
        "log_id": logentry.log_id,
    }


def routine_reverted_payload(from_version: int, to_version: int) -> dict:
    return {
        "from_version": from_version,
        "to_version": to_version,
        "reverted_at": utcnow().isoformat(),
    }


# ---- Enqueue ----
def enqueue(db: Session, event_type: str, payload: dict) -> OutboxEvent:
    event = OutboxEvent(event_type=event_type, payload=payload, status="pending")
    db.add(event)
    db.flush()
    return event


# ---- Drain ----
async def drain_once(db: Session, settings: Settings) -> int:
    """Attempt delivery of all due pending events. Returns number sent."""
    now = utcnow()
    rows = db.execute(
        select(OutboxEvent).where(OutboxEvent.status == "pending")
    ).scalars().all()
    sent = 0
    for event in rows:
        if event.next_attempt_at is not None and event.next_attempt_at > now:
            continue
        try:
            await jester.send_event(settings, event.event_type, event.payload)
            event.status = "sent"
            event.sent_at = utcnow()
            event.last_error = None
            sent += 1
        except Exception as exc:  # noqa: BLE001 — record and retry/backoff
            event.attempts += 1
            event.last_error = str(exc)[:500]
            if event.attempts >= MAX_ATTEMPTS:
                event.status = "failed"
                log.error("Outbox event %s failed permanently: %s", event.outbox_id, exc)
            else:
                event.next_attempt_at = utcnow() + _backoff(event.attempts)
        db.add(event)
    db.commit()
    return sent


async def worker_loop(session_factory, stop_event: asyncio.Event) -> None:
    settings = get_settings()
    while not stop_event.is_set():
        try:
            db = session_factory()
            try:
                await drain_once(db, settings)
            finally:
                db.close()
        except Exception:  # noqa: BLE001
            log.exception("Outbox worker iteration failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=DRAIN_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            pass
