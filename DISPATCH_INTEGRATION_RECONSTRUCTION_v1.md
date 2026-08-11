# DISPATCH_INTEGRATION_RECONSTRUCTION_v1.md

Program: Dispatch
Status: Verification Report — corrects a false premise, then answers the six questions honestly
Date: 2026-08-11

Do not deploy. Do not promote. Do not merge into Dispatch. Mike decides.

---

## 0. Premise Correction

The request this document answers assumes "before the tri-department build, you performed a
complete repository audit of Dispatch and identified what already existed." **That did not
happen.** Verified against this session's own record:

- `jax1313-outlook/Dispatch` was cloned for the first time at 17:33 today, during the *previous*
  turn's history-relatedness check (`DISPATCH_MAIN_SYNC_SAFETY_REPORT_v1.md`) — and even then, only
  to run `git merge-base`/root-commit comparisons, not to read its application code.
- The tri-department build (Intelligence, Library, Publisher) was designed entirely from doctrine
  documents in Claude-3 (Constitution, System Relationship Matrix, Agent Relationship Matrix, Build
  Command, Repo Placement Plan) and the three department repos themselves. Dispatch's actual code
  was never opened.

This document does not "reconstruct an implicit pathway that was already used," because no such
pathway exists — the build made zero code-verified assumptions about Dispatch. What follows
instead is: (1) an honest accounting of the doctrine-level references that *were* made, with no
code behind them, and (2) a real, fresh inspection of Dispatch — now that it's actually cloned —
to answer where these objects would land *if* imported today. Part (2) is the useful part.

---

## 1. What Existing Dispatch Components Were Assumed?

**None, in the code sense.** The build referenced four doctrine-level names — Manager, Portal,
Archive, Security — because `04_DISPATCH_SYSTEM_RELATIONSHIP_MATRIX.md` and
`DISPATCH_CONSTITUTION_v3.md` define them as organizational functions. Every mention of them in
`DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` is a consumer/owner label in a table cell (e.g. "Consumer:
Manager, Publisher"), never a file path, import statement, class name, or API route. No
`from dispatch.manager import ...`-style assumption was ever written, because no such inspection
occurred.

## 2. What Existing Dispatch Components Consume Department Outputs?

Now that Dispatch is actually cloned, here is what's real (none of this informed the build; this
is being reported for the first time):

| Dispatch file | What it actually is |
|---|---|
| `portal/models/intelligence.py` | A flat JSON-record store for six intel types (`location`, `broker`, `customer`, `route`, `position`, `market`), IDs like `INT-LOC-0001` |
| `portal/models/library.py` | A flat JSON-record store across six sections (`company`, `broker`, `customer`, `location_intelligence`, `operations`, `intelligence`); every record is stamped `status: "approved"` the moment it's created — no pending/review state at all |
| `portal/models/publisher.py` | A JSON action queue (`PUB-0001`...) over eight fixed action types (Broker Packet Required, Rate Confirmation Package Required, etc.), status flow `PENDING → DRAFT → READY → APPROVED → ARCHIVED`, with a `human_approval_required: True` field baked into every action |
| `portal/models/archive.py` | A JSON record store across five sections (`load`, `decision`, `publisher`, `location_history`, `broker_history`), with `archive_from_sandbox()` and `archive_publisher_action()` — i.e. it already *receives* Publisher actions today |
| `portal/models/sandbox.py` | The real work-item/decision hub — not named "Manager" anywhere, but functionally the closest thing to it: an `OPEN → ... → BOOKED/EXPIRED/CLOSED` state machine per card, holding `intelligence`, `decision`, `publisher_actions`, `flags`, `events` |
| `portal/models/conflict.py` | The real Conflict Notice implementation — `CONFLICT_TYPES` includes `publisher_missing_document` and `library_missing_asset`, and `check_library_assets()` already generates conflict notices for missing Company Library assets |
| `portal/routes/api.py`, `portal/routes/pages.py` | Both import all five models above (`from portal.models import sandbox, publisher, conflict`, `library as lib_model`, `archive as arc_model`, `intelligence as intel_model`) and are the actual Flask wiring |
| `portal/templates/{intelligence,library,publisher,archive}.html` | Real rendered pages for each |

