# DISPATCH_STAGE12_MANAGER_M4_M6_BUILD_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 12 Build Design — Narrow Build Prompt (Phases M4–M6)
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 and the same discipline every prior build stage in this plan has followed.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Approve Stage 12 build for phases M4-M6." Governed by `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §20 (phase definitions) and builds directly on the already-shipped Stage 12 M2+M3 (`dispatch/manager/`, `stage12-manager-foundation`, commit `acb9d76`).

---

## 1. Honest Readiness Check Before Scoping Any Code

Investigated each phase directly against the running codebase before writing anything below. The three phases are not equally ready:

| Phase | Readiness | Why |
|---|---|---|
| **M4 — Stage Gate Monitor** | **Not buildable as originally scoped.** No design authorizes this. | Tracking `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`/`DISPATCH_BLUEPRINT_DECISION_LOG.md` means reading state that lives in the **Claude-3 repository**, not Dispatch. Nothing in this codebase reads across repositories today — no such mechanism has ever been designed, let alone approved. Building one now (live GitHub fetch with credentials, or a new sync job) would be a materially larger, security-relevant change bolted onto what's supposed to be a narrow read-only monitor. This exact gap was already flagged, unresolved, in both `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §20 and `DISPATCH_STAGE12_MANAGER_BUILD_DESIGN_v1.md` §10. |
| **M5 — Archive/IFTA Monitor** | **Partially buildable.** IFTA half: yes. Archive half: no. | The Archive half needs the Archive Review Queue (`ARCHIVE_REVIEW_POLICY.md` §3), which `portal/models/archive.py` still does not implement — confirmed by direct inspection, unchanged since Stage 6's reconciliation. That's a separate, not-yet-authorized Stage 6 build; this build cannot manufacture a queue that doesn't exist. The IFTA half is genuinely buildable: `dispatch.services.list_ifta_report_approvals()` and `list_ifta_exceptions(approval_id)` already exist and are read-only. |
| **M6 — Security Alert Monitor** | **Fully buildable.** | `dispatch.security.store.list_security_events()` already exists, already tested (Stage 7), and is read-only. Nothing new needed on the security side. |

**Recommendation, applied in this design pending confirmation:** build M6 in full and M5 narrowed to its IFTA half only. Do not attempt M4 or M5's Archive half in this pass — both are blocked on decisions/prerequisites this build cannot resolve on its own. If Mike wants M4 pursued, the open question below needs an answer first; that answer, not this document, is what would unblock it.

**Open question for Mike, not assumed:** M4 needs a way for Manager to see Claude-3's stage status without becoming a live cross-repo integration. The one precedent this codebase already has is Stage 2's `dispatch/docs/` mirror — Claude-3 documents copied in, refreshed periodically, marked "do not edit here." A parallel approach (a small, manually-refreshed stage-status snapshot file mirrored the same way) is the lowest-risk option, but it's still a new pattern this document isn't authorized to invent unilaterally. Recommend deferring M4 to its own short design pass once Mike confirms that approach (or proposes a different one) — not bundled into this build.

---

## 2. What Gets Built: M6 (Security Alert Monitor)

**Signal source — new: `dispatch/manager/security_monitor.py`.** Unlike the five existing signal sources (one raw record → one signal), a security pattern is an *aggregation* over multiple `SecurityEvent` rows, so it gets its own module rather than a one-line addition to `signals.py`.

