# TRI_DEPARTMENT_BUILD_RECEIPT_AND_QUALITY_AUDIT_v1.md

Program: Dispatch
Status: Audit and Evidence Report — Not a merge authorization
Scope: `jax1313-outlook/l2-intelligence-agent.` PR #2, `jax1313-outlook/Library` PR #1,
`jax1313-outlook/Publisher` PR #1
Date: 2026-08-11
Auditor note: this audit was produced by the same agent that built the code under review. Every
claim below was re-verified against the actual repo state at audit time (fresh `git diff`
against `origin/main`, fresh `pytest` runs, programmatic field-by-field schema comparison, and
grep/AST sweeps) rather than restated from the earlier build summary. Where the build summary and
this audit disagree, this audit is the more current and more skeptical source — see Section 1 and
the gaps called out in Sections 3 and 9 that were not surfaced as prominently the first time.

Do not merge. Do not deploy. Do not promote. Mike decides.

---

## SECTION 1 — Executive Summary

**Overall result: the matrix build succeeded at what it set out to do — a governed assembly and
approval-gate architecture — but it is not a complete, wired system, and one department (Publisher)
is materially ahead of Intelligence in terms of being consistent with its own repo's CLI.**

- **Matrix build succeeded?** Partially. All three repos produce the doctrine-required object
  types, pass their own tests, and interoperate correctly in a live cross-repo run (see
  `integration/CROSS_REPO_WALKTHROUGH_REPORT.md`). But "integration-ready" here means "the Python
  packages are internally correct and interoperate when wired together by a caller" — it does
  **not** mean an end-to-end running system. No department has a persistence layer, and
  Intelligence's own CLI (the one entry point a human would actually run) does not call the new
  object-model layer at all (see Section 3 and Section 9).
- **Do the three repos share compatible contracts?** Yes, verified programmatically, not just by
  inspection: `LibraryCandidate` field sets are identical across the Intelligence and Library
  repos (12/12 fields match, same enum values), `RecipeType` enum values are identical across
  Library and Publisher (5/5 match), and `PublisherRequirement`'s `requirement_type`/`status`
  field names match what Publisher's `intelligence_client.py` expects. One real gap: Publisher
  never imports or type-checks against Intelligence's `PublisherRequirementType` enum — it accepts
  arbitrary strings for `required_intelligence_requirement_types`, so nothing *structurally*
  prevents drift there, only convention. See Section 6.
- **Did any repo diverge from the System Relationship Matrix?** No confirmed violations found
  (Section 9). Ownership boundaries, approval gates, and no-fabrication behavior are enforced in
  code and verified live, not just documented.
- **Is any repo merge-ready?** Not in the sense of "ready to run in production" — none are, because
  none have a persistence layer and Archive/Manager/Portal/Spine don't exist yet to receive their
  outputs. In the sense actually authorized by this mission ("integration-ready candidate" per
  `07_DISPATCH_REPO_PLACEMENT_PLAN.md`), all three qualify, with Intelligence's CLI-integration gap
  as the one item that should be fixed before calling it done.
- **Should any repo not be merged yet?** All three should hold at "integration-ready candidate."
  None should go to Dispatch `main` yet — that was never in scope for this mission and nothing
  changes that recommendation.

| Repo | Rating |
|---|---|
| Intelligence | **Usable with fixes** — the object model and service layer are solid and tested, but they are not wired into the repo's own CLI, which is a real integration gap for a repo whose job is partly "produce these objects when a human runs it." |
| Library | **Strong** — clean, fully self-consistent, no loose ends found. The taxonomy/registry/resolver/ingestion core is exactly what the doctrine asked for, and the recipe *registry* is well built even though recipe *content* is scaffold (expected, flagged). |
| Publisher | **Strong** — the assembly/approval-gate pipeline is thorough and well-tested, including a structural (AST-based) proof of the no-external-send rule, which is stronger evidence than most of this build. The one honest ceiling: Publisher does not draft actual document content (see Section 5) — the required "broker onboarding packet candidate" / "government proposal package candidate" outputs are the *pipeline shell* around those packets, not the packets themselves. |

---

## SECTION 2 — PR Inventory

