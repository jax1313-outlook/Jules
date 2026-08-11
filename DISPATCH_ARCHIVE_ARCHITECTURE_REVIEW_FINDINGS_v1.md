# DISPATCH_ARCHIVE_ARCHITECTURE_REVIEW_FINDINGS_v1

Program: Dispatch
Status: Investigation findings — **no code changes, no branch created, no implementation plan
authorized by this document.** This is the first phase of
`DISPATCH_ARCHIVE_ARCHITECTURE_REVIEW_MISSION_v1.md` ("a scoping/investigation pass... followed
by an explicit, Mike-approved implementation plan, before any code is touched").
Method: Real code read on `main` (not the Approval Chain Safety Gate branch — this investigation
describes the current mainline state), every call site traced with grep, no assumptions carried
over from the earlier reconciliation pass without re-verification.
Date: 2026-08-11

---

## Headline: The Original Framing Understated The Problem

`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md`'s Hard Conflict List item 4 says:
"Duplicate Archive engines inside Dispatch... `cin_lite/archive.py` becomes canonical.
`portal/models/archive.py` must become adapter/view or be retired." That framing assumed **two**
archive implementations. Real investigation of `main` found **four** distinct "completed/
archived" data sources, already rendered together — separately, honestly labeled, not
silently merged — on one Portal page (`GET /archive`, `portal/routes/pages.py::archive_view()`):

| # | Source | Storage technology | Domain | Section label on the page |
|---|---|---|---|---|
| 1 | `portal/models/archive.py` | Flat JSON file (`archive.json`) | Portal decisions, Publisher actions, location/broker history | 5 sections looped from `SECTION_LABELS` (e.g. "Load Archive," "Publisher Archive") |
| 2 | `cin_lite/archive.py` | Hash-verified file tree (`Raw/Processed/Intelligence/.../Proposals`) | Government-contract pursuit pipeline (SAM.gov contracts, proposals) | "DISPATCH Pipeline Archive" |
| 3 | `dispatch/store.py`'s `retention` SQL table | SQLite (via `dispatch/db.py`) | Freight-load operational retention (POD packages, evidence, financial/settlement summary) | "Dispatch Retention Archive" |
| 4 | `portal/models/sandbox.py`, filtered by status | Flat JSON file (`sandbox.json`) — **not actually archived, still live data** | Sandbox cards in a terminal status (PASS/CLOSED/EXPIRED/BOOKED) | "Sandbox — Archive Candidates" |

Source #3 was not identified in the earlier reconciliation pass at all. Source #4 is not really
a fourth *archive* — it's live data presented as "candidates" for archival, which is an honest
and arguably correct design choice, but changes what "resolving the duplication" even means.

## Why This Matters For The Mission's Original Plan

The original recommendation — "retire `portal/models/archive.py`, make `cin_lite/archive.py`
canonical" — does not actually work as stated once the real domains are visible:

- `portal/models/archive.py`'s 5 sections (`load`, `decision`, `publisher`, `location_history`,
  `broker_history`) have no natural home in `cin_lite/archive.py`'s structure, which is
  contract-pursuit-shaped (`Raw/Processed/Intelligence/Summaries/Routing/Pending/Outbox/
  Proposals`) — forcing them in would mean inventing new, unrelated subdirectory types inside a
  system whose whole design is contract-file-tree-shaped.
- `dispatch/store.py`'s retention table is a third, completely separate technology (relational,
  not file-based) for a fourth, completely separate domain (freight load compliance/evidence/
  financial retention — POD packages, settlements). Nothing about "make `cin_lite/archive.py`
  canonical" addresses this at all; it wasn't even in scope of the original comparison.
- These aren't really duplicates of *the same data* — they're separate departments' completed-
  work stores that happen to share the word "archive." The overlap that actually matters isn't
  "four systems store similar things," it's narrower: **is Publisher's specific approval-gated
  handoff (the thing the Approval Chain Safety Gate branch just fixed) consistently enforced no
  matter which of these four a Publisher-adjacent action ends up in?** Today the answer is: the
  gate was added to `portal/models/archive.py::archive_publisher_action()` only, because that is
  the only one of the four that Publisher actions actually flow into.

## Real Answers To The Five Original Scope Questions

1. **Does `portal/models/archive.py` get retired entirely, or become a thin adapter?** Neither,
   cleanly — see above. It stores Portal-native domains (Publisher/decision/location/broker
   history) that `cin_lite/archive.py` has no structural place for. Retiring it outright would
   require redesigning `cin_lite/archive.py`'s section model first, which is a much bigger
   change than "resolve a duplicate."
