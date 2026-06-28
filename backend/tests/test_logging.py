"""M1.4 / M1.5 — logging, edit window, past-date, outbox enqueue, milestones."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.db import SessionLocal
from app.models import OutboxEvent, SessionLog


def _outbox_types():
    db = SessionLocal()
    try:
        return [e.event_type for e in db.query(OutboxEvent).all()]
    finally:
        db.close()


def test_create_log_persists_and_enqueues(auth_client):
    r = auth_client.post(
        "/api/sessions/log",
        json={"status": "completed", "duration_minutes": 16, "rounds_completed": 4, "rating": 4},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["log"]["status"] == "completed"
    assert body["log"]["duration_minutes"] == 16
    assert "workout_logged" in _outbox_types()


def test_log_appears_in_history(auth_client):
    auth_client.post("/api/sessions/log", json={"status": "completed", "duration_minutes": 30})
    r = auth_client.get("/api/sessions")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_past_date_logging(auth_client):
    r = auth_client.post(
        "/api/sessions/log",
        json={"status": "missed", "duration_minutes": 0, "session_date": "2026-06-01"},
    )
    assert r.status_code == 200
    assert r.json()["log"]["session_date"] == "2026-06-01"


def test_patch_within_window(auth_client):
    created = auth_client.post(
        "/api/sessions/log", json={"status": "completed", "duration_minutes": 20}
    ).json()
    log_id = created["log"]["log_id"]
    r = auth_client.patch(f"/api/sessions/{log_id}", json={"rating": 5, "notes": "great"})
    assert r.status_code == 200
    assert r.json()["rating"] == 5


def test_patch_outside_window_rejected(auth_client):
    created = auth_client.post(
        "/api/sessions/log", json={"status": "completed", "duration_minutes": 20}
    ).json()
    log_id = created["log"]["log_id"]
    # Age the log past 24h.
    db = SessionLocal()
    try:
        row = db.get(SessionLog, log_id)
        row.logged_at = datetime.now(timezone.utc) - timedelta(hours=25)
        db.commit()
    finally:
        db.close()
    r = auth_client.patch(f"/api/sessions/{log_id}", json={"rating": 1})
    assert r.status_code == 409


def test_milestone_enqueued_at_seven(auth_client, monkeypatch):
    import app.routers.sessions as sessions_mod

    fixed_today = date(2026, 6, 29)  # Monday
    monkeypatch.setattr(sessions_mod, "today_date", lambda: fixed_today)

    # 7 consecutive planned-day completions ending on Monday 2026-06-29.
    planned_dates = [
        "2026-06-20",  # Sat
        "2026-06-22",  # Mon
        "2026-06-24",  # Wed
        "2026-06-25",  # Thu
        "2026-06-26",  # Fri
        "2026-06-27",  # Sat
    ]
    for d in planned_dates:
        auth_client.post(
            "/api/sessions/log",
            json={"status": "completed", "duration_minutes": 30, "session_date": d},
        )
    r = auth_client.post(
        "/api/sessions/log",
        json={"status": "completed", "duration_minutes": 30, "session_date": "2026-06-29"},
    )
    assert r.json()["streak"] == 7
    assert r.json()["milestone_hit"] == 7
    assert "milestone" in _outbox_types()
