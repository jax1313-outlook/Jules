# DISPATCH_STAGE6_ARCHIVE_IFTA_RECONCILIATION_v1.md

**Document Type:** Architecture Reconciliation — Stage 6 (Archive / IFTA)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Reconciliation Draft — analysis only, no implementation authorized
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document is Stage 6 of the Migration Plan (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16), scoped by Mike as an **architecture reconciliation stage only**. It does not write, modify, or propose committing any production code. It does not modify the Dispatch implementation. It does not open a pull request. It does not create migrations or new database tables. Every finding below is DISCOVER → MAP → REUSE → ALIGN — establishing what already exists and how it fits the governed architecture, before any implementation work is authorized.

The goal is not to redesign IFTA. The goal is not to redesign Archive. Nothing here changes either system.

**Mike Zachary is final authority. AI decides nothing. Mike decides.**

---

## 1. Executive Summary

**What Archive currently does.** There are three separate archive-shaped things in this codebase today, not one:

1. **`cin_lite/archive.py`** — the CIN-Lite government-contract archive. Real, working, SHA-256 hash-verified, fail-closed on tampering. Folder structure: `Raw/Processed/Intelligence/Summaries/Routing/Pending/Outbox/Proposals`.
2. **`portal/models/archive.py`** — a separate, much weaker JSON-file archive for operational records (completed Sandbox entries, Publisher actions). No hashing, no versioning, silently no-ops on a duplicate `source_id`.
3. **IFTA's own compliance archive** (`dispatch/services.py::_write_compliance_record()`) — a third archive, using the same hash-sidecar technique as #1 but deliberately kept as a sibling folder (`Compliance/`), not nested under CIN's tree.

**What IFTA currently does.** A complete, working, five-phase-deep compliance workflow: trip-leg and fuel-purchase intake → deterministic quarterly tax computation → six advisory exception detectors → evidence linkage with checksum verification → a human-gated draft→sealed finalization workflow authenticated by a mailed HMAC link → hash-verified compliance archival. Every phase was individually approved by Mike and individually walked through live before merging (see `PHASE2`–`PHASE7_*_WALKTHROUGH_REPORT_v1.md` in the Dispatch repo).

**What already aligns with the Blueprint.** `cin_lite/archive.py`'s hashing exceeds the Decision Matrix's own SHA-256 requirement. IFTA's `IFTAReportApproval` draft→sealed freeze is the closest working analogue to a Spine Approval Event anywhere in the codebase. The six exception detectors are advisory-only and never auto-block, which is exactly the Alert Governance Doctrine's required posture, already implemented before that doctrine existed. The suspect-entries confidence threshold is a working seed for Intelligence Verification's Partially Verified classification.

**What requires adaptation.** `portal/models/archive.py` needs the version-retention rule and Review Queue that `ARCHIVE_REVIEW_POLICY.md` requires — it has neither. `IFTAReportApproval`'s `approved_by` field is an email address, not an authenticated identity — Stage 7's job, not this stage's. Once Stage 4's generic Approval Event schema and Stage 7's identity layer both exist, `IFTAReportApproval` can be re-pointed at them without changing its proven freeze mechanics.

**What should remain unchanged.** The hash-write/verify/fail-closed mechanism in `cin_lite/archive.py`. The `IFTAReportApproval` freeze/refuse-resubmission/idempotent-reapproval logic. The six exception detectors' detection logic and their "sealed reads frozen data" guarantee. The deterministic IFTA tax computation and `IFTA_TAX_RATES` table. None of these are found to conflict with doctrine — they satisfy it already, in most cases better than doctrine was specified before this reconciliation existed.

---

## 2. Existing Archive Assessment

### 2.1 `cin_lite/archive.py` — the CIN-Lite contract archive

**Current purpose:** persist every stage of a government-contract's pipeline run (`Raw` fetched file → `Processed` metadata+contract → `Intelligence` rule-module JSON → `Summaries` text → `Routing` decision record), plus transient `Pending` decisions and `Outbox`/`Proposals` for the email control system and proposal workflow.

**Current strengths:**
- **Fail-closed integrity, write-time and read-time.** `_write_and_hash()` writes a `.sha256` sidecar alongside every artifact; `_read_verified()` recomputes and compares on every read; a mismatch raises `ArchiveIntegrityError` rather than silently serving corrupted or tampered data.
- **Tamper escalation without collision risk.** `record_integrity_exception()` writes a distinctly-named file (`Routing/{id}.integrity-exception-{uuid}.json`) rather than overwriting the real routing decision — a deliberate design choice made after the launch package's own review found the original approach would have destroyed the evidence a mismatch is meant to preserve (Phase 3 walkthrough report).
- **Both readers verified.** `load_artifact()` and `list_contracts()` both route through the same `_read_verified()` path — a real, tested gap-closure, not an assumption.
- **Deterministic, human-readable IDs.** `make_id()` produces `CIN-YYYYMMDD-{8 hex}`, consistent with this codebase's universal ID convention (confirmed again during Stage 4's implementation).

