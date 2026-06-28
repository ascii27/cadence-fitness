# `cadence_event` — Consumer Guide for Hermes / Eva

How Cadence emits events to Jester, and how the **Eva** agent (on Hermes) should interpret and act
on them. This is the consumer-facing companion to the producer contract in
`docs/superpowers/specs/2026-06-28-cadence-phase1-design.md` §9.

---

## 1. What this is

Cadence is a goal-driven fitness app. It has **no coaching logic of its own** — it surfaces a routine,
captures the user's workout outcomes, and reports them. Eva owns all tuning. These events are how Eva
*senses* what the user actually did so it can retune the routine and goals over time.

Every event is one Jester item of a **single type: `cadence_event`**. The specific kind is in the
`event_type` field. Eva should branch on `event_type`.

## 2. Delivery semantics (read this first)

- **At-least-once.** Cadence uses a durable outbox with retries (up to 5 attempts, exponential
  backoff). **Duplicates are possible.** Eva must handle events idempotently — dedupe on the natural
  key for each kind (below), don't append blindly.
- **Ordering is not guaranteed.** Use the `occurred_at` timestamp (ISO-8601) to order events, not
  arrival order.
- **Upsert, don't append, for `workout_logged`.** A given `log_id` can be re-sent with updated values
  if the user re-saves that day's log. Treat the latest `occurred_at` for a `log_id` as the current
  truth.
- **Timestamps** (`occurred_at`, `reverted_at`) are UTC, ISO-8601, currently **without** a `Z` suffix
  (e.g. `2026-06-28T17:22:00.123456`). `session_date` is the local **calendar date** of the session
  (`YYYY-MM-DD`) — use it for adherence/streak reasoning, not `occurred_at`.

## 3. Envelope

```json
{
  "event_type": "workout_logged | milestone | routine_reverted",
  "occurred_at": "2026-06-28T17:22:00.123456",
  "data": { /* kind-specific */ }
}
```

| field | meaning |
|---|---|
| `event_type` | which kind of event — branch on this |
| `occurred_at` | when Cadence emitted it (UTC); use for ordering/recency |
| `data` | kind-specific body, described per kind below |

---

## 4. Event kinds

### 4.1 `workout_logged` — the user logged a session

**Fires:** every time the user saves a workout log (today or a back-dated entry). This is the primary
adherence signal and the most frequent event.

**Dedupe / upsert key:** `data.log_id` (one stable id per session date; later `occurred_at` wins).

```json
{
  "event_type": "workout_logged",
  "occurred_at": "2026-06-28T17:22:00.123456",
  "data": {
    "log_id": "8f3c1e2a-…",
    "session_type": "strength",
    "status": "completed",
    "session_date": "2026-06-28",
    "day_of_week": "saturday",
    "label": "Upper Body & Core",
    "duration_minutes": 16,
    "rounds_completed": 4,
    "rating": 4,
    "readiness": "great",
    "swap_reason": null,
    "routine_version": 1,
    "health_metrics": { "avg_hr_bpm": null, "max_hr_bpm": null, "active_energy_kcal": null, "hrv_ms": null }
  }
}
```

| field | type | how Eva should read it |
|---|---|---|
| `log_id` | string | dedupe/upsert key |
| `session_type` | `run`\|`strength`\|`mobility`\|`rest` | what kind of work was done. `mobility` usually means a joint-pain swap occurred |
| `status` | `completed`\|`partial`\|`missed`\|`swapped` | **adherence outcome.** `completed`/`partial` = credit; `missed` = the user skipped; `swapped` = substituted |
| `session_date` | `YYYY-MM-DD` | the day this counts for (use for streak/adherence windows) |
| `day_of_week` | string | lowercase weekday; cross-check against the planned routine |
| `label` | string\|null | human label of the planned session |
| `duration_minutes` | int\|null | actual minutes trained (0 on `missed`) |
| `rounds_completed` | int\|null | AMRAP rounds for strength sessions — a **load/progress** signal |
| `rating` | int\|null (1–5) | subjective session quality (RPE-ish, higher = felt better) |
| `readiness` | `great`\|`tired`\|`joint_pain`\|null | pre-workout self-report. **`joint_pain` is the key risk signal** |
| `swap_reason` | `joint_pain`\|`tired`\|null | why the session was swapped, if it was |
| `routine_version` | int\|null | which routine version was active — tells Eva if its last change has "taken" |
| `health_metrics` | object | **null in Phase 1**; populated in Phase 2 (HealthKit: HR, energy, HRV) |

