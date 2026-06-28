"""Exercise catalog endpoint — the set Eva selects from (and the app renders)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_user_or_eva
from ..data.exercises import EXERCISES, by_slug
from ..schemas import CatalogExercise

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


def _to_out(ex: dict) -> CatalogExercise:
    return CatalogExercise(
        slug=ex["slug"],
        name=ex["name"],
        category=ex["category"],
        target=ex["target"],
        difficulty=ex["difficulty"],
        low_impact=ex["low_impact"],
        equipment=ex.get("equipment", "none"),
        unit=ex["unit"],
        instructions=ex["instructions"],
        cues=ex["cues"],
        image=f"/exercises/{ex['slug']}.svg",
    )


@router.get("", response_model=list[CatalogExercise])
async def list_exercises(_: str = Depends(require_user_or_eva)) -> list[CatalogExercise]:
    return [_to_out(ex) for ex in EXERCISES]


@router.get("/{slug}", response_model=CatalogExercise)
async def get_exercise(slug: str, _: str = Depends(require_user_or_eva)) -> CatalogExercise:
    ex = by_slug(slug)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return _to_out(ex)
