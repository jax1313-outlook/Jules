# STAGE_2_PUBLISHER_PROPOSAL_WRITER_BRIDGE_SCOPE_v1

Program: Dispatch
Status: **Scoping complete. Answers the eight required questions with evidence already on
record — no new code investigation needed, no implementation authorized. Awaiting scope
approval per `DISPATCH_END_TO_END_DEPLOYMENT_PLAN_v1.md`.**
Origin: Stage 2 of the locked-in end-to-end deployment plan.
Rule: No code changes authorized by this document. Do not implement until scope is approved.

---

## 0. A Finding That Changes The Shape Of This Scope — Read Before The Eight Questions

Question 1 ("what Publisher `action_type`(s) should be eligible to trigger a proposal draft?")
cannot be answered by simply picking from Publisher's existing 8 `ACTION_TYPES`, because **none
of them share subject matter with what `proposal_writer.py` actually drafts.**

Publisher's action types (`Broker Packet Required`, `Direct Shipper Packet Required`, `Rate
Sheet Request`, `Rate Confirmation Package Required`, `DocuSign Package Ready`, `Arrival Notice
Draft`, `POD/BOL Document Package Draft`, `Detention Evidence Draft`) are all freight-dispatch
documents — broker relationships, rate confirmations, delivery paperwork. `cin_lite`'s
`proposal_writer.draft_outline()` drafts federal contracting bid/no-bid proposal outlines (per
its own volume/section structure) for GovCon opportunities acquired via `cin_lite`'s SAM.gov
pipeline — an entirely different business domain. There is no existing Publisher action type
that a GovCon proposal outline would sensibly attach to, and no evidence anywhere in the
codebase that this was ever meant to be a literal one-to-one wire-up.

This means the honest scope of "connect Publisher to `cin_lite` proposal-writing capability" is
not "pick one of Publisher's 8 action types and call `draft_outline()` from it" — that would
produce nonsensical output (a GovCon compliance outline attached to a broker rate-confirmation
packet). The real open question, which only Mike can resolve, is which of two genuinely different
things this mission means:

- **(a) Reuse `proposal_writer.py`'s outline-assembly *mechanism*** (its section/volume template
  structure) as generic content-drafting infrastructure Publisher could apply to its own,
  freight-domain documents — treating `draft_outline()`'s pattern as reusable scaffolding, not
  its GovCon-specific content.
- **(b) Give Publisher a genuinely new action type** for GovCon-adjacent packaging work (which
  doesn't exist in `ACTION_TYPES` today), so the bridge connects real GovCon proposal work to
  Publisher's governance layer, leaving Publisher's 8 freight action types untouched and
  unbridged.

The eight questions below are answered on the assumption that **(b)** is the intended reading —
it matches the canonical matrix's original "Hybrid" framing more literally (tri-department
Publisher governs Publisher-shaped work; `cin_lite` drafts what it already drafts) and requires
no reinterpretation of `proposal_writer.py`'s purpose. If Mike intends (a) instead, this scope
would need to be redone around a template-reuse design, not a new-action-type design. This
substitution is flagged, not assumed silently.

## 1. What Publisher `action_type`(s) should be eligible?

Per the reading above: **a new, ninth action type**, e.g. `"GovCon Proposal Draft Required"`,
added to `ACTION_TYPES` — not repurposing any of the existing 8. This keeps the freight domain
and the GovCon domain cleanly separated inside the same queue, consistent with "clear
boundaries."

## 2. What minimum identifier bridge is needed?

A new field on the Publisher action record, `contract_id`, set at creation time from the
`cin_lite` contract this action concerns. Not a general identifier-unification (explicitly out
of scope) — just enough for this one action type to reference its `cin_lite` counterpart.
`sandbox_id` stays required and unrelated (Publisher's existing freight-opportunity linkage is
untouched); a GovCon-triggered action would need its own creation path that doesn't originate
from a `sandbox_id`, mirroring the "LIBRARY-" marker convention Stage 1 established for
non-sandbox-originated actions (e.g. `sandbox_id=f"GOVCON-{contract_id}"`).

## 3. What triggers the draft?

A new function, e.g. `publisher.request_proposal_draft(contract_id, ...)`, called from wherever
a human or `cin_lite` process decides a GovCon opportunity needs Publisher-tracked packaging —
not an automatic side effect of any existing transition. This creates the new action type at
`PENDING`, then a human-initiated "Generate Draft" step (mirroring the existing
`PENDING→DRAFT` button pattern) calls `proposal_writer.draft_outline()` and stores the result.

## 4. Does drafted content flow back into Publisher's queue, or stay in `cin_lite`?

**Stays in `cin_lite`, referenced by ID.** Storing the full outline text inside
`portal/models/publisher.py`'s JSON store would duplicate data across two systems with no
single source of truth — the same duplication problem Archive's Option A decision already
rejected for a different pair of systems. Publisher's action record holds only a reference
(e.g. `proposal_reference_id` returned by whatever `cin_lite` storage step runs), not the
content itself.

## 5. What approval discipline applies?

**Publisher's existing `approved_by` gate, extended to cover this new action type — not
`cin_lite`'s token-based approval.** This action lives in Publisher's queue and should follow
Publisher's governance uniformly across all 9 action types, rather than introducing a second
approval mechanism for just one of them. `cin_lite`'s HMAC-token flow stays exactly as-is for
its own, separate email-decision path — this bridge doesn't touch or replace it, it adds a
second, independent path to reach the same drafting function.

## 6. Where does approved content get archived, given Option A?

`cin_lite/archive.py` — Option A already declared it the canonical archive engine, and this
mission's own "do not reopen Archive consolidation" constraint forecloses migrating drafted
content into `portal/models/archive.py`. If Portal-side visibility is wanted, that's a read,
not a write — `reconciliation/adapters/archive_adapter.py`-style translation for display,
never a second copy of the content.

## 7. What test proves the full path works?

An integration test: create a GovCon-flavored Publisher action with a `contract_id` → call the
new draft-request function → assert a `proposal_reference_id` is stored on the action → attempt
`APPROVED` without `approved_by` (fails, matching the existing Publisher gate) → approve with a
valid identity → assert the archived content is reachable via `cin_lite/archive.py` using the
stored reference. Plus unit tests for the new action type's manifest (if any) and the
identifier-bridge field.

## 8. What UI/Portal changes are required?

Minimum: `publisher.html` needs to render the new action type like the existing 8 (already
generic per-type rendering, per the Publisher Completeness Review's finding that the template
iterates action types uniformly) — no new template needed, just the new `ACTION_TYPES` entry
and a rendering line for `contract_id`/`proposal_reference_id` alongside the existing
`sandbox_id` display. No new page. Matches Stage 1's choice to stay minimal on UI.

## What This Scope Does Not Resolve

Whether reading (a) or (b) from Section 0 is actually what Mike intends. Everything above is
scoped under reading (b); if (a) is intended, this document should not be treated as Stage 2's
final scope — say so and this gets rescoped around template reuse instead.

Mike decides.
