# MANAGER_ORCHESTRATION_REVIEW_v1

Program: Dispatch
Status: **Future work package — planning only. Phase 1 (existence check) complete; scoping not
started. Not a scoped implementation task.**
Origin: Named in this session's status-confirmation message alongside `ARCHIVE_DEAD_SECTION_
VALIDATION_MISSION_v1`, `SYNC_ENGINE_AUTHORITY_AND_BOUNDARY_REVIEW_v1`, and `INTELLIGENCE_
APPROVAL_CHAIN_REVIEW_v1`; sharpened into a concrete mission after `DISPATCH_INTEGRATION_
BRIDGE_INVESTIGATION_v1.md` flagged Manager Orchestration Review as a hard blocker for Bridge
planning (Section 7: no Manager destination object exists for the Bridge to transfer into).
Rule: No code changes authorized by this document. No module creation. This is a mission
definition and a record of Phase 1 findings, not the work itself.

---

## 1. What This Mission Is

The canonical matrix (`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md` Section 8)
declared: *"Manager: Not ready for full build. First map tri-department objects into existing
Work Item/Card/Conflict Notice surfaces."* Its target object flow (Section 6) ends with
`Archive Handoff → cin_lite Archive → Portal Card / Work Item / History` — implying Manager, or
something like it, is the eventual consumer/orchestrator sitting over Intelligence, Library,
Publisher, and Archive once their object flow is wired.

This mission exists to determine what Manager should actually be — its ownership boundary, its
data shape, its relationship to existing department-owned surfaces — before any of it is built,
and to formally record the Phase 1 finding that answered the prerequisite question: does any of
it exist today.

## 2. Phase 1 Finding (Complete)

A repo-wide investigation this session found **zero Manager code of any kind** in
`jax1313-outlook/Dispatch`:

- Case-insensitive grep for "manager" across every `.py`/`.html`/`.md` file in the repo returns
  exactly two hits, both non-matches: Python's own `contextlib.contextmanager` (unrelated stdlib
  import, `dispatch/db.py:12,442`) and a plain-English checklist string, `"Confirm bid/no-bid
  sign-off and assign proposal manager"` (`cin_lite/workflows/proposal.py:74`) — a human
  task-list label, not a system.
- No `/manager` route, blueprint, or endpoint exists in any of `portal/routes/{pages,api,
  decisions,dispatch_api,pipeline}.py`.
- No Manager-named template exists in `portal/templates/`.
- `portal/routes/dispatch_api.py` (2,128 lines — the one large file this program had previously
  flagged as not fully read) was scanned in full for its route list: it is entirely freight-load
  CRUD (`/loads`, `/milestones`, `/evidence`, `/exceptions`, `/pod`) — the `dispatch/` "Dispatch
  Data Engine" subsystem, not a cross-department orchestration layer. No routing, tracking, or
  creation logic in it touches Intelligence/Library/Publisher/Archive as a set.

What exists instead, each owned separately, with no shared owner:

| Concept | Real code | Owner |
|---|---|---|
| Cards | `portal/models/sandbox.py` | Sandbox (freight/SAM opportunities) |
| Queues | `portal/models/publisher.py::get_queue()`; `cin_lite.pipeline`'s `/pipeline`/`/queues` views | Publisher; cin_lite pipeline — two separate queue concepts |
| Conflict Notices | `portal/models/conflict.py` (290 lines, `create_notice()`, 13 `CONFLICT_TYPES`, `SEVERITIES`) | Standalone conflict-tracking store, `sandbox_id`-keyed |

"Manager" appears exclusively in planning documents (the canonical matrix, the tri-department
build's own design language) and has never been implemented, in any form, at any size.

## 3. Why This Blocks The Integration Bridge

`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md` Section 7 named this the most critical hard
blocker on Bridge planning: the Bridge's own target-systems list names "Manager work items/cards"
as a connection point, but there is no destination object for a transfer to land in. Scoping the
Bridge further without answering what Manager is would mean the Bridge silently inventing that
answer itself — exactly the kind of unscoped architecture decision this program's doctrine
requires stopping for.

## 4. Scope Questions This Mission Needs To Resolve

1. Does Manager become new storage (a real module/data store), or a **read-composition layer**
   only — analogous to `reconciliation/adapters/*.py`'s confirmed read-only design — that
   presents a unified view over existing department stores (Publisher queue, Library candidates,
   Intelligence records, Conflict Notices, Sandbox cards) without owning any new data itself?
2. What is a "Work Item," concretely? A new canonical object that wraps/references existing
   department records by ID (similar to how the tri-department build's shared contracts
   reference IDs across departments), or a renamed/repurposed version of an existing concept
   (Conflict Notice? Publisher action? Sandbox card)?
3. If Manager does own new state (contradicting option 1 above): does it need the same
   `RESERVED_SYSTEM_IDENTITIES`/approval-gate treatment already built into Library, Publisher,
   and Archive — i.e. does a "Manager decision" require the same non-self-approval discipline?
4. What would trigger Manager to create or update a work item? Does it depend on Stage 6's
   object-flow links existing first (per `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`), since a
   Manager view over disconnected departments has little to unify yet, or is a read-composition
   layer valuable even before those links are wired, since it would surface the disconnection
   itself?
5. Does Manager subsume `portal/models/conflict.py`'s Conflict Notices, or remain a distinct
   layer that Conflict Notices feed into alongside other departments' objects?
6. Does "Card" in the target flow's "Portal Card / Work Item / History" mean `sandbox.py`'s
   existing card concept should be generalized to a Manager-level card (any department object,
   not just freight opportunities), or does Manager introduce its own, third card concept?

## 5. What This Mission Should Produce

A design-level scoping document (not full implementation architecture) answering the questions
above, informed by the canonical matrix's own explicit deferral language — Manager was
deliberately declared "not ready for full build" until receiving objects are canonical, which
per `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md` they mostly still aren't. This mission's honest
output may be "Manager cannot be meaningfully scoped further until Stage 6 links 1, 3, 5, 6, 9
are resolved" — that is itself a valid, useful conclusion, not a mission failure.

## 6. What This Mission Is Not

Not authorization to build Manager, in any form — read-composition layer or otherwise. Not a
redesign of Conflict Notices, Sandbox cards, or Publisher/cin_lite queues, which stay as they are
regardless of this mission's outcome. Not a re-run of the Integration Bridge Investigation's other
findings (Intelligence/Publisher/Library completeness) — scoped specifically to what Manager is
and whether/how it can exist, given it currently does not.

Mike decides.
