# DISPATCH_ARCHIVE_ARCHITECTURE_REVIEW_MISSION_v1

Program: Dispatch
Status: **Future work package — planning only. Not a scoped implementation task.**
Origin: Spun out of `dispatch/canonical-reconciliation-integration` (Approval Chain Safety Gate
branch) at Mike's direction, as Stage 5 item 4 of
`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md`, deliberately excluded from that
branch's finalized scope.
Rule: No code changes authorized by this document. This is a mission definition to scope a
future piece of work, not the work itself.

---

## 1. What This Mission Is

`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md` Section 3 declared
`cin_lite/archive.py` the canonical Archive engine (SHA-256 hash-verified, fail-closed on
tampering, 26 dedicated tests) and flagged `portal/models/archive.py` (the duplicate, unverified
implementation) for retirement or downgrade to an adapter/view. That is Hard Conflict List item
4: "Duplicate Archive engines inside Dispatch."

This mission exists to actually resolve that duplication — decide what `portal/models/
archive.py` becomes, and execute the change safely.

## 2. Why This Was Not Done As Part Of The Approval Chain Safety Gate Branch

The Approval Chain Safety Gate branch (Stage 5 items 1-3) added an approval-status precondition
to one function, `archive_publisher_action()`, touching only the `publisher` section of
`portal/models/archive.py`. Item 4 is categorically different in size and risk:

- `portal/models/archive.py` has **five** sections (`load`, `decision`, `publisher`,
  `location_history`, `broker_history`), and item 4 would change behavior for all of them, not
  just the one the safety-gate fix touched.
- It has real existing callers beyond the Publisher path: `archive_from_sandbox()` is called
  from `sandbox.py`/`portal/routes/*.py` for `load` and `decision` records, unrelated to
  Publisher approval at all.
- `cin_lite/archive.py` uses an entirely different storage shape (`contract_id`-keyed file tree
  with hash sidecars) from `portal/models/archive.py` (flat JSON records) — reconciling them is
  not a drop-in swap, it's a data model migration.
- Downgrading `portal/models/archive.py` to "adapter/view only" (the matrix's suggested
  direction) requires deciding what it adapts *to* — does it read from `cin_lite/archive.py`
  directly? Through a translation layer? Does existing archived data in `portal/models/
  archive.py`'s JSON store need to be migrated into `cin_lite/archive.py`'s file tree, or left
  as legacy history?

None of these questions have answers yet. Answering them is this mission's job.

## 3. Scope Questions This Mission Needs To Resolve (Not Yet Answered)

1. Does `portal/models/archive.py` get retired entirely, or does it become a thin adapter that
   reads/writes through `cin_lite/archive.py`?
2. If it becomes an adapter: does `load`/`decision`/`location_history`/`broker_history` data
   move into `cin_lite/archive.py`'s section/subdirectory structure, or does
   `cin_lite/archive.py` need new sections to accommodate them (today it only has
   `Raw/Processed/Intelligence/Summaries/Routing/Pending/Outbox/Proposals`)?
3. What happens to existing data already stored in `portal/models/archive.py`'s JSON file
   (`archive.json`)? Migrate, leave as read-only legacy, or something else?
4. Do `sandbox.py`'s `archive_from_sandbox()` call site and any Portal routes/templates that
   read from `portal/models/archive.py::get_all()`/`get_section()` need to change, and if so,
   how many of them are there (this needs its own real grep/investigation, not an assumption)?
5. Does `cin_lite/archive.py`'s hash-verification/fail-closed behavior extend naturally to the
   sections currently unique to `portal/models/archive.py`, or does something about those
   sections' data shape make that harder than it looks?

## 4. What This Mission Should Produce

A scoping/investigation pass (mirroring how `DISPATCH_DEPARTMENT_RECONCILIATION_v1.md` was
produced — real code read, real call sites found, real answers to the questions above) followed
by an explicit, Mike-approved implementation plan, before any code is touched. Given the "safety
gate first, refactor separately" precedent just set, this mission should very likely also
produce its own dedicated branch, separate from `dispatch/canonical-reconciliation-integration`.

## 5. What This Mission Is Not

Not an excuse to also touch Library/Publisher approval logic (already finalized and closed in
the Approval Chain Safety Gate branch) or to start Stage 6 object-flow wiring. Archive
architecture only.

Mike decides.
