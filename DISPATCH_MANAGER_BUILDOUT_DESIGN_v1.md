# DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Manager Build-Out Design — Reconciliation and Behavior Specification
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code, no migration, no table, no PR, no implementation authorized by this document.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Doctrine sources used:** `DISPATCH_CONSTITUTION_v3.md`, `MANAGER.md`, `DISPATCH_FINAL_BLUEPRINT_v1.md`, `DISPATCH_SPINE_SPECIFICATION_v1.md`, `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md`, `LIBRARY_INGESTION_RULE.md`, `ALERT_GOVERNANCE_DOCTRINE.md`, `DISPATCH_VERSION_DOCTRINE.md`, `INTELLIGENCE_VERIFICATION_WORKFLOW.md`, `ARCHIVE_REVIEW_POLICY.md`, `PUBLISHER.md`, `INTELLIGENCE_ANALYST.md`, `DISPATCH_INTEGRATED_BLUEPRINT_v1.md`, `DISPATCH_REPO_RECONCILIATION_MATRIX_v1.md`, `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`, Stage 4/6/7/9/10/11 reconciliation and design documents, `DISPATCH_BLUEPRINT_DECISION_LOG.md`.
**Implementation sources inspected:** `jax1313-outlook/Dispatch` — `dispatch/`, `portal/`, `cin_lite/`, `tests/`, `DECISION_LOG.md`, `CLAUDE.md`, all Phase/Stage walkthrough reports.

---

## 0. Why This Document Exists

`MANAGER.md` already defines Manager's doctrine in full (13 sections, "Clean Repo Replacement Draft — Round 2"). What has never happened is what happened for every other organizational function — Security, Library, Archive/IFTA, Version Doctrine, Verification Workflow, Alert Governance — a **reconciliation against the actual, running Dispatch codebase**, turning doctrine into a buildable design.

This gap is not hypothetical; it is already recorded, three times, in this repository's own governance trail:

- `DISPATCH_STAGE11_MVP_INTEGRATION_RECONCILIATION_v1.md` §2 and §6: *"Manager has never had its own dedicated stage in the 13-stage plan."* Fit rating: **Weak Match**.
- `DISPATCH_STAGE11_MVP_INTEGRATION_RECONCILIATION_v1.md` §8, Open Question 3: *"Manager has no dedicated reconciliation stage in the 13-stage plan — does Mike want one added... given `dispatch/notifications.py`'s trigger seed was found useful but nothing has formally reconciled Manager's doctrine against it the way every other organizational function has been?"*
- `DISPATCH_BLUEPRINT_DECISION_LOG.md` (Stage 11 entry): the same open question, still unresolved as of the last logged entry.

This document is that missing reconciliation. It does not replace `MANAGER.md` — it is bound by it, cites it directly throughout, and turns its doctrine into the specific behavior, trigger, card, priority, and data model needed before implementation planning can begin. Nothing here authorizes a "Stage 11a" launch package on its own; that remains Mike's decision (see §26).

---

## 1. Executive Summary

**What Manager is.** Manager is the Run Office function for Dispatch (`MANAGER.md` §1; `DISPATCH_CONSTITUTION_v3.md` §7.1). It protects Mike's attention, receives structured reports, reacts to meaningful events, handles exceptions, prepares decision-ready cards, and coordinates the other organizational functions (Publisher, Intelligence Analyst, Library, Archive, Portal) through the Dispatch Spine and the Portal. Manager is a **cognitive function** in the sense the Constitution defines that term (§6.5): bounded reasoning, interpretation, and judgment support — never deterministic routing, storage, scoring, or approval mechanics, which belong to the Spine.

**What Manager is not.** Manager is not a chatbot. Manager is not a free-roaming LLM. Manager is not an autonomous dispatcher. Manager is not a replacement for Portal — Mike does not operate Manager directly, he operates through Portal (`MANAGER.md` §3.4; `DISPATCH_CONSTITUTION_v3.md` §6.2). Manager is not a replacement for the Spine — the Spine owns state, routing mechanics, validation, and audit; Manager interprets and prioritizes, it does not execute (`MANAGER.md` §11). Manager does not approve, submit, book, sign, certify, or alter doctrine (`MANAGER.md` §12; `DISPATCH_CONSTITUTION_v3.md` §15).

**Why Manager is needed.** Dispatch already produces meaningful signals across many independent systems — stalled-load notifications, Conflict Notices, IFTA exceptions and suspect entries, Publisher draft-ready events, Portal card status changes, Security permission denials — but nothing today reads all of them together, ranks them by actual consequence, or decides which ones are worth Mike's attention right now versus which can wait for a scheduled review. §4 below inventories this precisely: the raw event surface is real and mostly built; the prioritization and attention-protection layer above it is the one piece that has never existed.

**How Manager reduces Mike's cognitive load.** By doing what a competent human operations manager does: staying quiet during routine operation, combining related updates into one card instead of five, ranking by consequence before urgency, and only interrupting Mike for what genuinely needs his judgment (`MANAGER.md` §2, §10). Every other signal either logs silently or waits for a scheduled review.

**Why Manager must remain bounded.** Every failure mode named for Manager in the doctrine — becoming a chat interface, becoming a free-roaming router, hiding material risk to reduce noise, quietly picking up approval authority because it is "just faster" — is a failure mode that *increases* Mike's cognitive load rather than reducing it, by adding another system he has to supervise, correct, or distrust. Manager is powerful specifically because it is narrow. A Manager that could decide things would not protect Mike's attention; it would just move the risk Mike currently carries into a system nobody voted to give it to.

---

## 2. Manager Doctrine

This section restates governing doctrine verbatim/near-verbatim so the rest of this document has a fixed reference point. Nothing here is new; all of it is quoted or closely paraphrased from `MANAGER.md` and `DISPATCH_CONSTITUTION_v3.md` §6–7, §15.

- **Manager = Run Office.** *"Manager is the Run Office function for Dispatch."* (`MANAGER.md` §1)
- **Manager protects Mike's attention.** *"Manager protects Mike's attention, organizes work, receives structured reports, reacts to meaningful events, handles exceptions, prepares decision-ready cards, and keeps the Dispatch office coordinated."* (`MANAGER.md` §1)
- **Manager coordinates functions.** Manager routes exceptions and review needs to the right function — Publisher, Intelligence, Library, Archive, Portal — and lets routine work move quietly through the Spine (`MANAGER.md` §2, step 5–7).
- **Manager does not approve.** Confirmed in three places: `MANAGER.md` §1 ("Manager does not approve, commit, submit, book, sign, alter doctrine, or transfer authority"), §12 ("Approve work on Mike's behalf" is a forbidden action), and `DISPATCH_CONSTITUTION_v3.md` §7.1 ("Manager may not approve, submit, sign, book, certify, alter doctrine, create authority, or bypass Portal visibility").
- **Manager does not book loads.** `MANAGER.md` §12 forbidden action, explicit.
- **Manager does not submit documents.** `MANAGER.md` §12: "Submit packets externally" is forbidden. This includes CIN/SAM decisions, dispatch-load actions, and IFTA quarter submissions — Manager may surface that one of these gates is waiting, it may never trip it.
- **Manager does not alter doctrine.** `MANAGER.md` §12; `DISPATCH_CONSTITUTION_v3.md` §15 ("alter doctrine," "alter architecture," "change role boundaries" are Universal Forbidden Actions for every function, not just Manager).
- **Manager does not replace Portal.** *"Mike does not directly operate Manager. Mike operates through the Portal."* (`MANAGER.md` §3.4) Manager's human-facing output is always Portal-visible, never a direct conversation (`MANAGER.md` §10, last bullet).
- **Manager does not replace Spine.** *"Manager does not replace the Dispatch Spine. The Dispatch Spine handles deterministic operation: State, Routing mechanics, Validation, Storage, Queues, Audit logs, Scoring formulas, Automation triggers, Event records. Manager interprets office state, protects priorities, prepares meaningful cards, and escalates only when needed."* (`MANAGER.md` §11)
- **Manager does not become a free-roaming AI.** *"Manager is not a free-roaming autonomous agent. Manager is not a constant chatterbox. Manager is not a direct chat assistant for Mike."* (`MANAGER.md` §1) Reinforced by `DISPATCH_FINAL_BLUEPRINT_v1.md` §5.9's risk-table entry: *"Manager drifts into a free-roaming LLM router or direct chat interface"* — mitigated specifically by *"Manager §12 forbidden actions; activation strictly limited to four trigger classes."* The four-trigger-class boundary is not incidental — it is the named mechanism that keeps Manager from becoming exactly the thing this document must not build.

