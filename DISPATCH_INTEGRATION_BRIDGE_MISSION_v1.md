# DISPATCH_INTEGRATION_BRIDGE_MISSION_v1

Program: Dispatch
Status: **Future work package — planning only. Not a scoped implementation task.**
Origin: Spun out of `dispatch/canonical-reconciliation-integration` (Approval Chain Safety Gate
branch) at Mike's direction, as Stage 5 item 5 of
`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md`, deliberately excluded from that
branch's finalized scope.
Rule: No code changes authorized by this document. This is a mission definition to scope a
future piece of work, not the work itself.

---

## 1. What This Mission Is

`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md` Section 3 declared Publisher a
"Hybrid" canonical winner: tri-department governs (readiness/review/approval), Dispatch's
`cin_lite/agents/proposal_writer.py` drafts content. Hard Conflict List item 5 names the gap:
"Proposal writer exists outside Publisher governance... should become a Publisher content
worker, not an independent bypass path."

This mission exists to actually relate these two subsystems, which today do not know about each
other at all.

## 2. Why This Was Not Done As Part Of The Approval Chain Safety Gate Branch

Items 1-3 of Stage 5 each added a missing check to one existing function. Item 5 is not that
kind of change — it requires relating two subsystems that currently run on entirely separate
tracks:

- **`cin_lite`'s email-decision flow**: a contract is acquired → processed → routed by
  `agents/router.py` → a human clicks an action link in an email
  (`portal/routes/decisions.py`, HMAC-token verified) → `workflows/proposal.py::trigger()` fires
  → `agents/proposal_writer.py::draft_outline()` drafts content → archived via
  `cin_lite/archive.py::store_proposal()`.
- **`portal`'s action-queue flow**: a Publisher action is created via `portal/models/
  publisher.py::create_action()` → moves through `PENDING → DRAFT → READY → APPROVED →
  ARCHIVED` (now gated by the Approval Chain Safety Gate fix) → archived via `portal/models/
  archive.py::archive_publisher_action()`.

These are two different trigger mechanisms (email link vs. Portal API), two different action
vocabularies (`cin_lite.control.ACTIONS` vs. `PUBLISHER_STATUSES`/`ACTION_TYPES`), two different
archive destinations, and two different approval mechanisms. "Relate them" could mean several
genuinely different things, and picking one is a design decision, not a patch.

## 3. Scope Questions This Mission Needs To Resolve (Not Yet Answered)

1. Does the Portal action-queue flow gain the ability to invoke `proposal_writer.draft_outline()`
   directly (making it a callable content-generation step inside `update_action_status()`'s
   `DRAFT` transition, for example), or does the `cin_lite` email flow gain the Portal's
   approval-gate discipline (routing its "approve_proposal" trigger through something equivalent
   to `approved_by` validation)? Or both, converging on one flow?
2. Should Publisher action types (`ACTION_TYPES` in `portal/models/publisher.py`) and `cin_lite`
   control actions (`cin_lite/control.py::ACTIONS`) become one shared vocabulary, or stay
   separate with an explicit mapping between them?
3. Where does a proposal drafted by `proposal_writer.py` end up archived — `cin_lite/
   archive.py::store_proposal()` (its current destination) or does it also need to appear in
   `portal/models/archive.py`'s `publisher` section for Portal visibility? (This question
   depends on the outcome of the separate Archive Architecture Review mission — these two
   future missions are not fully independent.)
4. Does this mission depend on Stage 6 (object-flow wiring, from the original canonical matrix)
   being scoped first, since "relate the proposal writer to Publisher governance" is a specific
   case of the more general "wire the object flow" question?

## 4. What This Mission Should Produce

A real investigation of both flows end-to-end (tracing every call site, the way the Publisher/
Archive approval gaps were traced before being fixed) followed by a design decision Mike
approves explicitly, before any code changes. Given this mission's dependency on the Archive
Architecture Review mission's outcome (question 3 above), it may make sense to sequence Archive
Architecture Review first.

## 5. What This Mission Is Not

Not an excuse to also touch the Library/Publisher/Archive approval gates already finalized and
closed in the Approval Chain Safety Gate branch, and not the same mission as Archive
Architecture Review, even though the two overlap at question 3 above.

Mike decides.