**Current weaknesses:**
- **No version-retention concept.** There is no "Current + 3 Previous" rule, no Archive Review Queue, no Keep/Delete workflow. A superseded artifact is simply overwritten by the next write to the same path (the hash sidecar changes, the old hash is gone).
- **Backward-compatible-but-permissive on missing sidecars.** A pre-Phase-3 artifact with no `.sha256` file reads through unverified. Correct for backward compatibility, but means integrity coverage is not retroactive — only artifacts written after Phase 3 are actually protected.
- **No audit trail of *who* triggered a write**, only *what* was written and *when* (`decided_at`, `followed_recommendation`). This is a known, pre-existing gap the Reconciliation Matrix already flagged for Security (row 13), not something new found here.

**Current integrity protections:** SHA-256 sidecar hash, computed and verified on every write/read, fail-closed on mismatch, escalated to a `HUMAN_REVIEW` queue entry.

**Current retention behavior:** none — preserve-forever-by-overwrite, which is neither `ARCHIVE_REVIEW_POLICY.md`'s "preserve by default" (no versioning to preserve) nor its "not keep-forever-by-default" (there's no review mechanism to ever flag anything for removal either). This is a genuine gap, not a policy choice.

**Disposition:**
- **Preserve as-is:** the hash-write/verify/fail-closed mechanism, `make_id()`, the folder structure, the tamper-escalation-without-collision design.
- **Adapt:** add version retention (Current + 3) and an Archive Review Queue on top of the existing structure — additive, not a rewrite.
- **Defer:** retroactive hashing of pre-Phase-3 artifacts (explicitly out of scope per the Phase 3 launch package itself).
- **Never remove:** the fail-closed behavior. Doctrine (`ARCHIVE_REVIEW_POLICY.md` §1, `DISPATCH_CONSTITUTION_v3.md` §10) is unambiguous that serving unverified/corrupted data silently is worse than refusing to serve it.

### 2.2 `portal/models/archive.py` — the operational archive

**Current purpose:** record completed Sandbox entries and Publisher actions as historical records, organized by section (`load, decision, publisher, location_history, broker_history`).

**Current strengths:** simple, working, wired into the Portal's `/archive` page and the sandbox-to-archive flow on `PASS`/completion.

**Current weaknesses:**
- **No hashing, no integrity verification of any kind.**
- **Silently no-ops on a duplicate `source_id`** (`create_record()` returns the existing record rather than creating a new version) — the functional opposite of versioning.
- **The module's own docstring claims "audit bundles"; no audit-bundle structure exists in the file or anywhere else in the codebase** (confirmed by direct grep during the earlier reconciliation pass).

**Disposition:**
- **Adapt:** this is the one archive object genuinely under-built relative to doctrine. It needs versioning and a review queue before it can be called a governed Archive in the Blueprint sense.
- **Never remove:** the section-based organization and its role as the Sandbox lifecycle's terminal state — that structure is sound, only its integrity/versioning guarantees are missing.

### 2.3 IFTA's compliance archive (`dispatch/services.py::_write_compliance_record()`)

**Current purpose:** persist the frozen, sealed IFTA report snapshot and its payment recommendation as hash-verified compliance records.

**Current strengths:** reuses the exact SHA-256 sidecar technique Phase 3 proved for `cin_lite/archive.py`, reimplemented locally rather than cross-imported — and deliberately placed as a **sibling** of the CIN archive tree (`<DISPATCH_ARCHIVE_ROOT>/Compliance/`, not `.../CIN/Compliance/`), a design decision explicitly verified in the Phase 4 and Phase 5 walkthrough reports ("confirmed does NOT exist" checks against accidental nesting).

**Current weaknesses:** same version-retention gap as the other two — a sealed record is permanent (correctly, since sealing is a compliance freeze), but there's no Review Queue for it either, and no explicit tie into `ARCHIVE_REVIEW_POLICY.md`'s Monday Report critical-record escalation path (IFTA compliance records are exactly the kind of thing that policy names as Monday-Report-eligible).