---

## 3. Manager Position In The Architecture

Dispatch's five layers (`DISPATCH_CONSTITUTION_v3.md` §6; `DISPATCH_FINAL_BLUEPRINT_v1.md` §2):

| Layer | What it owns | Manager's relationship |
|---|---|---|
| **Authority Layer** | Mike Zachary — all decisions, approvals, submissions, commitments, doctrine, deployment. | Manager sits entirely below this layer. Manager may prepare information *for* Authority decisions; it never sits inside the Authority Layer, never simulates it, never substitutes for it. Every card Manager prepares carries the fixed closing sentence: *"This is a recommendation only. No action is authorized. Mike decides."* (`DISPATCH_CONSTITUTION_v3.md` §17) |
| **Presentation Layer** | Portal — the only way Dispatch becomes visible/usable to humans. | Manager has **no direct human interface**. Every Manager output that a human needs to see must render as a Portal card, using the Spine's `portal_cards` table. Manager may not add a chat box, a notification popup, or any other Mike-facing surface that bypasses Portal. |
| **Organizational Layer** | Manager, Publisher, Intelligence Analyst, Library, Archive, Portal — the business functions. | **This is where Manager lives.** Manager is a peer to Publisher/Intelligence/Library/Archive/Portal, not their supervisor with authority over them — it coordinates by routing and prioritizing, not by commanding. `DISPATCH_CONSTITUTION_v3.md` §6.3: these functions "may be supported by deterministic services, cognitive functions, or both," which is exactly Manager's supporting role to the others. |
| **Deterministic Layer** | The Dispatch Spine — state, routing mechanics, validation, queues, scoring formulas, audit logging, event records, storage. | Manager is a **consumer and requester** of the Spine, never its owner. Manager reads `work_items`/`events`/`conflict_events`; it requests transitions through the Spine's own `apply_transition()`/`transition()` machinery; it never writes `work_items.current_state` directly and never bypasses the single writer path Stage 4 established. |
| **Cognitive Layer** | Manager reasoning, Publisher drafting, Intelligence analysis — bounded reasoning only, per `DISPATCH_CONSTITUTION_v3.md` §6.5. | Manager's *reasoning* — prioritization, classification, card preparation — happens here. Cognitive-layer output is, by Constitutional rule, "always Portal-visible, never self-executing" (`DISPATCH_FINAL_BLUEPRINT_v1.md` §2.5). Manager's cognitive work is explicitly bounded to prioritization, card preparation, and escalation (`DISPATCH_FINAL_BLUEPRINT_v1.md` §5.9) — it never performs deterministic routing, storage, or scoring itself. |

**In one line:** Manager is an Organizational-Layer function whose reasoning lives in the Cognitive Layer, reads and requests (never writes directly) from the Deterministic Layer, surfaces everything through the Presentation Layer, and never enters the Authority Layer.

---

## 4. Existing Dispatch Assets That Already Behave Like Manager

Inspected directly against the running `jax1313-outlook/Dispatch` codebase.

| Asset | Location | Classification | Notes |
|---|---|---|---|
| Notification trigger points | `dispatch/notifications.py` (`notify_dispatched`, `notify_exception`, `notify_delivered`, `notify_pod_generated`, `notify_archived`, `notify_invoice_created`, `notify_payment_received`, `notify_payment_overdue`, `notify_settlement_disputed`, `notify_settlement_written_off`, `notify_stalled`) | **Partial Match** | This is the seed Stage 11 already identified: real, usable trigger points, but each one independently emails Mike with no shared prioritization, no combining of related updates, no consequence ranking. This is the raw Workflow Events trigger class (`MANAGER.md` §3.2) with no Manager layer above it yet. |
| Stalled-load / overdue-settlement scans | `dispatch/services.py` — `check_stalled_loads()`, `check_overdue_settlements()` | **Partial Match** | Deterministic detection logic already exists and is exactly the kind of signal Manager should consume for Exception Conditions (`MANAGER.md` §3.3). No classification, no priority assignment, no card preparation on top of it. |
| Conflict Notices | `portal/models/conflict.py` — `create_notice`, `check_dispatch_card()`, `check_booking_conflicts()`, `check_library_assets()`, `_derive_card_level()` | **Strong Match** | Closest existing analogue to a Manager-prepared card: has severity, `human_decision_required`, and an auto-derived 0–4 card level. Missing only the cross-system prioritization Manager doctrine requires — it only ever sees conflict-shaped events, never Publisher/Intelligence/Archive/Security events in the same ranked view. |
| `ExceptionNotice` (load-scoped exceptions) | `dispatch/models.py`, `dispatch/store.py` | **Partial Match** | A second, independent exception system from Conflict Notices — confirmed by Stage 10's reconciliation as one of five uncoordinated alert-shaped systems (see §14). Real signal, no shared Manager-facing view. |
| IFTA exceptions, `plausibility_warning`, suspect-entries | `dispatch/models.py::IFTAException`; `dispatch/services.py::list_suspect_ifta_fuel_purchases()` | **Partial Match / Missing** | `IFTAException` is a persisted record (usable). `plausibility_warning` and the suspect-entries confidence flag are **not persisted records at all** (Stage 10 finding) — they cannot be surfaced to Manager as addressable items until they become real rows. |
| Review/queue pages | `portal/routes/pages.py` — `/ifta/review`, `/exceptions`, `/queues`, `/pipeline`, `/conflicts` | **Weak Match** | Real human-review surfaces exist, but each is single-domain and separately navigated. There is no unified "what needs attention right now, ranked" view — which is precisely Manager's Staff Report function (`MANAGER.md` §5). |
| Archive review queue | `portal/models/archive.py` | **Missing** | No review/retention fields, no queue, no route. Confirms Stage 6's finding stands: the retention half of Archive doctrine (`ARCHIVE_REVIEW_POLICY.md` §3, Current + 3 Previous → Archive Review Queue → Keep/Delete) is unbuilt. Manager cannot surface what does not exist as a record yet. |
| Decision Log / walkthrough report discipline | `DECISION_LOG.md`, ten `PHASE*`/`STAGE*_WALKTHROUGH_REPORT*.md` files | **Strong Match (pattern, not code)** | This is exactly the audit/proof-chain discipline Manager doctrine assumes — every governed change has a verbatim approval and a walkthrough. Not owned by Manager and shouldn't be; cited here because it is the existing proof that "propose, then get Mike's verbatim approval, then execute, then report" is already how this codebase works. Manager's own build should follow the identical discipline. |
| Portal card_level / Version Doctrine (Stage 5) | `portal/models/sandbox.py`, `portal/models/conflict.py` — `CARD_LEVELS`, `_derive_card_level()`, `version`, `last_change` | **Strong Match** | The single most reusable existing asset for Manager. Proves the 0–5 card-level scale, auto-derivation with manual override, and non-noisy version bumping all work in production Portal code today. Weakness: **three independent implementations** of the same 0–5 scale (`sandbox.py`, `conflict.py`, `dispatch/spine/models.py::PortalCard`) — a real Conflict, not just a gap, since nothing unifies them today. |
| Scoring / recommendation logic | `dispatch/scoring.py` | **Weak Match, by design** | Deterministic RPM-band scoring belongs to the Spine/Deterministic Layer, not Manager. Listed here only to confirm the boundary: Manager may *consume* a `score` to decide card priority, it may never generate or alter one. |
| Finalization / HMAC decision gates | `cin_lite/email_delivery.py`, `dispatch/notifications.py`, `dispatch/services.py::approve_ifta_quarter()` | **Partial Match / Conflict** | Three independently-implemented `make_token`/`verify_token` HMAC gates, no shared module, and — per Stage 7 — currently unauthenticated (no session/role attached to who clicked the link). Manager may surface "a gate is waiting" as a Status/Review card; it must never touch the token or the gate itself. |
| Spine `ROUTED_TO_MANAGER` state | `dispatch/spine/state.py`: `"ROUTED_TO_MANAGER": []` | **Missing — a real structural gap, not a doctrine gap** | The Stage 4 Spine already reserves a Work Item state named exactly for this function, and it is a dead end: zero outbound transitions, zero consumer code anywhere in the repository. This is the clearest single piece of hard evidence that Manager was designed for from day one but never actually reconciled or built. Any future Manager implementation must define what `ROUTED_TO_MANAGER` transitions *to* — this document specifies that in §6, but does not build it. |
| Security event log | `dispatch/security/store.py::list_security_events()` (Stage 7) | **Strong Match (as a read source)** | A ready, structured stream of exactly the kind of Exception Condition input (`PERMISSION_DENIED`, `LOGIN_FAILURE`) Manager doctrine calls for. Not yet read by anything Manager-shaped. |

