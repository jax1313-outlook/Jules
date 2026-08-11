# DISPATCH_STAGE12_MANAGER_M7_POLICY_HOOK_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 12 Build Design — Phase M7 (Policy Routing Hook Candidate)
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 and the same discipline every prior build in this plan has followed — held especially firmly here given what this phase touches.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Approve Stage 12 build for M7." Governed by `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §18 (Manager Policy Engine Relationship) and §20's Phase M7 definition.

---

## 0. What This Document Does Not Do — Read This Section First

The original Manager mission's hard constraints, restated verbatim because they apply directly here: *"Do not design GX. Do not implement GX... Do not allow autonomous approval. Do not allow autonomous booking. Do not allow autonomous government submission. Do not allow autonomous contract commitment. Do not allow AI approval of truth, facts, packets, rates, compliance, or final documents... Mike decides."*

`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §18 is equally direct: *"This mission is explicit: do not design GX, do not implement GX. This section only describes how Manager's existing doctrine could later support a policy-routing layer, without building one."* And §20's own Phase M7 row: *"this phase should not proceed past design without Mike explicitly deciding he wants a policy engine at all."*

Mike's "Approve Stage 12 build for M7" is that explicit decision — but it authorizes exactly what M7 was ever defined to be: **"Define (not build) the interface shape a future policy engine could consume... documentation only, possibly a narrow read-only API surface if Mike wants one."** It does not authorize a policy engine, does not authorize anything that acts on Manager's output, and does not authorize anything that removes Mike from any decision loop. This design holds that line explicitly, not by omission.

## 1. What Gets Built: A Read-Only Reporting Surface, Nothing That Acts

Doctrine's own reasoning (§18): *"the natural seam is that Manager's Auto-log category is the only place such a thing could ever act without a person in the loop, because Auto-log is already defined as 'routine, expected, low-risk' with no card and no decision attached."* This design takes that seam literally and narrowly: the only thing exposed is a **count** of Auto-log-classified signals — nothing that requires human review, nothing with a card, nothing a future system could act on beyond acknowledging "N routine things happened, none of them needed anyone's attention."

**Concretely, "Auto-log" here means card_level 0** — `classify.ROUTINE` and `classify.NOISE` specifically. Not `Status` (card_level 1) — Status is still "awareness only" per `MANAGER.md` §9, a tier a human is still meant to eventually see, not something doctrine ever named as action-eligible for a future automated system. Excluding it is a deliberate, narrower reading of §18 than the literal words might allow, chosen because narrower is the safer direction to err on here.

## 2. Design

- **New module: `dispatch/manager/policy_candidates.py`.** One function, `auto_log_summary()`, which calls the existing, unmodified `staff_report.generate_staff_report()` and filters its already-computed `counts` dict down to just the `Routine`/`Noise` keys. Returns `{"auto_log_counts": {...}, "note": "Counts only. No individual signal detail is exposed or retained. Nothing here is actionable without further Mike-approved work; this is a Phase M7 candidate interface, not a working policy engine."}`.
- **`staff_report.py` is not modified.** `generate_staff_report()` already computes everything needed; this reuses its existing return value, the same pattern every prior signal-source addition has followed.
- **New route: `GET /api/manager/policy-candidates`.** Read-only, ungated (matching `/manager`'s own boundary — this exposes strictly less detail than `/manager` already shows publicly: aggregate counts of the *lowest-risk* classification tier only, no individual record data). Returns `auto_log_summary()` as JSON. No POST, no write, no parameters.
- **Nothing consumes this endpoint.** No scheduled job, no automation, no other part of this codebase calls it. It exists so a future, separately-designed, separately-approved system *could* read it — this build creates the interface shape, not a consumer of it. If Mike later wants an actual policy engine built against this interface, that is a distinct future mission requiring its own full design, explicitly outside this document's scope (per the hard constraint restated in §0).

## 3. Files In Scope

| File | Action | Purpose |
|---|---|---|
| `dispatch/manager/policy_candidates.py` | New | `auto_log_summary()` — reads `generate_staff_report()`'s existing output, filters to Auto-log-tier counts only |
| `portal/routes/manager.py` | Modify | New `GET /api/manager/policy-candidates` route (or a new tiny blueprint, if keeping `portal/routes/manager.py` focused on the page route is preferred — flagged, not decided, see Open Questions) |
| `tests/test_manager_foundation.py` | Modify | New tests — see §4 |

No file under `dispatch/spine/`, `dispatch/security/`, or any existing signal source is touched.

## 4. Test Plan

- `auto_log_summary()` returns only `Routine`/`Noise` counts, never `Status`, `Review Needed`, `Decision Needed`, `Conflict`, or `Archive` — even when signals of every classification are present simultaneously.
- No individual record data (load IDs, exception IDs, etc.) appears anywhere in the response — counts only, structurally verified.
- `GET /api/manager/policy-candidates` is GET-only (matching `/manager`'s own structural guard pattern).
- Structural guard: `policy_candidates.py` contains no call to any write, approval, booking, or submission function anywhere in the codebase — the same category of guard every prior Manager module has carried, here doing the most work of any of them given what this phase touches.
- Full regression suite re-run clean.

## 5. Open Questions For Mike

1. Should `GET /api/manager/policy-candidates` live in `portal/routes/manager.py` (the existing Manager blueprint) or does Mike want it kept in a clearly separate, easy-to-audit file given its sensitivity? Recommended default: keep it in `portal/routes/manager.py` for now — one blueprint, consistent with how every other Manager route lives together, and it's a three-line read-only route with nothing to hide.
2. Is exposing only Auto-log (`Routine`/`Noise`) counts sufficient, or does Mike want this interface to also describe (not expose data for, just describe in the `note` field) which other classifications exist and remain permanently out of scope for any future automated action? Recommended default: keep the response minimal — the existing `/manager` page and `MANAGER.md` itself already document the full taxonomy; this endpoint doesn't need to re-explain it.

## 6. Walkthrough Requirements

Required, live, matching every prior build's convention:
1. Seed a mix of signals spanning several classifications (at minimum one Auto-log-tier signal and one Review-Needed-or-above signal).
2. Confirm `GET /api/manager/policy-candidates` returns only the Auto-log-tier count, with no individual record data and no higher-tier classification counts.
3. Confirm `/manager` itself is completely unaffected (same cards, same summary, same behavior as before this build).
4. Full regression suite re-run clean.

## 7. Stop/Go

Go once the structural guards prove this module and route carry zero write/action/approval capability, the live walkthrough confirms the response is limited to Auto-log-tier counts only, and full regression is clean. **This design does not authorize, and no future work under its name may authorize, anything that acts on this data without a separate, explicit, full design-and-approval cycle of its own — the same discipline applied to every other governed capability in this codebase.**

Mike decides.

---

*End of DISPATCH_STAGE12_MANAGER_M7_POLICY_HOOK_DESIGN_v1.md.*
