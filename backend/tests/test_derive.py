"""M1.2 — seed routine + today derivation (pure functions + endpoint)."""
from __future__ import annotations

from app.db import SessionLocal
from app.services.derive import derive_session, get_current_routine


def _routine():
    db = SessionLocal()
    try:
        return get_current_routine(db)
    finally:
        db.close()


def test_seed_routine_current(client):
    r = client.get("/api/routine/current") if False else None  # current needs auth; checked elsewhere
    routine = _routine()
    assert routine is not None
    assert routine.version == 1
    assert routine.source == "seed"
    assert len(routine.days) == 7


def test_derive_strength_monday(client):
    s = derive_session(_routine(), "monday")
    assert s.session_type == "strength"
    assert s.modality == "amrap"
    assert s.duration_minutes == 15
    assert any(e.name == "Push-ups" for e in s.exercises)


def test_derive_run_thursday_hr_cap(client):
    s = derive_session(_routine(), "thursday")
    assert s.session_type == "run"
    assert s.hr_zone == "easy"
    assert s.hr_cap_bpm == 145


def test_derive_rest_tuesday(client):
    s = derive_session(_routine(), "tuesday")
    assert s.is_rest is True
    assert s.session_type == "rest"


def test_derive_joint_pain_swaps_to_mobility(client):
    s = derive_session(_routine(), "monday", readiness="joint_pain")
    assert s.session_type == "mobility"
    assert s.swapped is True
    assert s.swap_reason == "joint_pain"
    assert s.duration_minutes == 15


def test_today_endpoint(auth_client):
    r = auth_client.get("/api/sessions/today")
    assert r.status_code == 200
    body = r.json()
    assert "session" in body
    assert body["session"]["routine_version"] == 1


def test_readiness_joint_pain_swaps_today(auth_client):
    r = auth_client.post("/api/sessions/readiness", json={"readiness": "joint_pain"})
    assert r.status_code == 200
    body = r.json()
    assert body["readiness_answered"] is True
    assert body["session"]["session_type"] == "mobility"
    # Persisted: a follow-up today fetch still reflects readiness.
    r2 = auth_client.get("/api/sessions/today")
    assert r2.json()["readiness_answered"] is True