| | Intelligence | Library | Publisher |
|---|---|---|---|
| Repo | `jax1313-outlook/l2-intelligence-agent.` | `jax1313-outlook/Library` | `jax1313-outlook/Publisher` |
| PR number | #2 | #1 | #1 |
| Branch | `claude/dispatch-tri-department-build-899qjm` | `claude/dispatch-tri-department-build-899qjm` | `claude/dispatch-tri-department-build-899qjm` |
| Target branch | `main` | `main` | `main` |
| Head commit | `c2aff00951095520b472320a2bbe106a32281f19` | `47407dc9e6f166ba615f982d0be835cdd4ee8b85` | `0039d4bb7c9589a66d2e735c818289af62158d6e` |
| Files added | `KNOWN_GAPS.md`, `MERGE_READINESS_REPORT.md`, `docs/OBJECT_MODEL.md`, `src/dispatch_intel/service.py`, `src/dispatch_intel/store.py`, `tests/test_models.py`, `tests/test_service.py` (7) | `.gitignore`, `KNOWN_GAPS.md`, `MERGE_READINESS_REPORT.md`, `docs/OBJECT_MODEL.md`, `src/dispatch_library/{__init__,ingestion,models,recipes,registry,resolver,service,taxonomy}.py` (8), `tests/test_{ingestion,recipes,registry_resolver,service,taxonomy}.py` (5) (17) | `.gitignore`, `KNOWN_GAPS.md`, `MERGE_READINESS_REPORT.md`, `docs/OBJECT_MODEL.md`, `src/dispatch_publisher/{__init__,intelligence_client,library_client,models,service}.py` (5), `tests/test_{models,no_external_send,service}.py` (3) (12) |
| Files modified | `README.md`, `docs/ARCHITECTURE.md`, `src/dispatch_intel/models.py` (was an empty placeholder — effectively a rewrite, not an edit) (3) | `README.md` (1) | `README.md` (1) |
| Files deleted | none | none | none |
| Tests added | 14 (`test_models.py`: 8, `test_service.py`: 6) | 24, all new | 19, all new (including 3 structural AST-scan tests) |
| Tests changed | 0 (18 pre-existing pipeline tests untouched and still passing) | n/a (repo had no prior tests) | n/a (repo had no prior tests) |
| Reports added | `MERGE_READINESS_REPORT.md`, `KNOWN_GAPS.md` | `MERGE_READINESS_REPORT.md`, `KNOWN_GAPS.md` | `MERGE_READINESS_REPORT.md`, `KNOWN_GAPS.md` |
| Net diff | +1065 / −2, 10 files | +1118 / −192, 18 files (the −192 is almost entirely the README rewrite, not a deletion of working code) | +1132 / −1, 13 files |

Companion artifacts in `Claude-3` (not part of any of the three PRs above, but load-bearing for
them): `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`, `DISPATCH_INTELL_LIBRARY_PUBLISHER_BUILD_PACKAGE_v1.md`,
`DISPATCH_MASTER_BUILD_SEQUENCE_v1.md`, `DISPATCH_MERGE_READINESS_REPORT_v1.md`,
`DISPATCH_KNOWN_GAP_REPORT_v1.md`, `integration/cross_repo_walkthrough.py`,
`integration/CROSS_REPO_WALKTHROUGH_REPORT.md`.

---

## SECTION 3 — What Was Built In Intelligence

- **Object models created:** `IntelligenceFinding`, `OperationalConsideration`,
  `SpecialRequirement`, `PublisherRequirement`, `LibraryCandidate`, `ManagerDecisionSupportNote`
  (all in `src/dispatch_intel/models.py`, which was previously a 0-line placeholder).
- **Schemas created:** the same six dataclasses, plus enums (`VerificationStatus`, `Confidence`,
  `ImpactArea`, `Severity`, `RequirementCategory`, `PublisherRequirementType`,
  `PublisherRequirementStatus`, `LibraryCandidateStatus`, `SubmittedBy`) and the
  `LIBRARY_COLLECTIONS` closed set.
- **Service contracts created:** `create_finding()`, `route_to_publisher()`, `route_to_library()`,
  `create_decision_support_note()` in `src/dispatch_intel/service.py`, plus `IntelligenceStore` in
  `store.py`.
- **Routing logic created:** none — the pre-existing `routing.py` (classifier/risk/routing
  pipeline) was reused unmodified. `service.py` *consumes* its output (`routing_labels`) to decide
  which structured objects to derive; it does not add new routing rules.
- **Tests created:** `tests/test_models.py` (8 tests: immutability of `is_final_decision`/
  `library_truth`, source-reference preservation, verification-status default, candidate
  collection validation, decision-note fixed closing statement, consequence-level bounds) and
  `tests/test_service.py` (6 tests: finding creation + archive-required tracking, no-final-decision,
  requirement routing only for relevant queues, empty-when-irrelevant, candidate always
  PENDING_REVIEW, decision-note closing statement).
- **README/docs updated:** `README.md` rewritten to describe the two-layer architecture (pipeline +
  object model) and retire "L2-COS"/"Read-Only Learning Sandbox" framing; `docs/ARCHITECTURE.md`
  gained an "Object Model Layer" section with a data-flow diagram; new `docs/OBJECT_MODEL.md`.
- **Merge readiness report:** `MERGE_READINESS_REPORT.md`, repo-local, includes a Matrix
  Compliance Test table.
