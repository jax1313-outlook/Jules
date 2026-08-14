# DISPATCH_INTELLIGENCE_FINAL_INTEGRATION_LAUNCH_PACKAGE_v1

Program: Dispatch
Status: **Proposal. Awaiting Mike's approval before implementation** — matching the launch-
package discipline used for every prior IFTA phase (`DECISION_LOG.md`).
Origin: `DISPATCH_DEPLOYMENT_CRITICAL_PATH_v1.md`'s reframe — Dispatch is complete when a real
load runs end-to-end; Intelligence, Library integration, and Publisher integration are named
deployment-critical. This package designs that work against the real existing ecosystem, per
Mike's four required context categories, rather than against the abstract six-concept contract
in isolation (the mistake the tri-department reconciliation caught last time).

---

## 1. Governance Context

- Manager stays fully parked — no code in this package touches or depends on Manager. The
  Intelligence contract's 3.6 concept (Manager Decision Support Note) is explicitly **excluded**
  from this package for that reason, not forgotten.
- Every Hard Rule from `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` §7 still applies to anything
  built here: no self-approval, no autonomous external communication, no object becomes "truth"
  without an external `*_by` identity. This package adds nothing that violates any of them —
  confirmed against the real code below, not assumed.
- Scope test for every item in this package: Mike's own line from the critical-path update —
  "does this prevent me from running a real load through Dispatch?" Applied explicitly to each
  of the four remaining contract concepts in §4.

## 2. Architecture Context — What's Actually Real Today

Verified by direct read of the current code (`jax1313-outlook/Dispatch` @ `5274d47`), not
assumed from the contract document:

- **Intelligence** (`portal/models/intelligence.py`): flat CRUD store, 6 types, `verification_status`
  field (this session's PR #85), auto-archives every record on creation. Two producers:
  `create_inquiry()` (automated, broker-only) and the manual add form.
- **A working, tested, but unreachable bridge already exists.** `intelligence.promote_to_candidate()`
  (line 136) takes a broker-type Intelligence record and calls
  `library.add_record(submitted_by="machine", metadata={"source_finding_id": ..., "source_type": "INTELLIGENCE"})`.
  `library.py`'s `review_candidate()` gate already enforces external, non-system approval, and
  `_trigger_publisher_on_approval()` already auto-creates a Publisher "Broker Packet Required"
  action the moment a candidate with Intelligence provenance is approved. **The entire
  Intelligence → Library → Publisher chain for broker intelligence is built and tested end to
  end at the model layer right now.** The only thing missing is an HTTP route — no button
  anywhere calls `promote_to_candidate()`. This matches the readiness review's finding exactly.
- **Publisher** (`portal/models/publisher.py`): a real action queue (PENDING → DRAFT → READY →
  APPROVED → ARCHIVED) with per-action-type manifests (Broker Packet, Rate Confirmation, etc.)
  and an enforced external-approval gate. Actions are created today from ad hoc
  `trigger_reason`/`available_data`/`missing_data` arguments passed by whatever caller creates
  them (e.g. `library._trigger_publisher_on_approval()`) — there's no formal, Intelligence-owned
  "Publisher Requirement" object feeding this; it works via plain function arguments.
- **Conflict Notices** (`portal/models/conflict.py`) already flag `equipment_mismatch`,
  `missing_rate`, `hard_stop`, `scheduling_overlap`, and similar load-level issues today — ad
  hoc, not owned by Intelligence, not reusable across loads, but functionally present in the
  real load path right now.
- **Archive, Acquisition, Portal**: real and already integrated with the above (Intelligence
  auto-archives; Acquisition feeds the SAM/load pipeline Publisher's GovCon path already hooks
  into via `_trigger_govcon_draft()`).

## 3. Integration Context — Exact Touch Points

For the one concrete build proposed in this package (§5): a new route in
`portal/routes/api.py` (pattern-matching every existing `/api/intelligence/*` and
`/api/library/*` route) calls the already-existing `intel_model.promote_to_candidate(record_id)`
directly — no new model code, no new storage, no new archive path (archiving already happens at
Intelligence record creation and would happen again at Library's own supersede/reject path,
unchanged). A button in `portal/templates/intelligence.html`, next to the existing verification
badge, appears only on `intel_type="broker"` records and calls the new route — mirroring how
`conflicts.html`'s resolve button already calls `/api/conflict/resolve`.

## 4. End-State Context — What Actually Blocks a Real Load

Applying Mike's test to each of the four remaining contract concepts (Manager Decision Support
Note excluded per §1):

| Concept | Blocks running a real load end-to-end? | Reasoning |
|---|---|---|
| Library Candidate, Intelligence-originated (3.5) | **Arguably yes, cheaply fixed** | The chain exists and is tested but is literally unreachable by a real user today — that's a genuine "can't do this operationally" gap, not a missing feature. Fixing it is one route + one button, reusing fully-tested code. |
| Operational Consideration (3.2) | **No** | Conflict Notices already flag load-level operational issues (equipment mismatch, scheduling overlap, hard stops) in the real load path today. A formal Intelligence-owned version would make that knowledge *reusable across future loads*, which is valuable — but its absence does not stop this load from running. |
| Special Requirement (3.3) | **No** | Same reasoning — nothing in the real booking/dispatch path currently reads or requires a Special Requirement object to exist before a load can proceed. |
| Publisher Requirement, producing side (3.4) | **No** | Publisher already creates and processes real actions today via plain arguments (`trigger_reason`, `available_data`, `missing_data`). A formal Intelligence-produced version would make Publisher's inputs structured and reusable — genuinely useful, not currently blocking. |

## 5. What This Package Proposes To Build Now

**One change:** an HTTP route (`POST /api/intelligence/promote`, matching existing naming) plus
one template button, wiring the browser to the already-built, already-tested
`promote_to_candidate()` → `library.add_record()` → `review_candidate()` →
`_trigger_publisher_on_approval()` chain for broker-type Intelligence records. No new schema, no
new storage file, no new archive logic — every piece this touches already exists and is already
covered by tests (`tests/test_portal.py` lines ~1833-1875). This directly serves "operational
usability": a real broker relationship, once captured as Intelligence, can now actually become a
reusable Library asset and trigger a real Publisher packet, which currently cannot happen through
the UI at all.

**Everything else in §4 (Operational Consideration, Special Requirement, Publisher Requirement's
producing side) is recommended for the enhancement backlog**, not built now — none of them block
running a real load per Mike's own test, and Conflict Notices + Publisher's existing ad hoc
triggers already cover the operational ground they'd formalize. Worth revisiting after the first
real load actually runs, if the informal mechanisms prove insufficient in practice — a real-world
signal is a better basis for that design than building ahead of evidence.

## 6. Open Question For Mike

Approve the one-route build in §5 now? And separately: does the reasoning in §4 match your own
sense of what "operational usability" requires, or do you see a real-load scenario where
Operational Consideration / Special Requirement / Publisher Requirement's producing side would
actually be needed that this package is missing?

Mike decides.
