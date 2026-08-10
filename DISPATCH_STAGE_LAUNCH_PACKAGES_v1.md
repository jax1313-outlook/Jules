# DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md

**Document Type:** Staged Launch Package Set — Migration Plan Detail
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Planning Draft — expands `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16 (Migration Plan) into per-stage launch packages
**Authority:** Mike Zachary remains final authority

---

## Purpose

This document formalizes each of the 13 Migration Plan stages (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16) into a launch package, following the same pre-implementation discipline the Dispatch repository's own `DECISION_LOG.md` already uses for every governed capability change: a launch package precedes implementation, states scope and open questions, and is followed by a walkthrough report once built.

**No package in this document authorizes any code change, deployment, or commit to the Dispatch repository.** Each stage's Stop/Go line states exactly what closes it. A stage does not begin until the prior stage's Stop/Go criteria are met and Mike has signed off — the same sequencing already established in the Migration Plan.

Each package cites the specific `DISPATCH_REPO_RECONCILIATION_MATRIX_v1.md` rows and `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` Jules Build Matrix items it covers, so nothing here duplicates or drifts from those two documents — it only adds the next level of planning detail: open questions Mike needs to answer, and the explicit shape of each stage's deliverable before Jules is asked to build it.

---

## Stage → Jules Build Matrix Cross-Reference

| Stage | Status | Jules Items Covered | Code Touched? |
|---|---|---|---|
| 1. Inventory Freeze | **Approved** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | none | No |
| 2. Documentation Import | **Approved & executed** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | none | Yes — `Dispatch` branch `stage2-documentation-import` |
| 3. Blueprint Alignment | **Approved & executed** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | none | Yes — `Dispatch` branch `stage3-blueprint-alignment` |
| 4. Data Engine / Spine Reconciliation | **Approved & executed** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #7, #8 | Yes — `Dispatch` branch `stage4-spine-schemas` |
| 5. Portal Reconciliation | **Approved & executed** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #10, #11 | Yes — `Dispatch` branch `stage5-portal-reconciliation` |
| 6. Archive / IFTA Reconciliation | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #13 (+ IFTA migration onto Stage 4 output) — deferred to a future Stage 6 *build* package | No — Claude-3 only, `DISPATCH_STAGE6_ARCHIVE_IFTA_RECONCILIATION_v1.md` |
| 7. Security Foundation | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #1, #2, #3, #4, #5, #21 — deferred to a future Stage 7 *build* package | No — Claude-3 only, `DISPATCH_STAGE7_SECURITY_RECONCILIATION_v1.md` |
| 8. Version Doctrine Retrofit | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #12 — deferred to a future Stage 8 *build* package, possibly merged with a future Stage 6 build | No — Claude-3 only, `DISPATCH_STAGE8_VERSION_DOCTRINE_RECONCILIATION_v1.md` |
| 9. Verification Workflow Retrofit | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #6, #15 — deferred to a future Stage 9 *build* package | No — Claude-3 only, `DISPATCH_STAGE9_VERIFICATION_WORKFLOW_RECONCILIATION_v1.md` |
| 10. Alert Governance Retrofit | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #16, #17 — deferred to a future Stage 10 *build* package | No — Claude-3 only, `DISPATCH_STAGE10_ALERT_GOVERNANCE_RECONCILIATION_v1.md` |
| 11. MVP Integration | **Redefined as analysis-only; delivered** (see `DISPATCH_BLUEPRINT_DECISION_LOG.md`) | #9, #14 — deferred; #9 identified as the critical Sandbox/Spine wiring gap | No — Claude-3 only, `DISPATCH_STAGE11_MVP_INTEGRATION_RECONCILIATION_v1.md` |
| 12. Testing and Hold Review | Pending Stage 11 | none new — aggregates all above | No new code, full regression |
| 13. Production-Intent Promotion Decision | Pending Stage 12 | none | No |

Jules items **#20** (sync utility role decision) and **#22** (Scanner API placeholder documentation) are not tied to a specific stage — they are standalone, Low/Future priority, and may proceed independently whenever convenient, per their own rows in the Jules Build Matrix.

---

## Stage 1 — Inventory Freeze

**Status: APPROVED** — "Approve Stage 1", recorded in `DISPATCH_BLUEPRINT_DECISION_LOG.md`.

**Depends on:** Nothing (first stage).

**Purpose:** Freeze `DISPATCH_FINAL_BLUEPRINT_v1.md`, `DISPATCH_REPO_RECONCILIATION_MATRIX_v1.md`, `DISPATCH_INTEGRATED_BLUEPRINT_v1.md`, and `LIBRARY_INGESTION_RULE.md` as the current, controlling baseline for everything that follows.

**Scope:** No code — Claude-3 documents only.

**Doctrine source:** All four documents above; `DISPATCH_REPO_MANIFEST_v3.md`'s document-control discipline.

**Jules Build Matrix items:** None — this is a planning gate, not a build stage.

**Findings:** Nothing new to find — this stage ratifies the reconciliation work already completed, it doesn't perform new inspection.

**Open Questions for Mike:**
1. Are there any other pending doctrine amendments — beyond the Library Ingestion Rule already folded in — that should be resolved before the baseline freezes?
2. Should `jax1313-outlook/Dispatch-Old` remain permanently excluded from all future reconciliation work, or was it excluded only for this pass?

**Deliverables:** A confirmed, frozen baseline. No new files.

**Test plan:** N/A.

**Walkthrough report:** N/A — no code changes.

**Stop/Go:** Go once Mike confirms the four baseline documents as current, in writing (a recorded chat approval is sufficient, matching `DECISION_LOG.md`'s own verbatim-approval convention).

---

## Stage 2 — Documentation Import

**Status: APPROVED AND EXECUTED** — "Approve Stage 2", recorded in `DISPATCH_BLUEPRINT_DECISION_LOG.md`. Executed to `jax1313-outlook/Dispatch` branch `stage2-documentation-import` (commit `fc75bab`); branch pushed, no pull request opened.

**Depends on:** Stage 1 signed off. ✅ (`DISPATCH_BLUEPRINT_DECISION_LOG.md`, 2026-08-10)

**Purpose:** Copy governing Claude-3 documents into a new `dispatch/docs/` directory so builders working directly in Dispatch have doctrine alongside the code they're writing.

**Scope:** New `dispatch/docs/` directory only. No existing Dispatch file is touched.

**Doctrine source:** `SUPERSESSION_MAP.md` (current-vs-historical distinction, applied to Dispatch's copy); `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §15.