**How Eva should act:**
- **Joint longevity is the binding constraint.** `readiness == "joint_pain"` or `swap_reason ==
  "joint_pain"` (often surfacing as a `mobility` session) is a strong signal to **reduce load /
  deload**, especially if it recurs. Protect the joints over progression.
- **Repeated `missed`/`partial`** → the plan may be too demanding or mistimed; consider lowering
  volume or moving sessions.
- **Sustained `completed` + high `rating` + rising `rounds_completed`** → headroom to progress (e.g.
  bump the long run, per the user's marathon-build goal).
- Combine with `routine_version`: if recent logs are all on the latest version and going well, the
  last change is working.

### 4.2 `milestone` — an adherence streak threshold was reached

**Fires:** when the user's current streak hits exactly **7, 14, or 30** consecutive planned days
completed/partially completed (rest days don't break the streak). Emitted alongside the
`workout_logged` that triggered it.

**Dedupe key:** (`data.streak_days`, `data.log_id`) — or `(streak_days, session_date)`.

```json
{
  "event_type": "milestone",
  "occurred_at": "2026-06-28T17:22:00.123456",
  "data": { "milestone_type": "streak", "streak_days": 7, "session_date": "2026-06-28", "log_id": "8f3c1e2a-…" }
}
```

| field | type | meaning |
|---|---|---|
| `milestone_type` | string | always `"streak"` in Phase 1 |
| `streak_days` | int | the streak length reached: `7`, `14`, or `30` |
| `session_date` | `YYYY-MM-DD` | the day the milestone was hit |
| `log_id` | string | the log that pushed the streak over the line |

**How Eva should act:** treat as a positive consistency signal. Reasonable response is to consider a
**progression** (the seed routine's own example reason was *"Increased long run after 3-week
adherence"*) — while still respecting the joint-longevity constraint. Also useful for
encouragement/acknowledgement back to the user.

### 4.3 `routine_reverted` — the user rejected an Eva routine change

**Fires:** when the user clicks **Revert** on a routine update Eva pushed (allowed within 7 days of the
update). This is **direct negative feedback on Eva's last change.**

**Dedupe key:** (`data.from_version`, `data.to_version`).

```json
{
  "event_type": "routine_reverted",
  "occurred_at": "2026-06-28T17:22:00.123456",
  "data": { "from_version": 4, "to_version": 3, "reverted_at": "2026-06-28T17:22:00.123456" }
}
```

| field | type | meaning |
|---|---|---|
| `from_version` | int | the version Eva had pushed and the user **rejected** |
| `to_version` | int | the version restored (now active) |
| `reverted_at` | string | when the revert happened (UTC ISO-8601) |

**How Eva should act:** this is important. The change in `from_version` was **unwanted**. Eva should
**not re-apply the same change**, and should treat it as a learning signal about the user's
preferences (e.g. they didn't want that added session or that volume jump). The active routine is now
`to_version`; reconcile internal state to that. Consider asking *why* before re-tuning in that
direction.

---

## 5. How Eva acts back (inbound API)

Events are one direction (Cadence → Jester → Eva). To change anything, Eva calls the Cadence backend
directly at `https://cadence-fitness.exe.xyz`, authenticating with `Authorization: Bearer
{EVA_APP_KEY}`:

| call | effect |
|---|---|
| `PUT /api/routine` | Replace the routine (new version + `reason`). Auto-applies; user can revert within 7 days (→ may produce a `routine_reverted` event). |
| `PATCH /api/goals` | Update goals / constraints. |
| `GET /api/state` | **Catch-up / reconciliation.** Returns `routine_version`, `last_log_date`, and a 30-day adherence summary. Use this if events were missed or to confirm current state before acting. |

The `reason` string on `PUT /api/routine` is shown to the user in the app's "Eva adjusted your
routine" banner — write it for a human.

## 6. Quick handling checklist for Eva

1. Branch on `event_type`.
2. Dedupe on the kind's natural key (`log_id`; `streak_days`+`log_id`; `from_version`+`to_version`).
3. Order by `occurred_at`; for `workout_logged`, upsert by `log_id`.
4. Update the adherence/recovery model; weight `joint_pain` heavily (binding constraint).
5. On `routine_reverted`, suppress the rejected change and learn from it.
6. When unsure of current state (missed events, etc.), reconcile via `GET /api/state` before pushing
   a new `PUT /api/routine`.
