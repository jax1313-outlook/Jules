# DISPATCH_INTEGRATED_BLUEPRINT_v1.md

**Document Type:** Two-Repository Integration Blueprint
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Integration Blueprint Draft — bridges Claude-3 governance and Dispatch implementation
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document explains how two repositories — **Claude-3** (architecture, governance, doctrine, the final blueprint) and **Dispatch** (`jax1313-outlook/Dispatch`, the working implementation: `cin_lite/`, `dispatch/`, `portal/`, `sync/`, tests, deployment tooling, and a real phase-by-phase build history) — converge into one governed Dispatch platform.

This is not another architecture review, and it does not replace `DISPATCH_FINAL_BLUEPRINT_v1.md` — it extends that blueprint by reconciling it against real, working code. It is companion to `DISPATCH_REPO_RECONCILIATION_MATRIX_v1.md`, which this document cites throughout by row number.

No recommendation in this document authorizes deployment, production code, code merge, external submission, autonomous booking, autonomous approval, autonomous contract commitment, or authority transfer. This document does not propose deleting Dispatch, replacing Dispatch wholesale, resurrecting the 11-agent mesh, or using the Dispatcher Agent name. Existing code is never treated as approved merely because it exists; architecture is never treated as implemented merely because it is documented.

**Mike Zachary is final authority. Mike decides.**

---

## 1. Executive Integration Summary

**What Claude-3 contributes:** the governing law (Constitution, five-layer architecture, human authority model), the doctrine hardening layer (Version Doctrine, Intelligence Verification, Alert Governance, Security & Authentication), the Dispatch Spine specification (schemas, states, transitions), and `DISPATCH_FINAL_BLUEPRINT_v1.md` as the current target architecture.

**What Dispatch contributes:** a real, running, tested platform — a Flask portal, a SQLite-backed domain model (loads, IFTA, fleet, financials), a government-contract intelligence pipeline (`cin_lite/`) with nine deterministic rule modules and five bounded Claude-backed agents, a fail-closed archive-integrity mechanism, a proven IFTA finalization gate, 90 test files at 90% CI-enforced coverage, and a disciplined change-approval history (`DECISION_LOG.md` plus a walkthrough report for every governed change).

**Why both are needed:** Claude-3 without Dispatch is architecture nobody can use. Dispatch without Claude-3 is a real, valuable system with no authentication, no audit trail, no version doctrine, and at least one direct doctrine conflict (Library auto-approval, Reconciliation Matrix row 8) that a future user could reasonably rely on and be misled by. Neither repository alone is the platform; together they are.

**What the integrated Dispatch platform becomes:** Dispatch (the implementation repo) remains the production-intent codebase. It absorbs Claude-3's doctrine as retrofitted schemas, security foundations, and governance controls layered onto its existing working code — not a rewrite. Claude-3 remains the standing governance authority that the Dispatch repo's own `CLAUDE.md`, `DECISION_LOG.md`, and future launch packages must answer to.

**What must not happen:** Claude-3 must not be treated as replacing Dispatch's working code. Dispatch's existing code must not be treated as already satisfying doctrine merely because a same-named file exists (e.g., `portal/models/library.py` is not a governed Library — Matrix row 8). No autonomous action of any kind is authorized by this integration. No deployment, no code merge, and no production change is authorized by this document.

---

## 2. Source-of-Truth Hierarchy

1. **Mike Zachary** — final authority over all of it. Nothing below overrides Mike.
2. **Claude-3** — architecture and governance authority. When Dispatch's existing code conflicts with Claude-3 doctrine, Claude-3 governs (e.g., Library auto-approval must change; the doctrine does not bend to match the code).
3. **`DISPATCH_FINAL_BLUEPRINT_v1.md`** — the current target architecture within Claude-3. All integration work aims at this document's structure (five layers, six organizational functions, the Spine).
4. **`DISPATCH_REPO_RECONCILIATION_MATRIX_v1.md`** — the migration guide: the concrete, row-by-row bridge between target architecture and current code.
5. **Dispatch (`jax1313-outlook/Dispatch`)** — the implementation asset base. It is not a second, competing source of truth; it is where the doctrine gets built, and where valuable working patterns (the IFTA approval gate, the archive hashing mechanism, the deterministic rule modules) already exist and should be reused, not overridden by rewriting from scratch.

When Dispatch already implements something compatible with Claude-3 doctrine — even under a different name — preserve and adapt it. When it conflicts, Claude-3 governs, and the conflict is resolved by modifying Dispatch, never by weakening Claude-3 doctrine to fit existing code.

---

## 3. Current Dispatch Implementation Assessment

Dispatch is not a blank slate and not merely a prototype. It is a working, tested, two-domain platform:

- **`cin_lite/`** — a government-contract intelligence pipeline: SAM.gov acquisition (with local-sample fallback), nine deterministic rule modules producing structured `RuleResult` JSON, five bounded Claude-backed agents (extractor, summarizer, router, proposal writer, receipt-vision — every one with a deterministic/graceful fallback when no API key is configured), a checkbox-driven email control gate (5 actions), and a fail-closed, SHA-256-hash-verified archive.
- **`dispatch/`** — a SQLite-backed trucking/load-board domain: 27 tables covering loads, milestones, evidence, exceptions, POD, retention, financials, fleet, and IFTA compliance, each with a validated status enum. `IFTAReportApproval` is a genuine draft→sealed decision-gate object — the strongest Approval Event analogue in the codebase.
- **`portal/`** — a Flask app exposing ~180 routes across contract-pipeline, load-board, and IFTA workflows, plus six JSON-file-backed models (`sandbox`, `conflict`, `publisher`, `library`, `intelligence`, `archive`) that already loosely mirror Claude-3's organizational function names.
- **`sync/`** — a pull-only, manifest-tracked, conflict-preserving VPS-to-local sync utility, currently disconnected from the rest of the system.
- **`tests/`** — 90 test files; CI enforces 90% coverage on `cin_lite` and `dispatch` across Python 3.11–3.13.
- **`DECISION_LOG.md`** + 7 phase walkthrough reports — a real, working governance discipline: every change to a "governed capability" (the IFTA engine, the archive layer, the finalization gate) required Mike's verbatim approval and produced a walkthrough report before merging.