- Reads `dispatch.security.store.list_security_events()` for a rolling 24-hour window (computed from each event's own `timestamp`, no new persisted state).
- Groups `LOGIN_FAILURE` events by identity. Two shapes exist in the data (confirmed in `dispatch/security/auth.py::login()`): unknown-identity failures carry `user_id=None` and `details={"display_name": ...}`; wrong-PIN failures carry a real `user_id`. Grouping key: `user_id` if present, else `details.get("display_name")`.
- Groups `PERMISSION_DENIED` events by `(user_id, details.get("path"))`.
- **Threshold, matching the existing security-relevant discipline (`SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §4.3's own "repeated failed PIN attempts should trigger... review" language, and `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §9's "single failures auto-log; a pattern escalates"):** 3 or more matching events within the window → one Security Alert signal. Fewer than 3 → not surfaced at all (a single denial is the system working correctly, not an anomaly).
- Output: one normalized signal per pattern, `source_type="security_pattern"`, `source_id` built as `f"{event_type}:{key}:{window_date}"` so the same day's ongoing pattern for the same identity doesn't re-materialize a duplicate Work Item, while a new day's continued pattern gets its own fresh entry — bounded, not permanently silenced.

**Classification/priority:** always `Conflict` (card_level 4), always Tier 1 (safety/security/legal/compliance/authority) — no graduated severity, matching the design's own framing that a security pattern is inherently Tier 1 regardless of which specific pattern fired.

**Zero write access, anywhere.** `dispatch/manager/security_monitor.py` calls exactly one function — `list_security_events()` — and nothing else in `dispatch.security`. A structural guard test (matching the rigor `tests/test_security_foundation.py` already established) confirms no call to `create_user_with_pin`, `change_pin`, `reset_pin`, `revoke_pin`, `login`, `create_session`, or `revoke_session` anywhere in the new module.

---

## 3. What Gets Built: M5, IFTA Half Only

**Extends `dispatch/manager/signals.py`** with a sixth true signal source: `IFTA_EXCEPTION`.

- Reads `dispatch.services.list_ifta_report_approvals()`, filters to `status == "draft"` (submitted, not yet sealed — the window where an exception is still actionable before Mike finalizes the quarter). Sealed quarters are not re-scanned; their exceptions are historical record, not open work.
- For each draft approval, reads `dispatch.services.list_ifta_exceptions(approval_id)` — already a read-only function, already used by the existing `build_ifta_review_dashboard()`.
- `source_id` is the exception's own `exception_id` (every `IFTAException` already has one).

**Classification:** `Review Needed` (card_level 2) — matches doctrine's "advisory only, never blocks" framing (`dispatch/models.py::IFTAException`'s own docstring: "nothing in this codebase reads an exception as a reason to block a submission or a seal"); worth a look before sealing, not a hard stop.

**Priority:** Tier 1 (safety/security/legal/compliance/authority) — same reasoning already applied to IFTA suspect entries in the M2+M3 build: an uncorrected exception risks an inaccurate government filing.

**Known, accepted limitation, flagged not hidden:** once a quarter seals, this build does not retract or update the card for exceptions found in it — consistent with M2+M3's existing "no enrichment of existing Work Items" scoping. Since IFTA exceptions are explicitly advisory/historical regardless of seal status, a lingering card is a minor, low-consequence gap, not a correctness problem — flagged the same way the M2+M3 walkthrough report flagged its own known limitations.

---

## 4. Files In Scope

| File | Action | Purpose |
|---|---|---|
| `dispatch/manager/security_monitor.py` | New | Security event pattern detection (§2) |
| `dispatch/manager/signals.py` | Modify | Add `IFTA_EXCEPTION` source type + collection (§3); call `security_monitor` for the new `security_pattern` signals |
| `dispatch/manager/classify.py` | Modify | Add classifiers for `IFTA_EXCEPTION` (→ Review Needed) and `security_pattern` (→ Conflict, always) |
| `dispatch/manager/priority.py` | Modify | Add Tier 1 mapping for both new source types |
| `tests/test_manager_foundation.py` | Modify | New tests for IFTA exception detection (draft-only filter, dedup), security pattern detection (threshold, grouping, dedup-by-day), and structural guards proving zero write access to `dispatch.security` |

**`dispatch/manager/staff_report.py` needs no change** — the orchestrator is already source-type-agnostic; both new signal types flow through the existing classify → rank → dedup → materialize pipeline unmodified. This is the payoff of M2+M3's original design: adding a signal source doesn't require touching the core loop.

**No file under `dispatch/security/`, `portal/models/archive.py`, `cin_lite/`, or any existing route/template is modified.** M6 reads `dispatch/security/store.py`; it does not touch it.

---

## 5. Test Plan

- **Security pattern detection:** 2 `LOGIN_FAILURE` events for the same identity → no signal (below threshold). 3+ → one `Conflict`/Tier-1 signal. Mixed unknown-identity and known-identity failures for the same person are *not* conflated (different grouping keys, by design — an unknown-identity attempt and an authenticated wrong-PIN attempt are different risk shapes even if a human later realizes they're the same person). A second run within the same day does not duplicate the Work Item; a pattern continuing into a new day produces a fresh one.
- **IFTA exception detection:** exceptions on a `draft` approval are surfaced; exceptions on a `sealed` approval are not (re-scanned and confirmed absent from a fresh signal collection). Dedup holds across repeated runs.
- **Structural guards:** `security_monitor.py` never calls any `dispatch.security.auth` function, only `dispatch.security.store.list_security_events`. Regression confirms zero change to any existing IFTA, security, or archive behavior.
- **Full regression** re-run clean, matching every prior stage's bar.

---

## 6. Walkthrough Requirements

Required, live, matching the M2+M3 convention:
1. Seed 3 `LOGIN_FAILURE` events for one identity; confirm a Security Alert-shaped card appears on `/manager` at Conflict/Tier 1.
2. Seed 2 more (5 total, same identity, same day); confirm no duplicate card — dedup holds.
3. Create a draft IFTA report approval with at least one exception; confirm it appears on `/manager` at Review Needed/Tier 1.
4. Seal that approval; confirm a *fresh* signal collection no longer includes it as a new signal (its already-materialized card may still show, per the flagged limitation in §3 — confirmed, not silently assumed).
5. Full regression suite re-run clean.

---

## 7. Stop/Go

Go for M6 and M5's IFTA half once structural guards pass, the live walkthrough confirms correct pattern detection and dedup, and full regression is clean. M4 and M5's Archive half remain explicitly out of scope for this build — not a silent omission, a stated blocker requiring a separate decision (M4) or a separate, not-yet-authorized prerequisite build (M5 Archive half, Stage 6).

Mike decides.

---

*End of DISPATCH_STAGE12_MANAGER_M4_M6_BUILD_DESIGN_v1.md.*
