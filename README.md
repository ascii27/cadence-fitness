# Cadence

A goal-driven fitness habit engine. Cadence surfaces a training routine, captures what the user
actually did, and reports progress — but it holds **no coaching logic of its own**. The routine is
data, tuned over time by a remote agent (**Eva**, on Hermes); adherence is streamed out as events to
**Jester** so Eva can sense how things are going and retune.

**Live:** https://cadence-fitness.exe.xyz · **Status:** Phase 1 complete (web + backend)

---

## What it does

- **Before a session** — shows today's plan derived from the current routine, plus a readiness check
  (Great / Tired but OK / Joint pain). Joint pain swaps the session for a 15-min mobility block —
  joint longevity is the user's binding constraint.
- **After a session** — manual logging (status, duration, AMRAP rounds, 1–5 rating, notes); editable
  within 24h; any past date can be logged.
- **Over time** — adherence streaks, a 12-week calendar heatmap, weekly summaries.
- **Integrations** — Eva replaces the routine / updates goals via an authenticated API; every log
  emits a `workout_logged` event to Jester (plus `milestone` and `routine_reverted`).
- **Offline-first logging** — log submissions are queued in IndexedDB and synced on reconnect; a
  service worker caches the app shell.

Phase 2 (iOS + Apple Watch, HealthKit/WorkoutKit) is out of scope here but the data model and event
payloads are Phase-2-ready (`health_metrics` are null in Phase 1).

## Architecture

A single service: **FastAPI serves both the JSON API and the built React SPA** on one port. exe.dev's
proxy terminates TLS — there is no separate web server.

```
Internet ──TLS──> exe.dev proxy ──http──> uvicorn :8000 ──┬── /api/*  (FastAPI)
                                                          └── /*      (Vite SPA + index.html fallback)

   Eva  ──PUT/PATCH/GET  /api/{routine,goals,state}  (Bearer EVA_APP_KEY) ──▶  Cadence
Cadence ──outbox──▶  POST {JESTER_BASE_URL}/api/item/cadence_event  (Bearer JESTER_WRITE_KEY) ──▶ Jester ──▶ Eva
```

### Tech stack

| Layer | Stack |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (SQLite), Pydantic, Authlib, httpx; `uv` |
| Frontend | React 18 + Vite + TypeScript, Tailwind v4, React Router, TanStack Query, IndexedDB |
| Auth | Google OAuth (web, single allowlisted user) · `EVA_APP_KEY` bearer (Eva) · `JESTER_WRITE_KEY` (Jester) |
| Host | exe.dev VM `cadence-fitness`, systemd-managed |

## Repository layout

```
backend/
  app/
    main.py            FastAPI app: routers, session auth, SPA mount, outbox worker lifespan
    config.py          Settings (pydantic-settings, .env)
    db.py  models.py   SQLAlchemy engine + ORM (Routine, Goals, SessionLog, OutboxEvent)
    schemas.py         Pydantic request/response models
    auth.py            Google OAuth flow + session cookie; require_user / require_eva deps
    routers/           routines, goals, sessions, adherence, state, health, auth
    services/          derive (today), streaks, seed, jester (client), outbox (worker)
  tests/               pytest (36 tests) over a temp SQLite DB
frontend/
  src/
    pages/             Today, Log, History, Goals, Settings
    components/        SessionCard, ReadinessCheck, LogForm bits, CalendarHeatmap, EvaUpdateBanner, …
    lib/               api client, queries (TanStack), offlineQueue (IndexedDB), useOfflineSync, format
    main.tsx App.tsx   root, routing, auth gate, shell
  public/sw.js         app-shell service worker
  tests/               Vitest (offline queue + components)
deploy/
  cadence.service      systemd unit
  deploy.sh            build SPA → bundle into backend → rsync to VM → restart → health check
  .env.example         environment template
docs/
  cadence-event-contract.md                      consumer guide for Hermes/Eva
  superpowers/specs/2026-06-28-cadence-phase1-design.md   design of record
```

## Local development

