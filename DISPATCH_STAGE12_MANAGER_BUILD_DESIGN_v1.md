# DISPATCH_STAGE12_MANAGER_BUILD_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 12 Build Design — Narrow Build Prompt
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 (No Spec. No Prompt. No Build. No Approval. No Implementation.) and the same discipline Stage 4 and Stage 7 already followed.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Approve Stage 12 build." Governed by `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` in full — this document narrows that design's Phase M2 (Manager Notification Store) and Phase M3 (Manager Portal Card Preparation) into a concrete, narrow build prompt with files in scope, files out of scope, and a test plan, exactly as `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §23 recommended as the cleanest first Manager prototype: *"A read-only Staff Report generator... no new Work Items, no new writes to `work_items.current_state`, no security or archive scope yet."*

---

## 1. What This Build Is

Manager reads three already-existing, already-tested signal sources, classifies and ranks what it finds using `MANAGER.md`'s own taxonomy and priority framework, and — only for items that clear the Review Needed bar — creates a Work Item and a Portal Card through the Spine's existing, unmodified machinery. A new, read-only `/manager` Portal page renders the result. Nothing is approved, booked, submitted, or transitioned by anything other than Mike, ever, anywhere in this build.

This is Phases M2 and M3 combined into one build, because M3 (rendering) is not independently demonstrable without M2 (signal aggregation) — there would be nothing to render.

---

## 2. A Finding That Shapes This Build's Scope

Direct inspection of the running `jax1313-outlook/Dispatch` codebase, done before writing this design, found: **nothing in `portal/` reads or renders the Spine's `portal_cards` table.** Confirmed by a full-repo grep — zero references to `list_portal_cards`, `create_portal_card`, or `dispatch.spine` (excluding a documentation comment in `portal/auth_helpers.py`) anywhere under `portal/`.

This is the concrete, code-level form of the gap Stage 11 already named as the second-most-critical MVP issue: Jules #9, the Sandbox/Work Item bridge — the Spine exists but nothing in Portal displays what it produces. Without addressing this, Manager could write Work Items and Portal Cards all day and Mike would never see one.

**Recommended resolution (applied in this design, pending confirmation):** this build includes one minimal, new, read-only Portal route (`/manager`) that renders Spine `portal_cards` — nothing else. It does not touch `portal/models/sandbox.py`, `conflict.py`, or any existing template's rendering path. It does not attempt to solve Jules #9 generally (bridging Sandbox itself into Work Items) — it solves only the narrower problem this build actually needs: a place for Mike to see what Manager produces. This keeps the fix scoped to exactly what's required and leaves the broader Sandbox/Work Item bridge as its own, separately-scoped future item.

---

## 3. Signal Sources — What Manager Actually Reads

`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md`'s Phase M2 described this loosely as "`dispatch/notifications.py`'s trigger points." On inspection, `dispatch/notifications.py` is a send-path (it renders and emails), not a queryable signal log — hooking Manager into it would mean intercepting outbound email, which is a larger and riskier change than reading state. **Refinement, not a deviation from doctrine:** Manager instead calls the same read-only detection functions `notifications.py`'s callers already use internally, none of which are modified:

| Source | Function | Returns |
|---|---|---|
| Stalled loads | `dispatch.services.check_stalled_loads()` | Loads past their per-status stall threshold |
| Overdue settlements | `dispatch.services.check_overdue_settlements()` | Settlements past due date |
| Open exceptions | `dispatch.services.list_exceptions()` (unresolved only) | `ExceptionNotice` records |
| Unresolved conflicts | `portal.models.conflict.get_unresolved()` | Conflict Notices with `severity`/`human_decision_required` |
| IFTA suspect entries | `dispatch.services.list_suspect_ifta_fuel_purchases()` | Computed at read time (not persisted — Manager reads it live, does not attempt to persist it itself) |
| Existing Work Items | `dispatch.spine.store.list_work_items()` | Anything already in the Spine, so Manager doesn't duplicate what's already tracked |

`dispatch/notifications.py` itself is untouched — zero lines changed.

---

## 4. Classification and Priority — Pure Logic, No New Doctrine

- **Classification** — `MANAGER.md` §7's nine classes (Routine, Status, Review Needed, Decision Needed, Conflict, Authority, Archive, Library Candidate, Noise), applied per signal type:
  - Stalled load / overdue settlement below a severity threshold → **Status**.
  - Stalled load / overdue settlement above threshold, or any unresolved `critical`-severity Conflict Notice → **Decision Needed** or **Conflict** per `_derive_card_level`'s existing severity mapping.
  - Open `ExceptionNotice` → **Review Needed**.
  - IFTA suspect entry → **Review Needed** (Partially-Verified-shaped, per `INTELLIGENCE_VERIFICATION_WORKFLOW.md`, not blocking).