**Disposition:** preserve the hashing and sibling-placement decisions as-is; this record type is a strong candidate to be the **first** record type wired into a future Archive Review Queue, precisely because it's already the most rigorously governed of the three archives.

---

## 3. Archive vs Blueprint

| Blueprint Requirement (`ARCHIVE_REVIEW_POLICY.md` / `DISPATCH_FINAL_BLUEPRINT_v1.md` §9) | `cin_lite/archive.py` | `portal/models/archive.py` | IFTA compliance archive |
|---|---|---|---|
| Preserve-by-default | Strong Match — overwrite-on-rewrite is a gap, but nothing is ever silently deleted | Weak Match — dedup-on-duplicate silently drops the second write | Strong Match — sealed records are immutable by design |
| Not keep-forever-by-default (needs a review/purge path) | Missing | Missing | Missing |
| Current Version + Three Previous Versions retention rule | Missing | Missing | Missing |
| Archive Review Queue | Missing | Missing | Missing |
| Monthly Archive Review report | Missing | Missing | Missing |
| Monday Report escalation for critical records | Missing | Missing | Missing (despite being the strongest candidate for it) |
| Keep/Delete decision process + purge approval | Missing | Missing | Missing |
| Fail-closed integrity on read | **Strong Match** — exceeds doctrine, doctrine didn't originally specify fail-closed this explicitly | Conflict — no integrity check exists at all | **Strong Match** |
| Hash algorithm (SHA-256 not MD5, per Decision Matrix) | **Strong Match** | N/A (no hashing) | **Strong Match** |
| Relationship to Library (never merge Library and Archive) | Strong Match — no code path merges them | Strong Match — same | Strong Match — same |
| Audit trail (who/what/when) | Partial Match — what/when yes, who no | Weak Match — docstring claims it, code doesn't have it | Partial Match — same as `cin_lite/archive.py` |

