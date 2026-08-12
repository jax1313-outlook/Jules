# DISPATCH_END_TO_END_DEPLOYMENT_PLAN_v1

Program: Dispatch
Status: **Doctrine locked in. Sequence formalized. No implementation authorized by this
document — each stage requires its own separate, explicit go-ahead, per this program's standing
practice.**
Origin: Mike's "DISPATCH INTEGRATION DOCTRINE LOCK-IN" directive, formalizing the end-to-end
integration recommendation into a binding plan.
Rule: No code changes authorized by this document. This is the governing sequence document for
all future Dispatch integration work; individual stages get their own scope documents and their
own implementation go-aheads.

---

## 1. Architectural Decision

**One Repository. Many Departments. Clear Boundaries.**

Dispatch remains the runtime system. Tri-department repositories (`l2-intelligence-agent.`,
`Library`, `Publisher`) serve as contract and specification references, not runtime
dependencies.

## 2. Accepted Integration Strategy

**Path 1A — Extend Dispatch in place — accepted, goes first.** Dispatch's native models
(`portal/models/{intelligence,library,publisher,archive}.py`) grow toward the tri-department
contracts' shape, in Dispatch's own codebase, on Dispatch's own Flask/JSON-file runtime. No new
dependency, no new deploy target.

**Path 2 — Integration Bridge Mission (Publisher ↔ `cin_lite` Proposal Writer) — accepted,
follows Path 1A.**

**Path 1B — Vendor the tri-department repos as pip/git runtime dependencies — deferred.**
Reason: those repos are tested and valuable, but use in-memory reference stores and object
shapes (15-collection taxonomy, `candidate_id`/`proposed_object_code` splits) that don't match
Dispatch's current Flask/JSON-file runtime. Vendoring now would mean rewriting Portal
routes/templates around foreign shapes, or building storage adapters under another data model —
blast radius disproportionate to the current goal. Dispatch remains the deployable runtime.

## 3. Standing Decisions Reaffirmed, Not Reopened

- **Manager**: DORMANT / RESERVED CAPABILITY / NOT IMPLEMENTED. Preserved in architecture and
  documentation only (`jax1313-outlook/Dispatch:docs/MANAGER.md`). Not part of this integration
  plan's runtime scope.
- **Archive**: Option A, Maintain Separation. No consolidation, no migration, no merge.
  `cin_lite/archive.py` and `portal/models/archive.py` remain separate, as already decided.

## 4. Explicit Prohibitions

Do not reopen Manager. Do not reopen Archive consolidation. Do not vendor the tri-department
repos. Do not create a giant repo blob. Do not erase departmental boundaries.

## 5. Required Plan Sequence

### Stage 1 — Wire the Two Free Stage 6 Links

Purpose: create the first low-risk end-to-end movement between existing Dispatch departments,
finally giving the Library review gate (built, tested, unreached since Stage 5) real traffic.

Target links: (1) Intelligence → Library candidate promotion, (2) Library approval → Publisher
requirement trigger.

Constraints: stay narrow and mechanical. Do not attempt the full Intelligence contract. Do not
attempt all six missing Intelligence concepts. Do not fully rebuild Publisher. Do not vendor
outside repos.

Expected flow:
```
Existing Intelligence record
    -> Library candidate
    -> Library review_candidate()
    -> Approved Library item
    -> Publisher requirement trigger
```

Full scope, answering all eight required questions with evidence already on record:
**`STAGE_1_INTELLIGENCE_LIBRARY_PUBLISHER_LINK_SCOPE_v1.md`** (companion document, this
session).

**STAGE 1 — IMPLEMENTED.** Approved and executed on `dispatch/canonical-reconciliation-
integration` (commit `d77cbae`): `intelligence.promote_to_candidate()` (broker-type only) and
`library.py`'s `_trigger_publisher_on_approval()` hook, exactly as scoped, no deviation. Full
suite re-verified green.

### Stage 2 — Integration Bridge Mission

Purpose: connect Publisher to `cin_lite` proposal-writing capability. This is the main
end-to-end production bridge.

Core target:
```
Publisher -> Proposal Writer -> Draft/Outline -> Approval discipline -> Archive destination
```

Constraints, matching Stage 1's "stay narrow and mechanical" discipline: do not reopen Archive
consolidation (Option A stands — a drafted proposal's canonical home stays `cin_lite/archive.py`,
not migrated into `portal/models/archive.py`). Do not rebuild `cin_lite/agents/proposal_writer.py`
or its outline logic — reuse as-is. Do not merge `publisher.ACTION_TYPES` and
`cin_lite.control.ACTIONS` into one shared vocabulary — bridge via an explicit mapping, not a
unification. Do not weaken either system's existing approval gate (Publisher's `approved_by`
identity check, `cin_lite`'s HMAC-token verification) to make them fit together. Do not attempt
to unify `sandbox_id`/`action_id` with `contract_id` into one identifier system — use an explicit
reference field instead.

Required questions for Stage 2:

1. What Publisher `action_type`(s) should be eligible to trigger a proposal draft?
2. What minimum identifier bridge is needed between Publisher's `action_id`/`sandbox_id` and
   `cin_lite`'s `contract_id`?
3. What triggers the draft — a new Publisher status transition, an explicit new action, or a
   manual trigger separate from the existing `PENDING→DRAFT` flow?
4. Does drafted content flow back into Publisher's own queue as new data on the action, or stay
   entirely in `cin_lite`'s store, referenced only by ID?
5. What approval discipline applies to a bridged draft — Publisher's existing `approved_by` gate
   extended to cover it, `cin_lite`'s existing token-based approval, or a new explicit step?
6. Where does approved content get archived, given Option A?
7. What test proves the full path works?
8. What UI/Portal changes are required, if any?

Required output: **`STAGE_2_PUBLISHER_PROPOSAL_WRITER_BRIDGE_SCOPE_v1.md`** (companion document,
this session), which surfaces a prerequisite finding question 1 exposes: full scoping done there.
Ambiguity resolved via `DISPATCH_INTEGRATION_BRIDGE_SCOPE_v1.md`: Option A, `GOVCON_PROPOSAL`.

**STAGE 2 — IMPLEMENTED.** Approved and executed on `dispatch/canonical-reconciliation-
integration` (commit `48f22d5`): a ninth Publisher action type
(`"GovCon Proposal Draft Required"`), an optional `contract_id` field, and a `PENDING→DRAFT`
hook calling `cin_lite.pipeline.resolve_decision()` — the same function `cin_lite`'s own
email-decision flow uses. Full suite re-verified green.

**Both stages of this plan are now implemented.** Nothing further authorized past this point
without a new, separate go-ahead.

### Beyond Stage 2

Not yet specified. Per Section 5 of the prior end-to-end recommendation, a presentation-layer
consolidation pass (Portal's fragmented Card/Queue/History views, Stage 6 Link 10) was suggested
as a natural next step after Stages 1-2, but is not part of this locked-in doctrine until named
here explicitly.

## 6. Governance

Each stage requires its own explicit go-ahead before implementation, matching every prior stage
of this program (Stages 3-5 of the canonical reconciliation branch, the Publisher button fix, all
prior "start X" instructions). This document fixes the sequence and the doctrine; it does not
advance authorization past scoping.

Mike decides.
