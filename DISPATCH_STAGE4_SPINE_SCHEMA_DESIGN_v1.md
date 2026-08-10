# DISPATCH_STAGE4_SPINE_SCHEMA_DESIGN_v1.md

**Document Type:** Design/Spec for Review (Constitution §20 gate)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Awaiting Mike's design approval before implementation begins
**Authority:** Mike Zachary remains final authority

---

## Purpose

Constitution §20 (Implementation Rule): *"No Spec. No Prompt. No Build. No Approval. No Implementation."* Stage 4's own launch package Stop/Go criteria require Mike to review the schema design before implementation begins, not only before merge. This document is that design, incorporating your two Stage 4 answers:

1. New Spine tables live in the **same `dispatch.db` SQLite file** as everything else.
2. The new `events` table **coexists** with the existing `LoadActivity`/`activities` table — no migration, no dual-write, no replacement.

Nothing in this document is implemented yet. Once you approve this design (or request changes), I'll build it on a new branch off `stage3-blueprint-alignment` and report back before it merges anywhere.

---

## 1. Where This Lives

New module `dispatch/spine/` (mirroring the existing `dispatch/` package style):

```text
dispatch/
├── spine/
│   ├── __init__.py
│   ├── models.py     # dataclasses for the six schemas below, mirroring dispatch/models.py's style
│   ├── db.py          # table DDL + init function, called from dispatch/db.py's existing _init_db()
│   └── store.py       # CRUD functions, mirroring dispatch/store.py's style
```

`dispatch/spine/db.py` does **not** open its own connection or resolve its own file path — it reuses `dispatch/db.py`'s existing `_default_db_path()` / `get_connection()` machinery and is called from the same `_init_db()` pass that already creates the 27 existing tables. One file, one WAL-mode connection, one `PRAGMA foreign_keys=ON`, one migration pass — consistent with the existing codebase, not a parallel system.

---

## 2. The Six Schemas

