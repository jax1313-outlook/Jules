# SYNC_ENGINE_AUTHORITY_AND_BOUNDARY_REVIEW_v1

Program: Dispatch
Status: **Future work package — planning only. Not a scoped implementation task.**
Origin: `ARCHIVE_AUTHORITY_AND_OWNERSHIP_REPORT_v1.md` Phase 1 flagged `sync/engine.py` as an
8th archive-adjacent component "flagged, not fully investigated" — this mission exists to
actually investigate it. Named/registered at Mike's direction.
Rule: No code changes authorized by this document. No investigation of live transport
credentials/config beyond what's in version control. This is a mission definition, not the work
itself.

---

## 1. What This Mission Is

The Archive Authority Review found `sync/engine.py`'s `SyncEngine` class: a "pull-only
synchronization" mechanism (its own docstring) whose `SYNC_SUBDIRS` list —
`loads, brokers, customers, library, archive, publisher, locations, intelligence/location,
intelligence/broker, intelligence/customer, intelligence/route, intelligence/position,
intelligence/market` — mirrors the domain taxonomy of Library/Archive/Intelligence almost
exactly. It has real staging/commit/conflict machinery (`_sync_data_type`, `_validate_record`,
`_commit_record`, `_save_conflict`) but was not traced end-to-end: what actually calls
`_commit_record()`, what does it write, and does that write path go through the same
functions (`library.add_record()`, etc.) the Approval Chain Safety Gate just gated — or does it
write directly to the underlying JSON/file stores, bypassing every governance gate this program
has built so far?

**That last question is the one that matters most and is currently unanswered.** If
`_commit_record()` writes straight to `library.json`/`archive.json` rather than calling through
`portal.models.library.add_record()`, then an externally-synced file could become Library truth
(or Archive history) with no `submitted_by` distinction, no approval gate, and no trace of the
Approval Chain Safety Gate fix ever running on it at all — a bypass of the exact protection just
built, through a door nobody has checked yet.

## 2. Why This Wasn't Investigated As Part Of The Archive Review

The Archive Authority Review was scoped to archive-labeled components specifically; `sync/
engine.py` was noticed only because its subdirectory list happened to overlap. A real
investigation of a cross-cutting transport mechanism — what triggers it, what it's actually wired
to in a live deployment, whether `sync_config.example.json` reflects real production config or is
just a template — is a different kind of work than tracing archive call sites, and deserves its
own pass rather than a rushed add-on.

## 3. Scope Questions This Mission Needs To Resolve

1. Does `_commit_record()` call through `portal.models.{library,archive,intelligence,
   publisher}.py`'s own functions, or does it write to the underlying JSON files directly? (This
   is the load-bearing question — everything else is secondary to it.)
2. Is `SyncEngine` actually wired to a live, configured transport in any real deployment, or is
   it dormant/example-only? (`sync/config.py`, `sync/transport.py`, `sync_config.example.json`
   need a real read, not assumed from the filename.)
3. What triggers a sync run — a cron job, a manual CLI invocation (`cin-sync`, per `pyproject.
   toml`'s script entry), something else?
4. If source #1 above shows a direct-write bypass: does the same approval-gate logic need to
   extend to the sync commit path, mirroring how it was added to `portal/models/{library,
   publisher,archive}.py`?
5. What does `_save_conflict()` actually do when a synced record conflicts with local data — is
   there a human review step, or does one side silently win?

## 4. What This Mission Should Produce

A real trace of the sync commit path (mirroring how the Publisher/Archive call chain was traced
before the Approval Chain Safety Gate fix was written), a determination of whether question 1
reveals a live bypass of the existing governance gates, and — only if a bypass is confirmed — a
recommendation for whether this becomes an urgent follow-on to the Approval Chain Safety Gate
work specifically, given what that fix was built to prevent.

## 5. What This Mission Is Not

Not a general sync/transport feature review — scoped specifically to the authority/boundary
question (does sync bypass governance gates), not to sync's reliability, performance, or
configuration UX.

Mike decides.
