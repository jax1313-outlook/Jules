# STAGE_1_INTELLIGENCE_LIBRARY_PUBLISHER_LINK_SCOPE_v1

Program: Dispatch
Status: **IMPLEMENTED.** Scope approved and executed on `dispatch/canonical-reconciliation-
integration` (commit `d77cbae`), exactly as scoped below — no deviation. Full Dispatch suite
re-verified green.
Origin: Stage 1 of the locked-in end-to-end deployment plan.
Rule: No code changes authorized by this document. Do not implement until scope is approved.

---

## 1. What existing Intelligence record can produce a Library candidate?

Scope narrowly to `intel_type="broker"` records, not all six types. Reasoning: `create_inquiry()`
(`portal/routes/api.py:186-191`) is the only real automated Intelligence producer in the entire
codebase (confirmed exhaustively in `INTELLIGENCE_COMPLETENESS_REVIEW_v1`), and it already writes
`intel_type="broker"`. Library's existing `SECTIONS` already include `"broker"` as one of its six
sections. Piloting promotion on an already-flowing, already-matched type avoids inventing a
trigger for a type (like `"location"`, confirmed automation-dead) that has no real producer to
promote from. Other five types stay out of Stage 1's scope entirely.

## 2. What minimum fields are required for meaningful promotion?

`library.add_record()` needs `section`, `name`, `content`, `metadata`, `submitted_by`. Direct
mapping: intelligence `subject` → `name`, `content` → `content`. Two fields the Library
Completeness Review found entirely absent — `source_finding_id`, `source_type` — should be
captured **at the promotion function's call site**, not by expanding Intelligence's own schema
(expanding Intelligence's schema is explicitly out of scope per the "don't attempt the full
Intelligence contract" constraint). Minimum: `source_finding_id = <intelligence record's own
id>`, `source_type = "INTELLIGENCE"` (fixed), passed as `metadata` fields on the created Library
record, since `add_record()` already accepts an open `metadata` dict — no schema change to
`library.py` needed either.

## 3. Does Intelligence need a minimal verification_status or confidence field before promotion?

**Not required for Stage 1.** Library's own `review_candidate()` gate is what governs whether a
promoted record becomes truth — Intelligence's internal state doesn't need to carry that
information for the mechanical promotion function to work correctly. Adding it would also cross
into "attempt the full Intelligence contract," explicitly out of scope. Flagged, not decided: the
Intelligence Completeness Review already identified this as worth doing on its own merits (closes
a real display-layer risk), and `INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1` covers it — but it's a
separate, optional bundle, not a Stage 1 dependency. Recommend leaving it out of Stage 1 and
letting that separate mission decide it on its own timeline.

## 4. What should the Library candidate receive?

From the source Intelligence record: `name` (from `subject`), `content` (from `content`),
`section="broker"` (fixed, matching Q1's scope), `submitted_by="machine"` (existing parameter,
unchanged), plus the two provenance fields from Q2 in `metadata`. No new Library schema fields —
everything fits inside `add_record()`'s existing signature.

## 5. What Library approval event should trigger Publisher?

The success path of `review_candidate(approve=True, ...)` — specifically the branch where status
flips to `"approved"` (`portal/models/library.py:155-158`). A new trigger call added at the end of
that function (or immediately after it, at the `/api/library/review` route level) fires only on
approval, never on rejection.

## 6. What minimum Publisher requirement object is needed?

**None — reuse the existing `publisher.create_action()` function as-is.** Building a real
`PublisherRequirement` dataclass (confirmed fully absent by the Publisher Completeness Review) is
explicitly out of scope ("don't fully rebuild Publisher"). Stage 1's minimal "Publisher
requirement" is simply a `create_action()` call triggered by the approval event in Q5 — matching
what `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md`'s Link 3 already scoped: "needs a new
post-approval trigger... calls `publisher.create_action()`." A real `PublisherRequirement` object
stays deferred to a future, dedicated Publisher stage.

## 7. What test proves the full path works?

One integration test walking the whole chain: create a `broker`-type intelligence record → call
the new promotion function → assert a `pending_review` Library record exists with the correct
`section`/`name`/`content`/provenance `metadata` → call `review_candidate(approve=True,
reviewed_by=<non-reserved identity>)` → assert status flips to `approved` → assert a new
Publisher action now exists in the queue, referencing back to the originating candidate (e.g. via
`trigger_reason`). Plus targeted unit tests for the two new functions individually (promotion,
approval-trigger), mirroring this program's existing test style (e.g.
`test_publisher_cannot_archive_without_approval`).

## 8. What UI/Portal changes are required, if any?

**None — Stage 1 stays API/model-level only.** The Library Completeness Review already found no
review/approve UI exists on `/library` at all (self-acknowledged dormant route, not a bug). Stage
1 doesn't authorize building that UI. Worth flagging explicitly: Stage 1 will make that existing
gap newly consequential rather than theoretical, since real `pending_review` records will finally
exist and be visible on `/library` (status badge only) with no way for a human to act on them
through the page — the same gap the Library review already documented, just no longer
hypothetical. Not fixed here; noted for whoever picks up the Library review UI next.

## Summary: What Stage 1 Actually Builds

Two small functions plus their tests, nothing else:
1. `intelligence.promote_to_candidate(record_id)` (or equivalent) — reads a `broker`-type
   Intelligence record, calls `library.add_record()` with the mapping from Q2/Q4.
2. A post-approval hook on `review_candidate()`'s success path — calls
   `publisher.create_action()` per Q5/Q6.

No schema changes to `portal/models/intelligence.py`. No schema changes to
`portal/models/library.py` beyond using its existing `metadata` field. No new
`PublisherRequirement` object. No UI changes. No sixth Intelligence type. No vendoring.

Mike decides.
