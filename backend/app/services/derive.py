"""Derive today's session from the current routine, applying readiness swaps."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Routine
from ..schemas import DerivedSession, Exercise
from .seed import MOBILITY_SWAP


def today_date() -> date:
    return datetime.now().date()


def day_of_week_for(d: date) -> str:
    return d.strftime("%A").lower()


def get_current_routine(db: Session) -> Routine | None:
    return db.execute(
        select(Routine).where(Routine.is_current.is_(True))
    ).scalars().first()


def _day_from_routine(routine: Routine, day_of_week: str) -> dict | None:
    for day in routine.days:
        if day.get("day_of_week") == day_of_week:
            return day
    return None


def derive_session(
    routine: Routine | None,
    day_of_week: str,
    readiness: str | None = None,
) -> DerivedSession:
    """Build the session for a given weekday, applying a mobility swap on joint pain."""
    version = routine.version if routine else None

    # Joint pain → substitute a mobility block regardless of the planned session.
    if readiness == "joint_pain":
        return DerivedSession(
            day_of_week=day_of_week,
            session_type=MOBILITY_SWAP["session_type"],
            label=MOBILITY_SWAP["label"],
            modality=MOBILITY_SWAP["modality"],
            duration_minutes=MOBILITY_SWAP["duration_minutes"],
            exercises=[Exercise(**e) for e in MOBILITY_SWAP["exercises"]],
            is_rest=False,
            swapped=True,
            swap_reason="joint_pain",
            routine_version=version,
        )

    day = _day_from_routine(routine, day_of_week) if routine else None
    if day is None or day.get("session_type") == "rest":
        return DerivedSession(
            day_of_week=day_of_week,
            session_type="rest",
            label=(day.get("label") if day else "Rest") or "Rest",
            is_rest=True,
            routine_version=version,
        )

    return DerivedSession(
        day_of_week=day_of_week,
        session_type=day.get("session_type"),
        label=day.get("label"),
        modality=day.get("modality"),
        duration_minutes=day.get("duration_minutes"),
        exercises=[Exercise(**e) for e in day.get("exercises", [])],
        hr_zone=day.get("hr_zone"),
        hr_cap_bpm=day.get("hr_cap_bpm"),
        progression_rule=day.get("progression_rule"),
        is_rest=False,
        routine_version=version,
    )
