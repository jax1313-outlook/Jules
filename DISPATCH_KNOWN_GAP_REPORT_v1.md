# DISPATCH_KNOWN_GAP_REPORT_v1.md

Program: Dispatch
Status: Final Build Package — Known Gap Report
Deliverable: Known Gap Report (required final deliverable #6)
Date: 2026-08-11

---

## 1. Missing Source Material (Build Command Section 3)

None of the following were found in any repo in scope during this build. No content from these
documents was invented; where a structural scaffold was still needed, it is explicitly labeled
`SCAFFOLD — PENDING REAL SOURCE` in the relevant repo.

| Missing document | Affects | Where flagged |
|---|---|---|
| `DISPATCH_FINAL_BLUEPRINT_v1.md` | Program-wide | `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` §1 |
| `LIBRARY_INGESTION_RULE.md` | Library ingestion mechanics | Library `KNOWN_GAPS.md`; ingestion behavior instead derived directly from Constitution §7.4 + System Relationship Matrix Hard Rules |
| Library Department Core Object Model | Library schema | Library `docs/OBJECT_MODEL.md` |
| Operational Memory Systems in Organizations | Reference only | Not required for schema correctness |
| `publisher_recipes.json` | Recipe content | Library `docs/OBJECT_MODEL.md`, Publisher `KNOWN_GAPS.md` — recipe *types* are doctrine-named, required-item *content* is scaffold |
| Publisher MVP prototype / `publisher_mvp.py` | Publisher drafting patterns | Publisher `KNOWN_GAPS.md` |
| Publisher templates, Publisher Constitution Package, Legacy Publisher Emails 1-5 | Document content generation | Publisher `KNOWN_GAPS.md` |
| `Visibility_SOP.docx` | Visibility Package M1 content | Publisher `KNOWN_GAPS.md` — M1 scaffold only |
| `quality_control_statement.md`, `submission_email_template.md`, `technical_narrative_template.md` | Publisher content | Publisher `KNOWN_GAPS.md` |

None of these gaps block integration-ready status: they gate specific *content*, not the
*architecture* the build was scoped to deliver.

## 2. Architectural Gaps (by design, not oversight)

These are deliberate scope boundaries, not defects:

1. **No persistence layer in any repo.** All three departments' storage (`IntelligenceStore`,
   `ObjectRegistry`/`CandidateQueue`, and Publisher's stateless service functions) are in-process
   reference implementations. A Dispatch Spine-backed persistence layer is a separate build
   (Constitution §21 requires an approved Spine Specification before implementation) and each
   repo's service-surface boundary is exactly what such a layer would need to implement.
2. **No Archive department implementation.** Archive is Phase 4 of the System Relationship
   Matrix's Build Order Matrix and out of scope for this mission. Every repo tracks what it would
   need to hand to Archive (e.g. `is_archive_required`, `ArchiveHandoffPackage`) without an actual
   Archive to receive it.
3. **No Manager/Portal card generation.** Manager and Portal own card/work-item creation per
   System Relationship Matrix Section 3; none of the three built repos create Portal cards or
   Spine work items directly. Their outputs (Findings, Decision Support Notes, Review Packages,
   Missing Item Notices) are structured and ready for Manager to surface, but that wiring is a
   separate build.
4. **No Security department implementation.** Out of scope; the `Security` collection exists in
   Library's taxonomy as a placeholder per Build Command Section 4.2.
5. **No Publisher content-drafting layer.** Publisher's governed *assembly and approval-gate*
   machinery (request → workspace → readiness → inventory → review → approval → handoff) is
   complete and tested, but actual document/packet prose generation (cover letters, technical
   narratives, government form field values) requires the missing templates/prototype source
   listed in Section 1 above, plus a Mike-approved drafting-content policy.
6. **No Publisher-side Library Candidate nomination convenience wrapper.** The Library repo's
   candidate workflow accepts `SubmittedBy.PUBLISHER` and would work today if Publisher called it
   directly with matching field values; a `service.nominate_library_candidate()` wrapper in the
   Publisher repo is a small, deliberately deferred follow-up (see Publisher `KNOWN_GAPS.md`).
7. **Verification status ceiling.** Intelligence never assigns `VerificationStatus.VERIFIED` —
   only `PARTIALLY_VERIFIED` or `UNVERIFIED` — because true verification requires cross-source
   corroboration (a second Library or Archive reference) that this build's Intelligence-Library
   integration does not yet perform automatically. This is a conservative default per
   `INTELLIGENCE_VERIFICATION_WORKFLOW.md` Section 3.1, not a defect.

## 3. What Would Be Needed Before Dispatch Merge Candidacy

Per the Repo Placement Plan's promotion flow, after this build's "Claude Code review" stage:

- Independent human (Mike) review of all three repos' diffs and this build package.
- A decision on whether to stage in Hold/Test-Grounds before further promotion.
- Resolution (or explicit acceptance) of the architectural gaps in Section 2 — particularly the
  persistence layer, since no department can run continuously without one.
- The missing source material in Section 1, if Publisher's content-drafting layer is to be built
  next.

None of this is authorized or attempted by this build. Mike decides.
