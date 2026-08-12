# DISPATCH_INTEGRATION_BRIDGE_SCOPE_v1

Program: Dispatch
Status: **IMPLEMENTED.** Scope approved and executed on `dispatch/canonical-reconciliation-
integration` (commit `48f22d5`), exactly as scoped below — one deviation confirmed at
implementation time, not a departure: Section 3's flagged unknown (exact `cin_lite` call shape)
was resolved by reading `cin_lite/pipeline.py`/`cin_lite/workflows/proposal.py` fresh, landing on
`pipeline.resolve_decision(contract_id, "approve_proposal")` — the same function `cin_lite`'s own
email-decision flow calls. Full Dispatch suite re-verified green.
Origin: Stage 2 Decision — the ambiguity `STAGE_2_PUBLISHER_PROPOSAL_WRITER_BRIDGE_SCOPE_v1.md`
Section 0 raised is resolved. Option A chosen: Publisher gains a new action type, `GOVCON_PROPOSAL`,
as the bridge to `proposal_writer.py`. That decision is final and is not reopened by this
document — this document scopes the bridge around it.
Rule: No code changes authorized by this document. Scope only.

---

## 1. Approved Interpretation (Restated, Not Revisited)

```
Publisher Action -> proposal_writer.py -> Draft/Outline -> Publisher Approval Gate -> cin_lite Archive
```

Publisher owns the action. `proposal_writer.py` performs drafting, unchanged. Publisher remains
the approval authority; `approved_by` discipline is required, inherited from the existing gate,
not rebuilt. Archive follows Option A — drafted artifacts stay in `cin_lite/archive.py`. Manager
stays dormant. No vendoring. One repository, many departments, clear boundaries.

## 2. Data Model Changes

- **`ACTION_TYPES`** gains a ninth entry. Internal/mission designation: `GOVCON_PROPOSAL`. The
  literal string stored in `ACTION_TYPES` should match the existing human-readable convention of
  the other eight (e.g. `"Broker Packet Required"`) — proposed: `"GovCon Proposal Draft
  Required"`. Confirm exact literal at implementation time; not a deviation from the approved
  decision, just a style match to the existing list.
- **`create_action()`** gains one new optional parameter: `contract_id: str | None = None`,
  stored on the record only when provided (`None` for all 8 existing types — no behavior change
  for freight actions). This is the identifier bridge from Stage 2 Q2, implemented as a single
  shared field on the existing record shape rather than a parallel object or a new function.
- No changes to `PUBLISHER_STATUSES`, `RESERVED_SYSTEM_IDENTITIES`, or any existing action type's
  behavior.

## 3. Draft Generation

Hooks into the **existing `PENDING→DRAFT` transition** inside `update_action_status()`, the same
pattern Stage 1 used (hooking `_trigger_publisher_on_approval()` into `review_candidate()`'s
existing approval branch, not inventing a parallel status machine). When `new_status == "DRAFT"`
and `action["action_type"]` is `GOVCON_PROPOSAL`, call into `cin_lite`'s drafting capability using
`action["contract_id"]`, and store whatever reference identifier that call returns (e.g.
`proposal_reference_id`) on the action record.

**Exact call shape into `cin_lite` — to be confirmed against `cin_lite/workflows/proposal.py` and
`cin_lite/agents/proposal_writer.py` at implementation time, not asserted here from memory.**
What's already established: `draft_outline()` itself only returns a Markdown outline; archiving
is a separate step (`archive.store_proposal()`) currently performed by `proposal.trigger()`
alongside the email-decision flow's own brief-building. The bridge needs either (a) a direct call
to `draft_outline()` plus `archive.store_proposal()`, assembling a minimal brief itself, or (b) a
call into `proposal.trigger()`'s existing logic if it can be invoked outside the email-decision
context without carrying assumptions this new path can't satisfy. This is exactly the kind of
call-site detail implementation should verify by reading current code, not infer from this scope
document — flagged rather than guessed at.

For all 8 existing action types, this transition behaves exactly as it does today — the hook is
additive and type-gated, mirroring Stage 1's non-interference guarantee.

## 4. Approval Gate

**No new code required.** `update_action_status()`'s `APPROVED`-transition check (`approved_by`
required, must not be a `RESERVED_SYSTEM_IDENTITIES` member) already applies uniformly to every
action type, `GOVCON_PROPOSAL` included. This is the direct benefit of extending Publisher's
existing queue rather than building a parallel one — the governance work already done in Stage 5
covers this new type for free.

## 5. Archive

**No new archive code.** Per Option A, drafted content is archived by `cin_lite`'s own archiving
step (Section 3), landing in `cin_lite/archive.py` exactly as it does for the email-decision
flow today. `portal/models/archive.py` is not touched, written to, or extended. If Portal-side
visibility into archived GovCon proposals is wanted later, that's a read-only display question
(e.g. a `reconciliation/`-style translation for rendering), explicitly deferred — not part of
this bridge's write path.

## 6. UI Changes

Minimal, matching Stage 1's discipline. `publisher.html` already renders all 8 action types
through one shared template structure — `GOVCON_PROPOSAL` needs no new page, no new button. Two
new fields need an explicit display line each (`contract_id`, `proposal_reference_id` once set),
shown alongside the existing `sandbox_id` line. The existing "Generate Draft" and "Mark Approved"
buttons work unchanged — they already call `updatePublisherStatus(actionId, status)` generically;
the type-specific drafting behavior lives entirely in the backend hook (Section 3), invisible to
the button itself.

## 7. Entry Point / Creation

No new route. The existing manual `POST /api/publisher/create` route gains the ability to accept
an optional `contract_id` in its request body, passed through to `create_action()`. Whether a
human or a future `cin_lite`-side process is the real-world caller for GovCon proposal actions is
an operational question outside this scope document's job — the API surface supports either
without deciding it here.

## 8. Test Plan

One integration test walking the full chain: create a `GOVCON_PROPOSAL` action with a
`contract_id` → transition to `DRAFT` → assert `proposal_reference_id` is now set → attempt
`APPROVED` with no `approved_by` (fails, matching existing behavior) → approve with a valid
identity → assert status is `APPROVED` and the archived content is reachable via `cin_lite`'s
archive using the stored reference. Plus: a regression test confirming all 8 existing action
types' `PENDING→DRAFT` transition is unaffected (no drafting side effect fires for them), mirroring
Stage 1's "rejection/human-placed records don't trigger" negative tests.

## 9. What This Scope Does Not Include

No changes to `proposal_writer.py`'s drafting logic. No changes to `cin_lite`'s email-decision
flow, HMAC-token verification, or `cin_lite.control.ACTIONS` vocabulary — that path stays exactly
as it is, untouched, running in parallel. No archive migration or consolidation. No Manager
involvement. No vendoring of the tri-department repos. No new page or new route beyond the one
optional parameter noted in Section 7.

No implementation authorized yet. Scope only.

Mike decides.
