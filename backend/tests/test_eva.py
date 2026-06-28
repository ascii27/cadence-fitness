"""M1.6 / M1.8 — Eva inbound: routine replace, banner, revert, goals patch."""
from __future__ import annotations

from app.db import SessionLocal
from app.models import OutboxEvent

NEW_DAYS = [
    {"day_of_week": "monday", "session_type": "run", "label": "New Monday Run",
     "modality": "continuous", "duration_minutes": 40},
    {"day_of_week": "tuesday", "session_type": "rest", "label": "Rest"},
]


def test_put_routine_bumps_version(client, eva_headers):
    r = client.put("/api/routine", json={"reason": "Increase running", "days": NEW_DAYS}, headers=eva_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == 2
    assert body["source"] == "eva"
    assert body["eva_update_pending"] is True


def test_current_shows_eva_banner(client, auth_client, eva_headers):
    client.put("/api/routine", json={"reason": "Tune", "days": NEW_DAYS}, headers=eva_headers)
    r = auth_client.get("/api/routine/current")
    assert r.json()["eva_update_pending"] is True
    assert r.json()["reason"] == "Tune"


def test_acknowledge_clears_banner(client, auth_client, eva_headers):
    client.put("/api/routine", json={"reason": "Tune", "days": NEW_DAYS}, headers=eva_headers)
    auth_client.post("/api/routine/acknowledge")
    r = auth_client.get("/api/routine/current")
    assert r.json()["eva_update_pending"] is False


def test_revert_restores_previous_and_emits_event(client, auth_client, eva_headers):
    client.put("/api/routine", json={"reason": "Tune", "days": NEW_DAYS}, headers=eva_headers)
    r = auth_client.post("/api/routine/revert")
    assert r.status_code == 200
    assert r.json()["version"] == 1
    assert r.json()["is_current"] is True

    db = SessionLocal()
    try:
        types = [e.event_type for e in db.query(OutboxEvent).all()]
    finally:
        db.close()
    assert "routine_reverted" in types


def test_revert_without_previous_conflicts(auth_client):
    # Only the seed (v1) exists; nothing to revert to.
    r = auth_client.post("/api/routine/revert")
    assert r.status_code == 409


def test_goals_patch_and_get(client, auth_client, eva_headers):
    r = client.patch(
        "/api/goals",
        json={"goals": ["marathon_build", "joint_longevity"], "constraints": {"strength_cap_minutes": 15}},
        headers=eva_headers,
    )
    assert r.status_code == 200
    assert r.json()["updated_by"] == "eva"

    r2 = auth_client.get("/api/goals")
    assert r2.json()["goals"] == ["marathon_build", "joint_longevity"]
    assert r2.json()["constraints"]["strength_cap_minutes"] == 15


def test_goals_patch_requires_eva(client):
    r = client.patch("/api/goals", json={"goals": []})
    assert r.status_code == 401
