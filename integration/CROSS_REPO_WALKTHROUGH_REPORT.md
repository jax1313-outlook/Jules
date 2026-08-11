# CROSS-REPO WALKTHROUGH REPORT

Program: Dispatch
Build: Tri-Department Matrix Build (Intelligence → Library → Publisher)
Script: `integration/cross_repo_walkthrough.py`
Date: 2026-08-11

---

## Purpose

Demonstrate, with a real run rather than isolated unit tests, that the three department repos
(`l2-intelligence-agent.`, `Library`, `Publisher`) are field-compatible per
`DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` and enforce every Hard Rule when actually wired together
— not just individually. This satisfies Build Command Section 9's "demo/walkthrough report" and
Phase 5's "Cross Repo Integration / Contract Validation / Boundary Testing / No-Fabrication
Testing / No-Autonomous-Action Testing."

## How to reproduce

```bash
python3 integration/cross_repo_walkthrough.py \
  <path-to-l2-intelligence-agent.>/src \
  <path-to-library>/src \
  <path-to-publisher>/src
```

## Result

```
=== STEP 1: Intelligence — analyze a real example document ===
Finding f05c7e5a-...: routing_queue=['REVIEW_SOON', 'LOAD_BOARD_REVIEW', 'SPECIAL_REQUIREMENTS_REVIEW', 'NEEDS_MORE_INFO', 'COMPLIANCE_REVIEW', 'LIBRARY_CANDIDATE']
Intelligence LibraryCandidate: e8ae4f22-... collection=Route_Intelligence status=LibraryCandidateStatus.PENDING_REVIEW

=== STEP 2: Field-compatibility check — Intelligence candidate -> Library candidate ===
Field sets identical across repos: ['candidate_id', 'collection', 'created_at', 'proposed_body_or_reference', 'proposed_object_code', 'proposed_title', 'reviewed_at', 'reviewed_by', 'source_finding_id', 'source_type', 'status', 'submitted_by']
Reconstructed on Library side with zero field renaming.

=== STEP 3: Library — submit, review, and promote the candidate ===
Candidate promoted to Library truth: CAND-f05c7e5a v1 source=APPROVED_CANDIDATE accepted_by=Mike Zachary

=== STEP 4: Library — ingest two human-placed Publisher Parts, register a recipe ===
Registered BROKER_ONBOARDING_PACKET recipe requiring 2 present items + 1 deliberately missing item.

=== STEP 5: Publisher — pull from Library through the documented client boundary ===
Workspace pulled=['W9-TEMPLATE', 'COI-TEMPLATE'] pending=['MISSING-ITEM-X']
ReadinessPacket overall_status=INCOMPLETE, ReviewPackage status=DRAFT

=== STEP 6: Publisher — self-approval blocked, external approval succeeds ===
Self-approval correctly blocked: approver_id must identify a real human or approved-workflow reviewer, not a system identity (Hard Rule: Publisher may not approve itself)
ArchiveHandoffPackage created: f2071fb6-..., manifest=[...]

=== ALL INTEGRATION ASSERTIONS PASSED ===
This is a recommendation only. No action is authorized. Mike decides.
```

## What this proves

1. **Contract compatibility, not just parallel documentation.** Step 2 asserts the Intelligence
   repo's `LibraryCandidate` dataclass and the Library repo's `LibraryCandidate` dataclass have
   the exact same field set, at runtime, then reconstructs one from the other's serialized output
   with zero translation/renaming code. If a future change to either repo drifts the schema, this
   assertion fails loudly.
2. **No automatic Library truth.** The candidate is `PENDING_REVIEW` until an explicit
   `review_candidate(..., approve=True, reviewed_by="Mike Zachary")` call — verified by asserting
   `library.current(...)` returns `None` beforehand.
3. **No fabrication.** `MISSING-ITEM-X` was deliberately included in the recipe's required codes
   without a matching Library object. Publisher's `pull_libraries` correctly reports it in
   `pending_parts` rather than silently dropping it or inventing a placeholder, and it flows
   through to `ReadinessPacket.overall_status = INCOMPLETE` and a real `MissingItemNotice`.
4. **No self-approval.** Publisher attempting to approve its own review package with
   `approver_id="PUBLISHER"` raises `ValueError` and is caught; only `"Mike Zachary"` succeeds.
5. **Archive handoff gating.** The handoff succeeds only after the external approval — this
   script does not attempt (and the Publisher repo does not provide a code path for) creating a
   handoff from an unapproved review.
6. **The Live Library Adapter proves the documented Protocol boundary is real, not aspirational.**
   `LiveLibraryAdapter` in the walkthrough script wraps the actual `dispatch_library.service.
   LibraryService` and satisfies Publisher's `LibraryClient` Protocol with zero adaptation beyond
   an enum/string conversion at the recipe-type boundary — exactly the integration path documented
   in each repo's README.

## Scope note

This script is a build-verification tool, not application code — it is not part of any
department's own test suite or runtime, and it is not mirrored into Dispatch. It lives in
Claude-3 because Claude-3's role is architecture, reconciliation, and build-package control
(`07_DISPATCH_REPO_PLACEMENT_PLAN.md`), which cross-repo integration evidence falls under.
