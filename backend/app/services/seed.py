"""Seed data: the PRD §6 routine and default goals, loaded on first run."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Goals, Routine

DAYS_ORDER = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

# 15-min mobility block substituted when the user reports joint pain.
MOBILITY_SWAP = {
    "session_type": "mobility",
    "label": "Mobility & Stretch",
    "modality": "continuous",
    "duration_minutes": 15,
    "exercises": [
        {"name": "Full-body stretch flow", "reps": None, "note": "gentle, pain-free range"},
    ],
}

SEED_DAYS = [
    {
        "day_of_week": "monday",
        "session_type": "strength",
        "label": "Upper Body & Core",
        "modality": "amrap",
        "duration_minutes": 15,
        "exercises": [
            {"name": "Push-ups", "reps": None, "note": "max reps per round", "slug": "push-up"},
            {"name": "Plank", "reps": None, "note": "30 sec hold", "slug": "plank"},
        ],
    },
    {
        "day_of_week": "tuesday",
        "session_type": "rest",
        "label": "Rest",
    },
    {
        "day_of_week": "wednesday",
        "session_type": "run",
        "label": "Mid-week Run",
        "modality": "continuous",
        "duration_minutes": 52,
        "hr_zone": None,
    },
    {
        "day_of_week": "thursday",
        "session_type": "run",
        "label": "Easy Run",
        "modality": "continuous",
        "duration_minutes": 35,
        "hr_zone": "easy",
        "hr_cap_bpm": 145,
    },
    {
        "day_of_week": "friday",
        "session_type": "strength",
        "label": "Lower Body & Core",
        "modality": "amrap",
        "duration_minutes": 15,
        "exercises": [
            {"name": "Bodyweight squats", "reps": None, "note": "max reps per round", "slug": "bodyweight-squat"},
            {"name": "Glute bridge", "reps": None, "note": "max reps per round", "slug": "glute-bridge"},
            {"name": "Side plank", "reps": None, "note": "30 sec each side", "slug": "side-plank"},
        ],
    },
    {
        "day_of_week": "saturday",
        "session_type": "run",
        "label": "Long Run",
        "modality": "continuous",
        "duration_minutes": 50,
        "hr_zone": None,
        "progression_rule": "+10%/week, deload every 4th",
    },
    {
        "day_of_week": "sunday",
        "session_type": "rest",
        "label": "Rest",
    },
]

SEED_GOALS = ["marathon_build", "upper_body_strength", "fat_loss", "joint_longevity"]
SEED_CONSTRAINTS = {
    "rest_days": ["tuesday", "sunday"],
    "strength_cap_minutes": 20,
}


def ensure_seed(db: Session) -> None:
    """Load the seed routine and goals if none exist yet."""
    has_routine = db.execute(select(Routine.routine_id).limit(1)).first()
    if not has_routine:
        db.add(
            Routine(
                version=1,
                source="seed",
                reason="Initial seed routine",
                days=SEED_DAYS,
                is_current=True,
                acknowledged=True,
            )
        )

    has_goals = db.execute(select(Goals.id).limit(1)).first()
    if not has_goals:
        db.add(
            Goals(
                id=1,
                goals=SEED_GOALS,
                constraints=SEED_CONSTRAINTS,
                updated_by="seed",
            )
        )
    db.commit()
