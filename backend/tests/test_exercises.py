"""Exercise catalog endpoint + catalog integrity."""
from __future__ import annotations

from app.data.exercises import EXERCISES

VALID_CATEGORIES = {"push", "pull", "core", "lower", "mobility", "conditioning"}
VALID_DIFFICULTY = {"beginner", "intermediate", "advanced"}


def test_list_requires_auth(client):
    assert client.get("/api/exercises").status_code == 401


def test_list_with_session(auth_client):
    r = auth_client.get("/api/exercises")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 30
    slugs = {i["slug"] for i in items}
    assert {"push-up", "plank", "bodyweight-squat", "glute-bridge", "side-plank"} <= slugs
    sample = next(i for i in items if i["slug"] == "push-up")
    assert sample["image"] == "/exercises/push-up.svg"
    assert sample["instructions"] and sample["cues"]


def test_list_with_eva_key(client, eva_headers):
    r = client.get("/api/exercises", headers=eva_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 30


def test_get_one(auth_client):
    r = auth_client.get("/api/exercises/push-up")
    assert r.status_code == 200
    assert r.json()["name"] == "Push-up"
    assert r.json()["category"] == "push"


def test_get_unknown(auth_client):
    assert auth_client.get("/api/exercises/does-not-exist").status_code == 404


def test_catalog_integrity():
    slugs = [e["slug"] for e in EXERCISES]
    assert len(slugs) == len(set(slugs)), "slugs must be unique"
    for e in EXERCISES:
        assert e["category"] in VALID_CATEGORIES, e["slug"]
        assert e["difficulty"] in VALID_DIFFICULTY, e["slug"]
        assert isinstance(e["low_impact"], bool)
        assert e["instructions"], e["slug"]
        assert e["cues"], e["slug"]
        assert e["target"], e["slug"]


def test_seed_routine_exercises_have_valid_slugs(auth_client):
    """Every slug referenced by the seed routine exists in the catalog."""
    catalog = {e["slug"] for e in EXERCISES}
    routine = auth_client.get("/api/routine/current").json()
    for day in routine["days"]:
        for ex in day.get("exercises", []):
            if ex.get("slug"):
                assert ex["slug"] in catalog, ex["slug"]
