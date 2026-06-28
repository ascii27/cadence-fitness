"""Authentication: Google OAuth web sign-in + Eva bearer-key gate.

Web users sign in with Google; only allowlisted emails get a session cookie.
Eva authenticates inbound calls with a static bearer key.
A dev test-session bypass keeps the app testable without live Google.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from .config import Settings, get_settings
from .schemas import MeOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

_oauth = None


def _get_oauth(settings: Settings):
    """Lazily build an Authlib OAuth client if Google credentials are present."""
    global _oauth
    if _oauth is not None:
        return _oauth
    if not settings.google_client_id or not settings.google_client_secret:
        return None
    from authlib.integrations.starlette_client import OAuth

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    _oauth = oauth
    return _oauth


# ---- Dependencies ----
def require_user(request: Request) -> str:
    """Return the signed-in user's email or raise 401."""
    email = request.session.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return email


def require_eva(request: Request, settings: Settings = Depends(get_settings)) -> bool:
    """Validate the Eva bearer key on inbound integration endpoints."""
    auth = request.headers.get("authorization", "")
    expected = f"Bearer {settings.eva_app_key}"
    if not settings.eva_app_key or auth != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Eva key")
    return True


# ---- Routes ----
@router.get("/login")
async def login(request: Request, settings: Settings = Depends(get_settings)):
    oauth = _get_oauth(settings)
    if oauth is None:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    redirect_uri = f"{settings.public_base_url}/api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, settings: Settings = Depends(get_settings)):
    oauth = _get_oauth(settings)
    if oauth is None:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo") or {}
    email = (userinfo.get("email") or "").lower()
    if not email or (settings.allowed_email_set and email not in settings.allowed_email_set):
        raise HTTPException(status_code=403, detail="Email not allowed")
    request.session["email"] = email
    return RedirectResponse(url="/")


@router.post("/dev-login")
async def dev_login(request: Request, settings: Settings = Depends(get_settings)):
    """Issue a session without Google. Available only when dev_auth_bypass is on."""
    if not settings.dev_auth_bypass:
        raise HTTPException(status_code=404, detail="Not found")
    email = next(iter(settings.allowed_email_set), "dev@example.com")
    request.session["email"] = email
    return JSONResponse({"email": email})


@router.get("/me", response_model=MeOut)
async def me(email: str = Depends(require_user)) -> MeOut:
    return MeOut(email=email)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return JSONResponse({"ok": True})
