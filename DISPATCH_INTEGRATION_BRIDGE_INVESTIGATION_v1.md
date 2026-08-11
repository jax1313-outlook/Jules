# DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1

Program: Dispatch
Status: **Investigation complete. Dependency mapping only — not the Integration Bridge Mission
itself, not an implementation plan.**
Origin: Scope correction — authorized as a limited investigation to identify what must be known
before `DISPATCH_INTEGRATION_BRIDGE_MISSION_v1.md` can be safely planned. Explicitly not
authorization to start that mission, build, refactor, branch, or implement anything.
Rule: No code changes made. No branch created. Read-only against `jax1313-outlook/Dispatch`
(`dispatch/canonical-reconciliation-integration`, plus one new targeted read of
`portal/models/conflict.py` and a repo-wide grep for any Manager/work-item module — neither
found evidence of one existing). Synthesizes prior evidence
(`DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`, `ARCHIVE_AUTHORITY_AND_OWNERSHIP_REPORT_v1.md`,
`DISPATCH_DEPARTMENT_RECONCILIATION_v1.md`) plus this session's fresh checks.

---

## 1. Systems The Bridge Would Potentially Connect

| System | Code location | Current state |
|---|---|---|
| cin_lite email flow | `cin_lite/control.py`, `cin_lite/workflows/proposal.py`, `cin_lite/agents/proposal_writer.py`, `portal/routes/decisions.py` | Real, working, self-contained. HMAC-token gated, one-shot resolution per contract. |
| Portal action queue | `portal/models/publisher.py` | Real, working. `create_action()`/`get_queue()`/`update_action_status()` over one JSON store. |
| Publisher actions | Same module — "action queue" and "Publisher actions" are the same object set (Stage 6 Link 4 finding: Requirement and Workspace item are already the same record). |
| Library records/candidates | `portal/models/library.py` | Real, gated (`review_candidate()`), but the `submitted_by="machine"` candidate path is unreached — zero real callers repo-wide. |
| Intelligence outputs | `portal/models/intelligence.py` | Real storage, but no `status`/approval concept at all — flagged unresolved in `INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1.md`. |
| Manager work items/cards | **No such module exists.** Repo-wide grep for `work_item`, `WorkItem`, `class Manager`, `manager.py` returns zero matches anywhere in `portal/`, `dispatch/`, `cin_lite/`. Closest real analogs: `portal/models/sandbox.py` ("cards," freight opportunities) and `portal/models/conflict.py` (Conflict Notices — read this session, 290 lines, 13 `CONFLICT_TYPES`, `create_notice()` keyed by `sandbox_id`, `SEVERITIES` info/warning/critical, `human_decision_required` flag). Neither is a "Manager" module; both are department-specific, not a cross-department orchestration layer. |
| Archive destinations | `portal/models/archive.py` (id/section/record_data JSON) and `cin_lite/archive.py` (contract_id-keyed, hash-verified file tree) | Two separate, incompatible engines. Duplication question already closed — see Section 8. |

## 2. Objects That Might Move Between These Systems

| Object | Current shape / does it exist as a real object today |
|---|---|
| Email decision | Real — `cin_lite.control.ACTIONS` (`approve_archive`, `approve_proposal`, `reject`, `flag_review`, `deeper_analysis`), resolved in one step, no intermediate state. |
| Action item / Publisher request | Real — `publisher.create_action()` record; treated as one object (see Section 1). |
| Library candidate | Real shape (`add_record(submitted_by="machine")` → `pending_review` record), zero live producers. |
| Intelligence finding | Real storage shape exists (`intelligence.create_record()`), but no upstream "finding-generation" producer independent of a downstream trigger (`create_inquiry()` is itself triggered from a Publisher-adjacent sandbox action, not from Intelligence analysis). |
| Manager work item | **Does not exist as an object anywhere in the codebase.** Not a naming gap — no data model, no store, no route. |
| Archive record | Two incompatible shapes, not one object — see Section 1. |

## 3. Ownership Before Transfer

- Email decision: owned by `cin_lite` (GovCon contract flow) end to end — it doesn't currently transfer to another department's object, it resolves and terminates inside `cin_lite`.
- Action item / Publisher request: owned by Portal's Publisher module, created by a human "Pursue" click or a manual creation route — not produced by any other department automatically.
- Library candidate: would be owned by Intelligence before promotion, per the target flow — but since no producer exists (Section 1), there is no real "before" owner today, only a hypothetical one.
- Intelligence finding: owned by whichever caller writes it — today that's `create_inquiry()` (Publisher/sandbox-adjacent) or a manual API add, not an independent Intelligence-department process.
- Manager work item: no owner — no object exists.
- Archive record: owned by whichever engine wrote it. Portal-originated actions archive into `portal/models/archive.py`; `cin_lite`-originated contract data archives into `cin_lite/archive.py`. Each is self-contained; neither currently receives records from the other.

## 4. Ownership After Transfer (Target State, Per The Canonical Matrix — Not Current Reality)

- Intelligence Finding (Intelligence-owned) → Library Candidate (Library-owned once promoted) — mechanically plausible per Stage 6 Link 1-2, needs a new promotion function and a decision about which findings qualify.
- Library Candidate approved → Publisher Requirement (Publisher-owned) — needs a new post-approval trigger (Stage 6 Link 3), a content-mapping design choice.
- Publisher Requirement/Workspace → drafted content: **today this would-be transfer point is where ownership is genuinely contested.** Drafting is currently `cin_lite`-owned (`proposal_writer.py`), not Publisher-owned, and the two have no shared identifier or vocabulary (Stage 6 Link 5, evidenced in detail in `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`). Who owns the object after this transfer is exactly the unresolved question.
- Approved draft → Archive: which archive engine would own it after transfer is unresolved (Stage 6 Link 9) and currently blocked by the closed Archive Separation decision (Section 8).
- Archive → "Manager"/Portal display: no Manager module exists to take ownership. Today, fragments of this are owned separately by `sandbox.py` (cards), `conflict.py` (Conflict Notices), and the Publisher/pipeline/queues views (Stage 6 Link 10) — no single owner.

