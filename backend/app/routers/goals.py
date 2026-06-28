"""Goals endpoints: GET (user) + PATCH (Eva)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_eva, require_user
from ..db import get_db
from ..models import Goals, utcnow
from ..schemas import GoalsOut, GoalsPatchIn

router = APIRouter(prefix="/api/goals", tags=["goals"])


def _get_goals(db: Session) -> Goals | None:
    return db.execute(select(Goals).limit(1)).scalars().first()


@router.get("", response_model=GoalsOut)
async def get_goals(_: str = Depends(require_user), db: Session = Depends(get_db)) -> GoalsOut:
    goals = _get_goals(db)
    if goals is None:
        raise HTTPException(status_code=404, detail="No goals")
    return GoalsOut(
        goals=goals.goals,
        constraints=goals.constraints,
        updated_at=goals.updated_at,
        updated_by=goals.updated_by,
    )


@router.patch("", response_model=GoalsOut)
@router.patch("/", response_model=GoalsOut)
async def patch_goals(
    body: GoalsPatchIn,
    _: bool = Depends(require_eva),
    db: Session = Depends(get_db),
) -> GoalsOut:
    goals = _get_goals(db)
    if goals is None:
        goals = Goals(id=1, goals=[], constraints={})
        db.add(goals)
    if body.goals is not None:
        goals.goals = body.goals
    if body.constraints is not None:
        goals.constraints = body.constraints
    goals.updated_by = "eva"
    goals.updated_at = utcnow()
    db.commit()
    db.refresh(goals)
    return GoalsOut(
        goals=goals.goals,
        constraints=goals.constraints,
        updated_at=goals.updated_at,
        updated_by=goals.updated_by,
    )
