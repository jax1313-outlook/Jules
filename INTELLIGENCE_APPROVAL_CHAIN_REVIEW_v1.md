# INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1

Program: Dispatch
Status: **Future work package — planning only. Not a scoped implementation task.**
Origin: `ARCHIVE_AUTHORITY_AND_OWNERSHIP_REPORT_v1.md` Phase 4, question 4 flagged (not
confirmed) a boundary concern: `portal/routes/api.py::create_inquiry()` writes an Intelligence
record as an unreviewed side effect of a Portal API action — "the same shape of gap the Approval
Chain Safety Gate fixed for Library, just for Intelligence instead." Named/registered at Mike's
direction.
Rule: No code changes authorized by this document. This is a mission definition to scope a
future piece of work, not the work itself.

---

## 1. What This Mission Is

The exact evidence from the prior report:

```python
if entry.get("source_type") == "dispatch" and card.get("broker"):
    intel_model.create_record(
        intel_type="broker",
        subject=card["broker"],
        content=f"Inquiry drafted for load {entry.get('source_id', '')}",
        source=f"auto-contact:{sandbox_id}",
    )
```

(`portal/routes/api.py::create_inquiry()`.) This is a system-generated write into
`portal/models/intelligence.py` — no human reviewed or approved this specific record before it
became a stored Intelligence "product." `portal/models/intelligence.py` has no `status`,
`submitted_by`, or review-gate concept at all (confirmed in the Archive Authority Review's
inventory) — unlike `portal/models/library.py`, which now has exactly this distinction after the
Approval Chain Safety Gate fix.

This mission exists to determine whether Intelligence needs the same human-origin-vs-
machine-origin treatment Library just got, or whether Intelligence's doctrinal role (per the
tri-department build's own contract: Intelligence Findings are explicitly "recommendation only,"
`is_final_decision`/`library_truth` fixed False, never promoted to truth without a separate
review step) means a lighter touch is correct here — auto-generated Intelligence notes may be
fine to exist unreviewed *as recommendations*, in a way an auto-approved Library *fact* is not.

## 2. Why This Is Not Simply "Apply The Same Fix Again"

The Library gap and this one look similar on the surface (system writes data with no review) but
may not warrant the same fix, and treating them as identical without checking would be a
mistake in the other direction — over-applying a gate where the doctrine doesn't call for one:

- Library records are `status="approved"` — the word itself asserts truth. A system silently
  asserting truth is the exact forbidden pattern (Hard Conflict List item 1, now closed).
- Intelligence records in `portal/models/intelligence.py` carry no `status` field at all — they
  are not asserted as "approved" or as truth of any kind, just stored notes. Per the
  tri-department build's own `IntelligenceFinding` contract, Intelligence output is *supposed to*
  be unreviewed-by-default and only becomes truth via a separate Library-candidate promotion path
  — so an unreviewed Intelligence note may be doctrinally correct as-is, not a gap.

The real question this mission needs to answer is which of these two readings is right, not
assume the Library fix template applies unchanged.

## 3. Scope Questions This Mission Needs To Resolve

1. Does any code path treat a `portal/models/intelligence.py` record as truth/fact without
   further review (e.g., does anything read Intelligence records and present them to Mike as
   settled fact, rather than as a note/recommendation)? This determines whether the Library-style
   gate is actually needed here.
2. Are there other automated Intelligence-write call sites beyond `create_inquiry()`'s single
   confirmed one? (Not exhaustively checked in the Archive Authority Review — that pass found
   this one site and the generic human-facing `/api/intelligence/add` route, not a full trace of
   every possible producer.)
3. If a review gate is warranted: should it mirror Library's `submitted_by`/`review_candidate()`
   pattern exactly, or does Intelligence's "recommendation, not truth" doctrinal role call for a
   lighter marker (e.g. a `source_type: "system_generated"` tag with no promotion gate at all,
   just honest labeling)?
4. Does the tri-department build's own Intelligence repo (`l2-intelligence-agent.`) already model
   this distinction in a way Dispatch's `portal/models/intelligence.py` could adopt directly,
   given that repo's `IntelligenceFinding.is_final_decision`/`library_truth` pattern was purpose-
   built for exactly this question?

## 4. What This Mission Should Produce

A determination (with evidence, not assumption) of whether this is a real gap or doctrinally
acceptable behavior, and — only if a gap is confirmed — a scoped recommendation, informed by
question 4's comparison to the tri-department Intelligence repo's existing pattern.

## 5. What This Mission Is Not

Not an automatic re-run of the Library fix. Not a re-opening of the Archive Consolidation
question. Scoped specifically to this one call site and the doctrinal question it raises about
Intelligence's review posture, not a general Intelligence-department audit.

Mike decides.