## 5. Approval Gates Required Before Transfer

| Transfer point | Gate status |
|---|---|
| Into Library (candidate) | Built and working: `review_candidate()`, identity-checked against `RESERVED_SYSTEM_IDENTITIES`, requires `pending_review` status. Unreached in practice. |
| Into Publisher (action APPROVED) | Built and working: `update_action_status(..., approved_by=...)`, same identity check. |
| Into Portal Archive | Built and working: `archive_publisher_action()` requires a valid `approved_by` on the source action. |
| Into cin_lite proposal archive | **No identity-based gate.** HMAC token verification only proves the email link wasn't forged — it does not verify a specific reviewing identity, and there is no intermediate review object to gate (Stage 6 Link 6-7: no Draft Review Package exists). |
| Into/out of Intelligence | **No gate exists at all.** `portal/models/intelligence.py` has no `status` field, per `INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1.md` — unresolved whether Intelligence's "recommendation, not truth" doctrinal role means this is fine as-is or a real gap. |
| Into/out of "Manager" | Not applicable — no object exists to gate. |
| Across the two archive engines | No gate exists because no transfer path exists; blocked upstream by the closed Archive Separation decision. |

## 6. Current Gaps That Block Safe Bridge Design

1. No shared identifier between `cin_lite` (`contract_id`) and Portal (`sandbox_id`/`action_id`).
2. No shared action/status vocabulary (`cin_lite.control.ACTIONS` vs. `publisher.ACTION_TYPES`/`PUBLISHER_STATUSES`).
3. No Draft Review Package object exists anywhere to be transferred — `reconciliation/contracts.py` already declined to fabricate one, citing the No-Fabrication Rule (Dispatch has no `readiness_packet_id`/`inventory_id`/`missing_notice_id` to populate honestly).
4. Intelligence has no approval/status concept at all — the first link in the target object flow has no defined gate to design around.
5. Two incompatible archive engines, with the duplication question already closed at "Maintain Separation" (Option A) — any bridge writing across them would need to reopen a decision that's already settled.
6. No Manager/work-item module exists at all — a bridge "transfer to Manager" step currently has no real destination.
7. `reconciliation/adapters/*.py` cannot supply any needed write path — confirmed structurally read-only by design and docstring (Stage 6 finding); any new write logic belongs elsewhere.

## 7. Dependency On Completeness Reviews

- **Manager Orchestration Review — blocking, most critical.** The Bridge's own target list (Section 1) names "Manager work items/cards" as a system to connect to, but no such system exists in code. The Bridge cannot plan a transfer into a destination that hasn't been defined yet (new module? extension of `sandbox.py`? of `conflict.py`?). This has to be answered first.
- **Intelligence Completeness Review — blocking.** Intelligence currently has zero status/approval concept (Section 5), and `INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1` is unresolved. The Bridge's first potential link (Intelligence → Library) can't be designed without knowing whether Intelligence gets a review gate at all.
- **Publisher Completeness Review — soft blocker.** Determines whether Publisher's "Hybrid" role is meant to eventually gain its own content-generation capability, or stays a pure status tracker forever with drafting permanently external to it — this materially changes what a Publisher/Proposal-Writer bridge even looks like, but isn't a hard prerequisite the way Manager/Intelligence are, since Publisher's current shape is already well-evidenced (Stage 6 Links 3-4, 7-8).
- **Library Completeness Review — not blocking.** Library's write/promotion gate is already the best-understood link in the whole flow (Stage 5 fix + Stage 6 Links 1-2 evidence); a completeness review would refine detail, not remove a blocker.

## 8. Dependency On Other Unresolved Planning-Only Missions

- **`ARCHIVE_DEAD_SECTION_VALIDATION_MISSION_v1`** — no dependency. Scoped to `location_history`/`broker_history`/Route Intelligence, unrelated to the Publisher/Proposal-Writer/Library object-flow questions the Bridge concerns.
- **`SYNC_ENGINE_AUTHORITY_AND_BOUNDARY_REVIEW_v1`** — potential dependency, unconfirmed. If `sync/engine.py::_commit_record()` turns out to bypass the governance gates built in Stage 5 (that mission's still-open question), then any new write path the Bridge eventually adds would inherit the same bypass risk. Should be resolved before Bridge *implementation*, not necessarily before further Bridge *planning*.
- **`INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1`** — direct dependency, already covered in Section 7. Blocking.

## 9. Conclusion

**B) Not ready until department completeness reviews are done.**

Specifically: Manager Orchestration Review and Intelligence Completeness Review (which subsumes
`INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1`) are hard blockers — the Bridge's target systems list
names a destination (Manager) and a source gate (Intelligence approval) that do not exist yet in
any form, not partial ones needing refinement. Publisher Completeness Review is a soft blocker
that shapes the Bridge's design but doesn't block starting to scope it. Library Completeness
Review is not a blocker. This is not a single specific authority question (option C) — it's
multiple missing foundations the Bridge Mission would otherwise have to define for itself,
outside its own stated scope.

No implementation recommended. Integration Bridge Mission not started. No bridge built.

Mike decides.
