# DISPATCH_STAGE10_ALERT_GOVERNANCE_RECONCILIATION_v1.md

**Document Type:** Architecture Reconciliation — Stage 10 (Alert Governance Retrofit)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Reconciliation Draft — analysis only, no implementation authorized
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document is Stage 10 of the Migration Plan (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16), delivered in the same **Architecture Reconciliation Mode** Mike specified for Stages 6 through 9: no production code, no Dispatch repository modification, no pull request, no migrations, no new database tables, no Stage 10 build launch package. Discovery, mapping, reuse, alignment.

**Mike Zachary is final authority. AI decides nothing. Mike decides.**

---

## 1. Executive Summary

**What Stage 10 originally scoped.** Build the shared Mike-facing alert-governance control surface (suppress/alter/refine/downgrade/upgrade/merge/split/delete/create/change-level/change-destination); give real blocking behavior to authority-level Conflict Notices, which today are advisory even at high severity.

**What this reconciliation found that the original scope didn't fully anticipate.** There is not one alert/exception system to attach governance controls to — there are **five**, built independently across different features, none aware of the others:

1. `portal/models/conflict.py` — Conflict Notices (13 types, 3 severities, JSON-backed)
2. `dispatch/models.py::ExceptionNotice` — load-scoped exceptions (9 types, SQL-backed) — a **separate** system from #1, not the same records
3. `dispatch/models.py::IFTAException` — the six IFTA detectors (SQL-backed, insert-only, frozen-at-seal)
4. IFTA's `plausibility_warning` — an inline response field, **not a persisted record at all**
5. IFTA's suspect-entries confidence flag — computed at read time from `extraction_confidence`, **also not a persisted record**

This mirrors the same pattern Stage 6 found for Archive (three independently-built systems doing structurally similar things) and Stage 9 found for verification signals (independent seeds, no shared layer). It is the same underlying condition recurring: real capability, built well, per-feature — never unified. Stage 10's "one shared control surface instead of four separate ones" instinct was correct, and this reconciliation shows the need is larger than originally scoped: two of the five (#4, #5) cannot be governed by *any* future control surface without first becoming persisted, identifiable records, because there is currently nothing with an ID to attach a governance action to.

**What already aligns.** All five systems are already advisory-only by construction — none auto-blocks, auto-suppresses, or hides anything. This is Alert Governance Doctrine's core requirement, satisfied everywhere already, entirely by accident of how each was independently built rather than by design intent to follow this doctrine.

**What's missing.** Any Mike-facing control of any kind over any of the five. Any Alert Change Record. Any connection to Monday/Monthly reports (which, per earlier reconciliation stages, don't exist as concrete deliverables yet at all — a cross-cutting gap, not new here).

---

## 2. Alert Governance Requirements (Recap)

Per `ALERT_GOVERNANCE_DOCTRINE.md`: Mike is the alert governance authority and may suppress, unsuppress, alter, refine, enhance, downgrade, upgrade, merge, split, delete, create, or relevel any alert, or change its report destination — with **no uncontrolled automatic suppression** and no silent hiding of safety/compliance/authority/legal/business-commitment/source-conflict/role-boundary risk, ever. Every governance change produces an Alert Change Record (`alert_id, previous behavior, new behavior, reason, approved_by, timestamp, affected version, expected effect`). Manager may recommend refinement but may not permanently suppress a class without Mike's approval.

---

## 3. Existing Alert/Exception Systems Assessment

### 3.1 `portal/models/conflict.py` — Conflict Notices

13 `conflict_type` values, `SEVERITIES = [info, warning, critical]`, `human_decision_required` boolean, `card_level` (0–5, added Stage 5). `create_notice()`/`resolve_notice()` are the only mutation paths — no suppress, merge, split, or level-change action exists. `resolve_notice()` is a one-way close, not a governance action in the doctrine's sense (resolving *this instance* is not the same as Mike deciding the *alert rule itself* should behave differently going forward).

### 3.2 `dispatch/models.py::ExceptionNotice` — load-scoped exceptions

A **separate** model from Conflict Notices, scoped to Loads specifically: `delay, damage, missing_paperwork, equipment_issue, access_issue, weather, detention, refused, other`, `severity` (`low/medium/high/critical`), `status` (`open/investigating/resolved/closed`). This was not named in Stage 10's original scope (which listed "Conflict, exception, plausibility-warning, and suspect-entries panels") but is a real, distinct exception system that the phrase "exception panels" should be understood to include — confirmed via `dispatch/models.py` and the `/exceptions` Portal page.

