"""Routine endpoints: current/history/revert/acknowledge (user) + replace (Eva)."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_eva, require_user
from ..db import get_db
from ..models import Routine, utcnow
from ..schemas import RoutineOut, RoutineReplaceIn
from ..services import outbox
from ..services.derive import get_current_routine

router = APIRouter(prefix="/api/routine", tags=["routine"])

REVERT_WINDOW = timedelta(days=7)


def to_out(routine: Routine) -> RoutineOut:
    pending = False
    if routine.source == "eva" and not routine.acknowledged and routine.eva_applied_at:
        pending = (utcnow() - routine.eva_applied_at) <= REVERT_WINDOW
    return RoutineOut(
        routine_id=routine.routine_id,
        version=routine.version,
        created_at=routine.created_at,
        source=routine.source,
        reason=routine.reason,
        days=routine.days,
        is_current=routine.is_current,
        eva_update_pending=pending,
        eva_applied_at=routine.eva_applied_at,
    )


@router.get("/current", response_model=RoutineOut)
async def current(_: str = Depends(require_user), db: Session = Depends(get_db)) -> RoutineOut:
    routine = get_current_routine(db)
    if routine is None:
        raise HTTPException(status_code=404, detail="No routine")
    return to_out(routine)


@router.get("/history", response_model=list[RoutineOut])
async def history(_: str = Depends(require_user), db: Session = Depends(get_db)) -> list[RoutineOut]:
    rows = db.execute(select(Routine).order_by(Routine.version.desc())).scalars().all()
    return [to_out(r) for r in rows]


@router.post("/acknowledge", response_model=RoutineOut)
async def acknowledge(_: str = Depends(require_user), db: Session = Depends(get_db)) -> RoutineOut:
    routine = get_current_routine(db)
    if routine is None:
        raise HTTPException(status_code=404, detail="No routine")
    routine.acknowledged = True
    db.commit()
    db.refresh(routine)
    return to_out(routine)


@router.post("/revert", response_model=RoutineOut)
async def revert(_: str = Depends(require_user), db: Session = Depends(get_db)) -> RoutineOut:
    current_routine = get_current_routine(db)
    if current_routine is None:
        raise HTTPException(status_code=404, detail="No routine")
    if current_routine.eva_applied_at and (utcnow() - current_routine.eva_applied_at) > REVERT_WINDOW:
        raise HTTPException(status_code=409, detail="Revert window has passed")
    previous = db.execute(
        select(Routine)
        .where(Routine.version < current_routine.version)
        .order_by(Routine.version.desc())
    ).scalars().first()
    if previous is None:
        raise HTTPException(status_code=409, detail="No previous routine to revert to")

    current_routine.is_current = False
    current_routine.acknowledged = True
    previous.is_current = True
    outbox.enqueue(
        db,
        "routine_reverted",
        outbox.routine_reverted_payload(current_routine.version, previous.version),
    )
    db.commit()
    db.refresh(previous)
    return to_out(previous)


@router.put("", response_model=RoutineOut)
@router.put("/", response_model=RoutineOut)
async def replace(
    body: RoutineReplaceIn,
    _: bool = Depends(require_eva),
    db: Session = Depends(get_db),
) -> RoutineOut:
    max_version = db.execute(select(Routine.version).order_by(Routine.version.desc())).scalars().first() or 0
    # Demote the existing current routine.
    existing = get_current_routine(db)
    if existing is not None:
        existing.is_current = False
    new = Routine(
        version=max_version + 1,
        source="eva",
        reason=body.reason,
        days=[d.model_dump() for d in body.days],
        is_current=True,
        eva_applied_at=utcnow(),
        acknowledged=False,
    )
    db.add(new)
    db.commit()
    db.refresh(new)
    return to_out(new)
