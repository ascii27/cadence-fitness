"""Session endpoints: today derivation, readiness, logging, history."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_user
from ..db import get_db
from ..models import SessionLog, utcnow
from ..schemas import (
    LogCreateIn,
    LogPatchIn,
    LogSaveResult,
    ReadinessIn,
    SessionLogOut,
    TodayOut,
)
from ..services import outbox, streaks
from ..services.derive import (
    day_of_week_for,
    derive_session,
    get_current_routine,
    today_date,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

EDIT_WINDOW = timedelta(hours=24)


def _find_log_for_date(db: Session, session_date: str) -> SessionLog | None:
    return db.execute(
        select(SessionLog)
        .where(SessionLog.session_date == session_date)
        .order_by(SessionLog.logged_at.desc())
    ).scalars().first()


def _current_streak(db: Session) -> int:
    routine = get_current_routine(db)
    logs = db.execute(select(SessionLog)).scalars().all()
    return streaks.compute_current_streak(
        streaks.planned_days(routine),
        streaks.status_by_date(logs),
        today_date(),
    )


def _build_day(db: Session, d) -> TodayOut:
    """Derive the session for an arbitrary date, with its log if one exists."""
    date_str = d.isoformat()
    dow = day_of_week_for(d)
    routine = get_current_routine(db)
    existing = _find_log_for_date(db, date_str)
    readiness = existing.readiness if existing else None
    session = derive_session(routine, dow, readiness)
    log_out = None
    if existing and existing.status is not None:
        log_out = SessionLogOut.model_validate(existing)

    today = today_date()
    relativity = "today" if d == today else ("past" if d < today else "future")
    return TodayOut(
        session_date=date_str,
        session=session,
        log=log_out,
        readiness_answered=readiness is not None,
        streak=_current_streak(db),
        relativity=relativity,
    )


@router.get("/today", response_model=TodayOut)
async def today(_: str = Depends(require_user), db: Session = Depends(get_db)) -> TodayOut:
    return _build_day(db, today_date())


@router.get("/day/{date_str}", response_model=TodayOut)
async def day(
    date_str: str,
    _: str = Depends(require_user),
    db: Session = Depends(get_db),
) -> TodayOut:
    try:
        d = _parse(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date (expected YYYY-MM-DD)")
    return _build_day(db, d)


@router.post("/readiness", response_model=TodayOut)
async def set_readiness(
    body: ReadinessIn,
    _: str = Depends(require_user),
    db: Session = Depends(get_db),
) -> TodayOut:
    d = today_date() if not body.session_date else None
    date_str = body.session_date or d.isoformat()
    dow = day_of_week_for(today_date() if not body.session_date else _parse(body.session_date))
    routine = get_current_routine(db)

    logentry = _find_log_for_date(db, date_str)
    if logentry is None:
        logentry = SessionLog(
            session_date=date_str,
            day_of_week=dow,
            session_type=derive_session(routine, dow).session_type,
        )
        db.add(logentry)
    logentry.readiness = body.readiness
    if body.readiness == "joint_pain":
        logentry.swap_reason = "joint_pain"
    db.commit()

    session = derive_session(routine, dow, body.readiness)
    return TodayOut(
        session_date=date_str,
        session=session,
        log=SessionLogOut.model_validate(logentry) if logentry.status else None,
        readiness_answered=True,
        streak=_current_streak(db),
    )


def _parse(date_str: str):
    from datetime import date

    return date.fromisoformat(date_str)


@router.post("/log", response_model=LogSaveResult)
async def create_log(
    body: LogCreateIn,
    _: str = Depends(require_user),
    db: Session = Depends(get_db),
) -> LogSaveResult:
    date_str = body.session_date or today_date().isoformat()
    dow = day_of_week_for(_parse(date_str))
    routine = get_current_routine(db)
    version = routine.version if routine else None
    derived = derive_session(routine, dow)

    logentry = _find_log_for_date(db, date_str)
    if logentry is None:
        logentry = SessionLog(session_date=date_str, day_of_week=dow)
        db.add(logentry)
        logentry.logged_at = utcnow()

    logentry.session_type = body.session_type or (logentry.session_type or derived.session_type)
    logentry.label = body.label or logentry.label or derived.label
    logentry.status = body.status
    logentry.duration_minutes = body.duration_minutes
    logentry.rounds_completed = body.rounds_completed
    logentry.rating = body.rating
    logentry.notes = body.notes
    if body.swap_reason:
        logentry.swap_reason = body.swap_reason
    logentry.source = "manual"
    logentry.routine_version = version
    db.flush()

    # Outbox: workout_logged always; milestone if a threshold was reached.
    outbox.enqueue(db, "workout_logged", outbox.workout_logged_payload(logentry))
    db.commit()

    streak = _current_streak(db)
    hit = streaks.milestone_hit(streak)
    if hit is not None:
        outbox.enqueue(db, "milestone", outbox.milestone_payload(hit, logentry))
        db.commit()

    db.refresh(logentry)
    return LogSaveResult(
        log=SessionLogOut.model_validate(logentry),
        streak=streak,
        milestone_hit=hit,
    )


@router.patch("/{log_id}", response_model=SessionLogOut)
async def patch_log(
    log_id: str,
    body: LogPatchIn,
    _: str = Depends(require_user),
    db: Session = Depends(get_db),
) -> SessionLogOut:
    logentry = db.get(SessionLog, log_id)
    if logentry is None:
        raise HTTPException(status_code=404, detail="Log not found")
    if utcnow() - logentry.logged_at > EDIT_WINDOW:
        raise HTTPException(status_code=409, detail="Edit window (24h) has passed")
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(logentry, key, value)
    db.commit()
    db.refresh(logentry)
    return SessionLogOut.model_validate(logentry)


@router.get("", response_model=list[SessionLogOut])
async def list_logs(
    _: str = Depends(require_user),
    db: Session = Depends(get_db),
    session_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[SessionLogOut]:
    stmt = select(SessionLog).order_by(SessionLog.session_date.desc())
    if session_type:
        stmt = stmt.where(SessionLog.session_type == session_type)
    stmt = stmt.limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()
    return [SessionLogOut.model_validate(r) for r in rows]
