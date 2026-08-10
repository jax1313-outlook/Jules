# DISPATCH_STAGE7_SECURITY_FOUNDATION_DESIGN_v1.md

**Document Type:** Design/Spec for Review (Constitution §20 gate)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Awaiting Mike's design approval before implementation begins
**Authority:** Mike Zachary remains final authority

---

## Purpose

Constitution §20: *"No Spec. No Prompt. No Build. No Approval. No Implementation."* This is the design gate for Stage 7 build, following the same discipline used for Stage 4 (`DISPATCH_STAGE4_SPINE_SCHEMA_DESIGN_v1.md`) — but with more at stake: this build changes every Portal route from open to gated, and a wrong call on PIN storage is a security mistake, not a refactor to undo later. Nothing in this document is implemented yet.

This design answers Stage 7 reconciliation's four open questions with explicit recommendations, and surfaces two additional scope decisions the reconciliation didn't foresee, all flagged for your override before I write anything.

---

## 1. Answers to Stage 7 Reconciliation's Open Questions

| Question | Recommendation | Why |
|---|---|---|
| Single Authority user only, or Driver/External Viewer too on day one? | **Single Authority user (you) usable end-to-end. All four roles defined in the schema and permission model from the start** — so adding Driver/External Viewer login later needs no schema rework, just new routes. | Keeps the build tractable without narrowing the data model in a way that costs rework later. |
| Consolidate the two HMAC token implementations (`cin_lite/email_delivery.py`, `dispatch/notifications.py`)? | **Leave them separate.** Not touched by this build. | Both work correctly today. Mixing "add identity" with "refactor working, tested code" in one change adds risk for no functional gain right now. |
| Security Sub-Library PIN recheck — same build or follow-on? | **Follow-on, not bundled.** | It depends on Library's `origin` field (Jules #6, Stage 9's finding), which isn't built yet either. Keep this build focused on identity/session/role/PIN core. |
| Fix `/settings`'s unauthenticated secret-exposure now? | **Yes — trivial once the login/session gate exists**, since it's just one more route behind the same gate. | Real, live information-disclosure gap; near-zero marginal cost once the gate exists. |

**If any of these should go the other way, say so before I start.**

---

## 2. Two Scope Decisions the Reconciliation Didn't Foresee

### 2.1 Blanket route protection vs. a pilot subset

Every Portal route is open today — confirmed by grep, no exceptions. Stage 7 reconciliation's own capability table flagged "unauthenticated approval" as a live Conflict against doctrine, not a hypothetical one. **Recommendation: protect the whole Portal behind login in this build** (a `@login_required`-style check applied portal-wide), not a partial subset — a partial gate would leave the same doctrine violation standing for whatever's left uncovered, just narrower.

**Practical consequence you should know before approving:** once this ships, you will need to log in with a PIN to see *any* Portal page, including `/home`. If that's not what you want for a first pass (e.g., you'd rather keep browsing open and only gate the actual approval actions), say so now — it changes the build meaningfully.

### 2.2 The three HMAC email-approval gates stay untouched in this build

Stage 7 reconciliation recommended session auth as a *secondary layer* on top of the token gates eventually. Implementing that now creates a real UX conflict: those gates exist specifically so you can approve something by clicking a link from your phone, possibly without an active Portal session on that device. Requiring both a valid session *and* the token in this build could break that flow without your explicit sign-off on the trade-off.

**Recommendation: leave all three email-approval gates (CIN/SAM, dispatch-load, IFTA) exactly as they behave today in this build.** Real identity gets wired into the approval actions you take *through the logged-in Portal UI* (status changes, conflict resolution, publisher actions, IFTA submissions started from the UI) — not into the emailed-link endpoints. Whether the emailed links should later also require an active session is a separate decision with a real convenience cost, worth its own explicit call once you've used session login for a while.

---

## 3. Schema Design

