# DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1

Program: Dispatch
Status: **Investigation complete. Scoping only — no implementation authorized by this document.**
Origin: `DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md` Section 6, Stage 6
("Integrate object flow"), left unstarted when the `dispatch/canonical-reconciliation-integration`
branch was finalized at Approval Chain Safety Gate scope. Started at Mike's direction ("Scope
Stage 6 first") in place of directly implementing.
Rule: No code changes made or authorized by this document. Investigation was read-only against
`jax1313-outlook/Dispatch` branch `dispatch/canonical-reconciliation-integration`; no edits.

---

## 1. What This Document Is

The canonical matrix's target object flow is:

```
Intelligence Finding → Library Candidate → Library Review/Promotion → Publisher Requirement
→ Publisher Workspace → Proposal Writer/Content Worker → Draft Review Package → Human Approval
→ Archive Handoff → cin_lite Archive → Portal Card/Work Item/History
```

That's 11 nodes, 10 transitions. This document traces each transition against Dispatch's actual
code (file:line evidence, not assumption) and answers, per link: does this connection exist
today, and if not, what would building it actually require?

`docs/CANONICAL_RECONCILIATION_INTEGRATION.md:90` (written when the branch was finalized) already
stated flatly: *"No object-flow wiring exists... also out of scope for this finalized branch."*
This document is the detailed evidence behind that one-line statement.

Two structural facts anchor everything below:

- `reconciliation/adapters/*.py` (Stage 4's output) are confirmed **one-directional and
  read-only by design** — every file's docstring says so explicitly, none contain a `_save()`/
  `_load()` call, and a repo-wide `grep` shows they're imported only by their own tests. They
  translate Dispatch's existing records into canonical shapes for reporting; they do not, and
  structurally cannot without a scope change, write anything forward.
- `cin_lite/` and `portal/` are connected only one way: `portal/routes/*.py` imports `cin_lite`
  modules; nothing in `cin_lite` imports `portal`. This is the root cause of the Link 5 split
  below.

## 2. Link-by-Link Findings

**Link 1 — Intelligence Finding → Library Candidate: siloed, no code path.**
`portal/models/library.py::add_record(..., submitted_by="machine")` is the only function shaped
like a "Library Candidate" producer, and its own docstring admits nothing calls it that way yet
— confirmed by repo-wide grep, zero real call sites. Building this needs a new function (e.g.
`intelligence.promote_to_candidate()`) and a decision about which intelligence records qualify
and what triggers promotion.

**Link 2 — Library Candidate → Library Review/Promotion: fully built, unreached.**
`library.py::review_candidate()` (identity-gated via `RESERVED_SYSTEM_IDENTITIES`, requires
`pending_review` status) and its route `POST /api/library/review` are complete and correct — the
route's own docstring says it has no live traffic because Link 1 doesn't exist. Nothing to build
here; it's ready the moment Link 1 exists.

**Link 3 — Library Review/Promotion → Publisher Requirement: two disconnected manual surfaces.**
`review_candidate()` never calls `publisher.create_action()`. The only `create_action()` callers
are a human "Pursue" click on a freight opportunity and a manual creation route — both unrelated
to Library. Publisher *reads* Library's current snapshot at creation time (`available_data`/
`missing_data`) but nothing in Library *pushes* forward on approval. Needs a new post-approval
trigger — a genuine content-mapping decision, not a mechanical wire.

**Link 4 — Publisher Requirement → Publisher Workspace: already the same object.**
`create_action()`'s record *is* the workspace item, rendered straight off the same JSON store by
status group. Nothing to build. (Caveat: `update_action_status()` doesn't enforce that statuses
progress in order — a jump straight to `APPROVED` is currently possible if the caller supplies a
valid `approved_by`.)

**Link 5 — Publisher Workspace → Proposal Writer/Content Worker: real architectural split,
confirmed with line-level evidence.** This is `DISPATCH_INTEGRATION_BRIDGE_MISSION_v1`'s exact
scope, now confirmed rather than merely asserted:
- Publisher's own workspace has **no content-generation function anywhere** — `ACTION_TYPES` and
  `BROKER_PACKET_MANIFEST` are string labels, not generators.
- The only real drafting agent, `cin_lite/agents/proposal_writer.py::draft_outline()`, is
  reached exclusively through `cin_lite`'s own trigger chain: an HMAC-token email click →
  `portal/routes/decisions.py::process_decision()` → `cin_lite/pipeline.py::resolve_decision()`
  → `proposal.trigger()`.
- The two systems share no identifier (`sandbox_id`/`action_id` vs. `contract_id`), no action
  vocabulary (`publisher.ACTION_TYPES` vs. `cin_lite.control.ACTIONS`), no status model
  (`PUBLISHER_STATUSES` vs. one-shot email resolution), and no approval semantics
  (`approved_by` identity gate vs. HMAC token verification only).
This is a design decision, not a wire-up — matches what `DISPATCH_INTEGRATION_BRIDGE_MISSION_v1`
already scoped it as.

**Link 6 — Proposal Writer/Content Worker → Draft Review Package: object doesn't exist.**
`proposal.trigger()` goes straight from drafted outline to `archive.store_proposal()` with no
intermediate review state. `reconciliation/contracts.py` already explicitly declined to fabricate
a `DraftReviewPackage` shape for Dispatch, citing the No-Fabrication Rule — Dispatch has no
`readiness_packet_id`/`inventory_id`/`missing_notice_id` to populate one honestly. The object
needs to be designed before this link can be wired.