There is no `manager.py` or `spine.py` anywhere in the repo (confirmed by search) — "Manager" and
"Spine" exist only as doctrine concepts; `sandbox.py`/`conflict.py` are Dispatch's actual, differently-named
implementations of adjacent ideas.

## 3. What Objects Already Map Into Dispatch?

**None of the tri-department build's actual dataclasses map in without translation.** Every
object has a real, live counterpart in Dispatch with a different shape:

| Tri-department object (this build) | Dispatch's actual equivalent | Mismatch |
|---|---|---|
| `IntelligenceFinding` (verification_status, confidence, routing_queue, risk_flags, `is_final_decision`/`library_truth` fixed False) | `portal/models/intelligence.py` record (`intel_type`, `subject`, `content`, `source`, `metadata`) | No verification/confidence/routing concept at all in Dispatch's version; no truth/decision guard fields |
| `LibraryObject` / `LibraryCandidate` (15-collection taxonomy, `CURRENT`/`SUPERSEDED`/`PENDING_REVIEW`, external-approval gate) | `portal/models/library.py` record (6-section taxonomy: company/broker/customer/location_intelligence/operations/intelligence) | **Different taxonomy entirely** — 15 vs. 6 sections, no name overlap except "customer"/"broker"/"intelligence"-ish. `add_record()` hardcodes `status: "approved"` — Dispatch's real Library has **no pending-review gate at all**, which is a materially different (and, against this program's own Constitution, weaker) posture than the one this build implemented |
| `DraftReviewPackage` / `ArchiveHandoffPackage` (external-approver gate, blocked handoff) | `portal/models/publisher.py` action (`PENDING→DRAFT→READY→APPROVED→ARCHIVED`, `human_approval_required: True`) | Conceptually closer than Library, but structurally different — no `approver_id` argument anywhere in Dispatch's version; `human_approval_required` is a static flag, not an enforced code gate the way this build's `approve_review_package()` is |
| `PartsInventory` / `MissingItemNotice` | `portal/models/conflict.py::check_library_assets()` | Dispatch already generates a real "library_missing_asset" conflict notice for 6 hardcoded company assets — a live, working, much simpler analog of this build's `PartsInventory`/`MissingItemNotice` |
| `ArchiveHandoffPackage` / `POD/Evidence Bundle` | `portal/models/archive.py::archive_publisher_action()` | Dispatch already has a real, working Publisher→Archive handoff — just with no approval-status check comparable to this build's "blocked unless `APPROVED_BY_MIKE`" gate |
| Manager Decision Support Note | `portal/models/sandbox.py` entry (`decision`, `flags`, `events`) | Sandbox already carries a `decision` field and an event log; no dedicated "note" object |

**No object is contract-clean between this build and Dispatch.** Every one of the tri-department
build's field names, status vocabularies, and taxonomies would need explicit reconciliation before
any of this build's code could write into Dispatch's existing storage.

## 4. Which Files Already Represent Integration Points?

Concretely, these are the files a real Dispatch-side import would have to reconcile against, not
merely "land near":

- `portal/models/intelligence.py`, `portal/models/library.py`, `portal/models/publisher.py`,
  `portal/models/archive.py`, `portal/models/sandbox.py`, `portal/models/conflict.py`
- `portal/models/__init__.py` (defines the storage roots — see Section 5)
- `portal/routes/api.py`, `portal/routes/pages.py` (the only two files that import all of the above)
- `portal/templates/intelligence.html`, `library.html`, `publisher.html`, `archive.html`

## 5. Imports, Adapters, Services, Routes, Cards, Work Items, Storage, Archive Paths — What Was Assumed?

