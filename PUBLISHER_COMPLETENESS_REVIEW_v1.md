# PUBLISHER_COMPLETENESS_REVIEW_v1

Program: Dispatch
Status: **Investigation complete. Findings only — no fix applied, no implementation authorized
by this document.**
Origin: Named alongside Library/Intelligence/Manager reviews in this session's status
confirmation; sharpened into a concrete task ("start Publisher completeness review"). Scoped in
`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md` Section 7 as a soft blocker on Integration
Bridge planning.
Rule: No code changes made. Read-only against `jax1313-outlook/Dispatch`
(`dispatch/canonical-reconciliation-integration`) — full read of `portal/models/publisher.py`,
`portal/routes/api.py`'s Publisher routes, `portal/templates/publisher.html`/`base.html`,
`tests/test_portal.py`'s Publisher tests, and the `reconciliation/` Publisher adapter.

---

## 1. What This Review Is

The canonical matrix declared Publisher a "Hybrid" winner: the tri-department Publisher contract
governs (readiness/review/approval), Dispatch's `cin_lite` proposal writer drafts. This review
asks: relative to the tri-department Publisher's six object contracts (`PublisherRequirement`,
`PublisherRecipe`, `ReadinessPacket`, `PartsInventory`, `MissingItemNotice`,
`DraftReviewPackage`), how complete is Dispatch's real `portal/models/publisher.py`?

## 2. Six Contract Concepts — Completeness Verdicts

| Concept | Verdict | Evidence |
|---|---|---|
| `PublisherRequirement` | **None** | No requirement object anywhere. Closest artifact: 3 flat manifest string-lists (`BROKER_PACKET_MANIFEST` etc., `publisher.py:43-51`) covering only 3 of 8 `ACTION_TYPES`, no per-item metadata. |
| `PublisherRecipe` | **None** | No content-recipe object. `cin_lite/agents/proposal_writer.py` has an implicit outline template, but it lives outside Publisher and returns a raw string, not a structured object. |
| `ReadinessPacket` | **None** | `READY` is purely a status-string label (`PUBLISHER_STATUSES[2]`); no function validates readiness before a human clicks the "Mark Ready" button. |
| `PartsInventory` | **Partial** | `library.py::get_available_company_assets()`/`get_missing_company_assets()` compute an available/missing split, but it's Library-owned, a plain string list, and snapshotted once at action creation — never refreshed. |
| `MissingItemNotice` | **Partial (weak)** | `missing_data` field exists and is displayed, but has no ID, no dedicated notice object, no resolution workflow — unlike this same codebase's real Conflict Notice system (`portal/models/conflict.py`), which has all three. |
| `DraftReviewPackage` | **None — explicitly disclaimed in-repo** | `reconciliation/contracts.py:114-122` states outright it deliberately does not reconstruct this object, because Dispatch has no `readiness_packet_id`/`inventory_id`/`missing_notice_id` to populate honestly, and fabricating them would violate the No-Fabrication Rule. |

Four of six concepts are fully absent; the two partial ones are thin, one-directional snapshots
owned by a different department (Library), not real Publisher-native objects.

## 3. The One Real Gate, and Nothing Else

`update_action_status()` (`publisher.py:120-148`) governs all five status transitions
(`PENDING→DRAFT→READY→APPROVED→ARCHIVED`). Tracing each:

- **PENDING→DRAFT, DRAFT→READY**: validated only by "is this a known status string." No check of
  `manifest`, `available_data`/`missing_data`, or anything else. Nothing prevents any action, from
  any starting status, from being set to any of these two values.
- **READY→APPROVED**: the one real precondition in the whole file — requires a non-empty,
  non-reserved-identity `approved_by` (the Stage 5 fix), independently re-verified again in
  `archive_publisher_action()` before archival.
- **→ARCHIVED**: no extra check in `update_action_status()` itself; the archive step's own
  separate gate is what actually enforces approval before the record persists.

So the tri-department model's "readiness" concept — a real precondition before DRAFT can advance
to READY — has no Dispatch equivalent at all. Only the final approval step is gated.

## 4. Live Bug Found: The "Mark Approved" Button Does Not Work

This is a finding about current, deployed behavior, not future architecture — flagged
prominently and separately from the completeness gaps above.

