"""FastAPI application: API routers, session auth, SPA serving, outbox worker."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from . import auth
from .config import get_settings
from .db import SessionLocal, create_all
from .routers import adherence, goals, health, routines, sessions, state
from .services import outbox
from .services.seed import ensure_seed

# Built SPA lives here in production (frontend `npm run build` output copied in).
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()

    stop_event = asyncio.Event()
    worker = asyncio.create_task(outbox.worker_loop(SessionLocal, stop_event))
    app.state.outbox_stop = stop_event
    app.state.outbox_worker = worker
    try:
        yield
    finally:
        stop_event.set()
        worker.cancel()
        try:
            await worker
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Cadence", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        same_site="lax",
        https_only=(settings.env == "prod"),
        max_age=60 * 60 * 24 * 30,
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(routines.router)
    app.include_router(goals.router)
    app.include_router(sessions.router)
    app.include_router(adherence.router)
    app.include_router(state.router)

    _mount_spa(app)
    return app


def _mount_spa(app: FastAPI) -> None:
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    index_file = STATIC_DIR / "index.html"

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # API routes are matched before this catch-all; anything else serves the SPA.
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        if index_file.is_file():
            return FileResponse(index_file)
        return JSONResponse(
            {"detail": "SPA not built. Run the frontend dev server or build it."},
            status_code=200,
        )


app = create_app()