None of this is assumed obsolete. Sections 4–14 map each piece to Claude-3 doctrine in detail. The headline assessment: **Dispatch already prototypes roughly half of the Claude-3 MVP checklist**, under different names and without a unifying Spine — the integration work is substantially about naming, formalizing, and connecting what exists, plus building the parts that are genuinely missing (chiefly security/authentication and a unified Spine).

---

## 4. Architecture-to-Implementation Mapping

| Claude-3 Area | Already Implemented? | Partially Implemented? | Missing? | Conflicting? | Recommended Path |
|---|---|---|---|---|---|
| Authority Layer (Mike) | — | Yes — `DECISION_LOG.md` process | — | — | Formalize as the build-time Implementation Rule; extend toward runtime Approval Events |
| Presentation Layer (Portal) | — | Yes — home/queues/brief pages, `card_visual()` | — | — | Add `card_level`, version display; see §7 |
| Manager | — | Yes — `notifications.py` triggers | Cognitive prioritization layer | — | Integrate triggers; build the coordination layer on top |
| Publisher | — | Yes — `proposal_writer.py`, publisher queue | Approval enforcement | — | See §6, Matrix row 6 |
| Intelligence Analyst | — | Yes — extractor/summarizer/router agents | Verification classification | — | See §13 |
| Library | — | — | Promotion workflow, versioning | **Yes** — auto-approves everything | See §5, Matrix row 8 |
| Archive | — | Yes — `cin_lite/archive.py` hashing; `portal/models/archive.py` weak | Review queue, retention rule | — | Keep hashing; build queue (§8) |
| Dispatch Spine | — | Fragments only (Sandbox, SQLite, IFTA gate) | Unified schemas/state machine | — | Build New, informed by fragments (§6) |
| Version Doctrine | — | — | Entirely | — | Build New (§12) |
| Intelligence Verification | — | Yes — suspect-entries confidence threshold | Formal classification | Partially — Library's auto-approval conflicts | See §13 |
| Alert Governance | — | Yes — advisory-only exceptions/warnings by design | Mike-facing governance controls | — | See §14 |
| Security & Authentication | — | — | Entirely — zero auth of any kind | — | Build New (§11), Critical priority |
| Driver Portal | — | Yes — data model only | Access boundary | — | See Matrix row 3 |
| Broker/Customer Portal | — | — | Entirely (as an external boundary) | — | Build New, Future priority |
| Telematics | — | — | Entirely | — | Placeholder schema only, matches Blueprint §17's own deferred status |

---

## 5. Reuse Strategy

**Keep what matches** (no change needed): `dispatch/scoring.py`, `dispatch/db.py`'s SQLite pattern, `cin_lite/archive.py`'s hashing mechanism, `cin_lite/rules/*` (all nine deterministic modules), CI configuration, the test harness, local deployment tooling, `IFTAReportApproval`'s gate *mechanics* (its identity layer needs modification — see below).

**Modify what partially matches**: `portal/models/library.py` (remove unconditional auto-approval — Critical, Matrix row 8), `portal/models/archive.py` (add versioning/review-queue behavior), `portal/models/publisher.py` (enforce the existing `human_approval_required` flag instead of leaving it unchecked), the three HMAC email-decision gates (retrofit real identity onto working gate mechanics rather than replacing them), `DEPLOY_VPS.md`'s deployment posture (do not act on it until Security Foundation lands).

**Archive historical experiments**: none identified in the active Dispatch repo requiring archival at this time — `Dispatch-Old` exists as a separate repository and is explicitly out of scope for this integration per instruction.

**Reject architecture-breaking assets**: none found. Every asset inspected is either directly reusable, adaptable, or a clean placeholder gap — no asset actively contradicts Claude-3 doctrine in a way that can't be corrected in place (even Library's conflict is a one-function fix, not a structural rebuild).

**Build missing capabilities only after reconciliation**: Security/Authentication (Matrix rows 13, 29–31), the unified Spine schemas (row 10), Version Doctrine fields (row 26), and the External Viewer boundary (row 4) have no existing asset to adapt and must be built new — but only after the reconciliation in this document is reviewed by Mike, per the Migration Plan's staged gates (§16).

---

## 6. Dispatch Spine Integration Plan

**Can existing code become the first Spine candidate?** Partially, and only as a foundation to build on top of — not as a drop-in replacement.

**What already exists that's usable:**
- `dispatch/db.py`'s SQLite pattern (WAL mode, foreign keys enforced, idempotent `ALTER TABLE` migrations already proven twice) is a sound persistence mechanism for the Spine's Work Item, Event, Portal Card, Approval Event, Conflict Event, and Audit Event tables.
- `sandbox.py`'s `STATUSES` enum + append-only `events` list is the closest existing analogue to a Work Item + Event pair, and its `_validate_choice()`-style construction-time validation is a reasonable pattern to generalize into the Spine's state-transition guard.
- `IFTAReportApproval`'s draft→sealed freeze is a genuine, working, tested Approval Event pattern — its *mechanics* (freeze a snapshot, refuse resubmission, idempotent re-approval, insert-only exception ledger) should become the template for the Spine's generic Approval Event and Conflict Event handling.