Prereqs: Python 3.12+, [`uv`](https://docs.astral.sh/uv/), Node 18+.

```bash
# Backend (terminal 1) — http://localhost:8000
cd backend
uv sync
DEV_AUTH_BYPASS=true ALLOWED_EMAILS=you@example.com EVA_APP_KEY=dev-eva \
  uv run uvicorn app.main:app --reload

# Frontend (terminal 2) — http://localhost:5173 (proxies /api to :8000)
cd frontend
npm install
npm run dev
```

In dev, `DEV_AUTH_BYPASS=true` enables `POST /api/auth/dev-login`, which mints a session without
Google so you can work without OAuth credentials. **This must be `false` in production** — see Auth.

### Tests

```bash
cd backend  && uv run pytest        # 36 tests
cd frontend && npm test             # 9 tests (Vitest)
cd frontend && npm run build        # type-check + production build
```

## Deployment

Target: the exe.dev VM `cadence-fitness` (`https://cadence-fitness.exe.xyz`, public proxy, TLS by
exe.dev). The app data (SQLite) and `.env` live in `/home/exedev/cadence/` on the VM's persistent disk.

```bash
# One-time on the VM: create ~/cadence/.env from deploy/.env.example and fill in secrets.
# Then, from a clone with SSH access to the VM:
./deploy/deploy.sh
```

`deploy.sh` builds the SPA, bundles it into `backend/static/`, rsyncs the backend to the VM, installs
the systemd unit, `uv sync`s, restarts `cadence.service`, and curls `/api/health`.

```bash
ssh cadence-fitness.exe.xyz 'systemctl status cadence.service'        # service state
ssh cadence-fitness.exe.xyz 'journalctl -u cadence.service -f'        # live logs
```

## Configuration

Environment (see `deploy/.env.example`):

| var | purpose |
|---|---|
| `ENV` | `dev` \| `prod` (prod → secure cookies) |
| `PUBLIC_BASE_URL` | external URL, used to build the OAuth redirect |
| `DATABASE_URL` | SQLite path (absolute on the VM) |
| `SESSION_SECRET` | signs the session cookie |
| `ALLOWED_EMAILS` | comma-separated allowlist for Google sign-in |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth web client |
| `DEV_AUTH_BYPASS` | enables `/api/auth/dev-login`; **must be `false` in prod** |
| `EVA_APP_KEY` | bearer key Eva uses for inbound calls |
| `JESTER_BASE_URL` / `JESTER_WRITE_KEY` | outbound event delivery to Jester |

## API

All app endpoints require a signed-in session except `/api/health` (open) and the Eva endpoints
(which require `Authorization: Bearer {EVA_APP_KEY}`).

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/health` | none | healthcheck |
| GET | `/api/auth/login` → `/api/auth/google/callback` | none | Google OAuth |
| GET / POST | `/api/auth/me` · `/api/auth/logout` | session | current user / sign out |
| GET | `/api/sessions/today` | session | today's derived session + log + streak |
| POST | `/api/sessions/readiness` | session | record readiness (may swap to mobility) |
| POST | `/api/sessions/log` | session | create a log (emits `workout_logged`, maybe `milestone`) |
| PATCH | `/api/sessions/{log_id}` | session | edit a log within 24h |
| GET | `/api/sessions` | session | paginated history (filter by type) |
| GET | `/api/adherence` | session | current/longest streak + weekly summary |
| GET | `/api/routine/current` · `/history` | session | active routine (+ Eva-banner flag) / versions |
| POST | `/api/routine/revert` · `/acknowledge` | session | revert (≤7 days, emits `routine_reverted`) / dismiss banner |
| GET | `/api/goals` | session | current goals + constraints |
| PUT | `/api/routine` | **Eva** | replace routine (new version + reason) |
| PATCH | `/api/goals` | **Eva** | update goals / constraints |
| GET | `/api/state` | **Eva** | catch-up summary: routine version, last log date, 30-day adherence |

## Auth model

- **Web users** sign in with **Google OAuth**, restricted to `ALLOWED_EMAILS` (single-user). On
  success a signed, HttpOnly session cookie is set. Because the URL is public, the dev-login bypass is
  disabled in prod (`DEV_AUTH_BYPASS=false`).
- **Eva** authenticates inbound calls with `Authorization: Bearer {EVA_APP_KEY}`.
- **Jester** delivery uses `Authorization: Bearer {JESTER_WRITE_KEY}` outbound.

## Eva ⇄ Jester integration

- **Outbound (Cadence → Jester → Eva):** every saved log writes an event to a durable **outbox**; a
  background worker delivers it to Jester (`POST /api/item/cadence_event`) with retries and
  exponential backoff. All three event kinds — `workout_logged`, `milestone`, `routine_reverted` —
  share the single `cadence_event` item type, discriminated by an `event_type` field in an envelope.
  Delivery is **at-least-once**; consumers must dedupe.
- **Inbound (Eva → Cadence):** Eva replaces the routine, updates goals, and reads adherence state via
  the Eva-keyed endpoints above. Routine updates auto-apply with a 7-day revert window.

See **[`docs/cadence-event-contract.md`](docs/cadence-event-contract.md)** for the full event
contract and how Hermes/Eva should handle each kind, and
**[`docs/superpowers/specs/2026-06-28-cadence-phase1-design.md`](docs/superpowers/specs/2026-06-28-cadence-phase1-design.md)**
for the design of record.

## License

See [LICENSE](LICENSE).
