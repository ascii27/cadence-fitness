"""Application settings, loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Runtime
    env: str = "dev"  # dev | prod
    public_base_url: str = "http://localhost:8000"

    # Persistence
    database_url: str = "sqlite:///./cadence.db"

    # Web session / auth
    session_secret: str = "dev-insecure-session-secret-change-me"
    allowed_emails: str = ""  # comma-separated allowlist
    google_client_id: str = ""
    google_client_secret: str = ""
    # When true, /api/auth/dev-login issues a session without Google (dev/tests only).
    dev_auth_bypass: bool = True

    # Eva inbound
    eva_app_key: str = "eva-dev-key"

    # Jester outbound
    jester_base_url: str = ""
    jester_write_key: str = ""

    @property
    def allowed_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.allowed_emails.split(",") if e.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