**What must be built:**
- Generic `work_items`, `events`, `portal_cards`, `approval_events`, `conflict_events`, `audit_events` tables per `DISPATCH_SPINE_SPECIFICATION_v1.md` §5–14, added alongside (not replacing) the existing domain tables (`loads`, `ifta_report_approvals`, etc.).
- A shared state-transition guard function that existing entity-specific state machines (Load, Settlement, IFTAReportApproval) can be migrated to call, rather than only validating enum membership.
- The approved transition table itself (`DISPATCH_SPINE_SPECIFICATION_v1.md` §7) does not exist anywhere in Dispatch today and must be built new.

This is a **Build New, informed by Integrate** posture: the Spine is designed from the doctrine, but its first implementation deliberately reuses Dispatch's proven SQLite/migration/freeze-and-audit patterns rather than inventing new persistence machinery.

---

## 7. Portal Integration Plan

Existing portal implementation maps as follows:

- **Mike Cockpit** → `home.html`, `queues.html`, `brief.html` are the existing cockpit surface; they need `card_level` and version display added, not replacement.
- **Card workflow** → `sandbox.py` entries plus `helpers.card_visual()` are the existing card-rendering path. `card_visual()`'s score-threshold labeling (`HIGH VALUE MATCH` / `STRONG MATCH` / etc.) already implements the *visual* half of the Version Doctrine's own worked example (`DISPATCH_VERSION_DOCTRINE.md` §4) — it is missing only the `Ver: X` / `Last Change:` half.
- **Decision cards / Review cards / Status cards** → map to Sandbox's `STATUSES` transitions and Conflict's `severity` field; no explicit card-level taxonomy exists yet — add it as a field, not a rewrite.
- **Conflict cards** → `portal/models/conflict.py`'s `create_notice()`/`resolve_notice()` is a real, working Conflict Event analogue (Matrix row 12) but is advisory-only today (nothing blocks on an unresolved conflict) — this matches the *behavior* Alert Governance doctrine wants for non-critical alerts, but Conflict Notices tied to authority-level risk must actually gate, per Constitution §19.
- **Authority cards** → no existing analogue; must be built alongside the Security Foundation wave, since an Authority card is meaningless without an authenticated Authority role to act on it.
- **Version display** → entirely missing (Matrix row 26); add as a field on Sandbox/Library/Archive/Publisher records first.
- **Alert governance controls** → no Mike-facing suppress/merge/split UI exists; the underlying advisory alerts it would control (IFTA exceptions, plausibility warnings, conflicts) already exist and behave correctly.
- **Approval actions** → the three existing HMAC email-decision gates are the closest analogue to Portal-mediated approval actions; they need an authenticated-identity layer, not a new interaction model.

---

## 8. Archive Integration Plan

- **`cin_lite/archive.py`** already implements fail-closed, SHA-256-hash-verified read/write for the CIN contract archive (`Raw`/`Processed`/`Intelligence`/`Summaries`/`Routing`) — this satisfies, and exceeds, the Decision Matrix's own MODIFY instruction to use SHA-256 over MD5. **Keep as-is.**
- **`_write_compliance_record()`** in `dispatch/services.py` applies the identical hash-sidecar technique to IFTA compliance records, kept as a sibling of the CIN archive rather than nested under it — a deliberate, sound design choice already made and documented. **Keep as-is.**
- **Current Version + Three Previous Versions retention rule** (`ARCHIVE_REVIEW_POLICY.md` §2) has no existing analogue — `portal/models/archive.py`'s `create_record()` silently no-ops on a duplicate `source_id` rather than versioning it. This must be built new.
- **Archive Review Queue / Monthly Report / Monday Report escalation / Keep-Delete** — none exist today. Build new, using `portal/models/archive.py`'s existing section structure (`load, decision, publisher, location_history, broker_history`) as the record source once versioning is added.
- **Audit trail** — `portal/models/archive.py`'s docstring mentions "audit bundles" but no such structure exists in code (confirmed by grep). The Audit Event schema (§6) will supply this once built; Archive should consume it, not invent a parallel mechanism.

---

## 9. IFTA and Existing Workflow Integration

**Decision: IFTA becomes the proof-of-concept workflow for the Spine's Approval Event and exception/verification model — not a separate feature family, and not folded generically into "Archive/Compliance" as a label.**

Reasoning: `IFTAReportApproval`'s draft→sealed freeze, its six advisory exception detectors, and its `extraction_confidence`-based suspect-entries panel together form the most complete, tested, real-world instance of "deterministic computation → advisory findings → human-gated freeze → hash-verified archive" anywhere in Dispatch. Rather than build the Spine's Approval Event and Intelligence Verification schemas from nothing and separately port IFTA to them later, the recommended path is:

1. Treat IFTA's existing gate as the reference implementation while the generic Approval Event schema is designed (§6).
2. Once the generic schema exists, migrate `IFTAReportApproval` onto it (a Modify, not a rebuild — the freeze/refuse-resubmission/idempotent-reapproval logic is already correct and should be preserved).
3. Use the six exception detectors as the template for a general exception/alert framework (Alert Governance, §14), and the suspect-entries confidence threshold as the template for Intelligence Verification's Partially Verified classification (§13).

This keeps IFTA's own users (the compliance-record workflow Mike already approved phase-by-phase) unaffected during the transition, while letting the rest of Dispatch benefit from a pattern that's already proven in production use.

---

## 10. Sync Utility Integration Plan