All six follow `DISPATCH_SPINE_SPECIFICATION_v1.md` §5–14 field-for-field. IDs are `TEXT` UUIDs (matching the Spec's own JSON examples exactly, e.g. `"work_item_id": "uuid"`), not the human-readable prefixed sequence IDs used elsewhere in this codebase (`CIN-...`, `SBX-...`) — the Spine is new, unified infrastructure, not another domain-specific store, so it uses the Spec's own convention rather than inventing a seventh ID style. Timestamps are `TEXT` ISO-8601, matching every existing table. List/dict fields (`related_files`, `source_refs`, `allowed_actions`, `options`) are stored as JSON-serialized `TEXT`, matching how the codebase already handles similar fields elsewhere.

### 2.1 `work_items`

| Column | Type | Notes |
|---|---|---|
| `work_item_id` | TEXT PRIMARY KEY | uuid |
| `created_at` | TEXT | |
| `updated_at` | TEXT | |
| `source_type` | TEXT | |
| `source_id` | TEXT | |
| `current_state` | TEXT | validated against the state list (§3) at write time, Python-side — matching the existing `_validate_choice()` pattern in `dispatch/models.py`, not a DB `CHECK` constraint |
| `priority` | TEXT | |
| `consequence_level` | INTEGER | 0–5 |
| `assigned_function` | TEXT | |
| `required_action` | TEXT | |
| `source_confidence` | TEXT | |
| `due_date` | TEXT NULL | |
| `related_files` | TEXT | JSON array |
| `source_refs` | TEXT | JSON array |
| `validation_status` | TEXT | |
| `scoring_status` | TEXT | |
| `cognitive_status` | TEXT | |
| `portal_card_id` | TEXT NULL | soft reference to `portal_cards.card_id` |
| `final_disposition` | TEXT NULL | |

### 2.2 `events`

| Column | Type | Notes |
|---|---|---|
| `event_id` | TEXT PRIMARY KEY | |
| `timestamp` | TEXT | |
| `work_item_id` | TEXT | `REFERENCES work_items(work_item_id)` |
| `event_type` | TEXT | |
| `actor_type` | TEXT | |
| `actor_id` | TEXT | |
| `previous_state` | TEXT NULL | |
| `new_state` | TEXT | |
| `summary` | TEXT | |
| `source_refs` | TEXT | JSON array |
| `requires_audit` | INTEGER | 0/1 |

**Coexistence note:** `events` is scoped to Work Items only. `LoadActivity`/`activities` is untouched and continues logging Load-scoped comments/status-changes/assignments exactly as it does today. A Load does not get a `work_item_id` in Stage 4 — that generalization (Jules item #9) is explicitly out of scope here, per your answer to Open Question 2.

### 2.3 `portal_cards`

| Column | Type | Notes |
|---|---|---|
| `card_id` | TEXT PRIMARY KEY | |
| `work_item_id` | TEXT | `REFERENCES work_items(work_item_id)` |
| `created_at` | TEXT | |
| `card_level` | INTEGER | 0–5 |
| `card_type` | TEXT | |
| `title` | TEXT | |
| `summary` | TEXT | |
| `source_refs` | TEXT | JSON array |
| `recommendation` | TEXT | |
| `decision_needed` | TEXT NULL | |
| `allowed_actions` | TEXT | JSON array |
| `required_closing` | TEXT | defaults to the fixed Constitution §17 sentence |

### 2.4 `approval_events`

| Column | Type | Notes |
|---|---|---|
| `approval_event_id` | TEXT PRIMARY KEY | |
| `timestamp` | TEXT | |
| `session_id` | TEXT NULL | soft reference — no `sessions` table exists until Stage 7 |
| `user_id` | TEXT NULL | soft reference — no `users` table exists until Stage 7 |
| `role` | TEXT NULL | |
| `work_item_id` | TEXT | `REFERENCES work_items(work_item_id)` |
| `portal_card_id` | TEXT NULL | `REFERENCES portal_cards(card_id)` |
| `object_type` | TEXT | |
| `object_id` | TEXT | |
| `object_version` | INTEGER | |
| `action` | TEXT | one of the approved action values (Spine Spec §10) |
| `previous_state` | TEXT NULL | |
| `new_state` | TEXT | |
| `comments` | TEXT NULL | |
| `authentication_context` | TEXT NULL | JSON, per Security Spec §10 shape |
| `audit_id` | TEXT | `REFERENCES audit_events(audit_id)` |

**Interim identity gap, stated plainly:** `session_id`/`user_id`/`role` are nullable and unauthenticated until Stage 7 (Security Foundation) lands. Between Stage 4 and Stage 7, any code writing an `approval_event` must populate these the same way the existing three HMAC email-decision gates do today (e.g. `user_id: "reviewer"`, `role: null`) — this is a known, temporary, explicitly-flagged weakness, not a silent gap. Stage 7's own launch package already calls for retrofitting real identity onto these fields (Jules items #4/#5). No Stage 4 code should claim `approval_events` rows are authenticated before Stage 7 ships.

### 2.5 `conflict_events`

| Column | Type | Notes |
|---|---|---|
| `conflict_id` | TEXT PRIMARY KEY | |
| `timestamp` | TEXT | |
| `work_item_id` | TEXT | `REFERENCES work_items(work_item_id)` |
| `conflict_type` | TEXT | one of the 10 types (Spine Spec §11) |
| `affected_layer` | TEXT | |
| `affected_function` | TEXT | |
| `trigger` | TEXT | |
| `details` | TEXT | |
| `options` | TEXT | JSON array |
| `recommended_path` | TEXT | |
| `human_decision_needed` | INTEGER | 0/1 |
| `current_state` | TEXT | |

### 2.6 `audit_events`

| Column | Type | Notes |
|---|---|---|
| `audit_id` | TEXT PRIMARY KEY | |
| `timestamp` | TEXT | |
| `work_item_id` | TEXT NULL | nullable — some audit events (e.g. future security events) are not Work-Item-scoped |
| `event_id` | TEXT NULL | `REFERENCES events(event_id)` |
| `actor_type` | TEXT | |
| `actor_id` | TEXT | |
| `action` | TEXT | |
| `previous_state` | TEXT NULL | |
| `new_state` | TEXT NULL | |
| `source_refs` | TEXT | JSON array |
| `hash` | TEXT NULL | SHA-256 hex if hashing is used, matching `cin_lite/archive.py`'s existing convention (never MD5) |
| `notes` | TEXT NULL | |

---

## 3. State List and Transition Table

Implemented as a Python module (`dispatch/spine/state.py`), not database rows or `CHECK` constraints — matching the existing codebase's convention of validating status fields in Python (`_validate_choice()` in `dispatch/models.py`) rather than at the SQL layer.

- `STATE_LIST` — the 25 states from `DISPATCH_SPINE_SPECIFICATION_v1.md` §6, verbatim.
- `ALLOWED_TRANSITIONS` — a `dict[str, list[str]]` encoding every transition rule from §7, verbatim.
- A single `transition(work_item, new_state)` function is the only path that may change `work_items.current_state` — it checks `new_state in ALLOWED_TRANSITIONS[current_state]`, raises on violation, and writes the corresponding `events` row in the same call. No other code path may write `current_state` directly. This is what makes the state-transition tests (Stage 4's own test requirement) meaningful — they test this one function exhaustively rather than hoping every caller behaves.

---

## 4. What Stage 4 Does Not Do

- Does not touch `LoadActivity`, `Load`, or any of the 27 existing domain tables.
- Does not create `users`, `sessions`, or any Security Foundation table — those are Stage 7.
- Does not migrate `IFTAReportApproval` onto `approval_events` — that's Stage 6's pilot migration, which depends on this schema existing but is a separate, later change.
- Does not add `card_level` to Portal templates or wire any UI — that's Stage 5.
- Does not add real authenticated identity to `approval_events` — that's Stage 7, as stated in §2.4 above.

---

## 5. Test Plan (per Spine Spec §20 Build-Readiness Standard)

- Schema validation tests — every table's required fields, every JSON-serialized field round-trips correctly.
- State transition tests — every approved transition in `ALLOWED_TRANSITIONS` succeeds via `transition()`; every non-approved transition raises.
- A structural test confirming no code path writes `work_items.current_state` except through `transition()` (matching the existing codebase's own structural-guard test pattern, e.g. the read-only guard on `build_ifta_review_dashboard()`).

---

## 6. Items Left to Implementation Judgment (Not Blocking This Design Review)

- Exact JSON-serialization helper reused vs. newly written (the codebase likely already has one; reuse it).
- Whether `dispatch/spine/store.py` mirrors `dispatch/store.py` function-naming conventions exactly (recommend yes, for consistency).

These are noted so the design review isn't blocked on implementation-detail bikeshedding — Jules has latitude here, consistent with how prior IFTA phases handled "Decisions Made Under Best Judgement" in their own launch packages.

---

## Authority Closing

This is a design/spec document only. No table, file, or code exists yet as a result of this document.

Implementation begins only after Mike approves this design.

Mike decides.
