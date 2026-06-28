# Cadence — Phase 1 Design (Web + Backend)

**Date:** 2026-06-28 · **Status:** Approved for planning · **Supersedes PRD where noted**
**Source PRD:** Cadence Fitness Engine v5 (in conversation)

---

## 1. Scope

Build the **complete Phase 1** (PRD milestones 1.1–1.9): FastAPI + SQLite backend, React + Vite
web app, Eva inbound API, Jester outbound (outbox), readiness/swap, manual logging, history +
adherence, goals view, and offline reliability. Phase 2 (iOS/Watch/HealthKit) is out of scope but
the data model and Jester events are built Phase-2-ready (null `health_metrics` now).

Deployment target: the existing exe.dev VM **`cadence-fitness`** → `https://cadence-fitness.exe.xyz`
(LAX, port 8000, proxy now **public**).

### Decisions locked in this design

| # | Decision | Resolution |
|:--|:--|:--|
| Scope | Phase 1 milestones | All of 1.1–1.9 |
| Host | Where it runs | exe.dev `cadence-fitness` VM from day one |
| Frontend | Framework | React + Vite + TypeScript + Tailwind |
| Proxy/TLS | Caddy? | **No Caddy** — exe.dev proxy terminates TLS and forwards to :8000 |
| Auth (web) | How users sign in | **Google OAuth**, restricted to a single allowlisted email (proxy is public) |
| Auth (Eva) | Inbound auth | `EVA_APP_KEY` bearer token (generated below) |
| Auth (Jester) | Outbound auth | `JESTER_WRITE_KEY` bearer (provided by Michael) |
| Integrations | Real vs stub | Real endpoints; Jester base URL configurable + local stub for dev/test |
| Topology | Services | Single FastAPI service serves API **and** built SPA; one systemd unit |

This **supersedes** PRD §8.7 (static `APP_TOKEN` cookie) and the Phase-2 OAuth deferral in §11/§16:
web sign-in is Google OAuth in Phase 1. `APP_TOKEN` is removed.

---

## 2. Deployment Topology

- **One process, one port.** FastAPI serves `/api/*` and serves the built Vite assets for all other
  paths, with SPA fallback to `index.html`. No second web server, no CORS in production.
- **TLS/HTTPS** provided by exe.dev's proxy (`https://cadence-fitness.exe.xyz` → `127.0.0.1:8000`).
- **Process supervision:** a `systemd` unit (`cadence.service`) runs `uvicorn` on :8000, restarts on
  failure, starts on boot.
- **Dev mode:** backend on :8000 via `uvicorn --reload`; frontend on Vite dev server with `/api`
  proxied to :8000. Production build emits static assets consumed by FastAPI.
- **Data:** SQLite file at `~/cadence/cadence.db` on the VM's persistent disk. Manual backup =
  copy the file.

```
Internet ──TLS──> exe.dev proxy ──http──> uvicorn :8000 ──┬── /api/*  (FastAPI)
                                                          └── /*      (SPA static + fallback)
```

---

## 3. Repo Structure (monorepo)

```
cadence-fitness/
  backend/
    app/
      main.py            # FastAPI app, startup (seed, schema, outbox worker), SPA mount
      db.py              # SQLAlchemy engine/session, create_all
      models.py          # ORM models: Routine, Goals, SessionLog, OutboxEvent
      schemas.py         # Pydantic request/response models
      auth.py            # Google OAuth flow, session cookie, deps (require_user, require_eva)
      deps.py            # shared dependencies
      routers/
        routines.py      # current/history/revert (user) + PUT replace (Eva)
        goals.py         # GET (user) + PATCH (Eva)
        sessions.py      # today, log create, edit-within-24h, history
        adherence.py     # streak + weekly summary
        state.py         # Eva summary (GET, Eva key)
        auth_routes.py   # /api/auth/login, /callback, /logout, /me
        health.py        # /api/health (open)
      services/
        derive.py        # today's session from routine by day_of_week + readiness swap
        streaks.py       # streak + milestone computation
        seed.py          # §6 seed routine loader
        jester.py        # Jester HTTP client
        outbox.py        # outbox model ops + background drain worker
    tests/               # pytest (httpx against app, temp sqlite)
    pyproject.toml       # uv-managed
  frontend/
    src/
      pages/             # Today, Log, History, Goals, Settings
      components/        # SessionCard, ReadinessCheck, LogForm, CalendarHeatmap, EvaUpdateBanner, OfflineIndicator
      lib/               # api client, auth, offline queue (IndexedDB), query hooks
      sw.ts              # service worker (app-shell cache)
    tests/               # Vitest + React Testing Library
    vite.config.ts
  deploy/
    cadence.service      # systemd unit
    deploy.sh            # build frontend, rsync/scp, restart service
    .env.example
  docs/superpowers/specs/
```

