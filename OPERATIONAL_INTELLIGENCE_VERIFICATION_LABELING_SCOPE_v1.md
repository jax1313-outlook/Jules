# OPERATIONAL_INTELLIGENCE_VERIFICATION_LABELING_SCOPE_v1

Program: Dispatch
Status: **Scope only. Not yet approved for implementation.**
Origin: `INTELLIGENCE_COMPLETENESS_REVIEW_v1.md` found all six Intelligence contract concepts
absent from `jax1313-outlook/Dispatch`'s real code — the most severe gap of any department
reviewed this session. `DISPATCH_TRI_DEPARTMENT_MATRIX_BUILD_RECONCILIATION_v1.md` then found a
separate, well-built, tested candidate implementation of the full contract, but Mike decided
against adopting or integrating it — this scopes a narrow build directly against Dispatch's real
code instead, the original plan, consistent with Stage 1/Stage 2's own precedent. The candidate
build informs field naming below (for future compatibility, in case a fuller build is ever
approved) but nothing from it is adopted, copied, or depended on.
Rule: No code changes authorized by this document. Do not implement until scope is approved,
matching every prior stage this session.

---

## 0. Why This Slice, Not The Other Five Contract Concepts

Attempting the full six-concept Intelligence contract in one pass would repeat the exact mistake
already corrected for with Publisher and Library (both completeness reviews explicitly warned
against "attempt the full contract" overreach). `INTELLIGENCE_COMPLETENESS_REVIEW_v1.md` Section 5
already did the narrowing work: it traced the *specific, confirmed* risk from Intelligence's
current gap — not a hypothetical one — and named the fix directly: **"a lightweight labeling
change addresses the confirmed risk; nothing here shows a need for a promotion/approval gate the
way Library's was."** That review found zero downstream code paths treat Intelligence content as
trusted input for a decision; the only real, evidenced risk is **display-side**: `intelligence.html`
renders every record as a plain fact card, with no field to indicate it might be unverified,
because no such field exists. This scope closes exactly that gap. `Operational Consideration`,
`Special Requirement`, the Intelligence-producing side of `Publisher Requirement`, the
Intelligence-originating side of `Library Candidate`, and `Manager Decision Support Note` all stay
out of scope — not silently dropped, named here as deferred.

## 1. What field, exactly?

One new field: `verification_status`, three values — `UNVERIFIED` (default), `PARTIALLY_VERIFIED`,
`VERIFIED` — naming chosen to match `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` §3.1's own enum for
future compatibility, in case a fuller Intelligence build is ever separately approved. No other
field from the contract (`confidence`, `risk_flags`, `routing_queue`, `is_final_decision`,
`library_truth`, etc.) is added — those are part of the deferred concepts, not this slice.

## 2. What sets it, and when?

**Always defaults to `UNVERIFIED` at creation — automated or manual, no exception.** This is a
deliberate choice, not an oversight: the confirmed risk is specifically that content *reads as*
settled without saying so; letting a human self-certify `VERIFIED` at the moment of creation would
reopen exactly that risk in a different form. Matches the candidate build's own design choice
(`VerificationStatus.VERIFIED` is never assigned by its pipeline either) and the real contract's
"None to create" approval requirement — informative precedent, not a dependency.

**Changed only via the existing `/api/intelligence/update` route** (`portal/routes/api.py:360-361`,
`intel_model.update_record()`) — already exists, already reachable, just needs one new optional
parameter. No new gate, no new approval machinery, per the Completeness Review's own finding that
none is needed here. Reuse Before Create.

## 3. What happens to existing records that predate this field?

Read-time default, not a migration script: `record.get("verification_status", "UNVERIFIED")`
wherever the field is displayed or consumed. A missing field reads as unverified, never silently
as verified — matches the No-Fabrication posture the rest of this build follows.

## 4. Display change

`intelligence.html` gets one small badge per record showing its `verification_status` — plain
text/color distinction (e.g. muted for `UNVERIFIED`, a stronger visual treatment for `VERIFIED`),
matching this codebase's existing status-pill pattern already used elsewhere (Publisher, Library).
No new page, no new section — one addition to the existing per-record card markup.

## 5. UI for changing it — flagged, not built, matching Stage 1's own precedent

No button or form is added to actually call the update route from the UI in this scope. Stage 1
left exactly this kind of gap flagged rather than fixed for Library's review path ("Stage 1 will
make that existing gap newly consequential rather than theoretical... not fixed here"); this scope
follows the same precedent. The route exists and is reachable directly; a UI control for it is a
natural, small follow-up, not built here to keep this slice minimal.

## 6. Part B (separable): Archive requirement

`INTELLIGENCE_COMPLETENESS_REVIEW_v1.md` Section 4 found a second, independent unmet contract
requirement: Intelligence records are never archived — `portal/models/archive.py` never
references `intelligence.py` in either direction. This is mechanically simple to close (reuse
`archive.py`'s existing add pattern, same as every other department already does) and low-risk,
but it's a genuinely separate concern from the verification-labeling fix above — approvable
independently. Proposed: on `create_record()`, also write a minimal archive reference entry
(record ID, type, timestamp), mirroring how other departments' creation paths already touch
Archive. No change to `verification_status` behavior either way.

## 7. What test proves this works?

1. A newly created record (any `intel_type`, any origin) has `verification_status="UNVERIFIED"`.
2. A record loaded from storage that predates this field reads as `"UNVERIFIED"`, not `None` or an
   error.
3. `update_record()` with a `verification_status` argument changes it; without the argument,
   leaves it unchanged (matches existing `content`/`metadata` optional-arg behavior).
4. `intelligence.html`'s real rendered HTML contains the correct badge text for each of the three
   values, tested via a real Flask test client request (not just a template unit test), matching
   this session's Track D discipline of verifying real HTTP behavior, not just isolated tests.
5. (If Part B approved) creating a record produces a corresponding Archive entry, referencing the
   Intelligence record's real ID.

## Summary: What This Scope Actually Builds

**Part A (verification labeling)**:
1. One new field, `verification_status`, defaulting to `UNVERIFIED`, read-time-defaulted for
   legacy records.
2. One new optional parameter on the existing `update_record()`/`/api/intelligence/update` path.
3. One small display badge on `intelligence.html`.

**Part B (archive requirement), separable, Mike may approve independently**:
4. A minimal Archive reference entry written on Intelligence record creation.

**Explicitly not built here, and not abandoned**: `Operational Consideration`, `Special
Requirement`, `Publisher Requirement` (Intelligence-producing side), `Library Candidate`
(Intelligence-originating side), `Manager Decision Support Note`, any automated promotion to
`VERIFIED`, and a UI control for the update path. Each is its own future scope if pursued —
`DISPATCH_TRI_DEPARTMENT_MATRIX_BUILD_RECONCILIATION_v1.md` remains the reference point for what a
fuller build could look like, should Mike revisit that decision later.

Mike decides.