2. **Does data move into `cin_lite/archive.py`'s structure, or does it need new sections?** If
   any consolidation happens, `cin_lite/archive.py` would need new, generically-named section
   types (not `Raw`/`Processed`/`Intelligence`, which are contract-pipeline-specific) — this is a
   schema-extension decision on the "canonical" system, not a one-way migration into it as-is.
3. **What happens to existing data in `portal/models/archive.py`'s JSON file?** Real question,
   still unanswered — no migration tooling exists for any of these four stores today, and no
   sample-data volume was checked as part of this pass (would need to check actual deployed
   `archive.json` size, if any exists in a running instance, which this investigation had no
   access to).
4. **What callers need to change?** Traced exhaustively via grep, not assumed:
   - `portal/models/archive.py` callers: `portal/app.py` (dashboard count), `portal/routes/
     pages.py` (`archive_view()`, `total_count()` for a summary stat), `portal/routes/api.py`
     (`archive_from_sandbox()` × 2 call sites — on `PASS` action and one other; `archive_
     publisher_action()` × 1, the one the safety gate fixed).
   - `cin_lite/archive.py` callers: `cin_lite/email_delivery.py`, `cin_lite/pending.py`,
     `cin_lite/workflows/proposal.py`, `cin_lite/pipeline.py` (the core contract pipeline, `make_
     id`/`store`/`record_routing`), plus `portal/routes/pages.py` and `portal/routes/pipeline.py`
     for display and `load_artifact()` lookups.
   - `dispatch/store.py`'s retention table: triggered by exactly one function,
     `dispatch/services.py::archive_load()`, itself called from somewhere in `portal/routes/
     dispatch_api.py` (an 81KB file not read in detail this pass — flagged, not assumed empty).
   - The `/archive` page (`portal/routes/pages.py::archive_view()`) is the only place all four
     converge, and it already treats them as four separate, clearly labeled sections — this
     matters because it means **the presentation layer is not the problem**; any consolidation
     work is purely a storage/data-layer question.
5. **Does `cin_lite/archive.py`'s hash-verification extend naturally to the other sections'
   data?** Not evaluated in depth this pass because it's downstream of question 1-2 (there is no
   settled "target shape" yet to test hash-verification against). Worth noting: `dispatch/
   store.py`'s retention table already has its own integrity mechanism by virtue of being a real
   SQL table with typed columns (not file-based, so file-tampering is a different threat model
   entirely) — "does X extend to Y" may not even be the right question once source #3 is
   accounted for.

## Test Coverage Already In Place (Relevant To Any Future Implementation)

`tests/test_portal.py` already has real coverage of the combined `/archive` page:
`test_archive_renders`, `test_archive_shows_pipeline_contracts`, `test_archive_page_renders_
clean_error_on_integrity_mismatch`, `test_archive_five_sections`, `test_archive_table_shows_
columns`, `test_library_and_archive_are_separate`, plus `test_archive_from_sandbox_dispatch`/
`_sam` and the Stage-5-added `test_archive_publisher_action_requires_approval`. Any future
implementation work has a real regression baseline to work against — this is good news for risk,
not a blocker.

## Recommended Framing Correction (Not A Plan — A Reframed Question)

This mission's Section 3 question 1 ("retire or adapt `portal/models/archive.py`?") should be
replaced with three narrower, more answerable questions, because the four-source reality doesn't
support a single "which engine wins" decision:

1. **Should freight-load retention (`dispatch/store.py`) stay entirely separate?** Its domain
   (POD/evidence/financial compliance) has no relationship to contract-pursuit or Portal-decision
   archival — likely yes, no action needed there.
2. **Should Portal-decision archival (`portal/models/archive.py`) be consolidated into
   `cin_lite/archive.py`, or is "two file-based archives for two genuinely different domains"
   an acceptable permanent state, with the Approval Chain Safety Gate's precondition being the
   actual fix that mattered?** This is the real decision point, and it's a smaller one than the
   original framing implied.
3. **Is the `/archive` page's four-section presentation actually the right long-term Portal UX**,
   or should Mike want a single unified Archive view eventually — a Portal-layer question,
   separable from whatever happens at the storage layer?

## What This Document Does Not Do

No implementation plan, no branch, no code change. Per the mission document's own sequencing,
the next step is Mike's decision on the three reframed questions above — only after that does
"produce an explicit, Mike-approved implementation plan" become meaningful, because right now
there is no single settled direction to plan around.

Mike decides.
