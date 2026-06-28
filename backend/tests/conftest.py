"""Test fixtures: isolated SQLite DB + authenticated client."""
from __future__ import annotations

import os
import tempfile

# Configure environment BEFORE importing the app (settings + engine read these).
_TMPDIR = tempfile.mkdtemp(prefix="cadence-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMPDIR}/test.db"
os.environ["DEV_AUTH_BYPASS"] = "true"
os.environ["ALLOWED_EMAILS"] = "test@example.com"
os.environ["EVA_APP_KEY"] = "test-eva-key"
os.environ["SESSION_SECRET"] = "test-secret"
os.environ["ENV"] = "dev"
os.environ["JESTER_BASE_URL"] = ""
os.environ["JESTER_WRITE_KEY"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, SessionLocal, create_all, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.seed import ensure_seed  # noqa: E402

EVA_KEY = "test-eva-key"


@pytest.fixture(autouse=True)
def fresh_db():
    """Reset schema + seed before each test for isolation."""
    Base.metadata.drop_all(engine)
    create_all()
    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client():
    c = TestClient(app)
    resp = c.post("/api/auth/dev-login")
    assert resp.status_code == 200
    return c


@pytest.fixture
def eva_headers():
    return {"Authorization": f"Bearer {EVA_KEY}"}
