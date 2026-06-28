"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ---- Routine ----
class Exercise(BaseModel):
    name: str
    reps: Optional[int] = None
    note: Optional[str] = None


class RoutineDay(BaseModel):
    day_of_week: str
    session_type: str  # strength | run | mobility | rest
    label: Optional[str] = None
    modality: Optional[str] = None  # amrap | continuous
    duration_minutes: Optional[int] = None
    exercises: list[Exercise] = Field(default_factory=list)
    hr_zone: Optional[str] = None
    hr_cap_bpm: Optional[int] = None
    progression_rule: Optional[str] = None


class RoutineOut(BaseModel):
    routine_id: str
    version: int
    created_at: datetime
    source: str
    reason: Optional[str] = None
    days: list[RoutineDay]
    is_current: bool
    # Eva-banner signal: present + unacknowledged Eva update within revert window.
    eva_update_pending: bool = False
    eva_applied_at: Optional[datetime] = None


class RoutineReplaceIn(BaseModel):
    reason: Optional[str] = None
    days: list[RoutineDay]


# ---- Goals ----
class GoalsOut(BaseModel):
    goals: list[str]
    constraints: dict[str, Any]
    updated_at: datetime
    updated_by: str


class GoalsPatchIn(BaseModel):
    goals: Optional[list[str]] = None
    constraints: Optional[dict[str, Any]] = None


# ---- Sessions ----
class HealthMetrics(BaseModel):
    avg_hr_bpm: Optional[int] = None
    max_hr_bpm: Optional[int] = None
    active_energy_kcal: Optional[int] = None
    hrv_ms: Optional[int] = None


class DerivedSession(BaseModel):
    day_of_week: str
    session_type: str
    label: Optional[str] = None
    modality: Optional[str] = None
    duration_minutes: Optional[int] = None
    exercises: list[Exercise] = Field(default_factory=list)
    hr_zone: Optional[str] = None
    hr_cap_bpm: Optional[int] = None
    progression_rule: Optional[str] = None
    is_rest: bool = False
    swapped: bool = False
    swap_reason: Optional[str] = None
    routine_version: Optional[int] = None


class SessionLogOut(BaseModel):
    log_id: str
    logged_at: datetime
    session_date: str
    day_of_week: str
    session_type: str
    label: Optional[str] = None
    status: Optional[str] = None
    swap_reason: Optional[str] = None
    readiness: Optional[str] = None
    duration_minutes: Optional[int] = None
    rounds_completed: Optional[int] = None
    rating: Optional[int] = None
    notes: Optional[str] = None
    source: str
    health_metrics: dict[str, Any] = Field(default_factory=dict)
    routine_version: Optional[int] = None

    model_config = {"from_attributes": True}


class TodayOut(BaseModel):
    session_date: str
    session: DerivedSession
    log: Optional[SessionLogOut] = None
    readiness_answered: bool = False
    streak: int = 0
    relativity: Literal["past", "today", "future"] = "today"


class ReadinessIn(BaseModel):
    readiness: Literal["great", "tired", "joint_pain"]
    session_date: Optional[str] = None  # defaults to today


class LogCreateIn(BaseModel):
    status: Literal["completed", "partial", "missed", "swapped"]
    duration_minutes: int
    session_date: Optional[str] = None  # defaults to today; allows past-date logging
    session_type: Optional[str] = None
    label: Optional[str] = None
    rounds_completed: Optional[int] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = None
    swap_reason: Optional[str] = None


class LogPatchIn(BaseModel):
    status: Optional[Literal["completed", "partial", "missed", "swapped"]] = None
    duration_minutes: Optional[int] = None
    rounds_completed: Optional[int] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = None


class LogSaveResult(BaseModel):
    log: SessionLogOut
    streak: int
    milestone_hit: Optional[int] = None


# ---- Adherence / State ----
class WeeklySummary(BaseModel):
    week_start: str
    planned: int
    completed: int


class AdherenceOut(BaseModel):
    current_streak: int
    longest_streak: int
    weeks: list[WeeklySummary]


class StateOut(BaseModel):
    routine_version: int
    last_log_date: Optional[str] = None
    adherence_30d: dict[str, Any]


class MeOut(BaseModel):
    email: str
