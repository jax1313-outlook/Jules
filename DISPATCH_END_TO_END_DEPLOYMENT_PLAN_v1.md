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

**Do not implement Stage 1 until scope is approved.**

### Stage 2 — Integration Bridge Mission

Purpose: connect Publisher to `cin_lite` proposal-writing capability. This is the main
end-to-end production bridge.

Core target:
```
Publisher -> Proposal Writer -> Draft/Outline -> Approval discipline -> Archive destination
```

**Recorded exactly as specified so far.** The directive establishing this document cut off
immediately after "Archive destination," before Stage 2's required questions, constraints, or
required scope-output filename were given (Stage 1's equivalent detail was fully specified;
Stage 2's was not). Rather than inventing that detail, per this program's No-Fabrication
discipline, Stage 2 stays recorded at exactly this level of detail until the rest is provided.
The evidence base already exists to scope it fully once directed —
`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md` and Stage 6 Link 5's findings already trace
the vocabulary/identifier/approval-semantics mismatches between Publisher's action queue and
`cin_lite`'s email-decision flow in detail.

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