---

## 4. Authentication & Authorization

Three distinct auth contexts:

### 4.1 Web user — Google OAuth (single user)
- Library: **Authlib** + Starlette `SessionMiddleware` (signed cookie via `SESSION_SECRET`).
- Flow:
  1. `GET /api/auth/login` → redirect to Google consent.
  2. `GET /api/auth/google/callback` → exchange code, read verified email.
  3. If email ∈ `ALLOWED_EMAILS` → set HttpOnly signed session cookie → redirect `/`. Else 403.
  4. `GET /api/auth/me` → `{email}` or 401. `POST /api/auth/logout` clears session.
- All **user-scoped** `/api/*` endpoints require a valid session (dependency `require_user`).
- Frontend: on 401 from `/api/auth/me`, show a "Sign in with Google" screen linking to `/api/auth/login`.
- **Prerequisite (Michael):** create a Google Cloud OAuth Web client; authorized redirect URI
  `https://cadence-fitness.exe.xyz/api/auth/google/callback`; provide `GOOGLE_CLIENT_ID` +
  `GOOGLE_CLIENT_SECRET`. `ALLOWED_EMAILS=michael.roy.galloway@gmail.com`.

### 4.2 Eva inbound — bearer key
- Dependency `require_eva` checks `Authorization: Bearer <EVA_APP_KEY>`.
- Guards `PUT /api/routine`, `PATCH /api/goals`, `GET /api/state`.
- **Generated key (store in backend env, give to Eva):**
  `EVA_APP_KEY=eva_CvarUvmF7BwYKxKQREbEKZOQDTK9jPg6sCuSIwoTrDQ`

### 4.3 Jester outbound — bearer key
- Outbox worker sends `Authorization: Bearer <JESTER_WRITE_KEY>` (provided by Michael).

> Note: exe.dev's own proxy auth is bypassed because the proxy is public; all authz is enforced in-app.

---

## 5. Data Model

Per PRD §5, implemented as SQLAlchemy tables (JSON columns for nested structures):

- **routines** — `routine_id` (uuid pk), `version` (int, monotonic), `created_at`, `source`
  (`eva|seed`), `reason`, `days` (JSON array), `is_current` (bool). History = all rows; revert =
  flip `is_current` to the prior version.
- **goals** — single-row table: `goals` (JSON array), `constraints` (JSON), `updated_at`,
  `updated_by` (`eva|user`).
- **session_logs** — `log_id` (uuid pk), `logged_at`, `session_date`, `day_of_week`,
  `session_type`, `label`, `status`, `swap_reason`, `readiness` (`great|tired|joint_pain|null`),
  `duration_minutes`, `rounds_completed`, `rating`, `notes`, `source` (`manual|healthkit`),
  `health_metrics` (JSON, nulls in Phase 1), `routine_version`. One log per `session_date`
  (editable within 24h of `logged_at`).
- **outbox_events** — `outbox_id` (uuid pk), `event_type` (`workout_logged|milestone`), `payload`
  (JSON), `status` (`pending|sent|failed`), `created_at`, `sent_at`, `attempts`.

Schema created on startup via `create_all` (no Alembic in v1).

---

## 6. Backend Behavior

### 6.1 Today derivation (`services/derive.py`)
- Look up `is_current` routine, find the day matching today's `day_of_week` (server local date).
- Rest day (no matching day or `session_type` rest) → rest card payload (no log CTA), include streak.
- Readiness: if today's log has `readiness == joint_pain`, substitute a hardcoded **15-min mobility**
  block (`session_type: mobility`, `swap_reason: joint_pain`). The swap is reflected in the derived
  session and recorded on the log entry.
- `GET /api/sessions/today` returns `{session, log|null, readiness_answered: bool}`.

### 6.2 Readiness + logging (`routers/sessions.py`)
- Readiness answer is stored on/creates the day's log entry (answer persisted once per date).
- `POST /api/sessions/log`: required `status`, `duration_minutes`; optional `rounds_completed`,
  `rating`, `notes`. Pre-fill comes from the client (derived session). On save: persist log →
  enqueue `workout_logged` outbox event → recompute streak → if streak hits 7/14/30, enqueue
  `milestone` event. Returns the saved log + updated streak.