**Jules Build Matrix items:** None (documentation task).

**Findings:** Dispatch's own `CLAUDE.md` already references an external authoritative spec (`Final_Architecture_for_Hybrid_CIN-Lite_System (1).docx`) the same way this stage proposes — there's direct precedent in the repo for "doctrine lives alongside code, referenced not duplicated in spirit."

**Open Questions for Mike:**
1. ~~Full Claude-3 document set (21+ files), or only the four most load-bearing (Constitution, Final Blueprint, Security Spec, Spine Spec) plus the Library Ingestion Rule?~~ **Resolved:** the four load-bearing documents plus the Library Ingestion Rule — five files total: `DISPATCH_CONSTITUTION_v3.md`, `DISPATCH_FINAL_BLUEPRINT_v1.md`, `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md`, `DISPATCH_SPINE_SPECIFICATION_v1.md`, `LIBRARY_INGESTION_RULE.md`. Not the full 21+ file set.
2. Should `dispatch/docs/` be clearly marked "mirror — refreshed from Claude-3, do not edit here," or does Mike want a lighter-touch reference instead of a full copy? **Default applied pending confirmation:** mark it a mirror — add a short `dispatch/docs/README.md` stating these five files are refreshed from Claude-3 and should not be edited in place.

**Deliverables:** `dispatch/docs/` populated with the five files named in Open Question 1, plus a short `dispatch/docs/README.md` mirror notice.