New module `portal/security/` (mirroring `dispatch/spine/`'s structure), persisted in the **same `dispatch.db` file**, added to the existing `_init_db()` pass — consistent with Stage 4's precedent and not re-litigated here since nothing in the Stage 7 reconciliation suggested a different file.

### 3.1 `users`

| Column | Type | Notes |
|---|---|---|
| `user_id` | TEXT PRIMARY KEY | `_gen_id("USER")`, matching this codebase's universal ID convention |
| `display_name` | TEXT NOT NULL | |
| `role` | TEXT NOT NULL | `Authority` \| `Driver` \| `External Viewer` \| `System Service` |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `inactive` \| `locked` |
| `pin_record_id` | TEXT | soft reference to `pin_records.pin_record_id` |
| `created_at` / `updated_at` | TEXT NOT NULL | |
| `last_login_at` | TEXT | nullable |

Permissions are **not** a stored per-user column — they're a static role→permission lookup in code (mirroring how `dispatch/spine/state.py::ALLOWED_TRANSITIONS` is a Python dict, not a table), since this build assigns permissions by role, not individually. `authority_level` (a Security Spec field with no defined semantics beyond role in this build) is deferred, not included.

### 3.2 `pin_records`

| Column | Type | Notes |
|---|---|---|
| `pin_record_id` | TEXT PRIMARY KEY | |
| `user_id` | TEXT NOT NULL REFERENCES `users` | |
| `pin_hash` | TEXT NOT NULL | see Section 4 — never plaintext |
| `salt` | TEXT NOT NULL | random, unique per PIN |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `revoked` |
| `reset_required` | INTEGER NOT NULL DEFAULT 0 | |
| `failed_attempt_count` | INTEGER NOT NULL DEFAULT 0 | |
| `locked_until` | TEXT | nullable — set on lockout |
| `created_at` / `updated_at` | TEXT NOT NULL | |

### 3.3 `sessions`

| Column | Type | Notes |
|---|---|---|
| `session_id` | TEXT PRIMARY KEY | |
| `user_id` | TEXT NOT NULL REFERENCES `users` | |
| `role` | TEXT NOT NULL | snapshot at login — a later role change doesn't retroactively alter an already-issued session's permissions mid-session |
| `started_at` / `last_active_at` | TEXT NOT NULL | |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `expired` \| `revoked` |
| `authentication_method` | TEXT NOT NULL DEFAULT `'DISPATCH_PIN'` | |

### 3.4 `security_events`

| Column | Type | Notes |
|---|---|---|
| `event_id` | TEXT PRIMARY KEY | |
| `event_type` | TEXT NOT NULL | `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `PIN_CREATED`, `PIN_CHANGED`, `PIN_RESET`, `PIN_REVOKED`, `SESSION_CREATED`, `SESSION_EXPIRED`, `PERMISSION_DENIED` (Security Spec §16 list, trimmed to what this build actually produces) |
| `user_id` | TEXT | nullable — a `LOGIN_FAILURE` on an unrecognized identity has no user to attach to |
| `timestamp` | TEXT NOT NULL | |
| `details` | TEXT | JSON, e.g. failed-attempt count at time of lockout |

---

## 4. PIN Storage — the One Decision That Can't Be Casual

A PIN is short (likely 4–6 digits), meaning a raw salted hash — even SHA-256, which this codebase already uses correctly for *file-integrity* hashing in `cin_lite/archive.py` — would be brute-forceable offline in seconds if the database were ever exposed, because SHA-256 is intentionally fast. File-integrity hashing and credential hashing are different problems and must not share a technique.

**Recommendation: `hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, iterations=600_000)`** — stdlib only (no new dependency, consistent with `CLAUDE.md`'s "must remain lightweight" constraint), well-audited, and the iteration count is in line with current OWASP guidance for PBKDF2-SHA256. Validation re-hashes the entered PIN with the stored salt and compares with `hmac.compare_digest` (this codebase's own existing, correct pattern from the HMAC token gates).

**A defensible alternative:** `hashlib.scrypt` (also stdlib), which is memory-hard and somewhat more resistant to GPU-accelerated brute force on a low-entropy secret like a PIN. PBKDF2 is the more conservative, more widely-documented default; scrypt is the stronger but less common choice for this specific use case. I'd default to PBKDF2 unless you'd rather have scrypt — either is a legitimate call, and it's cheap to specify now and expensive to silently get wrong.

No plaintext PIN is stored, logged, or ever appears in a repository file, matching Security Spec §17's explicit prohibition.

---

## 5. Login Flow

1. User selects their identity (initially: just you) and enters a PIN.
2. Dispatch validates the PIN (Section 4) against the stored hash for that identity.
3. On success: create a `sessions` row, set a Flask session cookie signed with `PORTAL_SECRET_KEY` (finally used, for the first time, for its actual purpose), record `LOGIN_SUCCESS`, update `last_login_at`.
4. On failure: increment `failed_attempt_count`; after 5 consecutive failures, set `locked_until` (recommend 15 minutes) and record `LOGIN_FAILURE`; do not reveal whether the identity itself was valid (standard practice — don't let a failed attempt confirm a username exists).
5. Session enforcement: a check applied to protected routes loads the session from the cookie, verifies it's `active` and not expired, and attaches the current user/role to the request context. Per Section 2.1, this applies to every existing route unless you say otherwise.

---

## 6. What Gets Real Identity in This Build

- `approval_events.session_id`/`user_id`/`role` — populated from the real logged-in session for every approval action taken through the Portal UI (Sandbox status changes, Conflict resolution, Publisher action updates, IFTA report-approval submission started from `/ifta`). This finally closes the gap Stage 4's own test (`test_approval_event_interim_identity_gap_is_nullable`) was written to make visible rather than hide.
- `/settings` — gated behind Authority-only access (Section 1).
- Every other existing route — gated behind *any* valid session (Section 2.1), without new per-route permission logic beyond "logged in or not" in this first build. Fine-grained per-role route restrictions (Driver-only views, External-Viewer-only views) are out of scope until those roles actually have a build — this build's Role model exists in the schema but only Authority is functionally exercised end to end.

## 7. What Does Not Change in This Build

The three HMAC email-approval gates (Section 2.2). `cin_lite/archive.py`'s hashing (unrelated — file integrity, not credentials). `dispatch/spine/` (Stage 4 — this build populates its existing nullable fields, doesn't touch its schema). Any existing business logic, scoring, or IFTA computation.

---

## 8. Test Plan

Per Security Spec §17 build-readiness requirements: PIN creation/validation/lockout tests; session creation/expiry/revocation tests; permission-denied tests for the one meaningfully differentiated case this build has (Authority vs. everyone-else, since other roles aren't functionally built yet); a structural test confirming no plaintext PIN ever reaches a log line, response body, or stored column; regression tests confirming every existing route still functions correctly *for an authenticated session* (since blanket protection means every existing test that hits a route needs a logged-in test client — this is the largest mechanical part of this build, not the riskiest).

---

## 9. Open Questions Before I Start

1. Blanket route protection (Section 2.1) — confirmed, or do you want a narrower first pass?
2. PBKDF2-HMAC-SHA256 (Section 4) — confirmed, or scrypt?
3. Anything else from Section 1's table you want changed?

If you're fine with the recommendations as written, say **"Approve design"** (or similar) and I'll build it. If you want to change any of the above first, tell me which and I'll revise this document before touching any code.

---

## Authority Closing

This is a design/spec document only. No table, file, or code exists yet as a result of this document.

Implementation begins only after Mike approves this design.

Mike decides.