### 3.3 `dispatch/models.py::IFTAException` — the six IFTA detectors

Already characterized in Stage 6's reconciliation: advisory, insert-only, frozen-at-seal. The strongest-governed of the five today, in the sense that it already has the most disciplined lifecycle — but "disciplined lifecycle" and "governable by Mike" are different properties, and it has none of the latter either.

### 3.4 IFTA `plausibility_warning` — not a record

Attached as a field on the API response when adding a trip leg (Phase 2), if the fleet-MPG estimate falls outside `DEFAULT_MPG_BAND`. **Never persisted as its own row with an ID.** It is recomputed on the fly each time relevant data is queried.

### 3.5 IFTA suspect-entries — not a record

Computed at read time in `build_ifta_review_dashboard()` from `extraction_confidence` values already stored on `IFTAFuelPurchase` rows. The confidence value is persisted; the "this is suspect" *classification* is not — it's a threshold comparison performed fresh every time the dashboard renders.

---

## 4. Governance Actions Mapping

| Doctrine Action | Current Support (Any of the Five Systems) |
|---|---|
| Suppress / unsuppress | None |
| Alter / refine / enhance | Only via full record edit (no "adjust this alert's behavior" concept) |
| Downgrade / upgrade | `card_level` exists on Conflict Notices only (Stage 5); no action to change it post-creation |
| Merge / split | None |
| Delete (the alert *rule*, not an instance) | None — `resolve_notice()` closes one instance, not a rule |
| Create (a new alert rule) | None — new alert *types* require a code change today, not a Mike-facing action |
| Change report destination | Partial — `dispatch/notifications.py`'s trigger-to-recipient mapping is the closest existing analogue (a real, working "this event type notifies this address" pattern), but it is not Mike-configurable at runtime, only in code |

---

## 5. The Alert-vs-Record Structural Gap

This is the reconciliation's most important finding for scoping a future build. Alert Governance's own Change Record schema requires an `alert_id`. **Two of the five systems have no ID to govern**, because they are not records:

- `plausibility_warning` is a string computed and returned inline; there is nothing to suppress, no row to mark "Mike downgraded this."
- Suspect-entries' classification is a threshold comparison over an already-stored confidence value; the *classification itself* — the thing Mike might want to suppress or re-threshold — doesn't exist as a persisted, addressable thing.

**Consequence:** a future governance control surface cannot uniformly govern all five systems as they exist today. The three record-backed systems (Conflict Notices, Exception Notices, IFTA Exceptions) could receive governance actions directly. The two non-record systems (plausibility warnings, suspect-entries) would need to first become persisted, identifiable records — or governance for them would have to operate one level up, at the *rule* level (e.g., "Mike disables the MPG-band check entirely" via a config value), which is a different, coarser kind of control than the per-instance suppress/merge/split doctrine describes for the other three.

---

## 6. Relationship to Stage 4's Spine `ConflictEvent`

Stage 4 already built a generic `conflict_events` table (`dispatch/spine/`) with `conflict_type`, `affected_layer`, `affected_function`, `human_decision_needed`, `current_state` — fields that closely mirror `portal/models/conflict.py`'s Conflict Notice shape, deliberately, per Stage 4's own design. **Nothing today routes any of the five alert-shaped systems through it.** This raises the same question Stage 8 raised for Archive: should a future Alert Governance build (a) add governance controls directly on top of the existing five fragmented stores, or (b) migrate the record-backed three (Conflict Notices, Exception Notices, IFTA Exceptions) onto the Spine's `conflict_events` schema first, then build one governance surface over that single unified table? Option (b) would mean one governance implementation instead of three; option (a) is faster but perpetuates the fragmentation this reconciliation just documented.

---

## 7. Full Capability Table