**Test plan:** None (documentation only).

**Walkthrough report:** A short confirmation note is sufficient — no behavior change to verify.

**Stop/Go:** Go once the imported doc set matches Claude-3's active manifest exactly and Mike has answered both open questions.

---

## Stage 3 — Blueprint Alignment

**Status: APPROVED AND EXECUTED** — "Approve Stage 3", recorded in `DISPATCH_BLUEPRINT_DECISION_LOG.md`. Executed to `jax1313-outlook/Dispatch` branch `stage3-blueprint-alignment` (commit `4b60ead`, branched from `stage2-documentation-import`); branch pushed, no pull request opened.

**Depends on:** Stage 2 complete. ✅

**Purpose:** Update Dispatch's `CLAUDE.md` to reference the imported Final Blueprint alongside its existing CIN-Lite architecture spec, reconciling subsystem boundaries so a future builder isn't left guessing which "five layers" apply where.

**Scope:** `CLAUDE.md` only.

**Doctrine source:** Full `DISPATCH_FINAL_BLUEPRINT_v1.md`; `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §9 (IFTA/CIN-Lite layer mapping) and §4 (Architecture-to-Implementation Mapping).

**Jules Build Matrix items:** None directly — this is a prerequisite clarification for #7/#8.

**Findings:** CIN-Lite's own five layers (Acquisition / Processing / Control / Archive / Automation, per `CLAUDE.md`) are **not** the same five layers as Claude-3's architecture (Authority / Presentation / Organizational / Deterministic / Cognitive). `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §9 already maps CIN-Lite's layers onto Claude-3's Intelligence Analyst sub-layers and the Spine — `CLAUDE.md` must state this mapping explicitly rather than let two same-named "five layer" models sit side by side unreconciled.

**Open Questions for Mike:**
1. Should `CLAUDE.md` fully restate the Claude-3 five-layer model inline, or just cross-reference `dispatch/docs/DISPATCH_FINAL_BLUEPRINT_v1.md` with a short reconciliation paragraph?

**Deliverables:** Updated `CLAUDE.md` with the layer-mapping paragraph.

**Test plan:** None.

**Walkthrough report:** A short confirmation note is sufficient.

**Stop/Go:** Go once boundaries are unambiguous to a future builder — Mike confirms by reading the updated file.

---

## Stage 4 — Data Engine / Spine Reconciliation

**Status: APPROVED AND EXECUTED** — Open questions: "Same file, coexist during transition". Implementation: "Approve Stage 4", recorded in `DISPATCH_BLUEPRINT_DECISION_LOG.md`. Executed to `jax1313-outlook/Dispatch` branch `stage4-spine-schemas` (commits `09e51c7`, `bca3fcd`); branch pushed, no pull request opened. See `DISPATCH_STAGE4_SPINE_SCHEMA_DESIGN_v1.md` (design) and `STAGE4_SPINE_SCHEMA_WALKTHROUGH_REPORT_v1.md` (in the Dispatch repo, walkthrough).

**Depends on:** Stage 3 complete. ✅

**Purpose:** Build the generic Spine schemas (Work Item, Event, Portal Card, Approval Event, Conflict Event, Audit Event), informed by — not replacing — `sandbox.py`'s existing state/event pattern and `IFTAReportApproval`'s proven freeze mechanics.

**Scope:** New `dispatch/spine/` module. No changes to existing `dispatch/models.py` tables.

**Doctrine source:** `DISPATCH_SPINE_SPECIFICATION_v1.md` in full.

**Jules Build Matrix items:** #7 (Spine core schemas), #8 (Spine state transition table).

**Findings (from Reconciliation Matrix rows 10–14, 32):** the SQLite + WAL + idempotent-migration pattern already proven in `dispatch/db.py` is sound and reusable for the new Spine tables. No generic Work Item/Event/Approval Event/Conflict Event/Audit Event table exists today. Multiple independent per-entity enum state machines exist (`Load`, `Settlement`, `IFTAReportApproval`, etc.) but no shared transition-table concept governs them yet.