The sync utility supports **none of deployment/Archive-movement/backup directly today** — it is a working, well-built, but currently disconnected pull-only VPS-to-local tool. It does not touch `cin_lite/archive.py`'s Archive tree at all; its `DATA_TYPES` list includes a bucket literally named `"archive"` and one named `"library"`, but these are generic dispatch-domain JSON folders unrelated to the governed Archive/Library organizational functions.

**Recommendation: Investigate Further (Matrix row 20) before assigning it a role.** Candidate futures, none decided here:
- A genuine VPS-pull-only backup path for the eventual production deployment (its manifest/high-water-mark/conflict-preserving design is well suited to this).
- A feeder for Archive movement, if its `DATA_TYPES` buckets are formally connected to the Spine's Archive tables.
- Kept as a standalone operational utility outside the core runtime, unrelated to governance doctrine.

This requires Mike's decision on intended purpose before further build — the tool is safe to leave exactly as-is in the meantime (Low risk, Low priority).

---

## 11. Security Integration Plan

This is the integration's most urgent gap. Comparing Dispatch's actual security posture against `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md`:

| Doctrine Element | Exists in Dispatch? | Detail |
|---|---|---|
| Identity Doctrine | No | Zero identity records anywhere; grep confirmed |
| PIN Doctrine | No | Zero matches for "PIN" as a concept anywhere |
| Authority Doctrine | Partial | `DECISION_LOG.md` process captures Mike's approval of *code changes*; no runtime Authority role exists |
| Audit Doctrine | Weak | Only two hash-sidecar writes and free-text `LoadActivity`/`events` logs; no formal Audit Event schema |
| Roles (Authority/Driver/External Viewer/System Service) | No | Zero role field anywhere in the codebase |
| Approval Events tied to identity | Partial | `IFTAReportApproval.approved_by` is an email address string, not an authenticated identity |
| Driver access boundary | No | Driver data model exists; no access scoping exists |
| External Viewer access boundary | No | No external/internal separation exists at all — the whole portal is one open surface |
| System Service rules | No | No distinction between human and system actors anywhere |

