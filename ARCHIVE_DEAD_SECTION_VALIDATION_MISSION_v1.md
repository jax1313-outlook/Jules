# ARCHIVE_DEAD_SECTION_VALIDATION_MISSION_v1

Program: Dispatch
Status: **Future work package — planning only. Not a scoped implementation task.**
Origin: The "Archive Schema Cleanup" future mission named in `ARCHIVE_AUTHORITY_AND_OWNERSHIP_
REPORT_v1.md`'s Option A Decision Record (Maintain Separation, accepted). Named/registered at
Mike's direction.
Rule: No code changes authorized by this document. No file deletion. No schema changes. This is
a mission definition, not the work itself.

---

## 1. What This Mission Is

`ARCHIVE_AUTHORITY_AND_OWNERSHIP_REPORT_v1.md` Phase 1 found that `portal/models/archive.py`'s
`location_history` and `broker_history` sections are defined in `ARCHIVE_SECTIONS`/
`SECTION_LABELS`, rendered on the `/archive` page, but have **zero** confirmed producers anywhere
in the codebase — no human route, no automated call site. The same report flagged
`intelligence.py`'s `location` intel_type as similarly unproduced, and Route Intelligence
ownership as "ambiguous — no clear single owner."

This mission exists to **validate** those "dead" findings rigorously (a single grep pass is not
sufficient grounds for a deletion recommendation) and then decide what happens to each: implement
a real producer, remove the unused section, or leave it as documented-but-inactive.

## 2. Why Validation Before Action

The original report was explicit about its own limits: "route specifically deserves a second,
dedicated grep pass before this is treated as fully settled." A "no producer found" claim
deserves a higher bar before anything gets removed — sections could be:

- Populated by a caller this investigation didn't check (e.g. dynamically constructed section
  names, a code path in `portal/routes/dispatch_api.py`'s ~81KB file not read in full, or a
  script/cron job outside the Flask app entirely).
- Intentionally reserved for a near-term feature not yet wired up.
- Genuinely dead and safe to remove or leave empty.

Recommending deletion off a single grep pass would be exactly the kind of unverified claim this
program's own doctrine (No Fabrication Rule, applied reflexively to prior investigation output)
warns against treating as settled.

## 3. Scope Questions This Mission Needs To Resolve

1. Is there truly no producer for `location_history`/`broker_history` (`portal/models/
   archive.py`) and `location` (`portal/models/intelligence.py`), including indirect/dynamic
   construction, background jobs, and the unread portions of `portal/routes/dispatch_api.py`?
2. Is there a plausible near-term feature these sections were reserved for (check commit history/
   `DECISION_LOG.md` at the Dispatch repo root, not investigated this pass)?
3. For each confirmed-dead item: implement, remove from schema, or leave defined-but-hidden from
   the `/archive` page view (a presentation-only change, per the earlier report's Phase 5 finding
   that hiding empty sections improves usability without touching storage)?
4. Does Route Intelligence need a new owner (a new Library section? A new Intelligence type?), or
   is "no current implementation" an acceptable state for now?

## 4. What This Mission Should Produce

A validation pass with real evidence (commit history check, full read of the previously-unread
portions of `portal/routes/dispatch_api.py`, confirmation search across background jobs/scripts)
followed by a specific, small, Mike-approved recommendation per item — likely small enough to not
need its own dedicated branch, but that's a call for when this mission actually starts.

## 5. What This Mission Is Not

Not a re-opening of the Archive Consolidation question (deferred indefinitely, per the accepted
Option A decision) and not an excuse to touch `cin_lite/archive.py` or `dispatch/store.py`, which
this report found have no relationship to the dead-section question.

Mike decides.
