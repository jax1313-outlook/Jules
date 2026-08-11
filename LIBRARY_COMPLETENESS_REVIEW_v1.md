# LIBRARY_COMPLETENESS_REVIEW_v1

Program: Dispatch
Status: **Investigation complete. Findings only — no fix applied, no implementation authorized
by this document.**
Origin: Named alongside Publisher/Intelligence/Manager reviews in this session's status
confirmation; sharpened into a concrete task ("start Library completeness review"). Scoped in
`DISPATCH_INTEGRATION_BRIDGE_INVESTIGATION_v1.md` Section 7 as not blocking (Library's shape
already the best-evidenced link in the object flow).
Rule: No code changes made. Read-only against `jax1313-outlook/Dispatch`
(`dispatch/canonical-reconciliation-integration`) — full read of `portal/models/library.py`,
its API routes, templates, tests, and the `reconciliation/` Library adapter, plus `git log`
provenance checks.

---

## 1. What This Review Is

Relative to the tri-department Library contract (`DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`
Sections 3.5/4.1/4.2 and the Library repo's core operations —
`current`/`resolve_packet`/`submit_candidate`/`review_candidate`/`ingest_human_document`), how
complete is Dispatch's real `portal/models/library.py`?

## 2. Findings By Contract Concept

| Concept | Verdict | Evidence |
|---|---|---|
| Library Candidate | **Partial, real but shape-incomplete** | `add_record()`/`review_candidate()` exist and work, but `source_finding_id`, `source_type`, `proposed_object_code` are absent entirely; `submitted_by` stores only the generic string `"human"`/`"machine"`, never a real department identity — so the contract's specific "`reviewed_by` must not equal the submitter" rule can't actually be enforced at the identity level, only approximated against a hardcoded reserved-role list. |
| Library Object / CURRENT truth | **None** | No `HUMAN_PLACED`/`APPROVED_CANDIDATE` origin split, no separate object type created on approval — `review_candidate()` mutates the same dict in place. No versioning or supersession concept anywhere in the real model (only in the separate, non-authoritative `reconciliation/contracts.py` mirror). |
| 15 Library collections | **None — fixed at 6, ad hoc** | `SECTIONS` is hardcoded to exactly 6 (`company`, `broker`, `customer`, `location_intelligence`, `operations`, `intelligence`). The reconciliation adapter's own mapping table covers only 6 of the 15 canonical collections, with one (`"intelligence"`) mapped to a generic `"Reference"` catch-all by the adapter's own admission — the other 9 have no Dispatch equivalent at all. |
| `library.current(object_code)` | **None** | Only bulk retrieval (`get_all`, `get_section`) exists. No single-object-by-code lookup function anywhere; the three functions that find one record by ID do so via a private inline scan each, not a reusable API. |
| `library.resolve_packet()` / Publisher Recipe | **None on both sides** | Zero hits anywhere in the repo for `PublisherRecipe`, `resolve_packet`, or any recipe concept — confirms the Publisher Completeness Review's finding from the Library side too: this isn't a missing caller, it's a fully absent concept on both ends. |
| `ingest_human_document` | **None — same code path, different string** | No distinct human-ingestion function exists. `add_record(submitted_by="human")` is the same code path as machine submission, differing only in one branch's status assignment. The stored `submitted_by` value is an unvalidated echo of caller input, not a real provenance marker. |

## 3. Test Coverage

Model-level coverage is solid: creation, retrieval, update/delete, section validation, the
human-vs-machine status split, availability filtering, reviewer-identity rejection, and
approve/reject/reject-if-not-pending are all tested. API-level coverage exists for `add`,
`update`, `delete`. **Gap: `/api/library/review` — the HTTP route wrapping `review_candidate()`
— has zero test coverage anywhere**, unlike every other Library route. No test exercises review
from the page-rendering side either.

## 4. No UI Review Workflow Exists At All (Different In Kind From Publisher's Bug)

This is not a broken button — it's an absent one, and the codebase says so itself.
`portal/templates/library.html` wires only "Delete" and "Add Record" actions; no
`review`/`approve`/`reject` element, button, or JS function exists anywhere in the templates
(`libraryReview` has zero hits). The server route's own docstring
(`portal/routes/api.py:253-260`) states plainly that it has no live traffic today because nothing
calls `add_record(submitted_by="machine")` yet — this is acknowledged, intentional dormancy, not
a silent regression like Publisher's approval button.

**Practical consequence, distinct from "no traffic today":** if any future automated path starts
submitting machine candidates, the resulting `pending_review` records would render in
`library.html` with a status badge and **no way for a human to act on them through the UI at
all** — only a direct API or Python call could approve or reject. Worth noting now, before that
day arrives, rather than rediscovering it as a live bug later.

## 5. Adjacent Finding: Stale Reconciliation-Adapter Claim

`reconciliation/adapters/library_adapter.py` was written (Stage 4, commit `69ba19a`) before
Stage 5 (`1c7fb30`) added the `pending_review`/`rejected`/`reviewed_by` fields to `library.py`,
and was never updated. Its own inline comment still asserts Dispatch's Library "hardcodes
`status='approved'` on every record" and has "no who-approved-this field anywhere" — both false
now. Its `dispatch_record_to_library_object()` unconditionally reports every record, regardless
of actual status, as canonical `CURRENT` truth with `accepted_by=UNKNOWN_APPROVER` — meaning a
`pending_review` or `rejected` record would today be mis-reported as approved truth if anything
ever consumed this adapter's output. Lower severity than the Publisher case: nothing currently
consumes `reconciliation/` output in a live path (Stage 6 confirmed the whole package is
imported only by its own tests) — but the mismatch is real and untested, and would mislead
immediately if that changed. Not fixed here — flagged, mirroring how the Publisher review
flagged its own adapter's stale claim.

## 6. What This Review Does Not Do

Does not fix the stale adapter claim, add the missing review UI, or build any of the four fully
absent contract concepts (`Library Object`/CURRENT split, 15-collection taxonomy,
`current()` lookup, `resolve_packet`). Does not touch the Publisher or Intelligence sides of any
shared concept — those are separate reviews.

Mike decides.