**What must be built**: Identity, PIN, Session, Role, and Permission records exactly per `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §2–8, a login flow, and a retrofit of the three existing HMAC email-decision gates so `approved_by`/`entered_by` fields capture a real authenticated identity instead of a fixed reviewer email string or the literal string `"reviewer"`.

**What can be reused**: the HMAC-SHA256 token *mechanism itself* (already used correctly for possession-based link verification) can remain as a secondary confirmation layer for emailed approval links, layered on top of — not instead of — session authentication. `PORTAL_SECRET_KEY` is already configured (though currently unused) and can become the Flask session-signing key once sessions are actually implemented.

This is Critical priority and blocks VPS/network deployment entirely — `DEPLOY_VPS.md` already says so in its own words.

---

## 12. Version Doctrine Integration Plan

No object in Dispatch carries a version number or `Ver: X` display today (confirmed by grep — zero matches). Retrofit plan, in priority order:

1. **Sandbox entries** (`portal/models/sandbox.py`) — add a `version` integer, incremented on meaningful change (status change, score change, card data change), and a `last_change` label field populated at the same call sites that already write to the `events` list. This is the lowest-effort, highest-visibility retrofit, since `card_visual()` already renders the exact card shape Version Doctrine's worked example (`HIGH VALUE MATCH / Score: 97%`) targets — it only needs `Ver: 9` / `Last Change: Rate Updated` appended.
2. **Library assets** — add version fields as part of fixing the auto-approval conflict (§5) — a natural pairing, since a real promotion workflow needs version history anyway.
3. **Archive records** — add version fields as part of building the review queue (§8).
4. **IFTA records** — `IFTAReportApproval`'s `draft`/`sealed` status is itself a two-state version concept; extend it with an explicit `version` field once IFTA migrates onto the generic Approval Event schema (§9).
5. **Work items / Portal cards / load-opportunity reviews / reports** — apply once the Spine's generic schemas exist (§6), rather than retrofitting each domain table independently.

---

## 13. Intelligence Verification Integration Plan

Existing parsing/evidence/suspect-entry logic maps to the Verified / Partially Verified / Unverified / Rejected classifications as follows:

- **`extraction_confidence`** (from `receipt_vision.py`'s vision extraction, persisted on `IFTAFuelPurchase`) is a real confidence score already computed and stored. Mapping: below `DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD` (0.75) → **Partially Verified**; above threshold → still not automatically **Verified**, since a human (the dispatcher) explicitly clicking Save is the actual confirmation step today, matching doctrine's requirement that Partially Verified facts need explicit approval for use.
- **The nine `cin_lite/rules/*` deterministic modules** produce structured findings with no fabrication risk (pure regex/keyword matching, no LLM) — their output can be treated as **Verified** by construction, since it's derived directly from source text, not inferred.
- **The five Claude-backed agents' outputs** (extractor's strategic assessment, summarizer's summary, router's recommendation, proposal writer's outline) are recommendations/drafts by design and should be classified **Unverified** as factual claims (they are never claims of fact — they're interpretation) while remaining usable as Publisher/Intelligence *recommendations*, consistent with `INTELLIGENCE_VERIFICATION_WORKFLOW.md` §4's Publisher Use Rule.
- **`portal/models/library.py`'s unconditional `"approved"` status** is the direct conflict case: it currently behaves as if every record were **Verified and promoted** with zero review. Fixing this (§5, Matrix row 8) is a prerequisite for Intelligence Verification integration to mean anything for Library-bound facts.

---

## 14. Alert Governance Integration Plan

Existing alerts/warnings/panels and their mapping:

| Existing Panel | Alert Governance Mapping |
|---|---|
| IFTA plausibility warnings (mileage/MPG) | Non-blocking, informational — matches Level 1/2 |
| IFTA exception detectors (6 types) | Advisory, insert-only ledger, sealed-quarter freeze — matches doctrine's "never silently suppressed" + "frozen means frozen" principles exactly |
| Suspect Entries panel | Explicitly excluded from readiness rollup by deliberate design (Phase 7 decision) — matches doctrine's distinction between informational and governed findings |
| `portal/models/conflict.py` notices | Advisory today even for `human_decision_required=True` notices — needs a real gate for Level 4/5-equivalent conflicts |

**How Mike should control alert behavior**: none of the existing panels have a Mike-facing suppress/alter/merge/split/upgrade/downgrade control today. Recommended path: build one shared alert-governance control surface in Portal that all four panel types register against, rather than four separate ad hoc controls — this avoids replicating the same governance UI four times as Version Doctrine and card-level work land alongside it.

---

## 15. Repository Structure Recommendation

**The implementation remains in Dispatch.** Selected Claude-3 documents (the Constitution, the Final Blueprint, the Security Specification, the Spine Specification) should be copied — not moved — into a `docs/` directory inside the Dispatch repository so builders working directly in Dispatch have the governing doctrine alongside the code they're writing, exactly as `CLAUDE.md` already references `Final_Architecture_for_Hybrid_CIN-Lite_System (1).docx` as its "authoritative specification, read before generating code." Claude-3 remains the canonical, versioned source; Dispatch's copy is a working reference that gets refreshed when Claude-3 doctrine changes, never edited independently.

**Recommended future structure** (evolutionary, not a rewrite):

```text
dispatch/                    # existing repo root — kept
├── docs/                    # NEW — copied-in Claude-3 governing documents
├── cin_lite/                # existing — unchanged (Acquisition/Processing/Control/Archive/Automation)
├── dispatch/                # existing — unchanged (SQLite domain model, services, scoring)
│   └── spine/                # NEW — generic Work Item/Event/Portal Card/Approval Event/Conflict Event/Audit Event tables, additive to existing tables
├── portal/                  # existing — unchanged route/template structure
│   ├── models/               # existing six files — modified in place per §5–14, not replaced
│   └── security/              # NEW — Identity/PIN/Session/Role/Permission
├── sync/                    # existing — unchanged pending Mike's decision (§10)
└── tests/                   # existing — extended with new Spine/Security test categories, not a parallel suite
```

**This structure does not destroy existing working code.** Every existing directory is retained; new capability lands in new subdirectories (`dispatch/spine/`, `portal/security/`) or as additive changes to existing files (`portal/models/*.py`), matching the reuse-before-rebuild posture throughout this document.

---

## 16. Migration Plan

Each stage: Goal · Existing Dispatch assets affected · Claude-3 doctrine applied · Deliverables · Tests · Human review requirement · Stop/go criteria.

### Stage 1 — Inventory Freeze
- **Goal:** Freeze both repositories as the reconciliation baseline.
- **Assets affected:** None (read-only).
- **Doctrine applied:** `DISPATCH_REPO_MANIFEST_v3.md`'s document-control discipline, applied to Dispatch as well.
- **Deliverables:** This document and the Reconciliation Matrix, as the frozen baseline.
- **Tests:** None.
- **Human review:** Mike reviews and approves both documents as current.
- **Stop/Go:** Go only after Mike's explicit approval.

### Stage 2 — Documentation Import
- **Goal:** Copy governing Claude-3 documents into `dispatch/docs/`.
- **Assets affected:** New `docs/` directory only.
- **Doctrine applied:** `SUPERSESSION_MAP.md`'s current-vs-historical distinction.
- **Deliverables:** `docs/` populated with the Constitution, Final Blueprint, Security Spec, Spine Spec.
- **Tests:** None (documentation only).
- **Human review:** Confirm no legacy/superseded material is imported.
- **Stop/Go:** Go once the doc set matches Claude-3's active manifest exactly.

### Stage 3 — Blueprint Alignment
- **Goal:** Update `CLAUDE.md` to reference the imported Final Blueprint alongside (not replacing) its existing CIN-Lite architecture spec.
- **Assets affected:** `CLAUDE.md`.
- **Doctrine applied:** Full Final Blueprint.
- **Deliverables:** Updated `CLAUDE.md` pointing builders to both specs, with subsystem boundaries reconciled per §4 of this document.
- **Tests:** None.
- **Human review:** Mike confirms the reconciled subsystem boundaries.
- **Stop/Go:** Go once boundaries are unambiguous to a future builder.

### Stage 4 — Data Engine / Spine Reconciliation
- **Goal:** Build the generic Spine schemas (§6), informed by `sandbox.py` and `IFTAReportApproval` patterns.
- **Assets affected:** New `dispatch/spine/` module; no changes to existing `dispatch/models.py` tables.
- **Doctrine applied:** `DISPATCH_SPINE_SPECIFICATION_v1.md` in full.
- **Deliverables:** Work Item/Event/Portal Card/Approval Event/Conflict Event/Audit Event tables and schemas.
- **Tests:** State transition tests, schema validation tests.
- **Human review:** Mike reviews the schema design before implementation begins (per Constitution §20).
- **Stop/Go:** Go once all Spine build-readiness tests (Spine Spec §20) pass.

### Stage 5 — Portal Reconciliation
- **Goal:** Add `card_level` and version display to existing Portal pages.
- **Assets affected:** `portal/models/sandbox.py`, `conflict.py`, `helpers.card_visual()`, templates.
- **Doctrine applied:** Portal Blueprint, Version Doctrine.
- **Deliverables:** Card-level rendering, version display on Sandbox cards.
- **Tests:** Portal card tests, version display tests.
- **Human review:** Mike walks through the updated cockpit live.
- **Stop/Go:** Go when Mike confirms the cockpit reads correctly.

### Stage 6 — Archive / IFTA Reconciliation
- **Goal:** Migrate `IFTAReportApproval` onto the generic Approval Event schema; build the Archive Review Queue.
- **Assets affected:** `dispatch/services.py`, `portal/models/archive.py`.
- **Doctrine applied:** Archive Blueprint, Archive Review Policy.
- **Deliverables:** IFTA gate running on generic schema without behavior change; working Keep/Delete review queue.
- **Tests:** Archive retention tests, regression tests confirming IFTA behavior is unchanged.
- **Human review:** Mike runs one real IFTA submission/approval through the migrated path.
- **Stop/Go:** Go only if IFTA's existing tested behavior is provably unchanged.

### Stage 7 — Security Foundation
- **Goal:** Build Identity, PIN, Session, Role, Permission records and a login flow.
- **Assets affected:** New `portal/security/` module; retrofit `approved_by`/`entered_by` fields on the three email-decision gates.
- **Doctrine applied:** `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` in full.
- **Deliverables:** Working PIN login for at least an Authority role; authenticated `approved_by` on IFTA approval.
- **Tests:** PIN authentication tests, permission tests, approval audit tests.
- **Human review:** Mike tests his own login.
- **Stop/Go:** Go when Mike can log in with a PIN and every approval action captures his real identity — **this stage blocks any VPS/network deployment**.

### Stage 8 — Version Doctrine Retrofit
- **Goal:** Add version/last-change fields per §12's priority order.
- **Assets affected:** `sandbox.py`, `library.py`, `archive.py`, IFTA records.
- **Doctrine applied:** Version Doctrine.
- **Deliverables:** `Ver: X` / `Last Change:` visible on Sandbox cards first, then Library/Archive.
- **Tests:** Version display tests.
- **Human review:** Mike confirms the load-board example renders as specified.
- **Stop/Go:** Go when version increments correctly on meaningful change only.

### Stage 9 — Verification Workflow Retrofit
- **Goal:** Formalize Verified/Partially Verified/Unverified/Rejected classification; fix Library's auto-approval.
- **Assets affected:** `library.py`, `intelligence.py`, IFTA suspect-entries confidence mapping.
- **Doctrine applied:** Intelligence Verification Workflow.
- **Deliverables:** Library promotion requires an Approval Event; suspect-entries confidence maps to a real classification.
- **Tests:** Fact-grounding tests, no-fabrication tests.
- **Human review:** Mike reviews sample classifications.
- **Stop/Go:** Go when Unverified/Rejected facts are structurally blocked from Library truth.

### Stage 10 — Alert Governance Retrofit
- **Goal:** Build the shared alert-governance control surface (§14).
- **Assets affected:** Conflict/exception/plausibility/suspect-entries panels.
- **Doctrine applied:** Alert Governance Doctrine.
- **Deliverables:** One Mike-facing control surface covering all four panel types.
- **Tests:** Alert governance tests.
- **Human review:** Mike tests refining one real alert.
- **Stop/Go:** Go when every alert change is attributable to a recorded Mike action.

### Stage 11 — MVP Integration
- **Goal:** Confirm the combined result satisfies `DISPATCH_FINAL_BLUEPRINT_v1.md` §18's MVP checklist.
- **Assets affected:** All of the above, integrated.
- **Doctrine applied:** MVP Blueprint.
- **Deliverables:** One real load/opportunity evaluated end to end through the now-integrated Spine, Portal, Security, and Version Doctrine.
- **Tests:** Load evaluation tests, no-autonomous-action tests.
- **Human review:** Mike runs the full loop live.
- **Stop/Go:** Go when Mike confirms the loop works end to end with his own authenticated approval.

### Stage 12 — Testing and Hold Review
- **Goal:** Full regression across `cin_lite`, `dispatch`, and `portal`, plus every new test category.
- **Assets affected:** All.
- **Doctrine applied:** Testing and Validation Plan (Final Blueprint §22).
- **Deliverables:** Full CI-green suite at the existing 90% coverage bar or higher.
- **Tests:** Everything in §19 of this document (Jules Build Matrix "Tests Required" columns, aggregated).
- **Human review:** Full Mike walkthrough of every changed flow.
- **Stop/Go:** Go only on Mike's explicit sign-off.

### Stage 13 — Production-Intent Promotion Decision
- **Goal:** Decide whether the integrated Dispatch repo is ready for VPS/network deployment.
- **Assets affected:** None (decision only).
- **Doctrine applied:** Deployment and Promotion Path (Final Blueprint §23).
- **Deliverables:** A go/no-go decision from Mike.
- **Tests:** N/A.
- **Human review:** Mike's explicit deployment approval.
- **Stop/Go:** This document does not authorize this step. It occurs only under separate, explicit Mike approval at the time of promotion.

---

## 17. JULES BUILD MATRIX

Directly usable implementation instructions. No item here is approved for merge without the listed sign-off.

| # | Task Name | Existing File/Module to Inspect | Doctrine Source | Required Change | Reuse/Modify/Build New | Tests Required | Approval Needed Before Merge | Priority |
|---|---|---|---|---|---|---|---|---|
| 1 | Identity + PIN records | *(none — new)* `portal/security/` | `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` §2.1–2.2, §4 | Create `User`, `PinRecord` tables + PIN create/validate/reset/revoke functions | Build New | PIN creation, validation, failed-attempt lockout, reset, revocation | Mike | Critical |
| 2 | Session + Role/Permission model | *(none — new)* `portal/security/` | Security Spec §5–6 | Create `Session`, role enum (`Authority`, `Driver`, `External Viewer`, `System Service`), permission map | Build New | Permission tests per role | Mike | Critical |
| 3 | Login flow wired to Flask | `portal/app.py`, `portal/config.py` | Security Spec §4.3, §8 | Add login route, session cookie signed by existing (currently unused) `PORTAL_SECRET_KEY` | Build New | Login success/failure tests | Mike | Critical |
| 4 | Retrofit `approved_by` identity on IFTA gate | `dispatch/services.py::approve_ifta_quarter()`, `dispatch/models.py::IFTAReportApproval` | Security Spec §7, §9; Matrix row 31 | Replace email-string `approved_by` with authenticated `user_id` + `role`; keep HMAC link as secondary confirmation | Modify | Approval audit tests; regression tests confirming existing IFTA behavior unchanged | Mike | Critical |
| 5 | Retrofit identity on CIN + dispatch-load decision gates | `portal/routes/decisions.py`, `portal/routes/dispatch_api.py::dispatch_decision()` | Security Spec §7 | Same pattern as #4, applied to the other two email-decision endpoints | Modify | Approval audit tests | Mike | High |
| 6 | Fix Library unconditional auto-approval | `portal/models/library.py::add_record()` | `INTELLIGENCE_VERIFICATION_WORKFLOW.md` §7; Matrix row 8 | Remove hardcoded `"status": "approved"`; add `pending` status + promotion function requiring an Approval Event | Modify | Library promotion tests, no-fabrication tests | Mike | Critical |
| 7 | Spine core schemas | *(none — new)* `dispatch/spine/` | `DISPATCH_SPINE_SPECIFICATION_v1.md` §5–14 | Create Work Item, Event, Portal Card, Approval Event, Conflict Event, Audit Event tables | Build New | Schema validation tests | Mike (design review before build, per Constitution §20) | Critical |
| 8 | Spine state transition table | `dispatch/spine/` (from #7) | Spine Spec §6–7 | Implement approved state list + transition guard | Build New | State transition tests (every approved transition succeeds, every other rejected) | Mike | Critical |
| 9 | Generalize Sandbox into Work Item shape | `portal/models/sandbox.py` | Spine Spec §5; Matrix row 11 | Map `sandbox.py`'s `STATUSES`/`events` onto the new Work Item/Event tables without breaking existing routes | Integrate | Regression tests on all `portal/routes/api.py` sandbox routes | Mike | High |
| 10 | Add `card_level` field | `portal/models/sandbox.py`, `conflict.py`, Portal templates | `PORTAL_DESCRIPTION.md` §7; Matrix row 2 | Add `card_level` (0–5) to card-producing records; render by level in templates | Modify | Portal card tests | Not required (deterministic, low-risk) | High |
| 11 | Version + Last Change fields on Sandbox | `portal/models/sandbox.py`, `helpers.card_visual()` | `DISPATCH_VERSION_DOCTRINE.md` §3–7 | Add `version` int + `last_change` string, increment on meaningful change only | Modify | Version display tests | Not required | High |
| 12 | Version fields on Library + Archive | `portal/models/library.py`, `archive.py` | Version Doctrine §5 | Add version fields as part of task #6 and #14 | Modify | Version display tests | Mike (paired with #6) | High |
| 13 | Archive Review Queue | `portal/models/archive.py` | `ARCHIVE_REVIEW_POLICY.md` §2–4 | Add version retention rule (current + 3), Review Queue, Keep/Delete actions | Build New | Archive retention tests | Mike | High |
| 14 | Enforce Publisher `human_approval_required` | `portal/models/publisher.py::update_action_status()` | `PUBLISHER.md` §5, §11 | Block transition to `APPROVED` without a recorded Approval Event | Modify | No-fabrication / status-label tests | Mike | High |
| 15 | Intelligence Verification classification | `portal/models/intelligence.py`, `dispatch/services.py` (suspect-entries confidence) | `INTELLIGENCE_VERIFICATION_WORKFLOW.md` §3 | Map `extraction_confidence` and rule-module output to Verified/Partially Verified/Unverified/Rejected | Integrate + Build New | Intelligence verification tests | Mike | High |
| 16 | Conflict gate for authority-level conflicts | `portal/models/conflict.py` | `DISPATCH_CONSTITUTION_v3.md` §19 | `human_decision_required=True` + high-severity conflicts must actually block the related action, not just warn | Modify | Conflict event tests | Mike | Medium |
| 17 | Shared alert-governance control surface | Portal templates for `ifta_review.html`, `conflicts.html`, `exceptions.html` | `ALERT_GOVERNANCE_DOCTRINE.md` §3, §6 | One Mike-facing suppress/alter/merge/split control set, applied across all advisory panels | Build New | Alert governance tests | Mike | Medium |
| 18 | Driver Portal access boundary | `Driver` model, `driver_detail.html` | Security Spec §3.2, §13; Matrix row 3 | Scope Driver-role sessions (from #2) to driver-only routes/views | Build New (boundary) | Driver portal boundary tests | Mike | Medium |
| 19 | Telematics input placeholder schema | *(none — new)* `dispatch/spine/` | `DISPATCH_FINAL_BLUEPRINT_v1.md` §17 | Define GPS/HOS/ELD input schema Spine scoring can accept later; no live integration | Build New (placeholder only) | Schema validation only | Not required (placeholder) | Low |
| 20 | Sync utility role decision | `sync/*.py` | Matrix row 20 | No code change — produce a short options memo for Mike's decision on intended purpose | Investigate Further | N/A | Mike (decision, not code) | Low |

---

## 18. What Must Not Be Changed

**Do not change until reviewed, even though they are technically imperfect:**
- `IFTAReportApproval`'s core freeze/refuse-resubmission/idempotent-reapproval logic (`dispatch/services.py`) — proven, tested, owner-approved across five phases. Retrofit identity onto it (#4); do not rewrite its mechanics.
- `cin_lite/archive.py`'s hash-write/verify/fail-closed mechanism — already correct per doctrine.
- The nine deterministic rule modules (`cin_lite/rules/*.py`) — correct, tested, no LLM dependency, no change needed.
- The five agents' fallback pattern (`cin_lite/agents/*.py`) — already implements "never fail, never fabricate" correctly; do not add auto-execution to any of them.
- `dispatch/scoring.py` — already a strong, working implementation of the Spine's deterministic load/route factors; do not replace with a new scoring engine.
- CI configuration (`.github/workflows/ci.yml`) — no deploy step exists today; do not add one without a separate, explicit Mike approval.
- `IFTA_TAX_RATES` and the IFTA tax computation formula — out of scope for this integration entirely.

**Forbidden without Mike's explicit approval:**
- Any change to `DEPLOY_VPS.md`'s posture that results in exposing the portal to the network before Stage 7 (Security Foundation) is complete and signed off.
- Any change to `DECISION_LOG.md`'s past entries — it is an append-only record, per its own format note.
- Deleting, renaming, or restructuring `cin_lite/`, `dispatch/`, or `portal/` at the top level.
- Any code merge, deployment, or production change of any kind arising from this document.
- Treating any Jules Build Matrix item as pre-approved — every row still requires the listed sign-off before merge.

---

## 19. Risks and Mitigations

| Area | Risk | Mitigation |
|---|---|---|
| Duplicated logic | Building generic Spine schemas alongside existing entity-specific tables could create two parallel "truth" stores | Migrate existing tables onto the Spine incrementally (Stage 4, 6) rather than running both indefinitely; IFTA migration (#4) is the pilot |
| Drift between docs and code | Claude-3 doctrine evolves independently of Dispatch's `docs/` copy | Treat the Dispatch `docs/` copy as a refreshed reference, never edited independently of Claude-3 (§15) |
| Overwriting working code | Aggressive rewrite of `portal/models/*.py` could break the ~180 wired routes that depend on them | Every Jules Build Matrix item affecting existing files is scoped as Modify/Integrate with explicit regression-test requirements, never a rewrite |
| Old L2-COS terminology | `README.md` still carries a legacy section header | Low-risk naming cleanup, not urgent; rename opportunistically, not as a blocking task |
| Security gaps | The entire app is unauthenticated today; VPS deployment is currently unsafe | Stage 7 is a hard gate before any network exposure; `DEPLOY_VPS.md` already documents this risk in its own words |
| Versioning retrofit errors | Adding version counters to live records could increment on noise rather than meaningful change | Version display tests (Jules item #11) explicitly test "meaningful change only," per Version Doctrine §6 |
| Archive retention mistakes | Retrofitting the current+3 retention rule onto existing archive data could silently drop history if implemented carelessly | Preserve-by-default is the explicit default; no delete action ships without Keep/Delete review queue UI (#13) |
| Unfinished workflows | Sync utility's role is undefined; leaving it half-integrated could create silent data gaps | Investigate Further status (Matrix row 20) — explicitly not integrated until Mike decides its purpose |
| Hidden authority paths | The three HMAC email-decision gates today authenticate link possession, not identity — a forwarded email could currently "approve" something | Stage 7 + Jules items #4/#5 close this gap; until then, this is a known, named, Critical risk, not a silent one |

---

## 20. Final Recommendation

**Should Dispatch and Claude-3 be combined?** Yes — not by merging repositories, but by making Dispatch the implementation of Claude-3's doctrine, with Claude-3 remaining the standing governance authority Dispatch answers to (§2).

**Should Repo-3 documents be imported into Dispatch?** Yes, selectively — the Constitution, Final Blueprint, Security Specification, and Spine Specification, copied into a new `dispatch/docs/` directory (Stage 2), refreshed from Claude-3 whenever doctrine changes.

**Should Dispatch remain the production-intent repo?** Yes. It already has CI, a real test culture, a working persistence layer, and a genuine change-approval discipline. Nothing in this reconciliation found a reason to start over elsewhere.

**What should Jules build first?** Security Foundation (Jules items #1–3) and the Library auto-approval fix (#6) — the former because it blocks safe deployment and gates every future Approval Event retrofit, the latter because it is the single most doctrine-conflicting asset found and is a small, contained fix.

**What should Claude review after Jules builds?** Every item in the Jules Build Matrix marked "Approval Needed Before Merge: Mike" still needs a pre-merge doctrine check (does the implementation match the cited doctrine section, not just pass its tests) before it reaches Mike for final sign-off — this is exactly the Quality Control Review posture `REFINEMENT_ANALYST_REMOVAL.md` describes as appropriate for high-risk changes.

**What requires Mike's decision?** This document's approval as current; every Stage 1–13 stop/go gate; every Jules Build Matrix row marked "Mike"; the sync utility's intended purpose (§10); and, ultimately, any future production/VPS deployment decision, which nothing here grants.

**What is the cleanest next step?** Stage 1 (Inventory Freeze) — Mike reviews and approves this document and the Reconciliation Matrix as the frozen baseline, then Stage 2 (Documentation Import) can begin immediately since it carries no code risk.

---

## Authority Closing

This is an integration blueprint draft only.

No deployment is authorized.
No code merge is authorized.
No production change is authorized.
No doctrine change is authorized unless Mike approves.
No existing Dispatch code is deleted, replaced, or overwritten by this document.

Mike Zachary remains final authority.

**Mike decides.**