- **Priority** — `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §8's nine-tier framework, applied as a pure ranking function over classified signals. No new priority doctrine; this build only implements the ranking already specified.

---

## 5. What Gets Persisted — And What Doesn't

**Only signals classified Review Needed or above get a Work Item + Portal Card.** Routine/Status/Noise signals are counted in the Staff Report summary (a total, e.g. "14 routine items, no action needed") but are **not** individually persisted as Work Items — writing a row for every routine stalled-load check would create exactly the noise `MANAGER.md` §13 defines as failure, for zero governance value. This is a design decision worth Mike's explicit confirmation (flagged here, recommended default applied): if Mike wants every Auto-log-tier signal individually logged as a Work Item for completeness, that's a small, additive change to this same build — but the recommendation is not to, matching Attention Protection Rule #1 (`MANAGER.md` §10): "Keep routine work quiet."

**No new database table.** Every candidate in `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §19 (`manager_notifications`, `manager_recommendations`, etc.) was already marked "Later," not needed for M2/M3. Dedup (§6 below) uses the Spine's existing `work_items` table via `source_type`/`source_id` lookup — no new schema, matching the hard constraint against creating tables.

---

## 6. Dedup — Version Doctrine Where It Exists, Source-Identity Where It Doesn't

`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §16 specifies Version-Doctrine-based dedup (don't re-surface an unchanged item). On inspection, this only fully works today for **Sandbox** entries, which carry `version`/`last_change` since Stage 5. Conflict Notices, `ExceptionNotice`, and IFTA suspect entries do **not** have version fields yet — Stage 8's reconciliation flagged this as an open gap, not yet built.

**This build's dedup rule, stated plainly:** before creating a new Work Item for a signal, Manager checks `list_work_items()` for an existing, non-terminal Work Item with matching `source_type`/`source_id`. If one exists, Manager does not create a duplicate — it leaves the existing item alone (this build does not update/enrich existing Work Items yet; that's additive scope for a later pass, not required for the first prototype). Where a `version` field is available (Sandbox-sourced signals only), it is used to detect a genuine change worth re-surfacing even if a Work Item already exists in a terminal state (e.g., previously dismissed) — for all other sources, a terminal-state Work Item simply stays closed; Manager doesn't reopen it.

---

## 7. Spine Interaction — Exact State Path, Zero Schema Changes

A new Work Item created by Manager moves through **already-approved, already-allowed transitions only**:

```
CREATED → VALIDATION_PENDING → VALIDATED → PORTAL_CARD_PENDING → PORTAL_CARD_CREATED
```

Every one of these four transitions is already present in `dispatch/spine/state.py::ALLOWED_TRANSITIONS`, unmodified since Stage 4. **This build never touches `ROUTED_TO_MANAGER`** — that state's dead end (`"ROUTED_TO_MANAGER": []`, flagged in the buildout design as a structural gap) remains exactly as-is. It is not needed for Manager to originate and card-ify its own signals; it would only matter if some *other* function needed to explicitly hand a Work Item to Manager, which is out of scope here. This means **the `ROUTED_TO_MANAGER` transition-target amendment `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §21 listed as a build-matrix item is not required for this build** — resolved by finding a valid existing path instead, not by amending the Spine schema.

Every transition is executed through `dispatch.spine.store.apply_transition()` — the same single writer path every other function uses. No direct `current_state` write anywhere in Manager's code, enforced by a structural guard test (§9).

---

## 8. Files In Scope