- `PATCH /api/sessions/{log_id}`: allowed only within 24h of `logged_at`; else 409.
- Past-date logging: same `POST` with an explicit `session_date` (History "Log missed workout").

### 6.3 Adherence (`services/streaks.py`)
- **Streak** = consecutive days (walking back from today) where the day had a *planned* session and
  its log is `completed` or `partial`. Rest days don't break the streak (skipped, not counted).
- Weekly summary: planned vs completed per week. Calendar heatmap statuses derived from logs.

### 6.4 Eva updates (`routers/routines.py`, `goals.py`)
- `PUT /api/routine`: insert new row `version = max+1`, `source: eva`, `reason`, set `is_current`.
  Previous current row retained for revert.
- `GET /api/routine/current` includes a flag when the current routine is Eva-sourced and not yet
  acknowledged, so the SPA shows the **Eva update banner** (reason string, Keep/Revert).
- `POST /api/routine/revert`: restore the immediately-previous version as current; emit
  `routine_reverted` outbox event. Revert allowed within **7 days** (PRD D5) of the Eva update.
- `PATCH /api/goals`: replace goals/constraints, set `updated_by: eva`, bump `updated_at`.

### 6.5 Outbox worker (`services/outbox.py`)
- asyncio background task launched on FastAPI startup; every **60s** selects `pending`/retryable
  `failed` events and POSTs to Jester. Success → `sent` + `sent_at`. Failure → increment `attempts`,
  exponential backoff; after **max 5 attempts** → `failed` (terminal) and log an alert line.
- `JESTER_BASE_URL` env-configurable; a local stub server is used in dev/tests.

---

## 7. API Endpoints (auth mapping updated)

| Method | Path | Auth | Notes |
|:--|:--|:--|:--|
| GET | `/api/health` | none | healthcheck |
| GET | `/api/auth/login` | none | → Google |
| GET | `/api/auth/google/callback` | none | sets session |
| GET | `/api/auth/me` | session | current user or 401 |
| POST | `/api/auth/logout` | session | clears session |
| GET | `/api/routine/current` | session | active routine + Eva-banner flag |
| GET | `/api/routine/history` | session | versions |
| POST | `/api/routine/revert` | session | revert (≤7 days) |
| PUT | `/api/routine` | Eva key | replace routine |
| GET | `/api/goals` | session | current goals |
| PATCH | `/api/goals` | Eva key | update goals |
| GET | `/api/state` | Eva key | adherence summary for Eva |
| GET | `/api/sessions/today` | session | derived session + today's log |
| POST | `/api/sessions/log` | session | create log (+ outbox events) |
| PATCH | `/api/sessions/{log_id}` | session | edit within 24h |
| GET | `/api/sessions` | session | paginated history (filter by type) |
| GET | `/api/adherence` | session | streak + weekly summary |

---

## 8. Frontend

- **Stack:** React + Vite + TypeScript + Tailwind. Dark, mobile-first, no UI component library.
  React Router (5 routes), **TanStack Query** for server state.
- **Routes:** `/` Today, `/log` Log form, `/history` Heatmap + list, `/goals` Goals, `/settings`.
- **Components:** `SessionCard`, `ReadinessCheck` (Great / Tired but OK / Joint pain), `LogForm`
  (3-state status, duration slider+input, rounds counter for AMRAP, star rating, notes),
  `CalendarHeatmap` (12 weeks, green/yellow/red/grey, tap → day drawer), `EvaUpdateBanner`
  (reason + Keep/Revert), `OfflineIndicator` (header).
- **Tap targets ≥ 48px**, session card is the hero element.

### 8.1 Offline reliability (PRD §8.6)
- **Service worker** caches the app shell (static assets, last-known today/routine) for offline load.
- **Log submissions** go through an **IndexedDB queue** with optimistic UI: writes succeed locally
  instantly, a flush routine drains the queue to `POST /api/sessions/log` on reconnect
  (`online` event + periodic retry). No log lost on network failure. This is the highest-risk client
  piece and gets dedicated unit tests.
- Edits within 24h while offline queue as PATCH ops keyed by `log_id`.

---

## 9. Jester Event Contracts (for registration)

