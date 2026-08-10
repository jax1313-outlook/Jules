# DISPATCH_STAGE7_SECURITY_FOUNDATION_DESIGN_v1.md

**Document Type:** Design/Spec for Review (Constitution §20 gate)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Revised per Mike's design review — awaiting approval before implementation begins
**Authority:** Mike Zachary remains final authority

---

## Purpose

Constitution §20: *"No Spec. No Prompt. No Build. No Approval. No Implementation."* This is the design gate for Stage 7 build, following the same discipline used for Stage 4. Nothing in this document is implemented yet.

**Revision note:** this version replaces the original blanket-route-protection design with the split Mike specified: **Security Foundation** (this build) versus **Portal-Wide Enforcement** (a separate, later, not-yet-approved stage). The scope below is narrower than the first draft, on purpose.

---

## 1. The Two-Part Split

**Security Foundation — this build:**
- Identity
- PIN (creation, validation, change, reset, revocation, lockout)
- Session
- Role (schema for all four; only Authority functionally exercised)
- Audit (`security_events`)
- Approval Events (the *capability* to record real identity on an approval event when a session exists — not a mandate that any specific existing action route must now require login)
- Security Sub-Library (the PIN-recheck *mechanism*, built and tested; not yet wired to an actual gated Library section, since that depends on Library's `origin` field, which isn't built — Stage 9 territory)

**Portal-Wide Enforcement — explicitly NOT this build:**
- Deciding which existing pages require login
- Deciding which existing actions (Book, Pursue, Conflict resolution, Publisher approval, etc.) require login
- Any change to informational browsing behavior

This build produces working, tested login/PIN/session/role/audit infrastructure. It does not, by itself, change how any existing page or action behaves, with one named exception (Section 3).

---

## 2. Answers to Stage 7 Reconciliation's Open Questions

| Question | Answer | Why |
|---|---|---|
| Single Authority user only, or Driver/External Viewer too on day one? | **Single Authority user (you) usable end-to-end. All four roles defined in the schema from the start.** | Unchanged from the prior draft — no rework needed here. |
| Consolidate the two HMAC token implementations? | **Leave them separate. Not touched by this build.** | Unchanged. |
| Security Sub-Library PIN recheck — same build or follow-on? | **The re-check mechanism is built now (Section 1); wiring it to an actual Library section is a follow-on**, pending Stage 9's `origin` field. | Matches Mike's explicit inclusion of Security Sub-Library in this build's scope, without overreaching into Library work that isn't ready. |
| Fix `/settings`'s unauthenticated secret-exposure now? | **Yes.** | The one page-level "actual security risk" carve-out Mike specified — viewing that page *is* the risk, independent of any action. |

---

## 3. What Actually Changes in the Running Application

**Gated by this build:** `/settings` only, plus the new `/login`/`/logout` routes themselves. This is the one page where Mike's own carve-out applies directly — `/settings` exposes which secrets/keys are configured to any visitor today, which is a real information-disclosure risk regardless of whether anyone acts on what they see.

**Unchanged by this build:** every other existing page (`/home`, `/sam`, `/dispatch`, `/conflicts`, `/library`, `/archive`, `/intelligence`, `/publisher`, `/ifta`, `/fleet`, all of it) continues to work exactly as it does today, unauthenticated, per Mike's instruction to keep informational browsing behavior unchanged. Every existing action button (Interested/Pursue/Pass/Watch/Book, Conflict resolve, Publisher status update, IFTA submission) continues to work exactly as today — **none of them are modified to require login in this build.** The three HMAC email-approval gates are untouched, preserving the phone-approval workflow exactly as it works now, per Mike's explicit instruction.

**What this means for Approval Events concretely:** the capability to record a real `session_id`/`user_id`/`role` on an `approval_events` row is built and tested in this stage. Because no existing action route is being modified to require login, those rows will continue to be written with a null actor exactly as they are today, until a *separate*, future, explicitly-approved step (Portal-Wide Enforcement, or a narrowly-scoped follow-on) decides a specific action should require login. This build proves the capability works; it does not exercise it against real traffic yet. That is a deliberate, not an incomplete, design.

---

## 4. Schema Design

Unchanged from the prior draft — nothing about the schema itself needed revision, only how broadly it gets applied. New module `portal/security/`, same `dispatch.db` file, added to the existing `_init_db()` pass.

### 4.1 `users`

| Column | Type | Notes |
|---|---|---|
| `user_id` | TEXT PRIMARY KEY | `_gen_id("USER")` |
| `display_name` | TEXT NOT NULL | |
| `role` | TEXT NOT NULL | `Authority` \| `Driver` \| `External Viewer` \| `System Service` |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `inactive` \| `locked` |
| `pin_record_id` | TEXT | soft reference to `pin_records.pin_record_id` |
| `created_at` / `updated_at` | TEXT NOT NULL | |
| `last_login_at` | TEXT | nullable |

Permissions are a static role→permission lookup in code, not a stored column (mirrors `dispatch/spine/state.py::ALLOWED_TRANSITIONS`). `authority_level` deferred, not included.

### 4.2 `pin_records`