**Open Questions for Mike:**
1. ~~Do the new Spine tables live in the same `dispatch.db` SQLite file or a separate database file?~~ **Resolved: same file.**
2. ~~Should the Spine's generic Event table subsume `LoadActivity`'s existing free-text per-load log, or coexist?~~ **Resolved: coexist during the transition.** `events` is scoped to Work Items; `activities` (`LoadActivity`) remains untouched and continues serving Loads as it does today. No migration, no dual-write. Whether/how they eventually consolidate is a later decision (candidate: Stage 11, when Sandbox generalizes into the Work Item shape), not part of Stage 4.

**Design review (Constitution §20 — required before implementation begins):** see `DISPATCH_STAGE4_SPINE_SCHEMA_DESIGN_v1.md`.

**Deliverables:** `work_items`, `events`, `portal_cards`, `approval_events`, `conflict_events`, `audit_events` tables and schemas; the approved state list and a transition-guard function per Spine Spec §6–7.

**Test plan:** Schema validation tests; state transition tests (every approved transition succeeds, every non-approved transition is rejected) — the Spine Spec §20 build-readiness bar in full.

**Walkthrough report:** Required — this is genuinely new infrastructure, at the same rigor as the existing IFTA finalization gate's Phase 4 report.

**Stop/Go:** Go once all Spine build-readiness tests pass **and** Mike has reviewed the schema design before implementation begins (Constitution §20 requires design review before code, not only before merge).

---

## Stage 5 — Portal Reconciliation

**Status: APPROVED AND EXECUTED** — "Approve Stage 5", recorded in `DISPATCH_BLUEPRINT_DECISION_LOG.md`. Executed to `jax1313-outlook/Dispatch` branch `stage5-portal-reconciliation` (commits `2393883`, `1ab18b6`, based on `stage4-spine-schemas`); branch pushed, no pull request opened. See `STAGE5_PORTAL_RECONCILIATION_WALKTHROUGH_REPORT_v1.md` in the Dispatch repo.

**Depends on:** Stage 4 complete (Spine schemas exist, even if not yet fully wired). ✅

**Purpose:** Add `card_level` and version display to the existing Portal cockpit surface.

**Scope:** `portal/models/sandbox.py`, `conflict.py`, `helpers.card_visual()`, associated templates.

**Doctrine source:** Portal Blueprint (`DISPATCH_FINAL_BLUEPRINT_v1.md` §4); Version Doctrine (§11).

**Jules Build Matrix items:** #10 (`card_level` field), #11 (version + last-change on Sandbox).

**Findings:** `card_visual()` already implements the visual half of Version Doctrine's own worked example (`HIGH VALUE MATCH` / `Score: 97%`-style labeling) — it is missing only the `Ver: X` / `Last Change:` half, not the whole concept.

**Open Questions for Mike:**
1. Should `card_level` be derived automatically from existing fields (Conflict's `severity`, Sandbox's `status`) with a sane default, or set explicitly at creation? Recommendation: derive a default automatically, but allow Manager/Mike override — this matches Alert Governance's "refine, don't silently auto-decide" posture rather than introducing a new hardcoded rule.

**Deliverables:** `card_level` rendering on Portal cards; `Ver: X` / `Last Change:` on Sandbox cards.

**Test plan:** Portal card tests; version display tests (version increments only on meaningful change, per Version Doctrine §6).

**Walkthrough report:** Required, live on a dev server, matching the existing Dispatch convention.

**Stop/Go:** Go when Mike walks through the updated cockpit live and confirms it reads correctly.

---

## Stage 6 — Archive / IFTA Reconciliation

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike's detailed charter explicitly scoped this stage to architecture reconciliation only — no code, no Dispatch repository changes, no PR, no migrations, no new tables. Delivered as `DISPATCH_STAGE6_ARCHIVE_IFTA_RECONCILIATION_v1.md` (Claude-3 only). The original build scope below (IFTA migration onto the generic Approval Event schema, Archive Review Queue) is deferred to a future Stage 6 *build* launch package, not authorized by this delivery.

