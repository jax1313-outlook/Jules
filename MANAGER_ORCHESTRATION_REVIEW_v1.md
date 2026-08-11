# MANAGER_ORCHESTRATION_REVIEW_v1

Program: Dispatch
Status: **CLOSED — decision made.** Mike issued the Manager Preservation Decision: Manager
remains on the roster, designated DORMANT / RESERVED CAPABILITY / NOT IMPLEMENTED. Not built,
not deleted, not refactored. Recorded permanently in `jax1313-outlook/Dispatch` at
`docs/MANAGER.md` (`dispatch/canonical-reconciliation-integration`, commit `f92cc9f`) —
documentation only, no code/route/data model, no runtime participation, no data ownership.
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

---

## 7. Phase 2: Scope Questions — Findings

Started on explicit go-ahead ("start Manager orchestration review"). Investigation-only — no
code changes. Fresh evidence this pass: full read of `portal/models/conflict.py` (all 290
lines, previously only partially read) and `portal/models/sandbox.py`'s card structure, plus
synthesis of `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`,
`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md`, and `PUBLISHER_COMPLETENESS_REVIEW_v1.md`.

**Q1 — New storage or read-composition layer?** Evidence favors read-composition as the lower-
risk starting hypothesis, not yet a decision. Building new storage means Manager becomes a new
source of truth — exactly what the canonical matrix's Section 8 declared "not ready" for. A
read-composition layer, following the precedent already set by `reconciliation/adapters/*.py`
(deliberately read-only, no `_save()`/`_load()` anywhere), would let Manager exist without
inventing any new authoritative state or IDs — consistent with the No-Fabrication Rule already
invoked twice this program (once refusing to fabricate a `DraftReviewPackage`, once refusing to
fabricate Archive IDs). This is a recommendation for Mike's evaluation, not a resolution.

**Q2 — What is a "Work Item," concretely?** Today, a Work Item could only meaningfully wrap
objects that actually exist and are reachable: Publisher actions (real, working, per Stage 6
Link 4/8), Conflict Notices (real, working — see Q5), Sandbox cards (real, freight-specific).
Library candidates are real but unreached (zero live producers, per Stage 6 Link 1) and
Intelligence has no distinct sub-object types at all (per the in-progress Intelligence
Completeness Review's framing) — so a Work Item wrapping those two would have nothing to
reference yet. A Work Item is thus better scoped today as "a reference wrapper around Publisher/
Conflict/Sandbox records that exist," not a general cross-department object — the general case
waits on Stage 6.

**Q3 — Approval gate need?** Conditional on Q1. If Manager stays read-composition-only, there is
nothing to approve — a view has no state to gate. If Manager later gains any mutating action of
its own (e.g. a "route" or "resolve" function), it should get the same
`RESERVED_SYSTEM_IDENTITIES` treatment already applied consistently to Library, Publisher, and
Archive, for the same reason. Not yet applicable under the current, no-code state.

**Q4 — Trigger / dependency on Stage 6?** Directly answerable from
`DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`: Links 4, 8, and 10 already work; Link 2 is built but
unreached; Links 1, 3, 5, 6, 9 need a design decision or new trigger first. A read-composition
Manager view has real data to unify **today**, before Stage 6 completes, from exactly the parts
that already work: Publisher's queue, Conflict Notices, Sandbox cards, and Portal's existing
direct reads of `cin_lite` (Stage 6 Link 10). Notably, Stage 6 Link 10 already concluded that
unifying Portal's three fragmented archive/queue/card views is "a presentation-layer
consolidation, not a new data-flow" — which is functionally the same task as Q1's read-
composition hypothesis. **These may be the same piece of work, not two separate ones.** Library
and Intelligence data would have nothing to contribute to such a view until their respective
Stage 6 links are resolved.

**Q5 — Subsume or stay distinct from Conflict Notices?** New evidence changes this answer.
`portal/models/conflict.py` already has partial, unrealized cross-department ambition:
`CONFLICT_TYPES` includes `"publisher_missing_document"` and `"library_missing_asset"`
(`conflict.py:25-27`) alongside the freight-domain types. A real generator,
`check_library_assets()` (`conflict.py:275-289`), produces `library_missing_asset` notices
against a hardcoded required-assets list — but a repo-wide grep found **it is never called from
any route or service, only from a test** (`tests/test_portal.py:1003`). `"publisher_missing_document"`
has zero producers anywhere, including tests. So Conflict Notices already tried to be
cross-department-aware and that attempt was left half-wired. Given it has its own working
create/resolve lifecycle and UI already, the better-evidenced answer is **Manager composes over
Conflict Notices as one of several real sources, rather than subsuming it** — subsuming would
mean rebuilding a working system; composing reuses it as-is, consistent with Q1's hypothesis.

**Q6 — Generalize Sandbox's card, or a third concept?** `sandbox.py`'s `card_data` (confirmed via
fresh read) is tightly coupled to freight-lifecycle fields (`deadhead_miles`, `fuel_estimate`,
`engine_load_id`, SAM/Dispatch source distinction) — it does not generalize cleanly to a Library
candidate or Publisher action. Combined with Stage 6 Link 10's finding that Portal already
fragments "card" across three unrelated views, a third, generic Manager-level card concept (that
composes over Sandbox/Publisher/Conflict rather than replacing or extending Sandbox's own card)
is the better-evidenced answer, not a retrofit of `sandbox.py`.

**Net conclusion:** Manager is not yet fully blocked on Stage 6 the way earlier framing assumed.
A narrowly-scoped, read-composition-only Manager view over what already works today (Publisher
queue + Conflict Notices + Sandbox cards + Portal's existing `cin_lite` reads) is evidenced as
buildable now, without waiting on Library/Intelligence's unresolved links — but this document
does not authorize building it. Whether to scope that narrower version as its own follow-on
mission, or continue waiting for full Stage 6 resolution, is Mike's call.

Mike decides.
