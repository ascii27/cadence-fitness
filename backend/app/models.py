"""SQLAlchemy ORM models for Cadence Phase 1."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    # Naive UTC: SQLite does not persist tzinfo, so we keep all timestamps naive
    # to avoid aware/naive comparison errors.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Routine(Base):
    __tablename__ = "routines"

    routine_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    source: Mapped[str] = mapped_column(String, nullable=False)  # eva | seed
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    days: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # Set when an Eva update is applied; cleared once the user acknowledges (Keep).
    eva_applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=True)


class Goals(Base):
    __tablename__ = "goals"

    # Single-row table.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    goals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    constraints: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_by: Mapped[str] = mapped_column(String, default="seed")  # eva | user | seed


class SessionLog(Base):
    __tablename__ = "session_logs"

    log_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    session_date: Mapped[str] = mapped_column(String, nullable=False, index=True)  # YYYY-MM-DD
    day_of_week: Mapped[str] = mapped_column(String, nullable=False)
    session_type: Mapped[str] = mapped_column(String, nullable=False)  # run|strength|mobility|rest
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True)  # completed|partial|missed|swapped
    swap_reason: Mapped[str | None] = mapped_column(String, nullable=True)  # joint_pain|tired|null
    readiness: Mapped[str | None] = mapped_column(String, nullable=True)  # great|tired|joint_pain|null
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rounds_completed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String, default="manual")  # manual | healthkit
    health_metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    routine_version: Mapped[int | None] = mapped_column(Integer, nullable=True)


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    outbox_id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    event_type: Mapped[str] = mapped_column(String, nullable=False)  # workout_logged|milestone|routine_reverted
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String, default="pending", index=True)  # pending|sent|failed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