**Depends on:** Stage 4 complete (generic Approval Event schema exists). ✅ (for the deferred future build scope; not required for the analysis delivered)

**Purpose:** Migrate `IFTAReportApproval` onto the generic Approval Event schema as the pilot migration; build the Archive Review Queue.

**Scope:** `dispatch/services.py`, `portal/models/archive.py`.

**Doctrine source:** Archive Blueprint (`DISPATCH_FINAL_BLUEPRINT_v1.md` §9); Archive Review Policy.

**Jules Build Matrix items:** #13 (Archive Review Queue); the IFTA-to-Spine migration itself is called out explicitly in `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §9 as the reference pilot, not a separately numbered Jules item.

**Findings:** `IFTAReportApproval`'s freeze / refuse-resubmission / idempotent-reapproval logic is proven and tested across five owner-approved phases — it must be re-pointed at the generic schema, never rewritten.

**Open Questions for Mike:**
1. Does migrating IFTA onto the generic Approval Event schema require migrating already-sealed historical approval rows, or can existing rows stay in their current table untouched while only new approvals use the generic schema going forward?

**Deliverables:** IFTA gate running on the generic schema with provably zero behavior change; a working Keep/Delete Archive Review Queue.

**Test plan:** Archive retention tests; full regression across the existing ~120 IFTA-related tests (Phases 2–7) to confirm zero behavior change — this is a regression-test gate, not only a new-test gate.

**Walkthrough report:** Required — Mike runs one real IFTA submission/approval through the migrated path, exactly matching the existing per-phase convention.

**Stop/Go:** Go only if IFTA's existing tested behavior is provably unchanged.

---

## Stage 7 — Security Foundation

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike's detailed charter explicitly scoped this stage to Architecture Reconciliation Mode — no code, no Dispatch repository changes, no PR, no migrations, no new tables, no Security Foundation build, no Stage 7 build launch package yet. Delivered as `DISPATCH_STAGE7_SECURITY_RECONCILIATION_v1.md` (Claude-3 only). The original build scope below (Jules items #1–#5, #21) is deferred to a future Stage 7 *build* launch package, not authorized by this delivery.

**Depends on:** Stage 4 complete (Approval Event schema exists to retrofit identity onto). ✅ (for the deferred future build scope; not required for the analysis delivered)

**Purpose:** Build Identity, PIN, Session, Role, and Permission records and a login flow; retrofit real authenticated identity onto the three existing HMAC email-decision gates; build the PIN-gated Security sub-library.

**Scope:** New `portal/security/` module; `approved_by`/`entered_by` fields on the IFTA, CIN-contract, and dispatch-load decision gates; `portal/models/library.py`'s new security section.

**Doctrine source:** `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` in full; `LIBRARY_INGESTION_RULE.md` §6.

**Jules Build Matrix items:** #1, #2, #3, #4, #5, #21.

**Findings:** Zero authentication, authorization, PIN, or role mechanism exists anywhere in the running app today (Reconciliation Matrix rows 13, 23, 29–31, confirmed by direct grep sweep). `PORTAL_SECRET_KEY` is already configured but currently unused, and can become the Flask session-signing key once sessions exist. The existing HMAC token mechanism is sound as a *secondary* confirmation layer and does not need to be discarded.

**Open Questions for Mike:**
1. Beyond Mike as the Authority role, are there other real users who need an identity/role for the initial build — a dispatcher, a second reviewer — or does this stage only need to support a single Authority user for MVP?
2. Should the existing single-reviewer (`DISPATCH_EMAIL_REVIEWER`) email-link pattern be retired once session login exists, or kept as a secondary/backup approval path for when Mike is away from a logged-in session?

**Deliverables:** Working PIN login for at least the Authority role; authenticated `approved_by`/`entered_by` on all three decision gates; PIN-gated Security sub-library with reset capability.