**Summary:** the *integrity* half of Archive doctrine is already strongly satisfied by two of the three archives. The *retention/review* half is missing from all three, uniformly. This is a single, well-defined gap — not three different gaps — and closing it once (as a shared pattern, per Stage 6's own IFTA-first recommendation below) closes it for all three.

---

## 4. IFTA Workflow Assessment

### 4.1 What was inspected

- **Approval gates:** `submit_ifta_quarter_for_approval()` (freezes a snapshot, refuses resubmission — `AlreadySubmittedError`) and `approve_ifta_quarter()` (verifies an HMAC token, seals idempotently, computes the payment recommendation) — `dispatch/services.py`.
- **Evidence linkage:** `attach_ifta_fuel_evidence()`, `IFTAFuelEvidence` (a deliberately separate mirror of `EvidenceItem`, since fuel purchases aren't Load-scoped and the `evidence` table's `load_id` FK is `NOT NULL`), `resolve_ifta_evidence_for_snapshot()` ("skip, don't raise" on an unresolvable link).
- **Evidence review:** `/ifta/review` — `build_ifta_review_dashboard()`, a read-only dashboard combining tax position, jurisdiction breakdown, exceptions, and suspect entries.
- **Exception detection:** six detectors (`fuel_no_miles`, `miles_no_fuel_gap`, `fleet_mpg_out_of_band`, `broken_evidence_linkage`, `late_arrival_closed_quarter`, `corner_clipping`) — advisory-only, insert-only ledger, persisted at submission time, **frozen at seal time** (a sealed quarter's dashboard shows what was true at seal time, not what's true now — verified live in the Phase 6a walkthrough by tampering post-seal and confirming the dashboard didn't change).
- **Suspect entries:** `extraction_confidence` (from vision-assisted receipt scanning), `DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD = 0.75` (explicitly an uncalibrated placeholder, carried over from the reference system it was ported from), deliberately excluded from the readiness rollup — a resolved open question, not an oversight (Phase 7 walkthrough report).
- **Receipt processing:** `cin_lite/agents/receipt_vision.py::extract_fuel_receipt()` — Claude vision call, JSON-schema-constrained, graceful `{"available": False}` fallback on any failure, creates nothing itself (the dispatcher's explicit Save is still the human-confirmation step).
- **Finalization workflow:** `draft` → `sealed`, one-way, per `(year, quarter, vehicle_id)`, idempotent re-approval.
- **Walkthrough reports:** Phases 2, 3, 4, 5, 6a, 6b, 7 — seven independently reviewed, independently approved, independently tested increments, each with a live walkthrough against a real (throwaway) dev server.

### 4.2 What does IFTA already prove?

IFTA is a complete, working, five-times-iterated proof that this codebase's actual engineering team (across whatever tooling built it) can implement, in real production code, the exact pattern the Blueprint specifies in the abstract: **deterministic computation → advisory findings that never auto-block → a human-gated freeze → hash-verified archival → confidence-scored intake with a human-confirmation step.** That is not a coincidental resemblance — it is the same shape, built independently, proven across seven approved phases with zero regressions across the whole 2,373-test suite (as of Stage 5).

### 4.3 Which Dispatch concepts already exist inside IFTA?

| Blueprint Concept | IFTA's Working Analogue |
|---|---|
| Approval Event | `IFTAReportApproval` (draft→sealed) |
| Conflict Event / Alert (advisory) | The six exception detectors |
| Intelligence Verification (Partially Verified) | `extraction_confidence` + suspect-entries threshold |
| Archive integrity | `_write_compliance_record()`'s hash sidecar |
| Version freeze (sealed = immutable) | `sealed_at`, frozen dashboard reads |
| No Fabrication (never fail, never fabricate) | `receipt_vision.py`'s graceful degradation |
| Human-in-the-loop authentication (weak form) | HMAC-signed single-reviewer email link |

### 4.4 Which concepts are reusable?

- **The freeze/refuse-resubmission/idempotent-reapproval mechanics** — directly reusable as the reference implementation for the Spine's generic Approval Event, per Stage 4's own design note (already the plan; this reconciliation confirms it's still the right call after deeper inspection).
- **The six-detector pattern** (advisory, insert-only, frozen-at-seal) — directly reusable as the template for a general exception/alert framework (Stage 10's job).
- **The confidence-threshold-to-classification mapping** — directly reusable as the seed for formal Intelligence Verification classification (Stage 9's job).
- **The hash-sidecar-as-sibling-folder pattern** — directly reusable for any future archive that needs to coexist with `cin_lite/archive.py` without nesting under it.

---

## 5. IFTA Future Role

Evaluated against the six candidate categories:

- **Dispatch Module (pure business feature)** — true but incomplete. IFTA is a real business capability (fuel tax compliance) that Level 1 Transport needs regardless of platform architecture. Classifying it as *only* this would waste its architectural value.
- **Compliance Module** — accurate and necessary. This is IFTA's actual job. Any reconciliation that loses sight of this fails the business.
- **Spine Demonstration Module** — accurate and valuable. As shown in Section 4.3–4.4, IFTA is the only place in the codebase where the full Approval Event / advisory-alert / frozen-archive pattern already runs in production, tested, seven times over.
- **Archive Module** — partially accurate (its compliance records are a real archive), but IFTA is not primarily an archive — archival is one of its outputs, not its purpose.
- **Evidence Module** — partially accurate (fuel-purchase evidence linkage is real and reusable) but too narrow to describe the whole system.
- **Combination** — **recommended.**

**Recommendation:** IFTA should remain, first and foremost, a **Compliance Module** — that is its business identity and must not be diluted. Simultaneously, and without requiring any change to its own code, it should be formally recognized as the **Spine's reference implementation** for Approval Events and Alert Governance, per `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §9's already-approved direction — Stage 6's own analysis here reinforces rather than revises that call. Its compliance records continue flowing into the Archive category via their existing sibling-folder hashing pattern. It is not a Dispatch-load-board module, and it is not primarily an Evidence module (evidence linkage is a supporting feature, not IFTA's reason to exist).

This is a **Combination classification with a clear primary (Compliance) and a clear secondary, non-code-changing role (Spine reference pattern)** — not an even three-way split, and not a reason to rename or restructure anything.

---

## 6. Combined Reconciliation Matrix

| Capability | Current Fit vs Blueprint | Decision | Priority |
|---|---|---|---|
| Archive hash integrity (`cin_lite/archive.py`) | Strong Match | Keep | Low (already correct) |
| Archive hash integrity (`portal/models/archive.py`) | Conflict (absent) | Modify (future stage) | Medium |
| Archive hash integrity (IFTA compliance) | Strong Match | Keep | Low |
| Archive version retention (all three) | Missing (uniformly) | Build New (future stage, one shared pattern) | High |
| Archive Review Queue (all three) | Missing (uniformly) | Build New (future stage) | High |
| IFTA finalization gate mechanics | Strong Match (as a pattern) | Keep, promote as Spine reference | Low |
| IFTA exception detectors | Strong Match | Keep, promote as Alert Governance template | Low |
| IFTA suspect-entries confidence | Strong Match (seed) | Keep, promote as Verification template | Low |
| IFTA `approved_by` identity | Weak Match (email string, not identity) | Modify — belongs to Stage 7, not this stage | Critical (already tracked) |
| IFTA evidence linkage | Strong Match | Keep | Low |
| Monday Report critical-record escalation for IFTA compliance records | Missing | Build New (future stage) | Medium |

No row here contradicts the Reconciliation Matrix or Integrated Blueprint already approved — this table adds precision within Archive/IFTA specifically, it does not revise prior findings.

---

## 7. Reuse Strategy

**Preserve as-is (no future stage should touch these):**
- `cin_lite/archive.py`'s hash-write/verify/fail-closed mechanism and tamper-escalation design.
- `IFTAReportApproval`'s freeze/refuse-resubmission/idempotent-reapproval logic.
- The six exception detectors' detection logic and frozen-at-seal guarantee.
- `_write_compliance_record()`'s sibling-folder placement decision.
- The deterministic IFTA tax computation (`_ifta_aggregate()`, `IFTA_TAX_RATES`).

**Adapt (additive, in a future implementation stage, not this one):**
- Add version retention (Current + 3) and an Archive Review Queue as a **shared pattern** applied to all three archives at once, rather than three separate implementations — the gap is identical across all three (Section 3), so the fix should be too.
- Re-point `IFTAReportApproval` at the Spine's generic Approval Event schema (Stage 4 output) once Stage 7's identity layer exists to populate `approved_by` correctly — this was already the plan; nothing here changes it.
- Add IFTA compliance records to the Monday Report critical-record escalation path.

**Defer:**
- Retroactive hashing of pre-Phase-3 CIN artifacts (the Phase 3 launch package itself scoped this out; nothing found here changes that call).

**Reject:** none identified. No Archive or IFTA asset was found to conflict with doctrine in a way that requires removal or replacement.

---

## 8. What Must Not Change

Per this stage's explicit charter, nothing changes as a result of this document. Beyond that, for any future implementation stage:

- Do not rewrite `cin_lite/archive.py`'s hashing mechanism — extend it, never replace it.
- Do not alter `IFTAReportApproval`'s freeze semantics (one-way, refuse-resubmission, idempotent re-seal) — these are proven across five owner-approved phases.
- Do not change which four exception detectors read live data vs. frozen snapshot data, or the sealed-quarter freeze guarantee.
- Do not merge the three archives into one table/store without Mike's explicit doctrine decision — `DISPATCH_CONSTITUTION_v3.md` §15 forbids merging Library and Archive, and by the same logic, merging distinct archive scopes (contract intelligence vs. operational history vs. compliance records) is an architecture decision requiring the same level of explicit approval, not an implementation detail.
- Do not add authentication/identity fields to `approval_events`-adjacent IFTA code ahead of Stage 7 — that gap is real, tracked, and intentionally sequenced, not accidental.

---

## 9. Open Questions for Mike

These are architecture questions worth answering before any future Archive/IFTA *build* stage is scoped — none are blocking this reconciliation document, but each changes what that future launch package would say:

1. Should the shared version-retention/Review-Queue pattern (Section 7) be built once and applied to all three archives simultaneously, or piloted on the IFTA compliance archive first (the most rigorously governed of the three today) and extended afterward?
2. Should `portal/models/archive.py` eventually be replaced by routing operational records through the same hash-sidecar mechanism `cin_lite/archive.py` and IFTA's compliance archive already use, or does its JSON-section structure serve a genuinely different purpose that should remain a distinct, simpler store?
3. Does Mike want IFTA compliance records added to the Monday Report escalation path now (a small, low-risk addition), or bundled into the future Archive Review Queue work instead of shipped separately?

---

## 10. Recommendation and Next Steps

This reconciliation confirms the direction `DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §9 already set: IFTA becomes the Spine's proof-of-concept for Approval Events and Alert Governance, not a separate feature family, and its compliance archive is the strongest existing model for what a governed Archive should look like. Nothing discovered here changes that conclusion — it deepens it.

**No implementation is authorized by this document.** When Mike is ready to move from reconciliation to build, the next artifact would be a Stage 6 *build* launch package (matching the discipline used for Stage 4 and Stage 5) — covering the shared version-retention/Review-Queue pattern, and the IFTA-to-generic-Approval-Event migration once Stage 7 lands. That launch package does not exist yet and this document does not create it.

---

## Authority Closing

This is an architecture reconciliation document only.

No code was written. No file in the Dispatch repository was modified. No pull request was opened. No migration or database table was created. No implementation work occurred.

Mike Zachary remains final authority.

**Mike decides.**
