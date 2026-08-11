# DISPATCH_STAGE6_ARCHIVE_BUILD_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 6 Build Design — Narrow Build Prompt
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 and the same discipline every prior build stage in this plan has followed.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Approve Stage 6 build." Governed by `DISPATCH_STAGE6_ARCHIVE_IFTA_RECONCILIATION_v1.md` (analysis-only, delivered) and `ARCHIVE_REVIEW_POLICY.md`.

---

## 1. What Stage 6's Original Scope Actually Bundles

`DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`'s Stage 6 entry names two distinct pieces of work: (1) migrate `IFTAReportApproval` onto the generic Spine `ApprovalEvent` schema as a reference pilot migration, and (2) build the Archive Review Queue. These are not one task — they touch different code, carry different risk, and have different prerequisites. Bundling them into one build pass would repeat the mistake this plan has deliberately avoided everywhere else (Stage 7 split into Security Foundation vs. Portal-Wide Enforcement; Stage 12 split into three sequenced passes). This design recommends splitting them here too.

## 2. Investigation Before Scoping Any Code

**Finding 1 — Archive records have no version history at all today; the literal "Current + 3 Previous" rule cannot be built yet.** `ARCHIVE_REVIEW_POLICY.md` §2's Version Retention Rule is explicit: current version plus three previous are retained automatically, anything older than that enters the Review Queue. Direct inspection of `portal/models/archive.py::create_record()` found something stronger than "no version field" — **the function silently no-ops on a repeat `source_id`**: `for existing in data[section]: if existing.get("source_id") == source_id: return existing`. There is no multi-version history being kept in the first place; each source_id is archived exactly once, ever. The literal, doctrine-specified trigger for the Review Queue cannot exist until Stage 8 (Version Doctrine on Archive/Library — still "redefined as analysis-only; delivered," never built) gives Archive records a real version history to compare against.

