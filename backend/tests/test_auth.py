"""M1.1 — auth gate."""
from __future__ import annotations


def test_health_open(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_protected_requires_session(client):
    r = client.get("/api/sessions/today")
    assert r.status_code == 401


def test_session_after_dev_login(auth_client):
    r = auth_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "test@example.com"


def test_logout_clears_session(auth_client):
    auth_client.post("/api/auth/logout")
    r = auth_client.get("/api/auth/me")
    assert r.status_code == 401


def test_eva_endpoint_rejects_without_key(client):
    r = client.put("/api/routine", json={"days": []})
    assert r.status_code == 401


def test_eva_endpoint_rejects_bad_key(client):
    r = client.put("/api/routine", json={"days": []}, headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 401


def test_eva_endpoint_accepts_valid_key(client, eva_headers):
    r = client.get("/api/state", headers=eva_headers)
    assert r.status_code == 200
