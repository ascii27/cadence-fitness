"""M1.5 — outbox drain worker: success, retry/backoff, terminal failure."""
from __future__ import annotations

import app.services.jester as jester_mod
from app.config import get_settings
from app.db import SessionLocal
from app.models import OutboxEvent
from app.services import outbox


def _enqueue(payload_type="workout_logged"):
    db = SessionLocal()
    try:
        outbox.enqueue(db, payload_type, {"hello": "world"})
        db.commit()
    finally:
        db.close()


async def test_drain_success(monkeypatch):
    sent = []

    async def fake_send(settings, event_type, payload):
        sent.append((event_type, payload))

    monkeypatch.setattr(jester_mod, "send_event", fake_send)
    _enqueue()

    db = SessionLocal()
    try:
        n = await outbox.drain_once(db, get_settings())
        assert n == 1
        ev = db.query(OutboxEvent).first()
        assert ev.status == "sent"
        assert ev.sent_at is not None
    finally:
        db.close()
    assert sent and sent[0][0] == "workout_logged"


async def test_drain_failure_retries(monkeypatch):
    async def fake_send(settings, event_type, payload):
        raise RuntimeError("jester down")

    monkeypatch.setattr(jester_mod, "send_event", fake_send)
    _enqueue()

    db = SessionLocal()
    try:
        await outbox.drain_once(db, get_settings())
        ev = db.query(OutboxEvent).first()
        assert ev.status == "pending"
        assert ev.attempts == 1
        assert ev.next_attempt_at is not None
        assert "jester down" in (ev.last_error or "")
    finally:
        db.close()


async def test_drain_terminal_failure(monkeypatch):
    async def fake_send(settings, event_type, payload):
        raise RuntimeError("nope")

    monkeypatch.setattr(jester_mod, "send_event", fake_send)
    _enqueue()

    # Force attempts to the threshold, clearing backoff each round.
    db = SessionLocal()
    try:
        for _ in range(outbox.MAX_ATTEMPTS):
            ev = db.query(OutboxEvent).first()
            ev.next_attempt_at = None
            db.commit()
            await outbox.drain_once(db, get_settings())
        ev = db.query(OutboxEvent).first()
        assert ev.status == "failed"
        assert ev.attempts == outbox.MAX_ATTEMPTS
    finally:
        db.close()