**Finding 2 — three separate archive systems exist, and unifying them is a separate, larger scope than what's needed right now.** Confirmed again per Stage 6's own reconciliation: `cin_lite/archive.py` (SHA-256 hash-verified CIN contract archive), `portal/models/archive.py` (the operational/load archive — no integrity mechanism, no version history), and the IFTA compliance archive (`IFTAReportApproval`'s own freeze/seal lifecycle). "One shared gap, not three" was the reconciliation's framing, but that doesn't mean one build pass should touch all three architectures at once. `portal/models/archive.py` is specifically what Stage 12's Manager build (§4-M6 design) identified as blocking Manager's M5 Archive half — that's the concrete, motivated target. `cin_lite/archive.py` already has a working integrity mechanism and its own escalation path (`record_integrity_exception()` → `control.ACTIONS["flag_review"]`); the IFTA archive already has its own proven freeze/seal/approval lifecycle. Neither needs this build to touch it.

**Finding 3 — the Spine already anticipated exactly this capability.** `dispatch/spine/models.py::APPROVAL_ACTIONS` (Stage 4, unmodified since) already includes `APPROVE_ARCHIVE_KEEP` and `APPROVE_ARCHIVE_DELETE`. This is the same pattern Stage 7 found for `approval_events.session_id`/`user_id`/`role` — schema built ahead of the feature that would use it. This build reuses `dispatch.spine.store.create_approval_event()` directly; it does not invent new schema.

**Finding 4 — the IFTA migration is meaningfully higher-risk and has an unresolved open question.** `IFTAReportApproval`'s freeze/refuse-resubmission/idempotent-reapproval logic is "proven and tested across five owner-approved phases" — real financial/compliance-facing behavior. Stage 6's own launch package already carries an unresolved open question: whether migrating onto the generic schema requires migrating already-sealed historical rows, or whether existing rows can stay untouched while only new approvals use the generic schema. That question has never been answered. Attempting this migration in the same pass as a net-new Review Queue feature would mix a low-risk additive build with a high-risk migration of proven, tested behavior — exactly the kind of scope-mixing this plan's discipline has avoided everywhere else.

## 3. Recommended Scope For This Build

**Build the Archive Review Queue for `portal/models/archive.py` only, age-based rather than version-based (Finding 1's deviation, flagged not forced). Defer the IFTA-to-generic-schema migration to its own, separately-approved future build pass.**

This is a narrowing of "Approve Stage 6 build," not the full original scope — presented for confirmation via "Approve design," exactly as Stage 7's and Stage 12's narrower scopes were.

### Archive Review Queue v1

- **Trigger:** a record becomes eligible once its `archived_at` timestamp is older than a threshold — proposed default **180 days**, a documented, tunable default (same status as every threshold in the Manager build), not doctrine. This substitutes for the version-based trigger doctrine specifies, until Stage 8 makes the real one buildable.
- **Storage:** no new database table, no new file. Two additive fields on each existing archive record dict: `review_status` (`"pending"` default, `"kept"`, `"deleted"`) and `reviewed_at`/`disposition_reason` once acted on. `portal/models/archive.py` is JSON-file-based already; this is an additive field change to records already being written, not a schema migration.
- **Keep/Delete action:** a new, **Authority-gated** POST route (`/api/archive/review-decision`, using `portal.auth_helpers.authority_required` — the same decorator `/settings` already uses) records the decision as a real `ApprovalEvent` via `create_approval_event()`, action `APPROVE_ARCHIVE_KEEP` or `APPROVE_ARCHIVE_DELETE`, with **real `session_id`/`user_id`/`role`** — the first Portal action route in this codebase to actually populate those fields with a live identity, putting Stage 7's capability to its first real use. Also writes an `AuditEvent` in the same call (`create_approval_event(..., audit=AuditEvent(...))`), satisfying `ARCHIVE_REVIEW_POLICY.md` §6's "a delete action must record... audit event" requirement.
- **"Delete" does not physically delete anything in this build.** It records the disposition decision (`review_status="deleted"`) and the full approval/audit trail. Actually removing the record or its underlying evidence files from disk is a materially more dangerous, irreversible capability that deserves its own explicit design and Mike sign-off specifically on the purge mechanism — not bundled into a first build that's meant to prove the review/decision workflow works. This is flagged, not silently narrowed: if Mike wants real physical purge in this same pass, say so and it gets its own section before implementation.
- **Rendering:** a new panel on the existing `/archive` Portal page (`portal/templates/archive.html`), not a new page — reusing the page that already lists every archive section, matching the existing convention of one page per domain (`conflicts.html`, `exceptions.html`) rather than adding a `/archive/review` page that would fragment the existing view.

### Explicitly Not Part Of This Build

- The IFTA-to-generic-`ApprovalEvent`-schema migration — deferred to its own future build pass, its own open question about historical rows resolved separately before that pass begins.
- A version-accurate Review Queue trigger (Current + 3 Previous) — blocked on Stage 8, not attempted here.
- Extending review to `cin_lite/archive.py` or the IFTA compliance archive — both already have their own integrity/lifecycle mechanisms; unifying them under one Review Queue is a separate, later reconciliation if Mike wants it.
- Physical purge on Delete — recorded as a decision only, per above.
- The Monthly Archive Review Report (`ARCHIVE_REVIEW_POLICY.md` §4) as an actual delivered report — no report-delivery mechanism exists anywhere in this codebase yet (Stage 10's reconciliation found the same gap for Monday/Monthly reports generally); this build makes the underlying queue and decisions real and visible in Portal, it does not build a report-generation/delivery pipeline.
- Wiring Manager's M5 Archive half to consume this queue — a natural, low-risk follow-on once this ships, but its own separate task, not bundled here.

## 4. Files In Scope

| File | Action | Purpose |
|---|---|---|
| `portal/models/archive.py` | Modify | Add `list_review_queue(age_days=180)`, `mark_reviewed(record_id, section, disposition, reason)`; `create_record()` gains `review_status`/`reviewed_at`/`disposition_reason` defaults |
| `portal/routes/api.py` | Modify | New `POST /api/archive/review-decision`, `@authority_required`, calls `create_approval_event()` (+ `AuditEvent`) |
| `portal/templates/archive.html` | Modify | New Review Queue panel: age, section, suggested disposition fields per `ARCHIVE_REVIEW_POLICY.md` §4's report shape; Keep/Delete buttons, matching `conflicts.html`'s existing button convention |
| `portal/static/style.css` | Modify | Minor additive styling only, matching existing card conventions |
| `tests/test_archive_review_queue.py` | New | Full test suite — see §5 |

**No file under `cin_lite/`, `dispatch/services.py`'s IFTA functions, `dispatch/spine/`, or `dispatch/security/` is modified.** The Spine's `create_approval_event()` and Security's `authority_required` are consumed, not changed.

## 5. Test Plan

- **Queue eligibility:** a record archived 200 days ago appears in `list_review_queue()`; one archived 30 days ago does not; threshold is exact at the boundary.
- **Keep/Delete authorization:** an unauthenticated request to the decision route redirects/rejects; a non-Authority session gets 403 (matching `/settings`'s existing pattern); an Authority session succeeds.
- **ApprovalEvent correctness:** a Keep decision writes `action="APPROVE_ARCHIVE_KEEP"` with the real `session_id`/`user_id`/`role` of the acting Authority user; same for Delete with `APPROVE_ARCHIVE_DELETE`.
- **No physical deletion:** after a Delete decision, the underlying archive record and any referenced evidence files still exist on disk — only `review_status` changed. A structural guard test confirms no `unlink`/`rmtree`/file-delete call anywhere in the new code path.
- **Idempotency:** acting twice on the same record's review doesn't create two ApprovalEvents or silently overwrite the first decision without an audit trail.
- **Regression:** full existing suite re-run clean, matching every prior stage's "zero behavior change to anything not in scope" bar — in particular, `create_record()`'s existing dedup-on-repeat-`source_id` behavior must remain unchanged for every existing caller.

## 6. Walkthrough Requirements

Required, live, matching every prior build stage's convention:
1. Seed an archive record with a backdated `archived_at` (>180 days); confirm it appears in the new Review Queue panel on `/archive`.
2. Attempt the Keep/Delete action unauthenticated → rejected; log in as a non-Authority role → 403; log in as Authority → succeeds.
3. Confirm the resulting `ApprovalEvent` carries real identity, and an `AuditEvent` was written alongside it.
4. Confirm the underlying record/file is untouched after a Delete decision — only its `review_status` changed.
5. Full regression suite re-run clean.

## 7. Stop/Go

Go for the Archive Review Queue v1 (age-based, `portal/models/archive.py` only, Keep/Delete recorded not physically executed) once the authorization boundary and no-physical-deletion guarantee are proven, live and by test, and full regression is clean. The IFTA-to-generic-schema migration remains explicitly deferred — its own future build pass, its own design, its own resolution of the still-open historical-rows question, none of it authorized by this document.

Mike decides.

---

*End of DISPATCH_STAGE6_ARCHIVE_BUILD_DESIGN_v1.md.*