| File | Action | Purpose |
|---|---|---|
| `dispatch/manager/__init__.py` | New | Module docstring, placement rationale (mirrors `dispatch/spine/`, `dispatch/security/` — Manager's logic has no Flask/Portal dependency, learned from Stage 7's dependency-layering correction) |
| `dispatch/manager/signals.py` | New | Calls the six read functions in §3, returns a normalized list of raw signals |
| `dispatch/manager/classify.py` | New | Applies `MANAGER.md` §7's nine-class taxonomy to a raw signal |
| `dispatch/manager/priority.py` | New | Applies the nine-tier priority framework (`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §8) to a classified signal |
| `dispatch/manager/staff_report.py` | New | Orchestrates §3–§7: reads signals, classifies, ranks, dedups against `list_work_items()`, creates Work Items + Portal Cards for Review-Needed-and-above items via `apply_transition()` + `create_portal_card()`, returns a summary object (counts per class, ranked card list) |
| `portal/routes/manager.py` | New | `manager_bp` Blueprint, one route: `GET /manager` — calls `dispatch.manager.staff_report`, renders the result. Read-only; no POST, no action buttons |
| `portal/templates/manager.html` | New | Renders the Staff Report summary counts and the ranked Portal Card list, using the existing `.card-level` CSS classes from Stage 5 |
| `portal/routes/__init__.py` | Modify | Register `manager_bp`, no `url_prefix` (matches `security_bp`'s registration pattern) |
| `portal/templates/base.html` | Modify | Add one nav link to `/manager`, matching every other existing nav entry's style |
| `tests/test_manager_foundation.py` | New | Full test suite — see §9 |

**No file under `cin_lite/`, `dispatch/spine/`, `dispatch/security/`, `dispatch/notifications.py`, `dispatch/services.py`, `portal/models/sandbox.py`, or `portal/models/conflict.py` is modified.** All six signal-source functions are called, never altered.

---

## 9. Test Plan

- **Signal aggregation** — each of the six sources returns expected shape; empty-state handling (no stalled loads, no exceptions, etc.) produces a clean empty Staff Report, not an error.
- **Classification** — each of the nine `MANAGER.md` §7 classes is reachable and correctly assigned for representative fixture data per signal type.
- **Priority ranking** — Tier-1 signals always rank above Tier-9 regardless of insertion order; ties within a tier ordered by deadline/recency per the buildout design's conflict-handling rule.
- **Dedup** — a second run against unchanged signals does not create duplicate Work Items; a Sandbox-sourced signal with a changed `version` does create a fresh surfacing.
- **Spine interaction** — a created Work Item ends at `PORTAL_CARD_CREATED` via exactly the four-step path in §7; a Portal Card exists with the correct `card_level`, `card_type`, and the fixed `required_closing` sentence.
- **Structural guards** (matching the `tests/test_security_foundation.py` convention):
  - `dispatch/manager/` never writes `work_items.current_state` directly (source-scan, or a monkeypatched-write-detection test).
  - `dispatch/manager/` never calls any `dispatch.security.auth` write function, any `ApprovalEvent`-creating call representing a Mike decision, or any booking/submission function anywhere in the codebase.
  - `portal/routes/manager.py` exposes GET only — no POST/PATCH/DELETE route exists on `manager_bp`.
- **Portal rendering** — `GET /manager` returns 200, renders the Staff Report summary and ranked cards; a Level 0 (Routine/Auto-log) signal never appears as an individual card, only in the summary count.
- **Regression** — full existing suite re-run, matching every prior stage's "zero behavior change to anything not in scope" bar.

---

## 10. Explicitly Out Of Scope For This Build

- **Phase M4 (Stage Gate Monitor)** — needs a cross-repo read mechanism (Claude-3 ↔ Dispatch) not defined anywhere yet; a separate design question.
- **Phase M5 (Archive/IFTA Monitor, Archive half)** — blocked on the Archive Review Queue prerequisite build (Stage 6, not yet authorized); the IFTA half is already covered here via `list_suspect_ifta_fuel_purchases()` as a read-only signal, not as a dedicated monitor.
- **Phase M6 (Security Alert Monitor)** — a separate, security-adjacent build deserving its own rigorous walkthrough per the buildout design's own recommendation; not bundled into this first build.
- **Phase M7 (Policy Routing Hook)** — requires its own separate Mike decision on whether a policy engine is wanted at all.
- **The card-level unification Conflict** (three independent 0–5 implementations across `sandbox.py`/`conflict.py`/`PortalCard`) — a pre-existing issue, not new Manager scope; this build's `/manager` page reuses the Spine's own `PortalCard.card_level` directly and does not attempt to reconcile it with Sandbox's or Conflict's separate implementations.
- **Any write/action capability on `/manager`** — no approve, dismiss, promote, or route button. View-only, exactly as designed. Adding action buttons is Portal-Wide Enforcement-adjacent territory (it would need session/role awareness) and is not part of this build.
- **Enriching existing Work Items** — this build only creates new ones for previously-untracked signals; updating an existing Work Item's classification/priority as its underlying signal changes is additive future scope.

---

## 11. Walkthrough Requirements

Required, live, on a dev server — matching Stages 4, 5, and 7's convention:
1. Seed representative fixture data across all six signal sources (a stalled load, an overdue settlement, an open exception, an unresolved critical Conflict Notice, an IFTA suspect entry).
2. Run the Staff Report generator; confirm correct classification and priority ranking for each.
3. `GET /manager` live; confirm the rendered page shows the summary counts and the ranked card list, with Level 0 items reflected only in the count.
4. Re-run against unchanged data; confirm no duplicate Work Items or cards are created.
5. Confirm via direct DB inspection: every created Work Item's `current_state` is `PORTAL_CARD_CREATED`, reached through exactly the four allowed transitions in §7 — no other state was ever touched.
6. Full regression suite re-run clean.

---

## 12. Stop/Go

Go once: the structural guard tests pass (proving no direct `current_state` write, no security/approval-adjacent calls, GET-only route), the live walkthrough confirms correct classification/ranking/rendering/dedup, and full regression is clean. This build does not touch Security, Archive, Library, or any existing action route — a regression anywhere outside `dispatch/manager/`, `portal/routes/manager.py`, `portal/templates/manager.html`, and the two additive registration/nav edits listed in §8 would indicate scope drift, not a normal side effect of this build.

Mike decides.

---

*End of DISPATCH_STAGE12_MANAGER_BUILD_DESIGN_v1.md.*