`portal/templates/publisher.html`'s "Mark Approved" button calls the shared JS function
`updatePublisherStatus(actionId, status)` (`portal/templates/base.html:105-111`), which posts
only `{action_id, status}` to `/api/publisher/update`. **It never collects or sends
`approved_by`.** No input field, prompt, or form for it exists anywhere in `publisher.html`,
`brief.html`, or `base.html` — confirmed by grep, the only `approved_by` UI references anywhere
in the templates are in the unrelated IFTA module, which *displays* an already-recorded value,
not collects one. The pattern for collecting extra input via a JS prompt already exists in this
same file (`resolveConflict()`, `base.html:113-121`) — it's simply not applied to this button.

**Consequence:** every real click of "Mark Approved" in the live UI sends
`approved_by: null` (or omits it), hits `PublisherApprovalError` inside
`update_action_status()`, gets caught as a 400 by the API route, and surfaces only as a generic
`alert(data.error)` with no state change. The Stage 5 approval gate — this program's own prior
work — is correctly enforced in the model layer and reachable via direct API calls or tests, but
**a human using the actual Publisher page today cannot approve anything through it.**

This is invisible to the existing test suite: every test that exercises `APPROVED` either
supplies `approved_by` explicitly (the legitimate-path tests) or is specifically testing the
rejection path — no test simulates the real button's actual request shape.

## 5. `BROKER_PACKET_MANIFEST` — Display Metadata Only

Confirmed as the closest thing to a requirement/inventory list, and confirmed to do nothing
beyond that: defined, consumed exactly once at action-creation time via `_manifest_for()`,
rendered read-only as a checklist. It plays no role in any status transition — moving an action
through DRAFT/READY/APPROVED never re-checks the manifest against available/missing data. 5 of 8
`ACTION_TYPES` (Rate Sheet Request, DocuSign Package Ready, Arrival Notice Draft, POD/BOL
Document Package Draft, Detention Evidence Draft) get no manifest at all — `_manifest_for()`
returns `[]` for all of them, untested.

## 6. Test Coverage Gaps

- No test exercises the actual UI button flow (Section 4's bug is untested precisely because no
  test sends the real request shape a browser click produces).
- No test asserts manifest content, or its absence, for the 5 unmapped action types.
- No test exists for content generation, because no content-generation code exists to test.

## 7. Adjacent Finding: Stale Logic in the Reconciliation Layer

`reconciliation/adapters/publisher_adapter.py:39` hardcodes `is_approval_enforced = False`
unconditionally, and its own docstrings plus `reconciliation/README.md` state the Stage 5 gate
"has not yet been applied" — but it has (Section 3 above). The adapter's claim is stale relative
to the real model; it was written before the Stage 5 fix and never updated. This is dead/stale
documentation in the reconciliation layer, not a Publisher-model gap — flagged for whoever
maintains `reconciliation/` next, out of this review's scope to fix.

## 8. Effect On The Integration Bridge Sequencing Call

`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md` called this a soft blocker, reasoning that
Publisher's shape was "already well-evidenced." This review sharpens that: Publisher is less
complete than that framing implied — it's not just "a tracker without drafting," it also lacks a
`PublisherRequirement`/`ReadinessPacket` concept entirely, meaning the Bridge would need to
resolve *what a Publisher requirement even is* before it could decide how the Proposal Writer
should relate to it, not just decide the relation itself. Whether this promotes Publisher
Completeness Review from soft to hard blocker status is Mike's call, not this document's.

## 9. What This Review Does Not Do

Does not build any of the six missing/partial contract concepts. Does not resolve the
Publisher/Proposal-Writer split (Integration Bridge Mission's scope, unchanged). Does not touch
`reconciliation/adapters/publisher_adapter.py`'s stale `is_approval_enforced` flag.

Mike decides.

---

## 10. Execution Status Update

**Section 4's bug — FIXED**, on separate explicit go-ahead ("Fix the Mark Approved button bug
now"), on `dispatch/canonical-reconciliation-integration` (commit `f5a42dd`). `base.html`'s
`updatePublisherStatus()` now prompts for the approving identity and forwards `approved_by` when
the target status is `APPROVED`, mirroring the existing `resolveConflict()` prompt pattern. A
regression test (`test_mark_approved_button_sends_approved_by`) pins the fix at the rendered-page
level, since the original bug was invisible to any test exercising the API directly. Full
Dispatch suite re-verified green after the change.

All other findings in this document (Sections 2, 3, 5, 6, 7, 8) remain open and unactioned —
this status update covers only the one live bug, not the broader completeness gaps.

Mike decides.