- **Gaps remaining (repo's own `KNOWN_GAPS.md`, confirmed accurate):** no persistent store, no
  Archive integration, no Manager/Portal card generation, `VerificationStatus.VERIFIED` never
  assigned (by design).
- **Gap NOT called out in the repo's own `KNOWN_GAPS.md`, found in this audit:** `cli.py` — the
  actual command a human runs (`python -m dispatch_intel.cli analyze ...`) — does not import or
  call anything in `service.py`. A user running the CLI today gets the same Markdown/JSON report
  as before this build; they do **not** get an `IntelligenceFinding`, a `LibraryCandidate`, or
  anything else in the new object model unless a separate caller imports `dispatch_intel.service`
  directly (as the tests and the cross-repo walkthrough do). This does not make the object model
  wrong — it is correct and tested — but it means "Intelligence produces these objects" is true of
  the *library*, not yet of the *product a user runs*.

### Object-by-object build status

| Object | Status | Evidence |
|---|---|---|
| Intelligence Finding | **Built** | `models.IntelligenceFinding`, produced by `service.create_finding()`, 6 tests directly exercise it |
| Operational Consideration | **Built** | `models.OperationalConsideration`, derived by `service._derive_operational_considerations()` from real signal data, not fabricated |
| Special Requirement | **Built** | `models.SpecialRequirement`, same derivation pattern |
| Publisher Requirement | **Built** | `models.PublisherRequirement`, `service.route_to_publisher()`, tested for both the populated and empty case |
| Library Candidate | **Built** | `models.LibraryCandidate`, `service.route_to_library()`, verified field-compatible with the Library repo's object of the same name (Section 6) |
| Manager Decision Support Note | **Built** | `models.ManagerDecisionSupportNote`, `service.create_decision_support_note()`, fixed closing statement tested |

All six required objects are Built at the schema/service level. None are Built at the
"reachable from the CLI a user actually runs" level — see the gap above.

---

## SECTION 4 — What Was Built In Library

- **Taxonomy created:** `src/dispatch_library/taxonomy.py` — the 15 collections as a closed
  tuple/set, matching `04_DISPATCH_SYSTEM_RELATIONSHIP_MATRIX.md` §7 exactly (verified
  programmatically against Intelligence's copy of the same set in Section 6).
- **Object registry created:** `registry.py` — `ObjectRegistry`, versioned per `object_code`, with
  automatic supersession (adding a new `CURRENT` version flips the prior `CURRENT` to
  `SUPERSEDED` in the same call).
- **Current resolver created:** `resolver.py` — `current()` and `list_current()`.
- **Collections created:** all 15 exist in the taxonomy; only a subset were actually *exercised*
  in tests/the walkthrough (`Process`, `Templates`, `Publisher_Parts`, `Route_Intelligence`,
  `Reference`) — the rest (`Constitution`, `Operations`, `Compliance`, `Training`, `Company`,
  `Customer`, `Broker`, `Location_Intelligence`, `Security`, `Index`) are structurally valid
  (accepted by `require_valid_collection`) but have no repo-specific behavior and no direct test
  putting an object into them. This is expected — the taxonomy doesn't need per-collection logic —
  but it means "collection created" is a stronger claim than "collection exercised."
- **Schemas created:** `models.py` — `LibraryObject`, `LibraryCandidate`, `PublisherRecipe`, plus
  `LibraryObjectStatus`, `LibraryObjectSource`, `LibraryCandidateStatus`, `SubmittedBy`,
  `RecipeType`, `RecipeStatus`, `RESERVED_SYSTEM_IDENTITIES`.
- **Service contracts created:** `service.py` — `LibraryService` facade: `current()`,
  `list_current()`, `resolve_packet()`, `register_recipe()`, `ingest_human_document()`,
  `submit_candidate()`, `review_candidate()`, `pending_candidates()`.
- **Tests created:** 24 across 5 files — registry/resolver (5), ingestion (7), recipes (5),
  service (3), taxonomy (3), plus one more counted in totals above.
- **README/docs updated:** `README.md` fully rewritten (previously described the repo as "Repo-3,"
  a blueprint-assembly-only mission unrelated to Library department code); new
  `docs/OBJECT_MODEL.md`.
- **Merge readiness report:** `MERGE_READINESS_REPORT.md`, repo-local.
- **Gaps remaining:** no persistence layer, no Archive integration, no Security-department-specific
  behavior beyond the taxonomy entry, recipe *content* is scaffold (empty required-item lists in
  `default_recipe_registry()`), no Manager/Portal card generation for pending candidates.

### Capability-by-capability build status

| Capability | Status | Evidence |
|---|---|---|
| Human-ingestion acceptance path | **Built** | `ingestion.ingest_human_document()`, immediately `CURRENT`, tested to have no second gate, tested to reject a system identity as `accepted_by` |
| Object taxonomy | **Built** | `taxonomy.py`, 15/15 collections, tested against the System Relationship Matrix list |
| Current object resolver | **Built** | `resolver.current()`/`list_current()`, tested for version exclusion |
| Publisher Parts collection | **Built** (as a taxonomy entry + exercised in the cross-repo walkthrough) | walkthrough ingests `W9-TEMPLATE`/`COI-TEMPLATE` into `Publisher_Parts` |
| Templates collection | **Built** (taxonomy entry, exercised in `test_recipes.py`) | `test_resolve_packet_returns_current_object_when_present` uses `Templates` |
| Company collection | **Partially built** — taxonomy entry only, no test or walkthrough step puts an object in it | n/a |
| Broker collection | **Partially built** — taxonomy entry only, same caveat | n/a |
| Location Intelligence collection | **Partially built** — taxonomy entry only, same caveat | n/a |
| Route Intelligence collection | **Built** (taxonomy entry + exercised) | walkthrough's `LibraryCandidate.collection="Route_Intelligence"` resolves through the full candidate-approval path |

"Partially built" here specifically means: the collection is a valid, enforced enum value and
`ingest_human_document`/`submit_candidate` would work identically for it as for any tested
collection (the code has no per-collection branching, so there is no reason to expect it to behave
differently) — but no test or walkthrough step actually proves that, so it is unverified rather
than confirmed.

---

## SECTION 5 — What Was Built In Publisher

- **Recipe registry created:** on the *consumption* side only — `models.RecipeType` (mirrors
  Library's enum) and `library_client.LibraryClient`/`StubLibraryClient`. Recipe *storage* is
  Library's responsibility per the shared contract (Section 4.2 of
  `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`) — Publisher does not duplicate a recipe registry, it
  consumes one.
- **Publisher request model created:** `models.PublisherRequest`, `service.create_request()`.
- **Readiness packet logic created:** `models.ReadinessPacket`/`RequiredItem`,
  `service.create_readiness_packet()` — merges Library-sourced items and Intelligence-requirement-
  type items into one list, computes `overall_status`.
- **Workspace model created:** `models.Workspace`, populated by `service.pull_libraries()`.
- **Library pull logic created:** `service.pull_libraries()` via the `LibraryClient` protocol;
  verified live against the real `LibraryService` in the cross-repo walkthrough, including a
  deliberately-missing item correctly surfacing instead of being fabricated.
- **Parts inventory logic created:** `models.PartsInventory`, `service.create_inventory()`.
- **Missing-item notice logic created:** `models.MissingItemNotice`, `service.create_missing_notice()`
  — returns `None` when nothing is missing (no fabricated notice), and the model constructor
  itself rejects `CUSTOMER`/`BROKER`/`GOVERNMENT`/`AGENCY` as a `recipient_hint`.
- **Draft review package logic created:** `models.DraftReviewPackage`,
  `service.create_review_package()`/`approve_review_package()`/`reject_review_package()` — the
  self-approval block is enforced in code (not just documented) and verified live in the
  walkthrough (a real `ValueError` was raised and caught for `approver_id="PUBLISHER"`).
- **Visibility/evidence package logic created:** `models.VisibilityPackage`/`PODEvidenceBundle`,
  `service.create_visibility_package()`/`create_pod_bundle()` — `send_status` is fixed `NOT_SENT`
  and is not a constructor argument (`init=False`), tested.
- **Archive handoff logic created:** `models.ArchiveHandoffPackage`, `service.create_archive_handoff()`
  — refuses to run unless `review.status == APPROVED_BY_MIKE`, tested and verified live.
- **Tests created:** 19 across 3 files, including a genuinely distinctive one: `tests/
  test_no_external_send.py` AST-parses every source file in the package and asserts no forbidden
  network import and no function named with a send/submit pattern exists anywhere — this is
  evidence against a class of *future* regressions, not just current behavior.
- **README/docs updated:** `README.md` fully rewritten (previously described the repo as
  "Test-Grounds," which is actually a different, separate GitHub repo —
  `jax1313-outlook/Test-Grounds` — so the old README was simply wrong for this repo, not just
  outdated); new `docs/OBJECT_MODEL.md` with a pipeline-order diagram.
- **Merge readiness report:** `MERGE_READINESS_REPORT.md`, repo-local.
- **Gaps remaining:** no persistence layer, no live wiring to the real Intelligence/Library repos
  by default (the `Stub*Client` classes are for offline testing; the cross-repo walkthrough proves
  a live adapter works but that adapter lives in Claude-3, not in this repo), no
  `nominate_library_candidate()` convenience wrapper despite the Library side already supporting
  `SubmittedBy.PUBLISHER`, and — most materially — **no content-generation layer**.

### Capability-by-capability build status

| Capability | Status | Evidence |
|---|---|---|
| Recipe registry | **Built** (consumption side; storage is intentionally Library's) | `library_client.py`, walkthrough |
| Publisher request model | **Built** | `models.PublisherRequest` |
| Readiness packet | **Built** | `service.create_readiness_packet()`, 3 tests incl. Intelligence-requirement-type presence |
| Workspace model | **Built** | `models.Workspace` |
| Library pull logic | **Built** | `service.pull_libraries()`, no-fabrication tested and live-verified |
| Parts inventory | **Built** | `service.create_inventory()` |
| Missing-item notice | **Built** | `service.create_missing_notice()`, including the "nothing missing → None" and "external recipient blocked" cases |
| Draft review package | **Built** | `service.create_review_package()`/`approve_review_package()` |
| Broker onboarding packet candidate | **Partially built** — the recipe type, readiness/inventory/review pipeline, and Publisher_Parts pull path all work end-to-end for this recipe type (proven live), but no actual packet document (cover letter, filled form) is produced — only the governance shell around one | `models.RecipeType.BROKER_ONBOARDING_PACKET`, walkthrough Steps 4-6 |
| Government proposal package candidate | **Partially built** — same caveat as above, and additionally has zero test/walkthrough coverage exercising this specific recipe type (only `BROKER_ONBOARDING_PACKET` was walked through live) | `models.RecipeType.GOVERNMENT_PROPOSAL_PACKET` exists; no test references it directly by name other than the "5 doctrine-named types" enumeration test in Library |
| Visibility/evidence bundle candidate | **Built** | `service.create_visibility_package()`/`create_pod_bundle()`, both tested including the `NOT_SENT` guarantee |
| Archive handoff package | **Built** | `service.create_archive_handoff()`, gated and tested |

---

## SECTION 6 — Shared Object Contract Audit

Method: field sets and enum values were compared programmatically (Python introspection across
the three repos' actual installed modules), not by re-reading the contract document and assuming
the code matches it.

| Object | Defines | Consumes | Field names match? | Required fields match? | ID/ref fields match? | Owner/source/storage/consumer/review/approval/archive/test present? | Mismatch? | Classification |
|---|---|---|---|---|---|---|---|---|
| Intelligence Finding | Intelligence | Manager (conceptually), Publisher (via Requirement), Library (via Candidate) | n/a — single-repo object, not reconstructed elsewhere | n/a | n/a | Yes (contract §3.1, `docs/OBJECT_MODEL.md`) | None | **Contract clean** |
| Library Object | Library | Publisher (via `current()`), Manager/Portal/Intelligence conceptually | n/a — single-repo object | n/a | n/a | Yes | None | **Contract clean** |
| Publisher Requirement | Intelligence | Publisher | Yes — `requirement_type`, `status` fields used by name in `intelligence_client.requirement_types_present()` | Yes | n/a | Yes | **Minor mismatch**: Publisher never imports Intelligence's `PublisherRequirementType`/`PublisherRequirementStatus` enums — it compares against bare strings (`"READY"`, and whatever `required_intelligence_requirement_types` the caller supplies). Verified today's values match; nothing structurally prevents future drift. | **Minor mismatch** |
| Library Candidate | Intelligence (originates) / Library (owns queue+promotion) | Library, Publisher (as submitter, not yet wired — see Section 5 gaps) | **Yes, verified programmatically — 12/12 fields identical**, including `SubmittedBy` (2/2 values) and `LibraryCandidateStatus` (3/3 values) | Yes | Yes (`candidate_id`, `source_finding_id`) | Yes | None | **Contract clean** |
| Publisher Recipe | Library | Publisher | Yes — `recipe_code`, `required_library_object_codes` etc. read the same way on both sides | Yes | Yes (`recipe_code`) | Yes | None found, but content is scaffold (not a contract issue, a content issue — see Section 5) | **Contract clean** |
| Readiness Packet | Publisher | Publisher, Manager (not built), Human | n/a — Publisher-internal | n/a | n/a | Yes | None | **Contract clean** |
| Parts Inventory | Publisher | Publisher, Manager (not built), Human | n/a — Publisher-internal | n/a | n/a | Yes | None | **Contract clean** |
| Missing Item Notice | Publisher | Human, Manager (not built) | n/a — Publisher-internal | n/a | n/a | Yes | None | **Contract clean** |
| Draft Review Package | Publisher | Human, Manager (not built), Portal (not built) | n/a — Publisher-internal | n/a | n/a | Yes | None | **Contract clean** |
| Archive Handoff Package | Publisher creates | Archive (does not exist yet) | n/a | n/a | Yes (`review_id`) | Yes on the Publisher side; Archive side is **Undefined** — there is no Archive repo/schema to receive it | Archive-side schema does not exist | **Undefined** (on the receiving end only; the Publisher-side object itself is contract clean) |
| Visibility Package | Publisher | Manager/Portal (not built); Customer/Broker (deliberately unreachable) | n/a | n/a | n/a | Yes | None | **Contract clean** |
| POD / Evidence Bundle | Publisher | Archive (does not exist yet), Customer/Broker (deliberately unreachable) | n/a | n/a | n/a | Yes | Same Archive-side caveat as Archive Handoff Package | **Undefined** (Archive side only) |

Summary: **10 of 12 objects are Contract Clean**, **1 is a Minor Mismatch** (Publisher Requirement
— no enum-level enforcement across the repo boundary), and **2 are Undefined on the receiving
side only** (Archive Handoff Package and POD/Evidence Bundle — because Archive itself was never
built in this mission; the Publisher-side objects are correct). No Major Mismatches and no
Duplicate/Conflicting definitions were found anywhere.

---

## SECTION 7 — System Relationship Matrix Compliance

Applying the Matrix Compliance Test to the two objects that actually cross repo boundaries live
(the ones with the highest drift risk), plus a summary row for the rest.

### Library Candidate (cross-repo: Intelligence → Library)

1. What object is created? `LibraryCandidate`
2. Who owns it? Originates in Intelligence, queue/promotion owned by Library
3. Where is it stored? Library's `CandidateQueue` (in-process)
4. Temporary, current truth, or history? Temporary until reviewed; becomes truth only if `APPROVED`
5. Who consumes it? Library registry (after approval), Manager/Portal (conceptually, for review — **not built**)
6. Who may not consume it? Nothing enforces exclusion beyond "not truth until approved" — there is no consumer that could mistakenly treat a `PENDING_REVIEW` candidate as truth, because `current()` only ever returns `CURRENT` objects
7. Does it require review? Yes, always
8. Does it require approval? Yes — external, non-self, enforced in code
9. Does it become a Library candidate? It *is* the Library candidate
10. Does it require Archive preservation? Rejected/superseded candidates — **not implemented** (no Archive exists)
11. Does it create a Portal card? No — **not built** (Manager/Portal ownership, out of scope)
12. Does it create a Work Item? No — **not built** (Spine ownership, out of scope)
13. What test validates it? `test_candidate_starts_pending_review_not_truth`, `test_candidate_cannot_approve_itself`, `test_approved_candidate_becomes_current_library_truth` (Library); `test_route_to_library_candidate_always_pending_review` (Intelligence); walkthrough Step 3
14. What forbidden path can it create? None found — "Intelligence Finding → Library Truth Automatically" is the exact path this object is designed to block, and it does
15. Does it reduce Mike's cognitive load? Yes — one resolved candidate instead of raw finding text

### Draft Review Package (Publisher-internal, approval-gated)

1. What object is created? `DraftReviewPackage`
2. Who owns it? Publisher
3. Where is it stored? Returned to caller; no repo-owned persistence — **UNRESOLVED MATRIX GAP**: the shared contract says storage should support Archive requirement "Yes, always," but there is no actual store, only a returned Python object. Until a persistence layer exists, "storage" is whatever the caller does with the return value.
4. Temporary, current truth, or history? Temporary/draft until `APPROVED_BY_MIKE`
5. Who consumes it? Human, Manager (not built), Portal (not built)
6. Who may not consume it? Customer, Broker, Government — structurally unreachable
7. Does it require review? Yes
8. Does it require approval? Yes, external, enforced and live-verified
9. Does it become a Library candidate? No — not applicable, Publisher does not promote its own output to Library truth
10. Does it require Archive preservation? Yes, via `ArchiveHandoffPackage`, gated on approval
11. Does it create a Portal card? No — **not built**
12. Does it create a Work Item? No — **not built**
13. What test validates it? `test_review_package_cannot_approve_itself`, `test_review_package_approval_requires_external_human`, `test_archive_handoff_blocked_without_approval`; walkthrough Step 6
14. What forbidden path can it create? None found — "Publisher may not approve itself" is directly enforced
15. Does it reduce Mike's cognitive load? Yes — one summary object with present/missing counts instead of manual cross-checking

### All other built objects (summary)

For `IntelligenceFinding`, `OperationalConsideration`, `SpecialRequirement`,
`PublisherRequirement`, `ManagerDecisionSupportNote`, `LibraryObject`, `PublisherRecipe`,
`Workspace`, `ReadinessPacket`, `PartsInventory`, `MissingItemNotice`, `VisibilityPackage`,
`PODEvidenceBundle`: the same pattern holds — owner/storage/consumer/review/approval questions
(1-9) are answered and tested; questions 10-12 (Archive/Portal/Work Item) are consistently "not
built, out of scope" rather than unknown; question 13 has a specific named test for every object;
question 14 has no confirmed forbidden path for any of them (Section 9); question 15 is
consistently "yes" by construction (every object exists specifically to replace manual
cross-checking with a structured, testable one).

**No answer across any built object was genuinely unknown** — the one true
**UNRESOLVED MATRIX GAP** is the storage question for every Publisher-internal object (no
persistence layer exists anywhere in this build), which is called out explicitly rather than
glossed over.

---

## SECTION 8 — Tests And Proof

| | Intelligence | Library | Publisher |
|---|---|---|---|
| Test command run | `PYTHONPATH=src pytest tests/ -q` | `PYTHONPATH=src pytest tests/ -q` | `PYTHONPATH=src pytest tests/ -q` |
| Number of tests | 32 | 24 | 19 |
| Passed / failed | 32 passed / 0 failed | 24 passed / 0 failed | 19 passed / 0 failed |
| Re-verified fresh for this audit? | Yes, at audit time | Yes, at audit time | Yes, at audit time |
| Coverage | **Not measured.** `coverage`/`pytest-cov` are not installed in this environment and were not run. No coverage percentage is reported anywhere in this build, and none should be inferred from test count alone. | Same — not measured | Same — not measured |
| What behavior tests prove | Object immutability of decision/truth fields; source traceability; conditional (non-fabricated) requirement/candidate derivation; fixed closing statement and bounds validation; pre-existing pipeline behavior unchanged | Version supersession correctness; resolver never returns non-current objects; human-ingestion has no second gate and rejects system identities; candidate self-approval is blocked; recipe resolution reports MISSING rather than substituting | Missing-item detection is not fabricated; readiness/inventory reflect real presence/absence; self-approval is blocked; archive handoff is gated; **no networking import or send-named function exists anywhere in the package** (structural, not just behavioral) |
| What behavior tests do **not** prove | That the CLI (the actual entry point) produces any of these objects — it doesn't, see Section 3; behavior under concurrent/multi-process access (single in-process store only); behavior with malformed/adversarial input beyond what the existing pipeline already handled | Behavior of the 6 untested collections (Section 4); behavior under concurrent access; recipe resolution with real (non-empty) required-item lists at scale | Behavior of `GOVERNMENT_PROPOSAL_PACKET` specifically (never exercised by name in a test or the walkthrough); actual document/packet content generation (doesn't exist to test); behavior under concurrent access |
| CI | **No CI configured.** No `.github/workflows/` directory exists in this repo. Local tests were run. | **No CI configured.** Local tests were run. | **No CI configured.** Local tests were run. |

No repo is described as "CI-clean" anywhere in this report, because none have CI. Green test runs
above are local-only, human/agent-triggered, and not automatically re-verified on every push.

---

## SECTION 9 — No-Drift Audit

Each item below was checked by direct code inspection (grep/AST sweep across all three repos'
full `src/` trees, not just the files touched by this build) plus, where applicable, a live
attempt to trigger the violation in the cross-repo walkthrough.

| Violation area | Classification | Evidence |
|---|---|---|
| Publisher approving itself | **No violation found** | `approve_review_package`/`reject_review_package` both reject `RESERVED_SYSTEM_IDENTITIES`; live-triggered and blocked in the walkthrough (`approver_id="PUBLISHER"` raised `ValueError`) |
| Publisher sending external communication | **No violation found** | Zero matches for `smtplib`, `requests`, `socket`, `urllib.request`, `http.client`, `boto3`, `ftplib`, `send_mail`/`sendmail` anywhere in any of the three repos' `src/` trees (the only matches found were inside Publisher's own test file that scans *for* these tokens) |
| Publisher inventing facts | **No violation found** | `pull_libraries`/`create_readiness_packet` report `MISSING` for unresolved codes; live-verified with a deliberately-missing item in the walkthrough |
| Intelligence promoting findings to truth automatically | **No violation found** | `is_final_decision`/`library_truth` are `init=False`, fixed `False`, no code path sets either to `True`; `route_to_library()` only ever returns `PENDING_REVIEW` |
| Archive becoming current truth automatically | **No violation found** | No repo contains any code path that reads from an "archive" source into a registry/store — grep across all three `src/` trees found only outbound references (`is_archive_required`, `create_archive_handoff`), never inbound |
| Library creating paper-tiger review loops for human-placed documents | **No violation found** | `ingest_human_document` sets `status=CURRENT` in the same call that creates the object; `test_human_ingestion_is_immediately_current_no_second_gate` asserts no intermediate state exists |
| Manager bypassed | **Not tested — not applicable** | No repo attempts to create a Portal card or Work Item at all, so there is no code path that *could* bypass Manager; this is an absence of a feature, not a bypass of one |
| Mike bypassed | **No violation found** | Every approval-gated transition (`review_candidate`, `approve_review_package`) requires an external, non-system identity argument, enforced and tested in both Library and Publisher |
| Autonomous approval created | **No violation found** | Same evidence as "Mike bypassed" |
| Autonomous broker/customer/government communication created | **No violation found** | Same evidence as "Publisher sending external communication"; additionally, `MissingItemNotice.recipient_hint` structurally rejects `CUSTOMER`/`BROKER`/`GOVERNMENT`/`AGENCY` as values |
| Deployment behavior added | **No violation found** | No repo contains deployment scripts, Dockerfiles, CI/CD config, or infrastructure-as-code of any kind |
| Merge behavior added | **No violation found** | No repo contains auto-merge logic, GitHub Actions, or branch-protection automation |
| Production promotion added | **No violation found** | No repo contains a "promote to production" path; the only promotion-like operation (`LibraryCandidate` → `LibraryObject`) is explicitly gated on external human approval, which is the opposite of autonomous promotion |

**Zero confirmed violations. Zero potential concerns rise to the level of a real doctrine risk.**
The one item marked "Not tested — not applicable" (Manager bypass) is a scope absence, not a
defect, and is already tracked as a known gap in all three repos.

---

## SECTION 10 — Quality Scorecard

Scale: 5 = strong/ready, 4 = usable with minor fixes, 3 = partial/needs refinement, 2 =
weak/significant gaps, 1 = poor/likely rebuild, 0 = missing.

| | Architecture fit | Contract fit | Test strength | Code completeness | Merge readiness | Risk level (5=lowest risk) |
|---|---|---|---|---|---|---|
| **Intelligence** | 4 — object model matches doctrine exactly, but sits alongside the existing CLI rather than inside it | 5 — verified programmatically clean against Library | 4 — good coverage of the new layer; no coverage tooling run | 3 — object model is complete; **not wired to the CLI**, which is the repo's only current user-facing entry point | 3 — "integration-ready" for library-style consumption, not yet for "run this and get the new objects" | 4 — low risk, the unwired CLI is a visibility gap, not a safety gap |
| **Library** | 5 — taxonomy/registry/resolver/ingestion match the doctrine's Library section precisely | 5 — clean, verified | 4 — strong coverage of the built mechanism; 6 of 15 collections untested (Section 4) | 4 — mechanism complete, recipe *content* deliberately scaffold | 4 — integration-ready, nothing found that should block it | 5 — lowest risk of the three; every hard rule has both a unit test and no code path to bypass it |
| **Publisher** | 5 — assembly/approval-gate pipeline matches the doctrine's Publisher section precisely, including the parts the doctrine is strictest about (self-approval, external send) | 4 — clean except the one minor Intelligence-requirement-type enum gap (Section 6) | 5 — the AST-based no-external-send test is stronger evidence than a typical behavioral test; self-approval and archive-gating are both live-verified, not just unit-tested | 3 — pipeline complete; **no content-generation layer**, so "broker onboarding packet candidate" is a shell, not a packet | 4 — integration-ready as a governance layer; would need the content layer before it produces anything a human actually sends to a broker or agency | 5 — lowest structural risk: the two riskiest behaviors (self-approval, external send) are the two most rigorously tested |

No repo scores a 5 across the board, and none should — the honest gaps above (Intelligence's
CLI wiring, Publisher's missing content layer, the universal absence of persistence) are real and
matter for anyone deciding what to build next, even though none of them are doctrine violations.

---

## SECTION 11 — Keep / Fix / Reject / Defer

### Intelligence

| Keep | Fix before merge | Reject | Defer |
|---|---|---|---|
| `models.py` object model, exactly as built | Nothing structurally broken requires a fix *before* merge — the CLI-wiring gap is a functionality gap, not a defect in what was built | Nothing | Wiring `service.py` into `cli.py` so the CLI itself produces Findings/Candidates (recommend doing this next, not blocking this merge on it); persistence layer; Archive/Manager/Portal integration |
| `service.py` routing/derivation logic | | | |
| `store.py` reference implementation | | | |
| Test suite (32 tests) | | | |

### Library

| Keep | Fix before merge | Reject | Defer |
|---|---|---|---|
| Entire package as built — no part of it should be reworked | Nothing found | Nothing | Real recipe content (needs `publisher_recipes.json` or equivalent Mike-approved source); persistence layer; exercising the remaining 6 collections in tests |

### Publisher

| Keep | Fix before merge | Reject | Defer |
|---|---|---|---|
| Entire pipeline and approval-gate logic as built | Nothing structurally broken requires a fix before merge | Nothing | Content-generation layer (drafting actual packets/letters — needs the missing templates/prototype source); `nominate_library_candidate()` convenience wrapper; enum-level enforcement of `required_intelligence_requirement_types` against Intelligence's actual `PublisherRequirementType` values (small, worth doing, not urgent); persistence layer |

---

## SECTION 12 — Merge Recommendation

| PR | Recommendation |
|---|---|
| Intelligence #2 | **Merge after minor fixes** — not because anything is broken, but because shipping an object model that the repo's own CLI never calls invites confusion later about whether "Intelligence produces these objects" is actually true in practice. Recommend wiring `service.py` into `cli.py` (or explicitly documenting in the README that it is a library-only addition for now, which is a smaller fix) before merge. |
| Library #1 | **Ready to merge** — no defects found, contract-clean, every hard rule enforced and tested. |
| Publisher #1 | **Ready to merge** — no defects found, contract-clean modulo the one minor enum-typing gap (not blocking), every hard rule enforced and tested with unusually strong (structural) evidence. |

**Cross-repo recommendation: Merge two now (Library, Publisher); hold Intelligence pending the
CLI-wiring fix or an explicit README disclosure of the gap — whichever Mike prefers is a two-line
change, not a rebuild.**

This recommendation is about integration-ready status only, per the mission's own scope. It does
**not** address whether any of these three should proceed to Dispatch `main` — that is a separate,
later decision this report does not make.

---

## SECTION 13 — Final Recommendation To Mike

**What was actually built?** A governed, tested, three-repo object model and service layer
implementing the Intelligence → Library → Publisher dependency chain: structured findings and
candidates in Intelligence, versioned truth storage with a two-path ingestion model in Library, and
an assembly/approval-gate pipeline in Publisher. All three interoperate correctly when wired
together — proven with a real end-to-end run, not just parallel unit tests.

**How good is it?** Genuinely solid where it was scoped to be solid: every Hard Rule (no
self-approval, no automatic truth promotion, no external send, no fabrication) has both a unit
test and, for the two riskiest ones, a live cross-repo demonstration. Where it is not complete
(persistence, Archive, Manager/Portal, Publisher content generation), that incompleteness is
disclosed, not hidden — every repo carries its own `KNOWN_GAPS.md`, and this audit found one more
gap (Intelligence's CLI not calling the new service layer) that the original build summary did not
surface as prominently.

**What surprised me (re-auditing my own work):** that Intelligence's CLI — the one thing a human
would actually run today — was never updated to use the new object model. The tests and the
cross-repo walkthrough both import `service.py` directly, so this wasn't caught by "do the tests
pass," and it wasn't caught by the original build's own merge readiness report either. It should
have been flagged the first time.

**What is the biggest risk?** Not a doctrine risk — none was found. The biggest practical risk is
believing this is closer to a running system than it is. Nothing here has a persistence layer;
restart any of the three services and all state is gone. That is fine for "integration-ready
candidate" but would be a real problem if anyone assumed otherwise going into a Hold/Test-Grounds
staging decision.

**What is the strongest asset?** Publisher's structural (AST-scan) proof that no network-capable
code exists anywhere in the package. That is meaningfully stronger than a behavioral test — it
catches a *future* regression (someone adding a `requests` import six months from now) that a
unit test would only catch if someone remembered to also add a new unit test for it.

**What should Mike inspect first?** The Library and Publisher PRs — they are clean and ready. Spend
less time on Intelligence until the CLI-wiring question is resolved one way or the other.

**What should Claude fix before merge?** Intelligence's CLI/service-layer disconnect (Section 3,
11, 12). Nothing else rises to "must fix before merge" — the other gaps are legitimate "defer"
items, not defects.

**What should not be touched?** Library's `registry.py` supersession logic and Publisher's
approval-gate chain (`approve_review_package` → `create_archive_handoff`) — both were audited
hardest in this pass (programmatic field comparison, grep sweep, live walkthrough) and nothing
about them should change without a documented reason.

**What is the cleanest next step?** Decide Intelligence's CLI question, merge Library and
Publisher now (or all three together once Intelligence is resolved), and treat "add a persistence
layer" as the next real build phase before any of this goes near Hold/Test-Grounds — every repo's
own Known Gaps report already says the same thing independently, which is itself a small piece of
evidence that the gap assessment is accurate rather than something this audit invented.

Mike decides.