`POST {JESTER_BASE_URL}/api/item/{event_type}` with `Authorization: Bearer {JESTER_WRITE_KEY}`,
`Content-Type: application/json`. Item types and payload shapes to register in Jester:

### `workout_logged`
```json
{
  "log_id": "8f3c…uuid",
  "session_type": "run | strength | mobility | rest",
  "status": "completed | partial | missed | swapped",
  "session_date": "2026-06-28",
  "day_of_week": "saturday",
  "label": "Long Run",
  "duration_minutes": 52,
  "rounds_completed": null,
  "rating": 4,
  "readiness": "great | tired | joint_pain | null",
  "swap_reason": "joint_pain | tired | null",
  "routine_version": 3,
  "health_metrics": {
    "avg_hr_bpm": null,
    "max_hr_bpm": null,
    "active_energy_kcal": null,
    "hrv_ms": null
  }
}
```

### `milestone`
```json
{
  "milestone_type": "streak",
  "streak_days": 7,
  "session_date": "2026-06-28",
  "log_id": "8f3c…uuid"
}
```

### `routine_reverted`
```json
{
  "from_version": 4,
  "to_version": 3,
  "reverted_at": "2026-06-28T17:22:00Z"
}
```

(`milestone` fires at streak = 7, 14, 30. `health_metrics` are null in Phase 1, populated in Phase 2.)

---

## 10. Testing Strategy

- **TDD throughout** (superpowers TDD skill): write failing test → implement → green → refactor.
- **Backend:** pytest + httpx `TestClient` over a temp SQLite DB. Cover: today derivation (each
  weekday + rest + joint-pain swap), log create/edit-24h boundary, streak/milestone math, Eva
  PUT/PATCH/revert/7-day window, auth deps (session required, Eva key required, healthcheck open),
  outbox enqueue + worker drain against a local Jester stub (success, retry, terminal-fail).
- **Frontend:** Vitest + React Testing Library for components; dedicated unit tests for the IndexedDB
  offline queue (enqueue, flush-on-reconnect, dedupe, failure retention).
- **Smoke:** one Playwright test for today → log → history happy path (post-OAuth, using a test
  session bypass in dev).

---

## 11. Environment Variables

```
# Backend (.env on VM)
DATABASE_URL=sqlite:////home/exedev/cadence/cadence.db
SESSION_SECRET=iUbVIikBMzB8QH4FMgC9Jl2dp_cLvpgPC0icTljPyVVNCZ0gzyGBww7-UPCzvBMl
ALLOWED_EMAILS=michael.roy.galloway@gmail.com
GOOGLE_CLIENT_ID=<from Google Cloud OAuth client>      # Michael to provide
GOOGLE_CLIENT_SECRET=<from Google Cloud OAuth client>  # Michael to provide
EVA_APP_KEY=eva_CvarUvmF7BwYKxKQREbEKZOQDTK9jPg6sCuSIwoTrDQ
JESTER_BASE_URL=<https://…>          # Michael to provide
JESTER_WRITE_KEY=<bearer>            # Michael to provide
PUBLIC_BASE_URL=https://cadence-fitness.exe.xyz
```

---

## 12. Prerequisites Michael Must Provide

1. **Google OAuth client** (Web): redirect URI `https://cadence-fitness.exe.xyz/api/auth/google/callback`
   → `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`.
2. **Jester:** `JESTER_BASE_URL` and `JESTER_WRITE_KEY`; register item types `workout_logged`,
   `milestone`, `routine_reverted` using the §9 contracts.
3. (Already done) VM `cadence-fitness` exists and proxy is **public**.

`EVA_APP_KEY` and `SESSION_SECRET` are generated above; hand `EVA_APP_KEY` to Eva.

---

## 13. Milestone Mapping (PRD §13)

The implementation plan will sequence these: 1.1 backend skeleton → 1.2 seed + today derivation →
1.3 Today view + readiness/swap → 1.4 logging → 1.5 Jester outbox → 1.6 Eva inbound + banner →
1.7 history + adherence → 1.8 goals → 1.9 offline. Auth (OAuth) is built in 1.1 as the gate for all
user endpoints.

---

## 14. Out of Scope (Phase 1)

Native mobile, Apple Watch, HealthKit/WorkoutKit, live during-workout timers/HR, nutrition, multi-user,
in-app coaching logic, Android/Health Connect. Data model and Jester events are Phase-2-ready.