**Link 7 — Draft Review Package → Human Approval: exists on the Publisher side only.**
`update_action_status(..., "APPROVED", approved_by=...)` is a real, enforced gate (this branch's
Stage 5 work). No equivalent exists on the cin_lite proposal side, because Link 6's object
doesn't exist yet to be approved. Blocked on Link 6.

**Link 8 — Human Approval → Archive Handoff: already works, Publisher-queue side.**
`update_publisher_action()` calls `archive_publisher_action()` inline on `ARCHIVED` transition,
which itself refuses to archive without a valid `approved_by` (the Stage 5 fix). Nothing to
build here. No cin_lite-side equivalent, for the same reason as Link 7.

**Link 9 — Archive Handoff → cin_lite Archive: two incompatible archive engines, already
deferred.** `portal/models/archive.py` (id/section/record_data JSON) and `cin_lite/archive.py`
(contract_id-keyed, hash-verified file tree) have no bridge; the existing `archive_adapter.py`
docstring says so directly and declines to build one. This duplication question was already
spun out to `DISPATCH_ARCHIVE_ARCHITECTURE_REVIEW_MISSION_v1.md`, which is closed at "Maintain
Separation" (Option A) — so this link is not just unbuilt, it's **currently decided against**
being unified. Building it would require reopening that closed decision.

**Link 10 — cin_lite Archive → Portal Card/Work Item/History: the most-built link, but
fragmented across three parallel systems instead of unified.** Portal directly reads
`cin_lite.archive`/`pending`/`pipeline` at render time with no adapter needed — but
`archive_view()` renders three unrelated archive sources side by side on one page
(`portal/models/archive.py`, `cin_lite/archive.py`, `dispatch/store.py`'s retention table), and
"Card"/"queue" concepts are similarly split: Portal cards come from `sandbox.py` (freight
opportunities), not from cin_lite state at all; `/pipeline` and `/queues` read cin_lite's
pipeline directly; Publisher's own queue (Link 4) is a third, separate view. Nothing new needs
connecting — this is a presentation-layer consolidation question, not a data-flow gap.

## 3. Adjacent Finding Not in Original Scope (flagging per Conflict Notice Rule)

The investigation surfaced a duplication not previously documented: **two independent,
disconnected invocations of `cin_lite`'s intelligence-processing modules exist in Dispatch.**
`portal/helpers.py::load_and_process_sam()` calls `cin_lite.acquisition`/`processing`/
`summarizer`/`router` directly to populate Portal's SAM opportunity cards — bypassing
`cin_lite.pipeline.process_contracts()`'s archive/pending-store/email-checkpoint gate entirely.
Meanwhile `cin_lite.pipeline.process_contracts()` (the full, gated pipeline) feeds the separate
`/pipeline` and `/queues` views. Same source modules, two different call paths, one skips every
governance checkpoint the other enforces. This wasn't asked for by Stage 6 scoping and is
adjacent to, not part of, the 10 links above — flagging it here rather than silently expanding
this document's scope. Whether this needs its own mission document is Mike's call.

## 4. Tractability Summary

**Already works or fully built, just unreached — verify only:**
Link 2 (Library review/promotion), Link 4 (Requirement = Workspace), Link 8 (Publisher-side
archive handoff), Link 10 (Portal already reads cin_lite directly, needs consolidation not
connection).

**Mechanical new call sites, but each still needs a content/trigger design choice:**
Link 1 (Intelligence → Library candidate), Link 3 (Library approval → Publisher requirement).
Note: `reconciliation/adapters/*.py` cannot be extended for these — they're structurally
read-only by design; any real write path belongs in `portal/models/*.py` or a new bridge module.

**Require an actual architecture decision before any code — not wiring tasks:**
Link 5 (Publisher ↔ Proposal Writer — `DISPATCH_INTEGRATION_BRIDGE_MISSION_v1`'s exact scope,
now evidenced), Link 6 (Draft Review Package object doesn't exist), Link 7 (blocked on Link 6),
Link 9 (blocked on the already-closed Archive Separation decision — would require reopening it).

## 5. Resolves the Circular Dependency Noted in the Integration Bridge Mission

`DISPATCH_INTEGRATION_BRIDGE_MISSION_v1.md` Section 3, question 4 asked whether it depends on
Stage 6 being scoped first. Answer, now that Stage 6 is scoped: **yes, and that dependency is now
satisfied for Link 5 specifically.** This document confirms Link 5 is exactly and only the
Integration Bridge Mission's scope — no broader Stage 6 context changes what that mission needs
to resolve. The Integration Bridge Mission can now proceed on its own, using Section 2's Link 5
evidence above as its starting trace, without waiting on the rest of Stage 6.

## 6. What This Document Does Not Do

Does not authorize building any link. Does not reopen the closed Archive Separation decision
(Link 9 stays blocked on that). Does not expand into the new SAM-duplication finding (Section 3)
beyond flagging it. Does not propose an implementation sequence beyond the tractability grouping
in Section 4 — sequencing, if authorized, is a separate decision.

Mike decides.