| Alert Governance Capability | Doctrine Source | Current Asset | Current Fit | Reuse / Modify / Build New | Notes |
|---|---|---|---|---|---|
| Advisory-only, never auto-suppress | Doctrine §1–2 | All five systems, by construction | **Strong Match** | Reuse (behavior already correct) | True by accident of independent design, not by following this doctrine |
| Mike governance authority (suppress/alter/etc.) | Doctrine §3 | None | Missing | Build New | See Section 4 |
| Alert Change Record | Doctrine §5 | None | Missing | Build New | Needs `alert_id` — two of five systems don't have one (Section 5) |
| Alert levels aligned to Portal consequence levels | Doctrine §4 | `card_level` on Conflict Notices only (Stage 5) | Partial Match | Modify | Not present on Exception Notices or IFTA Exceptions |
| Relationship to Manager (recommend, not silently suppress) | Doctrine §7 | Manager function itself not yet reconciled/built | Missing | Build New | Out of this stage's scope — depends on Manager's own future build |
| Relationship to Reports (Monday/Monthly/destination change) | Doctrine §9 | `dispatch/notifications.py` trigger-to-recipient mapping | Weak Match | Modify | Code-configurable today, not Mike-configurable at runtime; Monday/Monthly reports don't exist as deliverables yet |
| Unified alert data model | Implied by "one shared control surface" (Blueprint §14) | Spine `conflict_events` (Stage 4) exists but unused by any producer | Partial Match | Reuse (schema) + Modify (wire producers to it) | See Section 6 |
| Non-record alerts (plausibility warnings, suspect-entries) | N/A — structural prerequisite | None | Missing | Build New | Must become persisted records before any governance action can target them |

---

## 8. Relationship to Other Stages

- **Stage 4 (Spine, delivered).** The `conflict_events` schema is a direct, ready-made target for unifying the three record-backed alert systems — Section 6.
- **Stage 5 (Portal, delivered).** `card_level` already exists on Conflict Notices; extending it to Exception Notices and IFTA Exceptions is additive, consistent work, not new design.
- **Stage 6 (Archive, reconciled).** Rejected/resolved alert instances presumably archive somewhere eventually — no current code path does this for any of the five systems; worth noting as a downstream consideration for whichever future build lands first.
- **Stage 9 (Verification, reconciled).** IFTA's suspect-entries confidence float is now relevant to *two* future builds (Verification's Partially Verified classification, and this stage's alert governance) — both would touch the same underlying `extraction_confidence` field for different purposes. A future build sequencing decision, not a conflict.

---

## 9. What Already Exists

Five independently-working advisory systems, all correctly non-blocking. `card_level` on Conflict Notices. `dispatch/notifications.py`'s trigger-to-recipient routing (a real, working "change report destination" analogue, just not Mike-configurable). Stage 4's `conflict_events` Spine schema, unused but ready.

## 10. What Is Missing

Any governance action of any kind, on any of the five systems. Any Alert Change Record. Persisted, addressable records for plausibility warnings and suspect-entries (a structural prerequisite, not just a missing feature). Monday/Monthly report integration (cross-cutting gap, confirmed again here).

## 11. What Can Be Reused

Stage 4's `conflict_events` schema, as the unification target for the three record-backed systems. `dispatch/notifications.py`'s trigger-to-recipient pattern, as the starting point for a Mike-configurable "change report destination" control. `card_level`'s existing derivation logic (Stage 5) as the template for extending levels to the other alert systems.

## 12. What Should Remain Unchanged

The advisory-only, never-auto-block behavior of all five systems — this is doctrine-correct today and any future build must preserve it, not tighten it into something that silently blocks. IFTA's frozen-at-seal guarantee for its own exceptions (a sealed quarter's exceptions are historical record; a future governance action changing the *rule* going forward must not rewrite what a sealed period already showed).

---

## 13. Open Questions for Mike

1. Should a future build unify the three record-backed alert systems onto Stage 4's `conflict_events` schema before adding governance controls (fewer total controls to build, but touches more existing code), or add governance controls directly to the three existing stores as they are (faster, but perpetuates three separate implementations)?
2. For the two non-record alerts (plausibility warnings, suspect-entries), does Mike want per-instance governance eventually (which requires making them persisted records first), or is rule-level governance (e.g., a config toggle to disable/adjust the MPG band or confidence threshold entirely) sufficient?
3. Given Monday/Monthly reports don't exist yet as concrete deliverables (confirmed across multiple reconciliation stages now), should "change report destination" be scoped down for an initial build to just Portal-card-level vs. email, deferring report-specific routing until those reports themselves are built?

## 14. Recommendation and Next Steps

This reconciliation confirms Stage 10's original instinct (one shared control surface, not four) was right, and sharpens it: the real prerequisite work is partly structural (two of five alert types need to become records before they can be governed at all) and partly a sequencing choice (unify onto Stage 4's schema first, or govern the fragments directly). Both are real engineering decisions with different costs, not something to default on without Mike's input.

**No implementation is authorized by this document.** A future Stage 10 build launch package is the next artifact, not created here.

---

## Authority Closing

This is an architecture reconciliation document only.

No code was written. No file in the Dispatch repository was modified. No pull request was opened. No migration or database table was created. No Alert Governance capability was built or implemented.

Mike Zachary remains final authority.

**Mike decides.**