| Column | Type | Notes |
|---|---|---|
| `pin_record_id` | TEXT PRIMARY KEY | |
| `user_id` | TEXT NOT NULL REFERENCES `users` | |
| `pin_hash` | TEXT NOT NULL | see Section 5 — never plaintext |
| `salt` | TEXT NOT NULL | random, unique per PIN |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `revoked` |
| `reset_required` | INTEGER NOT NULL DEFAULT 0 | |
| `failed_attempt_count` | INTEGER NOT NULL DEFAULT 0 | |
| `locked_until` | TEXT | nullable — set on lockout |
| `created_at` / `updated_at` | TEXT NOT NULL | |

### 4.3 `sessions`

| Column | Type | Notes |
|---|---|---|
| `session_id` | TEXT PRIMARY KEY | |
| `user_id` | TEXT NOT NULL REFERENCES `users` | |
| `role` | TEXT NOT NULL | snapshot at login |
| `started_at` / `last_active_at` | TEXT NOT NULL | |
| `status` | TEXT NOT NULL DEFAULT `'active'` | `active` \| `expired` \| `revoked` |
| `authentication_method` | TEXT NOT NULL DEFAULT `'DISPATCH_PIN'` | |

### 4.4 `security_events`

| Column | Type | Notes |
|---|---|---|
| `event_id` | TEXT PRIMARY KEY | |
| `event_type` | TEXT NOT NULL | `LOGIN_SUCCESS`, `LOGIN_FAILURE`, `PIN_CREATED`, `PIN_CHANGED`, `PIN_RESET`, `PIN_REVOKED`, `SESSION_CREATED`, `SESSION_EXPIRED`, `PERMISSION_DENIED` |
| `user_id` | TEXT | nullable |
| `timestamp` | TEXT NOT NULL | |
| `details` | TEXT | JSON |

### 4.5 Security Sub-Library re-check (mechanism only)

A function, not a table: `require_security_sublibrary_pin(session)` — re-validates a PIN at the moment of access, distinct from the general login PIN check, per `LIBRARY_INGESTION_RULE.md` §6. It reuses `pin_records`/the same validation function as login (Section 5), called a second time at a different trigger point — no second PIN system. Built and unit-tested in this stage; **not called from any route yet**, since there is no "security" Library section to protect until Stage 9's `origin` field work lands. This satisfies Mike's inclusion of Security Sub-Library in this build's scope without inventing a Library feature that isn't ready.

---

## 5. PIN Storage

Unchanged — confirmed accepted: the distinction between file-integrity hashing (`cin_lite/archive.py`'s existing SHA-256 use) and credential hashing is a settled point, not open for reconsideration.

**Proceeding with `hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, iterations=600_000)`** — stdlib only, no new dependency, in line with current OWASP guidance for PBKDF2-SHA256. Validation re-hashes the entered PIN with the stored salt and compares with `hmac.compare_digest`. If you'd rather have `hashlib.scrypt` (memory-hard, also stdlib, a defensible stronger alternative) instead, say so — otherwise I'll build with PBKDF2.

No plaintext PIN is stored, logged, or ever appears in a repository file.

---

## 6. Login Flow

1. User selects identity (initially: just you) and enters a PIN.
2. Dispatch validates the PIN against the stored hash.
3. On success: create a `sessions` row, set a Flask session cookie signed with `PORTAL_SECRET_KEY` (used for its actual purpose for the first time), record `LOGIN_SUCCESS`, update `last_login_at`.
4. On failure: increment `failed_attempt_count`; after 5 consecutive failures, set `locked_until` (15 minutes) and record `LOGIN_FAILURE`; do not reveal whether the identity itself was valid.
5. Session enforcement: a reusable check (decorator/function) that loads the session from the cookie and attaches the current user/role to the request context — **built and available, but in this build only applied to `/settings` and the new `/login`/`/logout` routes themselves**, per Section 3. Applying it more broadly is Portal-Wide Enforcement's decision, not this build's.

---

## 7. What Does Not Change in This Build

Every existing page's unauthenticated browsing behavior. Every existing action route's current (unauthenticated) behavior. The three HMAC email-approval gates and the phone-approval workflow they support. `cin_lite/archive.py`'s hashing. `dispatch/spine/`'s schema (this build only proves it *can* be populated with real identity, doesn't force it to be, on any current route). Any existing business logic, scoring, or IFTA computation.

---

## 8. Test Plan

PIN creation/validation/lockout tests. Session creation/expiry/revocation tests. `/settings` access-denied-when-logged-out / access-granted-when-Authority tests. A structural test confirming no plaintext PIN ever reaches a log line, response body, or stored column. A test proving `create_approval_event()` correctly populates `session_id`/`user_id`/`role` **when called with a real session** (proving the capability, per Section 3) alongside the existing Stage 4 test proving it stays correctly null without one. Security Sub-Library PIN-recheck unit tests (function-level, no route to test against yet). **A full regression pass confirming every existing route and every existing test continues to pass completely unauthenticated, unchanged** — this is the "nothing broke" guarantee this build's narrower scope makes easy to satisfy, unlike the blanket-protection draft which would have required updating every existing route test to log in first.

---

## 9. Open Questions Before I Start

1. PBKDF2-HMAC-SHA256 (Section 5) — proceeding with this unless you say scrypt.
2. Anything in Section 1's split, or Section 3's "what changes," that should be different?

If this matches what you intended, say **"Approve design"** and I'll build it. If not, tell me what to change and I'll revise again before touching any code.

---

## Authority Closing

This is a design/spec document only. No table, file, or code exists yet as a result of this document.

Implementation begins only after Mike approves this design.

Mike decides.
