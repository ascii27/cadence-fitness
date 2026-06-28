"""Day traversal — GET /api/sessions/day/{date} for arbitrary dates."""
from __future__ import annotations


def test_day_derives_weekday_session(auth_client):
    # 2026-06-29 is a Monday → strength "Upper Body & Core" in the seed routine.
    r = auth_client.get("/api/sessions/day/2026-06-29")
    assert r.status_code == 200
    body = r.json()
    assert body["session"]["session_type"] == "strength"
    assert body["session"]["label"] == "Upper Body & Core"


def test_day_rest_weekday(auth_client):
    # 2026-06-30 is a Tuesday → rest.
    r = auth_client.get("/api/sessions/day/2026-06-30")
    assert r.json()["session"]["is_rest"] is True


def test_day_relativity_past_and_future(auth_client):
    assert auth_client.get("/api/sessions/day/2020-01-01").json()["relativity"] == "past"
    assert auth_client.get("/api/sessions/day/2099-01-01").json()["relativity"] == "future"


def test_today_endpoint_relativity(auth_client):
    body = auth_client.get("/api/sessions/today").json()
    assert body["relativity"] == "today"
    # The same date via /day/ is also "today".
    same = auth_client.get(f"/api/sessions/day/{body['session_date']}").json()
    assert same["relativity"] == "today"


def test_day_invalid_date(auth_client):
    assert auth_client.get("/api/sessions/day/not-a-date").status_code == 400


def test_day_shows_log_when_present(auth_client):
    auth_client.post(
        "/api/sessions/log",
        json={"status": "completed", "duration_minutes": 40, "session_date": "2026-06-13"},
    )
    body = auth_client.get("/api/sessions/day/2026-06-13").json()
    assert body["log"] is not None
    assert body["log"]["status"] == "completed"
    assert body["relativity"] == "past"


def test_day_requires_auth(client):
    assert client.get("/api/sessions/day/2026-06-29").status_code == 401
