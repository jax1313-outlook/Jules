# INTELLIGENCE_COMPLETENESS_REVIEW_v1

Program: Dispatch
Status: **Investigation complete. Findings only — no fix applied, no implementation authorized
by this document.**
Origin: Named alongside Publisher/Library/Manager reviews in this session's status confirmation;
sharpened into a concrete task ("start Intelligence completeness review"). Broader in scope than
`INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1` (still unstarted), which asked only about the
`create_inquiry()` approval-posture question — one part of what this review covers.
Rule: No code changes made. Read-only against `jax1313-outlook/Dispatch`
(`dispatch/canonical-reconciliation-integration`) — full read of `portal/models/intelligence.py`
(entire 105-line file), its API routes, templates, tests, and the `reconciliation/` Intelligence
adapter.

---

## 1. What This Review Is

Relative to the tri-department Intelligence contract (`DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`
Sections 3.1-3.6 — Intelligence Finding, Operational Consideration, Special Requirement,
Publisher Requirement's producing side, Library Candidate's originating side, Manager Decision
Support Note), how complete is Dispatch's real `portal/models/intelligence.py`?

## 2. Baseline: What Dispatch's Intelligence Actually Is

A single flat JSON-backed CRUD store, one record shape used for all six `intel_type` categories
(`location, broker, customer, route, position, market`):
```
id, intel_type, subject, content, source, metadata, created_at, updated_at
```
That's the entire schema. No sub-typing, no status machine, no review gate — confirmed by a full
read of the file.

## 3. Findings By Contract Concept — All Six Absent

| Concept | Verdict | Evidence |
|---|---|---|
| Intelligence Finding (3.1) | **Nothing** | Of 17 contract fields, only ~3 have even a loose analog. No `verification_status`, `confidence`, `risk_flags`, `routing_queue`, `is_final_decision`, or `library_truth` — zero hits, repo-wide. |
| Operational Consideration (3.2) | **Nothing** | No substructure of any kind exists — no `impact_area`/`severity`/`consideration_id`. |
| Special Requirement (3.3) | **Nothing** | Same — no `category`/`mandatory`/`requirement_id`. |
| Publisher Requirement, producing side (3.4) | **Nothing** | Zero hits for `requirement_type`/`NEEDS_SOURCE`/`PACKET_COMPONENT` anywhere — confirms the Publisher Completeness Review's finding from the other direction: neither side of this relationship exists. |
| Library Candidate, Intelligence-originated (3.5) | **Nothing** | Intelligence never touches `library.py` in either direction — corroborates the already-established "zero `submitted_by=machine`" finding from a different angle. |
| Manager Decision Support Note (3.6) | **Nothing** | No note/recommendation object exists independent of Manager's non-existence — no `recommendation`/`risk_if_ignored`/`consequence_level`/fixed closing statement. |

This is the most severe completeness gap found across the three department reviews so far —
Publisher and Library each had partial equivalents for some concepts; Intelligence has none.

## 4. Two Contract Requirements Confirmed Unmet

- **"Must always archive" — unmet.** `portal/models/archive.py` never imports or references
  `portal/models/intelligence.py` or any of its record IDs. No Intelligence record is ever
  archived, contract or otherwise.
- **"Manager review before Portal visibility" — unmet, and structurally can't be met as built.**
  `/intelligence` renders every record from `get_all()` directly, with no status/review filter —
  there's no status field to filter on. Every record, automated or manual, is immediately
  visible with no gate.

## 5. Answering the Core Approval-Chain Question With Evidence

`INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1`'s central question was whether anything treats an
Intelligence record as settled fact without review. This review answers it directly:

**On the display side: yes, structurally.** `intelligence.html` renders each record as a plain
fact card — subject, content, source, timestamp — with no verification badge, no "unreviewed"
language, no confidence indicator, because there is no such field to render. It reads exactly
like a settled knowledge-base entry. The reconciliation layer's own translation
(`intelligence_adapter.py`) independently reaches the same conclusion: it maps every intel record
to `status=CURRENT` (not `DRAFT_CANDIDATE`) because there's no unsettled state available to map
to instead, while carefully avoiding claiming human verification
(`source=LEGACY_UNVERIFIED_ORIGIN`, whose own comment says calling it verified "would claim a
fact that is not established").

**On the consumption side: no.** A repo-wide check found zero downstream code paths — Publisher,
Archive, Sandbox, the freight dispatch engine — that read an Intelligence record's content and
act on it as trusted input. The only two consumers are the `/intelligence` page itself and a
home-page record count. So the risk this review can confirm is specifically **a human-facing
display presenting unreviewed content without saying so** — not an automated system silently
treating unverified intelligence as truth for a decision. That distinction matters for scoping
any future fix: a lightweight labeling change addresses the confirmed risk; nothing here shows a
need for a promotion/approval gate the way Library's was.

This should let `INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1` close or narrow substantially — its
question 1 ("does any code path treat an Intelligence record as truth without review?") is now
answered with evidence; question 2 ("are there other automated write call sites?") is also
answered below. Formal closure is Mike's call, not this document's.

## 6. Automated Write Call Sites — Now Exhaustively Confirmed

Exactly two producers exist, confirmed via a repo-wide grep of every `intel_model.` call site:
`create_inquiry()` (automated, hardcoded to `intel_type="broker"`, fires on a specific sandbox
condition) and the manual `/api/intelligence/add` route. A third function,
`intelligence_update()`, exists but has no UI hook anywhere — reachable only by direct API call.
No other producer exists anywhere in `portal/`, `dispatch/`, `cin_lite/`, or `reconciliation/`.
This confirms and closes the "not exhaustively checked" caveat from the earlier, narrower
approval-chain mission's own framing.

## 7. `location` intel_type — Confirmed Automation-Dead

Matches the prior investigation's flag exactly: `"location"` is a defined, UI-reachable
`intel_type` with its own page section, but zero automated call sites anywhere create one — every
`location` record in the system, in tests or in principle through the live app, is
human-entered via the manual "+ Add Record" flow.

## 8. No Field-Mismatch Bug, But One Real Gap

Traced the full `/api/intelligence/add` path — template button → JS → route → model — end to
end. Unlike Publisher's approval button, **field names are consistent at every layer; no
mismatch bug exists here.** The one real gap found: the UI never offers a way to set `source` or
`metadata` when manually adding a record, so every human-entered record has an empty `source`
field in practice — meaning even the weakest, most optional 3.1 analog field is unpopulated for
manual entries too, not just automated ones.

## 9. Test Coverage

Solid for what exists: creation, retrieval, update, type validation, count, the six-type
assertion, the API routes, and the one `create_inquiry()` auto-write test (which only checks the
broker name lands correctly, nothing about review state — consistent with there being no review
state to check). Nothing tests a status/verification/confidence concept, archiving, or automated
`location` production, because none of those exist to test.

## 10. What This Review Does Not Do

Does not build any of the six missing contract concepts, add a review gate, add archiving, or
change the display template to flag unreviewed content. Does not itself close
`INTELLIGENCE_APPROVAL_CHAIN_REVIEW_v1` — provides the evidence that mission needed, closure is
Mike's call.

Mike decides.