**Test plan:** PIN authentication tests (creation, validation, failed-attempt lockout, reset, revocation), permission tests, approval audit tests, PIN re-check access tests for the Security sub-library.

**Walkthrough report:** Required, and should be the most rigorous walkthrough of any stage — this closes the platform's single most critical gap.

**Stop/Go:** Go when Mike can log in with a PIN and every approval action captures his real identity. **This stage is a hard blocker on any VPS/network deployment**, per `DEPLOY_VPS.md`'s own self-reported blocker.

---

## Stage 8 — Version Doctrine Retrofit

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike instructed Architecture Reconciliation Mode — no code, no Dispatch repository changes, no PR, no migrations, no new tables, no build package. Delivered as `DISPATCH_STAGE8_VERSION_DOCTRINE_RECONCILIATION_v1.md` (Claude-3 only). The original build scope below (Jules item #12) is deferred to a future Stage 8 *build* launch package, not authorized by this delivery — and per the reconciliation's own finding, may be best merged with a future Stage 6 Archive build package rather than built separately.

**Depends on:** Stage 5 complete (Sandbox version pattern already proven). ✅ (for the deferred future build scope; not required for the analysis delivered)

**Purpose:** Extend version/last-change fields to Library and Archive records (Sandbox is already covered by Stage 5).

**Scope:** `portal/models/library.py`, `archive.py`; IFTA records.

**Doctrine source:** Version Doctrine §5 (system-wide application).

**Jules Build Matrix items:** #12.

**Findings:** None new beyond Stage 5's.

**Open Questions for Mike:**
1. For human-placed Library documents (immediate-accept per the Library Ingestion Rule), does re-uploading a revised file always create a new version, or should there be a "replace this exact record" option that logs a `Last Change` note without incrementing `Ver`? Recommendation: always a new version — `LIBRARY_INGESTION_RULE.md` §8 already states immediate acceptance does not exempt a record from version tracking — but this affects the upload UX, so it's flagged for confirmation rather than assumed.

**Deliverables:** `Ver: X` / `Last Change:` on Library and Archive records.

**Test plan:** Version display tests.

**Walkthrough report:** A short confirmation note is sufficient — this is a low-risk, additive field change.

**Stop/Go:** Go when version increments correctly on meaningful change only, verified against both the human-ingestion path and the cognitive-promotion path.

---

## Stage 9 — Verification Workflow Retrofit

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike instructed Architecture Reconciliation Mode — no code, no Dispatch repository changes, no PR, no migrations, no new tables, no build package. Delivered as `DISPATCH_STAGE9_VERIFICATION_WORKFLOW_RECONCILIATION_v1.md` (Claude-3 only). The original build scope below (Jules items #6, #15) is deferred to a future Stage 9 *build* launch package, not authorized by this delivery.

**Depends on:** Stage 7 complete (origin-gating needs a real identity to attribute origin to) and Stage 8 complete. ✅ (both reconciled; for the deferred future build scope, not required for the analysis delivered)

**Purpose:** Formalize Verified / Partially Verified / Unverified / Rejected classification for cognitively-derived candidates; add the `origin` field to Library ingestion so Publisher-generated candidates are correctly routed to the promotion workflow instead of the human-ingestion path.

**Scope:** `portal/models/library.py` (`origin` field), `intelligence.py`, IFTA suspect-entries confidence mapping.

**Doctrine source:** `INTELLIGENCE_VERIFICATION_WORKFLOW.md`; `LIBRARY_INGESTION_RULE.md`.

**Jules Build Matrix items:** #6, #15.

**Findings:** `extraction_confidence` + the suspect-entries threshold is a strong existing seed for Partially Verified. The nine deterministic rule modules can be treated as Verified by construction (pure text extraction, no inference). The five Claude-backed agents' outputs are recommendations, not factual claims, and should classify as Unverified-as-fact while remaining usable as Publisher/Intelligence recommendations.

**Open Questions for Mike:**
1. The existing `DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD = 0.75` is an admitted "uncalibrated placeholder" per Phase 7's own walkthrough report — is it acceptable as the initial Verified/Partially-Verified boundary for this retrofit, or does Mike want it recalibrated first?

**Deliverables:** Library `origin` field wired (human vs. publisher/intelligence/archive); non-human origins gated through the promotion workflow; suspect-entries confidence mapped to a real verification classification.

**Test plan:** Library ingestion-path tests (human immediate-accept, non-human gated), fact-grounding tests, no-fabrication tests.

**Walkthrough report:** Required — this stage directly touches the corrected Library finding from the reconciliation matrix.

**Stop/Go:** Go when Unverified/Rejected facts are structurally blocked from Library truth via the promotion path, while human-placed documents remain provably ungated.

---

## Stage 10 — Alert Governance Retrofit

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike instructed Architecture Reconciliation Mode — no code, no Dispatch repository changes, no PR, no migrations, no new tables, no build package. Delivered as `DISPATCH_STAGE10_ALERT_GOVERNANCE_RECONCILIATION_v1.md` (Claude-3 only). The original build scope below (Jules items #16, #17) is deferred to a future Stage 10 *build* launch package, not authorized by this delivery.

**Depends on:** Stage 5 complete (card model exists to attach controls to). ✅ (for the deferred future build scope; not required for the analysis delivered)

**Purpose:** Build the shared Mike-facing alert-governance control surface; give real blocking behavior to authority-level conflicts that today are only advisory.

**Scope:** Conflict, exception, plausibility-warning, and suspect-entries panels.

**Doctrine source:** `ALERT_GOVERNANCE_DOCTRINE.md`; Constitution §19 (Conflict Notice Rule).

**Jules Build Matrix items:** #16, #17.

**Findings:** The existing advisory panels already behave correctly by doctrine's own standard (never silently suppress). The actual gap is narrower: there is no Mike-facing control surface, and `conflict.py`'s `human_decision_required=True` notices don't currently block anything, even for high-severity conflicts.

**Open Questions for Mike:**
1. Should the shared control surface be one new page, or a control widget embedded on each existing panel (`ifta_review.html`, `conflicts.html`, `exceptions.html`)? Recommendation: one shared widget reused across panels, per `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §14's reasoning against building the same governance UI four separate times.

**Deliverables:** One Mike-facing control surface covering all four panel types (suppress/alter/merge/split/upgrade/downgrade); real blocking behavior for `human_decision_required=True` high-severity conflicts.

**Test plan:** Alert governance tests.

**Walkthrough report:** Required — Mike tests refining one real alert live.

**Stop/Go:** Go when every alert change is attributable to a recorded Mike action.

---

## Stage 11 — MVP Integration

**Status: REDEFINED AS ANALYSIS-ONLY AND DELIVERED.** Mike instructed Architecture Reconciliation Mode — no code, no Dispatch repository changes, no PR, no migrations, no new tables, no build package. Delivered as `DISPATCH_STAGE11_MVP_INTEGRATION_RECONCILIATION_v1.md` (Claude-3 only) — an honest gap scorecard rather than a confirmation, since Stages 6–10 produced analysis, not builds. Identifies Stage 7 (Security) as the true MVP critical path and Jules #9 (Sandbox/Work Item bridge) as the second-most-critical gap. Original build scope (Jules #9, #14) deferred to a future Stage 11 *build* launch package.

**Depends on:** Stages 4–10 complete. ✅ (all reconciled; only Stages 4–5 actually built)

**Purpose:** Confirm the combined result of every prior stage satisfies the Final Blueprint §18 MVP checklist end to end — one real load/opportunity evaluated through the fully integrated Spine, Portal, Security, and Version Doctrine.

**Scope:** All prior stages, integrated. Jules #9 (generalize Sandbox into the Work Item shape) and #14 (enforce Publisher's `human_approval_required` flag) land here if not already folded into Stage 4/6.

**Doctrine source:** MVP Blueprint (`DISPATCH_FINAL_BLUEPRINT_v1.md` §18).

**Jules Build Matrix items:** #9, #14.

**Findings:** None new — this is a confirmation/integration stage, not a discovery stage.

**Open Questions for Mike:**
1. Driver Portal access boundary (#18) and the telematics input placeholder (#19) are Medium/Low priority and explicitly not required for MVP per Final Blueprint §18.2 — should they be attempted opportunistically during this stage if time allows, or explicitly deferred to a dedicated post-MVP wave?

**Deliverables:** One real load/opportunity evaluated end to end, with Mike's own authenticated approval captured through the integrated system.

**Test plan:** Load evaluation tests; no-autonomous-action tests (confirm no booking/approval path exists without an authenticated Approval Event).

**Walkthrough report:** Required, and should be the capstone walkthrough — the single clean end-to-end proof `DISPATCH_FINAL_BLUEPRINT_v1.md` §25 already names as "the cleanest first prototype."

**Stop/Go:** Go when Mike confirms the loop works end to end with his own authenticated approval.

---

## Stage 12 — Testing and Hold Review

**Depends on:** Stage 11 complete.

**Purpose:** Run full regression across `cin_lite`, `dispatch`, and `portal`, plus every new test category introduced in Stages 4–11, together as one suite.

**Scope:** All.

**Doctrine source:** Testing and Validation Plan (`DISPATCH_FINAL_BLUEPRINT_v1.md` §22).

**Jules Build Matrix items:** None new — this stage aggregates every prior stage's test requirements.

**Findings:** Existing CI already enforces 90% coverage on `cin_lite` + `dispatch`; this stage extends that bar to the new `portal/security/` and `dispatch/spine/` modules rather than replacing the existing standard.

**Open Questions for Mike:**
1. Should the 90% coverage threshold apply immediately to the new `portal/security/` and `dispatch/spine/` modules, or is a lower initial bar (e.g. 80%, tightened later) acceptable for the first Hold Review pass?

**Deliverables:** A full CI-green suite at the existing coverage bar or higher, run across every stage's changes together — not stage-by-stage in isolation.

**Test plan:** Every test category listed across all Jules Build Matrix rows, run as one combined suite.

**Walkthrough report:** A full Mike walkthrough of every changed flow — the most comprehensive review point in the entire plan.

**Stop/Go:** Go only on Mike's explicit sign-off. This stage is itself the Hold gate, not a build stage.

---

## Stage 13 — Production-Intent Promotion Decision

**Depends on:** Stage 12 complete and signed off.

**Purpose:** Decide whether the integrated Dispatch repository is ready for VPS/network deployment.

**Scope:** Decision only — no code.

**Doctrine source:** Deployment and Promotion Path (`DISPATCH_FINAL_BLUEPRINT_v1.md` §23).

**Jules Build Matrix items:** None — this is a decision, not a build task.

**Findings:** `DEPLOY_VPS.md`'s two self-reported blockers (no authentication; Flask debug server) must be independently re-verified as closed at this point, not assumed closed simply because Stage 7 shipped earlier in the sequence.

**Open Questions for Mike:**
1. Does Mike want a formal re-walk of `DEPLOY_VPS.md`'s "Blockers to Resolve" checklist as an explicit part of this stage, even though Stage 7 addressed them structurally?

**Deliverables:** A go/no-go decision from Mike, recorded the same way `DECISION_LOG.md` records every other governed approval — verbatim text, not a paraphrase.

**Test plan:** N/A.

**Walkthrough report:** N/A.

**Stop/Go:** This document does not authorize this step by itself. No launch package can pre-approve a deployment decision — it occurs only under separate, explicit Mike approval at the time of promotion.

---

## Authority Closing

This document is a planning tool that expands the Migration Plan into launch-package detail.

It does not authorize any code change, commit, or deployment to the Dispatch repository.
It does not alter doctrine.
It does not approve any Jules Build Matrix item for merge.

Each stage still requires Mike's explicit sign-off, in order, before the next stage's build work may begin.

**Mike decides.**