**Summary of the gap:** every individual signal Manager needs already exists somewhere in the codebase in some form. What has never existed is the layer that reads across all of them, classifies, ranks by consequence, combines related updates, and decides what earns a Portal card versus a silent log entry. That layer is Manager, and it is entirely unbuilt.

---

## 5. Manager Trigger Model

Extends `MANAGER.md` §3's four trigger classes with the full set of concrete triggers required for Dispatch as it exists today. Every trigger below is either Scheduled Review, Workflow Event, Exception Condition, or Portal-Mediated Human Action — no fifth class is introduced.

| Trigger | Class | Source | Required Input | Manager Action | Portal Output | Human Review? | Creates Work Item? | Creates Portal Card? |
|---|---|---|---|---|---|---|---|---|
| Scheduled review (morning/EOD/weekly/monthly) | Scheduled Review | Manager's own schedule | Current queue snapshot across all functions | Compile Staff Report, rank by priority framework (§9) | Status/Review card(s), combined where possible | Optional, Mike's discretion | No (reads existing) | Only if something is above Level 0 |
| Workflow event (Publisher draft ready, Intelligence finding ready, Library/Archive candidate created, Portal card status changed) | Workflow Event | Publisher/Intelligence/Library/Archive/Portal | Event payload + source Work Item reference | Classify, assign priority, route to owning function or Portal | Review or Decision card per §7 classification | Depends on classification | Enriches existing Work Item | If Level ≥ 2 |
| Exception condition (missing source, contradictory source, failed validation) | Exception Condition | Spine `ValidationResult` / `ConflictEvent` | Validation/conflict record | Classify severity, escalate per priority framework | Conflict card if Level 4 | Yes if Level ≥ 3 | Enriches existing Work Item | Yes, Level 3–4 |
| Portal-mediated human action (Mike approves/rejects/requests revision/defers) | Portal-Mediated Human Action | Portal → `approval_events` | ApprovalEvent record | Log outcome, update priority queue, notify affected function | None (Mike already acted) | No | Enriches existing Work Item | No |
| Security event: login failure, permission denied, lockout | Exception Condition | `dispatch/security/store.py::list_security_events()` | SecurityEvent record | Classify per §10; single failure = auto-log, repeated/PERMISSION_DENIED pattern = escalate | Security Alert Card if pattern crosses threshold | Yes for patterns, no for single events | New Work Item for a pattern, not for a single event | Yes for patterns only |
| Archive review event (item enters Archive Review Queue) | Workflow Event | `portal/models/archive.py` (once retention/review is built — see §11) | Archive record + version | Prepare monthly-report candidate | Archive Review Card | Yes, Keep/Delete needs Mike | New Work Item | Yes, Level 2 |
| Library event (candidate created, missing asset detected) | Workflow Event | `portal/models/library.py` | Library record | Human-placed: auto-log only, no card (§12). Publisher-generated: prepare review card. | Library Review Card (Publisher-origin only) | Only for Publisher-origin | New Work Item for Publisher-origin only | Only for Publisher-origin |
| Publisher draft ready | Workflow Event | `portal/models/publisher.py::update_action_status()` → READY | Publisher record | Prepare Review Card, route to Mike | Review Card | Yes | Enriches existing Work Item | Yes, Level 2–3 |
| Intelligence finding ready | Workflow Event | `portal/models/intelligence.py` | Intelligence record | Route to Portal, classify per Verification Workflow status if present | Status or Review Card depending on classification | Depends on classification | Enriches existing Work Item | If Level ≥ 1 |
| High-value load/opportunity | Exception Condition | `portal/models/sandbox.py` (`_HIGH_VALUE_SCORE_THRESHOLD`) | Sandbox entry, score | Bump priority, prepare Decision Card, dedupe against prior version (§16) | Decision Card | Yes | Enriches existing Work Item | Yes, Level 3 |
| Stage launch package status change | Scheduled Review / Workflow Event | `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md` (Claude-3 side, out of Dispatch's runtime — see §17) | Stage status | Track only, recommend next stage | Stage Gate Card | Yes | N/A (not a Dispatch Work Item — a planning artifact) | Yes, Level 1–2 |
| Failed validation | Exception Condition | Spine `ValidationResult` | validation_status = FAIL | Classify, route to owning function | Review or Conflict Card | Depends on severity | Enriches existing Work Item | If Level ≥ 2 |
| Missing source | Exception Condition | Spine `ConflictEvent` (MISSING_SOURCE type) | ConflictEvent record | Escalate per No Fabrication Rule | Conflict Card | Yes | Enriches existing Work Item | Yes, Level 4 |
| Conflict raised | Exception Condition | Spine `ConflictEvent`, `conflict_events` table | ConflictEvent record | Pause routing, escalate | Conflict Card | Yes | Enriches existing Work Item | Yes, Level 4 |
| Suspect entry (IFTA) | Exception Condition | `dispatch/services.py::list_suspect_ifta_fuel_purchases()` | Suspect flag | Classify as Partially Verified per Verification Workflow, escalate for review, dedupe on version | Review Card | Yes | New Work Item once persisted (currently not persisted — see §4) | Yes, Level 2 |
| Deployment / promotion gate | Exception Condition | Stage 12/13 launch packages, `DEPLOY_VPS.md` | Gate status | Surface readiness/blockers only | Deployment Warning Card | Yes, always | N/A (planning artifact) | Yes, Level 5 (Authority) |
| Test failure | Exception Condition | CI / `pytest` run output | Test result | Auto-log if isolated and pre-existing-baseline; escalate if it blocks a stage gate | Test Failure Card, only if it blocks something Mike is waiting on | Only if blocking | No | Only if blocking |

---

## 6. Manager Work Item Relationship

**Governing rule:** Spine owns state. Manager never owns it (`MANAGER.md` §11; Stage 4 design: *"a single `transition()` function is the only path that may change `work_items.current_state`"*).

**Manager may:**
- **Request a Work Item** — ask the Spine to create one (`dispatch/spine/store.py::create_work_item()`) when a trigger in §5 has no existing Work Item to attach to.
- **Enrich a Work Item** — attach classification, priority, and routing recommendation as data (`priority`, `assigned_function`, `required_action` fields already exist on `WorkItem`), never by writing `current_state` directly.
- **Classify a Work Item** — apply the nine-class taxonomy from `MANAGER.md` §7 (Routine/Status/Review Needed/Decision Needed/Conflict/Authority/Archive/Library Candidate/Noise).
- **Recommend routing** — propose which state a Work Item should move to next and which function should own it, then **call the Spine's own `transition()`/`apply_transition()` to execute that specific, already-defined, already-allowed move** — the same mechanism every other function uses, not a Manager-owned bypass.
- **Prepare Portal cards** — write to `portal_cards` via `create_portal_card()`, exactly as Stage 4 defined it, including the fixed `required_closing` sentence.
- **Monitor queue health** — read `list_work_items()`, `list_events()`, `list_conflict_events()` to build the Staff Report (`MANAGER.md` §5).

**Manager may not:**
- Bypass `transition()` — no direct `UPDATE work_items SET current_state = ...` anywhere in Manager's code, ever.
- Change `WorkItem.current_state` directly, for any reason, including "obviously safe" routine moves.
- Approve — never write an `ApprovalEvent` with an `action` value that represents Mike's decision (APPROVE_DRAFT, APPROVE_PACKET, APPROVE_LIBRARY_PROMOTION, APPROVE_LOAD_PURSUIT, APPROVE_DEPLOYMENT, etc.). Manager may only *read* `approval_events` to know what Mike already decided.
- Reject — same rule, same reason.
- Complete — Manager does not mark a Work Item COMPLETED; that is a Spine-driven consequence of Mike's approval or a deterministic process finishing, not Manager's call.
- Archive — Manager may recommend ARCHIVED as a destination and prepare the Archive Review Card; it does not execute the transition into ARCHIVED itself for anything requiring Keep/Delete judgment.
- Deploy — never touches Stage 12/13 deployment mechanics.
- Modify security — never touches `dispatch/security/` tables, never resets a PIN, never creates a session (see §10).

**Exact interaction points:**

| Spine table | Manager reads | Manager writes |
|---|---|---|
| `work_items` | Yes — full read for queue health, classification, priority | Only via `create_work_item()` (new) and `apply_transition()` (state moves the Spine already allows) — never a raw `UPDATE` |
| `events` | Yes — to know what already happened | Yes, via `create_event()`, to log its own classification/routing actions as an auditable event (actor_type = "manager") |
| `portal_cards` | Yes — to avoid duplicate cards | Yes, via `create_portal_card()` — this is Manager's primary write surface |
| `conflict_events` | Yes — to know what's already flagged | Yes, via `create_conflict_event()` when Manager itself detects a MISSING_SOURCE/CONTRADICTORY_SOURCE condition from cross-referencing two functions' outputs — Manager may *raise* a conflict, it may never *resolve* one |
| `approval_events` | Yes — to know what Mike already decided, and to populate `session_id`/`user_id`/`role` when acting on Mike's behalf is never appropriate; Manager never creates rows here | No — zero write access |
| `audit_events` | Yes, for its own transparency | Yes, via `create_audit_event()`, logging every Manager-initiated action (classification, card creation, routing recommendation) for the same proof-chain reasons every other function is audited |

**On `ROUTED_TO_MANAGER`:** this Spine state currently has zero outbound transitions (`dispatch/spine/state.py`: `"ROUTED_TO_MANAGER": []`). A future Manager build must define, and get Mike's approval for, what states `ROUTED_TO_MANAGER` may transition to — most plausibly `PORTAL_CARD_PENDING` (card prepared, awaiting Mike), `ROUTING_PENDING` (re-routed to another function), or `DEFERRED`. This document flags the gap; it does not close it. Closing it is a Spine schema amendment and requires the same design-then-approval discipline as Stage 4 itself.

---

## 7. Manager Portal Card Model

All card types use the Spine's existing `PortalCard` fields (`card_id`, `work_item_id`, `card_level`, `card_type`, `title`, `summary`, `source_refs`, `recommendation`, `decision_needed`, `allowed_actions`, `required_closing`). `required_closing` is **always** the fixed sentence from `DISPATCH_CONSTITUTION_v3.md` §17: *"This is a recommendation only. No action is authorized. Mike decides."* — no card type below overrides this.

| Card Type | Purpose | Card Level | Source Trigger | Allowed Actions | Forbidden Actions | Mike Must Decide? |
|---|---|---|---|---|---|---|
| **Status Card** | Passive awareness of a state change | 1 | Any Workflow Event with no decision attached | View, dismiss | Approve, edit underlying record | No |
| **Review Card** | Something may benefit from a look, not urgent | 2 | Publisher draft ready, Intelligence finding, Library Publisher-origin candidate, Archive review item | View, mark reviewed, request revision (routes to owning function) | Approve on Mike's behalf, submit | Optional |
| **Decision Card** | Mike must choose between options | 3 | High-value opportunity, failed validation needing a call, repeated alert pattern | View, choose an offered option (routes the choice back through Spine `transition()`) | Choose *for* Mike, pre-select a default | Yes |
| **Conflict Card** | Source/doctrine/validation conflict, work paused | 4 | ConflictEvent (any of the 10 types), missing source, contradictory source | View, resolve (Mike's resolution triggers the actual transition) | Auto-resolve, guess a resolution, proceed without resolution | Yes |
| **Authority Card** | Final approval or business commitment needed | 5 | Deployment gate, government submission, contract commitment, doctrine change proposal | View, forward to the correct approval surface (email gate, Portal action) | Approve, submit, execute | Yes, always |
| **Archive Review Card** | Keep/Delete judgment on a retained item past Current + 3 | 2 | Archive Review Queue entry (`ARCHIVE_REVIEW_POLICY.md` §3) | View, present Keep/Delete choice | Delete, purge, auto-keep past policy window | Yes |
| **Library Review Card** | Publisher-generated Library candidate awaiting promotion review | 2–3 | Publisher output nominated for Library, per `LIBRARY_INGESTION_RULE.md` §5 | View, present promote/reject choice | Promote without Mike, treat as truth before approval | Yes |
| **Security Alert Card** | Pattern in security events worth Mike's attention | 3–4 | Repeated LOGIN_FAILURE, PERMISSION_DENIED pattern, PIN reset request | View, acknowledge | Reset a PIN, grant access, modify a role, unlock an account | Yes |
| **Stage Gate Card** | A Migration Plan stage is ready for the next action | 1–2 | Stage Launch Package status change | View, see recommended next stage | Approve the stage, execute the stage | Depends — informational unless a Go/No-Go decision is due |
| **Test Failure Card** | A test failure blocks something Mike is waiting on | 2–3 | CI/pytest failure tied to a pending stage gate or deployment | View, see failure summary | Merge despite failure, waive the test requirement | Yes, if it blocks a gate |
| **Deployment Warning Card** | Deployment/promotion readiness status | 5 | Stage 12/13 gate, `DEPLOY_VPS.md` blockers | View, see blocker list | Deploy, promote, waive a blocker | Yes, always |

---

## 8. Manager Priority Framework

Base ranking is `MANAGER.md` §6 (consequence first, urgency second), extended with the explicit categories this mission requested, folded in at the consequence tier they actually belong to rather than appended as a separate list — duplication would just create two competing priority orders.

1. **Safety, security, legal, compliance, or authority risk** — merges `MANAGER.md` §6 item 1 with this mission's separate safety/security/legal/compliance/authority items; these are one tier, not five, because they share the same property: getting them wrong has consequences no urgency calculation can outweigh.
2. **Active revenue opportunity** (`MANAGER.md` §6 item 2) — includes high-value loads/opportunities.
3. **Customer, broker, shipper, or driver-facing need** (`MANAGER.md` §6 item 3) — includes driver operational issues and customer/broker visibility issues named in this mission.
4. **Government packet or opportunity deadline** (`MANAGER.md` §6 item 4) — deadline-driven work generally.
5. **Operational positioning or route risk** (`MANAGER.md` §6 item 5).
6. **Document production work** (`MANAGER.md` §6 item 6).
7. **Library, Archive, or cleanup work** (`MANAGER.md` §6 item 7) — includes archive retention and library maintenance.
8. **Discovery or research intake** (`MANAGER.md` §6 item 8).
9. **Deferred improvement work / routine system status** (`MANAGER.md` §6 item 9).

**Conflict handling between priorities:** when two items compete for Mike's attention, Manager ranks by tier first (1 through 9), and only uses recency/deadline proximity to order items *within* the same tier. A Tier 1 item is never delayed by an unresolved Tier 4 item, no matter how close its deadline is. If two Tier 1 items compete simultaneously, Manager does not silently pick — it presents both on one combined card so Mike sees the actual conflict rather than a synthesized ranking he didn't ask for. Manager never resolves a cross-tier conflict by omission (leaving one off the card); the Attention Protection Rules (`MANAGER.md` §10) govern how much detail each gets, not whether it appears at all.

---

## 9. Manager And Security

Manager's boundary here is explicit doctrine, not inferred: *"Manager may see user role, session status, and action outcome when needed for coordination. Manager may not see plaintext PIN values."* (`SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §12.1)

| Security signal | Manager's interaction |
|---|---|
| Login events (`LOGIN_SUCCESS`/`LOGIN_FAILURE`) | Read-only, via `dispatch/security/store.py::list_security_events()`. Single failures auto-log (Tier 9). A pattern of repeated failures for one identity escalates to a Security Alert Card (Tier 1). |
| Permission failures (`PERMISSION_DENIED`) | Read-only. A single denial (e.g., a Driver role hitting `/settings`) auto-logs — that's the system working correctly. A pattern targeting the same resource repeatedly escalates. |
| Suspicious activity | Manager may correlate multiple SecurityEvent rows (e.g., failed logins across several identities in a short window) into one Security Alert Card. Manager does not itself define what "suspicious" means beyond simple pattern thresholds Mike has approved — it does not invent new security heuristics. |
| PIN reset requests | Per `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §4.3 note: *"Repeated failed PIN attempts should trigger lockout or Manager / Authority review."* Manager's role is exactly that: surface the review need on an Authority Card. Manager never calls `dispatch.security.auth.reset_pin()` itself — that function already requires `approved_by_user_id`, and Manager is never that approver. |
| Security Sub-Library status | Manager may report *that* the Security Sub-Library exists and its general status (has content / stale / needs attention) without ever performing the PIN re-check itself. `require_security_sublibrary_pin()` belongs to the auth/Portal boundary, not Manager. |
| Unauthenticated approval attempts | Not currently possible to detect as a distinct signal — Stage 7's build left the three HMAC gates unauthenticated by design (deferred to Portal-Wide Enforcement). Until that stage exists, "approval attempt with missing identity" is the *normal* current state of all three gates, not an anomaly Manager can flag without producing constant noise. Manager should not raise this as a Security Alert until Portal-Wide Enforcement exists to define what "should have been authenticated but wasn't" actually means. |
| `approval_events` with missing identity | Stage 4 design explicitly permits `session_id`/`user_id`/`role` to remain `NULL` until identity is wired in — this is documented, expected behavior for anything not yet covered by Stage 7's narrow `/settings` gate, not a conflict. Manager should not treat every null-identity `ApprovalEvent` as an alert; that would flag the majority of the system's current, doctrine-compliant behavior. |
| Stage 7 security gaps (Portal-Wide Enforcement not yet built) | Manager may surface this as a standing Stage Gate Card ("Security Foundation built; Portal-Wide Enforcement not yet authorized") — informational, low-urgency, Tier 9 unless Mike raises its priority. |

**What Manager may never do here:** grant access, reset a PIN, create or revoke a session, change a role, or approve any Authority action tied to security. Every one of these stays inside `dispatch/security/auth.py`, callable only through the Portal routes and only by the identity actually authorized to call them.

---

## 10. Manager And Library

Governed entirely by `LIBRARY_INGESTION_RULE.md`.

**Manager must understand:**
- *"Any document placed into any Library by a human is accepted immediately. No verification workflow. No approval workflow. No promotion workflow."* (§2) — *"A human placing a document into Library is itself the approval act."*
- Publisher-generated assets are the explicit exception — they remain under Publisher's §9/§14 review flow (§3, §5).
- The Security Sub-Library requires its own separate PIN check at the moment of access (§6) — Manager reports status, never performs the check.

**Manager may:**
- Report Library status (what sections exist, what's populated, what's stale) as part of a scheduled review Status Card.
- Identify missing documents — `portal/models/library.py::get_missing_company_assets()` already exists for this; Manager consumes it, does not reimplement it.
- Identify stale assets, using Version Doctrine (§16) — a Library record whose version hasn't changed in a long time, or one flagged during an Archive/Library review cycle.
- Prepare Library Review Cards **only for Publisher-generated candidates awaiting promotion** — never for human-placed documents, which need no card at all.

**Manager may not:**
- Challenge human Library ingestion — no "are you sure" card, no verification step, no delay, for anything a human directly placed. Doing so would directly violate §2's core rule.
- Create paper-tiger approval loops — a card that exists only to be rubber-stamped is exactly the "noise" `MANAGER.md` §13 defines as failure.
- Treat human-ingested documents as untrusted — per §4, a human-placed document is source, not an inference; Manager's own No Fabrication obligations do not apply to it because Manager isn't the one asserting anything about it.

---

## 11. Manager And Archive / IFTA

Grounded in Stage 6's findings (`DISPATCH_STAGE6_ARCHIVE_IFTA_RECONCILIATION_v1.md`) and `ARCHIVE_REVIEW_POLICY.md`.

Manager should recognize three separate archive-shaped assets, not conflate them:
- **CIN contract archive** (`cin_lite/archive.py`) — hash-verified (SHA-256 sidecar files, `_write_and_hash()`/`_read_verified()`, fail-closed on mismatch via `ArchiveIntegrityError`). Strongest integrity story of the three.
- **Operational/load archive** (`portal/models/archive.py`) — no hashing, no retention/review fields yet.
- **IFTA compliance archive** — `IFTAReportApproval`'s freeze/idempotent-reapproval logic, proven across five owner-approved phases.

Stage 6's central finding stands: the *integrity* half of Archive doctrine is strongly satisfied by two of three; the *retention/review* half (Current + 3 Previous → Archive Review Queue → Keep/Delete, `ARCHIVE_REVIEW_POLICY.md` §3) is **missing uniformly across all three** — one shared gap, not three separate ones. Manager cannot surface an Archive Review Queue that doesn't exist yet; it can only surface this gap itself as a standing Stage Gate Card until a future Archive build closes it.

IFTA is confirmed by Stage 6 as a **Combination role**: primarily the Compliance Module, secondarily the reference pattern for Approval Event / Alert Governance mechanics that the rest of Dispatch should eventually converge onto.

**How Manager surfaces each:**
- **Archive review needs** — once the Archive Review Queue exists (a future build), Manager prepares an Archive Review Card per item, Keep/Delete choice presented to Mike, never decided by Manager.
- **Retention review** — same mechanism, scheduled-review-triggered (monthly cycle per `ARCHIVE_REVIEW_POLICY.md` §4).
- **IFTA exceptions** — read from `IFTAException` records, classified and routed as Review or Conflict cards depending on severity.
- **Suspect entries** — currently computed at read time, not persisted (§4). Manager cannot create a durable Work Item for a suspect entry until it becomes a real row; until then Manager may only surface it transiently during an IFTA review page visit, not as a standing tracked item.
- **Compliance review** — IFTA quarter approval status, surfaced as a Stage Gate / Authority Card when a quarter is ready for Mike's sign-off.
- **Evidence review** — POD/receipt evidence awaiting review, surfaced as Review Cards.
- **Monday Report candidates** — `ALERT_GOVERNANCE_DOCTRINE.md` §7 and Stage 10's findings note that no alert system is currently connected to a Monday/Monthly report deliverable because that report doesn't exist as a built artifact yet. Manager's Staff Report model (§13 of `MANAGER.md`) is the natural mechanism to eventually produce it, but building the report itself is out of scope for this design.

---

## 12. Manager And Publisher

Per `PUBLISHER.md` §3 (Publisher's approved inputs include "Manager work item assignments") and §9 (Publisher must not "bypass Manager when escalation is required").

**Manager may:**
- Assign Publisher work — create or route a Work Item with `assigned_function = "Publisher"`.
- Receive Publisher draft-ready signals — `portal/models/publisher.py`'s `PUBLISHER_STATUSES` transition to `READY`.
- Prepare Review Cards for Mike once a draft is ready.
- Route missing-source issues back to Publisher (or escalate as a Conflict if Publisher itself can't resolve it).
- Escalate Publisher conflicts — e.g., Publisher flags it cannot proceed without a fact Library doesn't have.
- Monitor draft status across all in-flight Publisher work as part of the Staff Report.

**Manager may not:**
- Draft as Publisher — Manager never writes packet/document content itself.
- Approve Publisher output — that's an Authority Card outcome, Mike's decision.
- Submit Publisher output — external submission is forbidden to both functions independently (`PUBLISHER.md` §9, `MANAGER.md` §12).
- Convert Publisher drafts into Library truth — that promotion step is explicitly Mike's decision, gated by `LIBRARY_INGESTION_RULE.md` §5, never automatic and never Manager's to trigger.

---

## 13. Manager And Intelligence Analyst

Per `INTELLIGENCE_ANALYST.md` §10: *"Manager receives Intelligence findings, prioritizes work, protects Mike's attention, and determines whether a finding needs Portal visibility. The Intelligence Analyst does not manage the office. The Intelligence Analyst supplies meaning."*

**Manager may:**
- Request interpretation from Intelligence when a Work Item needs it.
- Receive Intelligence findings as structured input.
- Route findings to Portal — deciding *whether* a finding needs Portal visibility is explicitly Manager's job per the quote above, not Intelligence's.
- Route verified findings to Library candidates if the Verification Workflow classification supports it — see §14's classification gate.
- Escalate uncertainty — a finding classified Partially Verified or Unverified routes to a Review/Conflict card rather than silently becoming a Status card.
- Prepare decision cards drawing on Intelligence's output.

**Manager may not:**
- Act as Intelligence Analyst — Manager doesn't interpret raw information itself; that's a distinct cognitive function with its own charter.
- Decide load pursuit — pursuit is a Decision Card outcome for Mike, however strong the Intelligence signal.
- Alter scoring doctrine — scoring stays in the Deterministic Layer (`dispatch/scoring.py`), untouched by Manager regardless of what Intelligence recommends.
- Treat Intelligence interpretation as final approval — per `INTELLIGENCE_VERIFICATION_WORKFLOW.md` §3, only **Verified** findings "may proceed" without further gating, and even those still flow through Portal for Mike's visibility, not silently into action.

---

## 14. Manager And Alert Governance

Governing doctrine, verbatim: *"Manager may recommend alert refinement. Manager may not permanently suppress alert classes without Mike approval. Manager protects attention, but Mike governs alert behavior."* (`ALERT_GOVERNANCE_DOCTRINE.md` §7)

Stage 10's reconciliation found **five independent alert-shaped systems, none aware of the others**: Conflict Notices, `ExceptionNotice`, `IFTAException`, IFTA `plausibility_warning` (not persisted), and IFTA suspect-entries (not persisted). All five are already advisory-only "by accident of independent design," per Stage 10 — a fact worth stating plainly because it means Manager's job is not to *make* these systems advisory (they already are), it is to give Mike one coordinated view across all five instead of five separate, uncoordinated ones.

**Manager may:**
- Detect repeated alerts — the same alert firing across multiple review cycles without resolution, using Version Doctrine to identify true repeats versus new occurrences (§16).
- Recommend merge/split — e.g., "these three Conflict Notices are really one underlying issue" — as a proposal on a card, never executed automatically.
- Recommend escalation/downgrade of a specific alert instance, based on the priority framework (§9).
- Surface alert fatigue — if one alert class is firing so often it's clearly noise, Manager may flag this pattern to Mike as its own Review Card.
- Prepare Alert Governance cards summarizing cross-system alert activity for scheduled reviews.

**Manager may not:**
- Permanently suppress any alert class without Mike's explicit approval — recommending a suppression and Mike approving it are two different, sequential things; Manager's card ends where the recommendation ends.
- Hide safety/security/compliance/authority risks, ever, regardless of how it might reduce noise — this is both `MANAGER.md` §12 ("hide material risk from Mike") and Tier 1 of the priority framework (§8) at once; there is no version of "reduce noise" doctrine permits that touches Tier 1.
- Override Mike's alert preferences — if Mike has already set a preference (e.g., "don't surface routine settlement-aging checks on the morning briefing"), Manager honors it; Manager does not decide preferences on Mike's behalf, it only asks when a preference doesn't yet exist for a given case.

---

## 15. Manager And Version Doctrine

Manager uses `Ver: X` and `Last Change` (`DISPATCH_VERSION_DOCTRINE.md`) as its primary mechanism for **not re-surfacing the same thing repeatedly** — this is a load-bearing part of Attention Protection (`MANAGER.md` §10: "Keep routine work quiet").

**The rule:** Manager tracks, per Work Item/card source, the last version it already surfaced to Mike. On the next scheduled review or trigger, Manager compares current `version`/`last_change` against what it already showed. If unchanged, it does not re-surface — the item stays silently logged. If changed, it surfaces again, using the `last_change` plain-language label (e.g., "Rate Updated," "Mike Requested Revision") rather than a raw timestamp, exactly as `DISPATCH_VERSION_DOCTRINE.md` §4's worked example does: *"HIGH VALUE MATCH / Score: 97% / Ver: 9 / Last Change: Rate Updated"*.

**Examples:**
- **Repeated high-value opportunity** — if a sandbox entry stays at the same `version` across three scheduled reviews, Manager shows it once, then keeps it in the background until either its version changes or Mike hasn't acted and its priority tier demands re-escalation regardless (Tier 1–2 items don't go silent just because they're unchanged).
- **Repeated suspect entry** — same version across review cycles means Manager doesn't re-flag it as new; it stays in the standing IFTA review list without generating a fresh card each time.
- **Repeated archive review item** — an item sitting unresolved in the Archive Review Queue doesn't get a new card every monthly cycle; it gets counted in the summary, with age noted, not re-announced as if new.
- **Repeated Publisher draft** — a draft still at READY status with no version change since Manager last surfaced it doesn't regenerate a Review Card; it's still pending, not newly pending.
- **Repeated Security alert** — a security pattern already surfaced and acknowledged by Mike doesn't reappear identically; only a *new* pattern or a version-changed severity does.

**Why not timestamps:** `DISPATCH_VERSION_DOCTRINE.md` is explicit that a raw timestamp is "strictly less useful under time pressure" than a `Ver:`/`Last Change` pair — a timestamp tells Mike *when* something happened, not *whether it's the same thing he already saw*. Manager's whole purpose is protecting attention; using version identity rather than time-based staleness to decide what's worth re-showing is the mechanism that actually does that.

---

## 16. Manager And Stage Launch Packages

Manager tracks the state of the Migration Plan (`DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`) as **planning-artifact awareness**, not as Dispatch runtime Work Items — the 13 stages live in the Claude-3 governance repository, not in the Dispatch Spine's `work_items` table, and Manager should not force them into a schema built for operational work.

**Manager should track:**
- **Current stage** — which of the 13 is active, per the cross-reference table.
- **Dependencies** — which stage is blocked on which prior stage's Stop/Go criteria.
- **Open questions** — each stage's unresolved questions for Mike, so a Stage Gate Card can list them directly rather than making Mike re-read the launch package.
- **Approval status** — approved/executed vs. analysis-only-delivered vs. pending, per `DISPATCH_BLUEPRINT_DECISION_LOG.md`.
- **Test status** — pass/fail counts from the most recent walkthrough report for a stage.
- **Walkthrough reports** — whether one exists and what it confirmed.
- **Blocked items** — anything explicitly deferred (e.g., Portal-Wide Enforcement, Archive Review Queue).
- **Next recommended stage** — Manager's own synthesis of the above.

**Manager may recommend next stage.** Manager may not approve it — that remains a verbatim "Approve Stage N" from Mike, exactly as every stage in this Migration Plan has required so far, with no exception carved out for Manager itself.

---

## 17. Manager Decision Routing Model

| Category | Definition | Examples |
|---|---|---|
| **Auto-log** | Logged for the record, no card, no interruption. Routine, expected, low-risk. | Routine system status; a successful non-critical test; ordinary document ingestion (human-placed Library upload, per §10); a single login success; a stalled-load check finding nothing stalled. |
| **Prepare for review** | Worth Mike's attention when he has a moment, not urgently. Review Card, Level 2. | Publisher draft ready; an item entering the Archive Review Queue; a repeated alert pattern crossing the fatigue threshold (§14); a stale Library asset. |
| **Escalate to Mike** | Cannot wait for a scheduled review; Decision, Conflict, or Authority Card, Level 3–5. | An authority action awaiting sign-off; a deployment/promotion gate; an external submission ready to go; a contract commitment; a security risk pattern; a legal/compliance risk; a proposed doctrine change. |

The category a trigger lands in follows directly from the priority tier it belongs to (§8) and the card level it would generate (§7) — this table is a restatement of those two frameworks from the "how urgently does Mike need to know" angle, not a fourth independent system.

---

## 18. Manager Policy Engine Relationship

This mission is explicit: **do not design GX, do not implement GX.** This section only describes how Manager's *existing* doctrine could later support a policy-routing layer, without building one.

Manager already produces exactly the kind of structured, classified, prioritized output a future policy engine would need as its input — that's what §5's trigger table and §17's routing categories already are. If Mike later wants a policy engine (a "GX") to make faster low-stakes routing calls, the natural seam is that Manager's **Auto-log** category is the only place such a thing could ever act without a person in the loop, because Auto-log is already defined as "routine, expected, low-risk" with no card and no decision attached.

**What Manager may recommend to a future policy engine** (recommendations only — nothing here is decided by this document):
- Routine documentation actions already classified Auto-log.
- Stage transition recommendations, still requiring Mike's verbatim approval exactly as today.
- Test report generation.
- Harmless report creation (Staff Reports, status summaries).
- Security escalation — recommend that a pattern needs Authority attention, never resolve it.
- Authority escalation generally.

**What must remain human authority, permanently, regardless of any future policy engine:** everything in `DISPATCH_CONSTITUTION_v3.md` §15's Universal Forbidden Actions list — approve, submit, certify, sign, invent facts, decide rates, decide compliance, decide legal sufficiency, decide business strategy, decide government pursuit, decide final package readiness, book loads, commit company assets, promote drafts into Library truth, alter doctrine, alter architecture, change role boundaries, create new agents without approval, bypass Portal, bypass Manager when escalation is required, bypass Mike. A policy engine inherits Manager's boundaries; it does not get to renegotiate them by being a different kind of system.

---

## 19. Manager Data Model Candidate

Design only — no tables created by this document.

| Candidate record | Purpose | Owner | Relationship to Spine | Needed now or later? |
|---|---|---|---|---|
| `manager_notifications` | Manager's own log of what it surfaced and when, distinct from the underlying `events` — this is Manager's memory of its own past output, used for Version-Doctrine-based dedup (§16). | Manager | References `work_item_id`, does not duplicate Spine's `events` table — Spine records what happened; this records what Manager *told Mike* about it. | Later — needed once Manager actively surfaces recurring items and must avoid re-showing them. Not needed for a first design/reconciliation pass. |
| `manager_recommendations` | Manager's routing/classification recommendations, kept as their own auditable record separate from the `PortalCard.recommendation` field, so a recommendation's history survives even if the card is later dismissed. | Manager | Loosely linked to `work_item_id` and `card_id`. | Later — useful once volume makes "what did Manager suggest last time" worth querying independently of card history. |
| `manager_stage_status` | A local cache of the Claude-3-side Stage Launch Package status table (§16), so Manager doesn't need to fetch it live from the other repository on every scheduled review. | Manager | Not Spine-owned at all — this mirrors a Claude-3 governance artifact, not a Dispatch Work Item. | Later, and only if stage tracking needs to be fast/offline; a live read is simpler and avoids a stale-cache risk until proven necessary. |
| `manager_attention_queue` | The current, live-ranked list of what's waiting for Mike, computed from `work_items` + `portal_cards` + the priority framework — essentially a materialized view, not new source-of-truth data. | Manager | Fully derived from Spine data; could plausibly be a query rather than a table. | Later, and only as a performance optimization if computing it live becomes slow — this is the strongest candidate for "don't build a table you don't need yet." |
| `manager_alert_summaries` | Rolled-up counts/patterns across the five alert-shaped systems (§14) for a given review period — e.g., "Conflict Notices: 3 open, 1 stale." | Manager | Reads from all five underlying systems; writes only a summary, never touches their source records. | Later — needed once Alert Governance's cross-system view is actually built; premature before that. |
| `manager_work_item_links` | Explicit many-to-many links when one real-world issue spans multiple Work Items across functions (e.g., a Publisher draft blocked by a missing Library asset). | Manager | References multiple `work_item_id`s. | Later — a genuine need once cross-function coordination volume justifies it; `WorkItem.related_files`/`source_refs` may already cover the simple cases. |

**None of the above is needed for Phase M1** (this document). They are candidates for Phase M2 onward, and each should get its own narrow design/approval pass before a single `CREATE TABLE` is written, per `DISPATCH_CONSTITUTION_v3.md` §20's Implementation Rule.

---

## 20. Manager Implementation Phases

| Phase | Goal | Modules Affected | Dependencies | Tests Required | Human Review? | Stop/Go |
|---|---|---|---|---|---|---|
| **M1 — Manager Reconciliation and Design** | This document. Establish doctrine-to-codebase mapping, trigger model, card model, priority framework. | None (Claude-3 only) | Stages 4, 5, 7 (Spine, Portal cards, Security) already built. | None — design only. | Yes — Mike review of this document. | Go when Mike approves this design, or sends it back for revision. |
| **M2 — Manager Notification Store** | Build the minimal read layer that lets Manager consume existing signals (`dispatch/notifications.py` triggers, Conflict Notices, security events) into one internal, queryable view — no new Work Items yet, no cards yet. | New, narrow module reading existing tables. No writes. | M1 approved. | Read-only integration tests against existing fixtures. | Yes, walkthrough required. | Go only if this introduces zero behavior change to any existing notification/alert system. |
| **M3 — Manager Portal Card Preparation** | Wire `create_portal_card()` calls for the highest-value, lowest-risk card types first (Status, Review) from the M2 signal store. | `dispatch/spine/store.py` (consumer only), new Manager card-preparation code. | M2 complete. | Card-creation tests; no-duplicate-card tests (Version Doctrine dedup). | Yes, walkthrough required, live Portal demonstration. | Go only if no existing card-producing code path (Sandbox, Conflict) is altered — additive only. |
| **M4 — Manager Stage Gate Monitor** | Track Stage Launch Package status (§16) and prepare Stage Gate Cards. | Claude-3-side read (via whatever mechanism Mike approves — manual sync or otherwise; not specified here), Manager card layer. | M3 complete. | Tests confirming Manager never writes to the Claude-3 tracking documents themselves. | Yes. | Go only if Manager remains strictly read-only against `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`/`DISPATCH_BLUEPRINT_DECISION_LOG.md`. |
| **M5 — Manager Archive / IFTA Monitor** | Surface Archive review needs (once the Archive Review Queue itself exists — a prerequisite build, not part of this phase) and IFTA exceptions/suspect entries. | Read-only against `portal/models/archive.py`, `dispatch/services.py` IFTA functions. | M3 complete; Archive Review Queue build (a separate, not-yet-authorized stage) for the Archive half specifically. | Tests confirming read-only access; no archive record is ever modified by Manager. | Yes. | Go on IFTA half independent of Archive half, since IFTA exceptions already exist as records and don't require a prerequisite build. |
| **M6 — Manager Security Alert Monitor** | Read `dispatch/security/store.py::list_security_events()`, detect patterns, prepare Security Alert Cards. | Read-only against `dispatch/security/`. | M3 complete; Stage 7 (already built). | Tests confirming zero write access to `users`/`pin_records`/`sessions` tables — a structural guard test, matching the pattern already used in `tests/test_security_foundation.py`. | Yes, and this walkthrough should be as rigorous as Stage 7's own, since it touches security-adjacent surface. | Go only if a structural guard test proves Manager code never calls any `dispatch.security.auth` write function. |
| **M7 — Manager Policy Routing Hook Candidate** | Define (not build) the interface shape a future policy engine could consume from Manager's Auto-log category — documentation only, possibly a narrow read-only API surface if Mike wants one. | None, or a narrow read-only endpoint at most. | M2–M6 complete, giving Manager enough real classified output to know what a policy hook would actually need. | N/A unless code is written, which is not this phase's default scope. | Yes, and this phase should not proceed past design without Mike explicitly deciding he wants a policy engine at all — see §18. | Go/No-Go on this phase is itself a full Mike decision, not an assumed next step. |

Each phase follows `DISPATCH_CONSTITUTION_v3.md` §20 exactly: no spec, no prompt, no build, no approval, no implementation — in that order, for every phase, not just M1.

---

## 21. Manager Build Matrix

| Task Name | Existing File/Module To Inspect | Doctrine Source | Required Change | Reuse/Modify/Build New | Tests Required | Approval Needed Before Merge | Priority |
|---|---|---|---|---|---|---|---|
| Signal read layer (notifications, exceptions, conflicts) | `dispatch/notifications.py`, `dispatch/services.py`, `portal/models/conflict.py` | `MANAGER.md` §4 | New read-only aggregation module | Reuse existing triggers, build new aggregator | Read-only integration tests | Yes — design + Mike approval | High |
| Work Item classification | `dispatch/spine/models.py::WorkItem` | `MANAGER.md` §7 | Apply 9-class taxonomy as derived data, not schema change | Reuse `WorkItem` fields (`priority`, `assigned_function`) | Classification unit tests | Yes | High |
| `ROUTED_TO_MANAGER` transition targets | `dispatch/spine/state.py` | Spine Spec §7; this document §6 | Define allowed outbound transitions from `ROUTED_TO_MANAGER` | Modify `ALLOWED_TRANSITIONS` (Spine schema amendment, not Manager code) | Full Spine regression, matching Stage 4's own test rigor | Yes — this is a Spine change and needs the same design discipline as Stage 4 itself | High |
| Card preparation layer | `dispatch/spine/store.py::create_portal_card()` | `DISPATCH_CONSTITUTION_v3.md` §17; this document §7 | New Manager-side caller, no schema change | Reuse existing function | Card creation + dedup tests | Yes | High |
| Card level unification | `portal/models/sandbox.py`, `portal/models/conflict.py`, `dispatch/spine/models.py::PortalCard` | This document §4 (flagged Conflict) | Reconcile three independent 0–5 implementations into one shared source of truth | Modify (careful, additive-first) | Regression across all three existing card-producing paths | Yes, and this one specifically needs its own design pass — it's a pre-existing Conflict, not new Manager scope | Medium |
| Priority ranking engine | New | This document §8 | New, small, pure-function ranking logic | Build new | Unit tests per tier, conflict-handling tests | Yes | High |
| Version-based dedup (`manager_notifications` candidate) | New | This document §16, §19 | New table only if M2's live-query approach proves insufficient | Build new, deferred | Dedup correctness tests | Yes | Medium |
| Security event pattern detection | `dispatch/security/store.py` | `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §12.1; this document §9 | New read-only pattern detector | Build new | Structural no-write guard tests (matching `tests/test_security_foundation.py` convention) | Yes, rigorous | Medium |
| Stage Launch Package tracker | `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md` (Claude-3 side) | This document §16 | Read mechanism TBD — not specified here | Build new | Read-only tests | Yes | Low |
| Archive Review Queue trigger consumption | `portal/models/archive.py` | `ARCHIVE_REVIEW_POLICY.md`; this document §11 | Blocked on a prerequisite Archive Review Queue build (out of Manager's own scope) | N/A until prerequisite exists | N/A | N/A until prerequisite build is approved | Low (blocked) |
| Policy routing hook | New | This document §18 | Interface documentation only, code only if separately approved | Design only for now | N/A | Yes, full separate Mike decision | Low |

---

## 22. Manager Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Manager becomes chatbot | No direct human-facing conversational surface exists in this design (§3: Presentation Layer is Portal-only). Every human-facing output is a Portal card. No chat endpoint is proposed anywhere in §20–21. |
| Manager becomes router | Manager recommends routing and, for already-defined Spine transitions, executes the specific move through `transition()`/`apply_transition()` — the same mechanism every function uses. It never invents new routing logic outside Spine's `ALLOWED_TRANSITIONS`, and it never becomes the thing that decides *whether* a transition is allowed — the Spine already owns that. |
| Manager bypasses Spine | §6 states explicitly and repeatedly: no direct `current_state` writes, ever. M6's structural guard test pattern (already proven in Stage 7) is the concrete enforcement mechanism — a source-scanning test that fails the build if Manager code ever writes `current_state` outside `apply_transition()`. |
| Manager hides alerts | §14 explicitly forbids permanent suppression without Mike's approval and forbids hiding Tier 1 risk under any circumstance. The Version Doctrine dedup mechanism (§16) reduces *repeated* surfacing of the *same* unchanged item — it never suppresses a genuinely new or changed signal. |
| Manager over-notifies Mike | The entire Priority Framework (§8), card-level model (§7), and Attention Protection Rules (`MANAGER.md` §10) exist specifically to prevent this — Auto-log is the default for anything not classified above it (§17), not an afterthought. |
| Manager duplicates Portal | Manager has no rendering surface of its own — it writes to `portal_cards`, which Portal already renders. §7's card model reuses the exact schema Stage 4/5 already built; nothing new is rendered outside Portal. |
| Manager approves actions | §6 and §7 both state Manager never writes an `ApprovalEvent` representing Mike's decision. Every card's `required_closing` is the fixed non-authorization sentence. This is the single most repeated constraint in this document by design. |
| Manager blurs with Intelligence | §13 draws the line explicitly: Intelligence supplies meaning, Manager prioritizes and routes it. Manager never interprets raw information itself — it consumes Intelligence's already-interpreted output. |
| Manager blurs with Publisher | §12 draws the same line: Manager assigns and routes Publisher work, it never drafts, approves, or submits Publisher output itself. |
| Manager becomes autonomous agent | Activation is strictly limited to the four trigger classes (§5) — Manager does not act outside a trigger firing, and every trigger in §5 traces back to Scheduled Review, Workflow Event, Exception Condition, or Portal-Mediated Human Action, with no fifth "Manager decided to check on something" class introduced anywhere in this document. |
| Manager conflicts with future policy engine | §18 explicitly declines to design or implement a policy engine and states that any future one inherits Manager's boundaries rather than renegotiating them — the Universal Forbidden Actions list (`DISPATCH_CONSTITUTION_v3.md` §15) binds any future system operating in Manager's role, not just Manager's own code. |

---

## 23. Final Recommendation

**Is Manager sufficiently defined after this document?** Yes, for the purpose of implementation *planning*. `MANAGER.md`'s doctrine was already complete; what was missing was the reconciliation against the actual, running codebase — which triggers exist and which don't, which card infrastructure is reusable and which needs unification, exactly where Manager sits relative to the Spine's `ROUTED_TO_MANAGER` dead end, and how Manager's boundaries interact with Security, Library, Archive, Publisher, Intelligence, and Alert Governance as those functions actually exist today rather than as they were originally specified. That reconciliation is now done.

**Is Manager ready for implementation planning?** Yes, in the same sense every other stage in this Migration Plan became ready after its reconciliation: the next step is a launch package (a "Stage 11a," or wherever Mike wants it sequenced in the 13-stage table), not code. This document is not that launch package — it is the design a launch package would cite.

**What should be built first?** Phase M2 (Notification Store) and M3 (Portal Card Preparation), in that order. They are the lowest-risk, highest-value slice: read-only aggregation of signals that already exist, followed by reusing Portal card infrastructure Stage 5 already proved works. Neither touches Security, Archive, or the Spine's state machine.

**What should not be built?** The `ROUTED_TO_MANAGER` transition-target amendment (§6, §21) and the card-level unification across `sandbox.py`/`conflict.py`/`PortalCard` (§4, §21) should wait until M2/M3 prove out the simpler pieces — both are pre-existing structural gaps this document surfaced, not new Manager scope, and both deserve their own narrow design pass rather than being bundled into Manager's first build. The Policy Routing Hook (M7, §18) should not be built at all until Mike makes a separate, explicit decision that a policy engine is something he wants — this document takes no position on that question.

**What requires Mike's decision?** Everything in §20's "Human Review?" column, without exception — but concretely, right now: (1) whether to add a dedicated Manager stage to the 13-stage plan at all, closing the gap Stage 11 flagged; (2) if so, where it sits in the stage numbering and what it depends on; (3) whether M2/M3 should be scoped as one combined launch package or two sequential ones; (4) whether a policy engine is wanted at all (§18) — no default assumption either way.

**What should Claude review next?** The card-level unification Conflict (§4, §21) — three independent 0–5 implementations of the same doctrine concept is the kind of drift that gets harder to fix the longer it's left alone, and it predates Manager entirely (it's a Stage 5 byproduct). A short, standalone reconciliation of just that one item, before Manager's own build begins, would prevent Manager from becoming a fourth independent implementation of the same scale.

**What should never be delegated to Manager?** Every item in `DISPATCH_CONSTITUTION_v3.md` §15's Universal Forbidden Actions list, permanently — approval, submission, certification, signing, fact invention, rate/compliance/legal-sufficiency decisions, business strategy, government pursuit decisions, final package readiness, load booking, asset commitment, Library truth promotion, doctrine or architecture change, role boundary change, new-agent creation without approval, bypassing Portal/Manager-escalation/Mike. This list does not shrink as Manager matures; nothing in this design proposes narrowing it.

**What is the cleanest first Manager prototype?** A read-only Staff Report generator: Manager reads `dispatch/notifications.py`'s existing trigger points, `portal/models/conflict.py`'s Conflict Notices, and `dispatch/spine/store.py`'s `list_work_items()`, classifies each per `MANAGER.md` §7, ranks by the priority framework (§8), and produces one combined Status/Review card set for a single scheduled review — no new Work Items, no new writes to `work_items.current_state`, no security or archive scope yet. It proves the classification and prioritization logic in isolation, against real data, with the smallest possible write surface (`portal_cards` only), before anything touches the Spine's state machine or the security/archive boundaries this document also defines.

Mike decides.

---

*End of DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md.*