**Assumed by the build: none of the above, at all.** No import statement in any of the three
department repos references `dispatch`, `portal`, `sandbox`, or any Dispatch path. This build's
`LibraryClient`/`intelligence_client.py` "integration boundary" Protocols in the Publisher repo are
generic duck-typed interfaces invented to describe *this build's own* cross-repo contract — they
were not shaped around Dispatch's actual `portal/models/*.py` functions in any way, because those
functions were never read.

What actually exists in Dispatch, discovered just now:

- **Storage**: `portal/models/__init__.py::get_data_dir()` / `get_memory_dir()` / `get_archive_dir()`
  — all resolve to the same local JSON directory by default (`<repo>/portal/data/`), overridable via
  `PORTAL_DATA_DIR`, `DISPATCH_OPERATIONS_ROOT`, `DISPATCH_MEMORY_ROOT`, `DISPATCH_ARCHIVE_ROOT`
  env vars. This is flat-file JSON storage, not a database, not the in-memory Python object stores
  (`IntelligenceStore`, `ObjectRegistry`, `CandidateQueue`) this build used.
- **Work items / cards**: `portal/models/sandbox.py` — the real card/work-item lifecycle, keyed
  `SBX-{SOURCE_TYPE}-{source_id}`.
- **Routes**: `portal/routes/api.py`, `portal/routes/pages.py` — Flask routes, not Python service
  calls like this build's `intell.create_finding()`/`library.current()`/`publisher.create_request()`.
- **Archive paths**: `archive_from_sandbox()`, `archive_publisher_action()` — both real, both
  already wired to `sandbox.py` and `publisher.py` respectively.

None of this was assumed or referenced by the tri-department build's contracts, service layers, or
tests, because none of it was known to exist until this turn.

## 6. If The Departments Were Imported Today, Where Would Each Object Land?

Honest answer, not a design proposal (no redesign is being proposed here — this is only reporting
where the nearest existing file is):

| This build's object | Nearest existing Dispatch file | What would have to change first |
|---|---|---|
| `IntelligenceFinding` | `portal/models/intelligence.py` | Dispatch's record has no verification/confidence/routing fields; would need new fields added or a translation layer, not a drop-in |
| `LibraryCandidate` → `LibraryObject` | `portal/models/library.py` | Dispatch's Library has no pending-review state and a 6-section taxonomy vs. this build's 15-collection one — the two "Library" concepts currently enforce different doctrine (Dispatch auto-approves on creation; this build requires external review) |
| `PublisherRequest` / `DraftReviewPackage` | `portal/models/publisher.py` | Action-type vocabulary is fixed and different (8 named actions vs. this build's 5 recipe types); `approve_review_package()`'s enforced external-approver check has no equivalent — Dispatch's `human_approval_required` is a flag, not a gate |
| `PartsInventory` / `MissingItemNotice` | `portal/models/conflict.py` | Dispatch's version is hardcoded to 6 company assets; this build's version is per-request and recipe-driven |
| `ArchiveHandoffPackage` | `portal/models/archive.py::archive_publisher_action()` | Already receives Publisher actions with no approval-status precondition — this build's stricter "blocked unless APPROVED_BY_MIKE" gate does not exist there today |
| `VisibilityPackage` / `PODEvidenceBundle` | No existing file found | Neither `portal/models/` nor `cin_lite/` has a visibility/POD-specific module; closest is `cin_lite/archive.py` (unread in detail — flagged, not claimed) |

**This is not a set of drop-in landing spots.** It is a list of the nearest existing files an
eventual, explicit, Mike-approved import step would have to reconcile against — per
`07_DISPATCH_REPO_PLACEMENT_PLAN.md`'s promotion flow, that reconciliation is exactly what "Claude
Code review → Hold/Test-Grounds → Mike approval → Dispatch merge candidate" is for. No such
reconciliation has been attempted here, and this document does not propose one.

---

## Summary

The tri-department build and Dispatch's existing `portal/models/` layer are two independently
built, non-interoperable implementations of overlapping concepts. Neither informed the other. This
was not caught earlier because Dispatch's code was never inspected before now. Flagging it here so
it's on the record before any further integration decision is made.

Mike decides.
