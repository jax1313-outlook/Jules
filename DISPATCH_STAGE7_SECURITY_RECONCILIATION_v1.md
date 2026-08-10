# DISPATCH_STAGE7_SECURITY_RECONCILIATION_v1.md

**Document Type:** Architecture Reconciliation — Stage 7 (Security and Authentication)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Reconciliation Draft — analysis only, no implementation authorized
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document is Stage 7 of the Migration Plan (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16), scoped by Mike as **Architecture Reconciliation Mode only** — the same mode used for Stage 6. It does not write, modify, or propose committing any production code. It does not modify the Dispatch implementation. It does not open a pull request. It does not create migrations or new database tables. It does not build or implement Security Foundation. It does not produce a Stage 7 build launch package — that remains a separate, later artifact, not created here.

The purpose is to determine how `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md` — which already exists as approved doctrine — integrates with the Dispatch implementation as it actually exists today. This is not a redesign of the specification.

**Mike Zachary is final authority. AI decides nothing. Mike decides.**

---

## 1. Executive Summary

**What the Security Specification requires.** A four-question standard (who is this user, how was it verified, what may they do, what did they do) backed by five doctrine pillars — Identity, PIN, Authority, Audit — four roles (Authority, Driver, External Viewer, System Service), a PIN lifecycle, a Session model, a Permission model, and a Portal-mediated Approval Flow that ties every Authority action to an authenticated session and an audit record.

**What Dispatch currently has.** Confirmed by direct code inspection and a full grep sweep during earlier reconciliation work: **zero authentication, zero authorization, zero role model, zero PIN mechanism, and zero per-user audit trail anywhere in the running application.** `portal/config.py` configures a `SECRET_KEY` but nothing in the codebase ever uses it (no Flask session, no cookie, no CSRF token is ever issued). The only access-control-adjacent mechanism anywhere is a shared-secret HMAC-SHA256 token pattern on three email-based decision endpoints, which authenticates *possession of a mailed link*, not a user's identity.

**What already aligns.** The HMAC token *mechanics themselves* — proper secret-based signing, constant-time comparison, sound failure handling — are correctly implemented and directly reusable as a secondary confirmation layer once real session authentication exists. Stage 4 already anticipated this entire reconciliation: the Spine's `approval_events` table has `session_id`/`user_id`/`role` fields that are deliberately nullable specifically because Stage 4's own design document named Stage 7 as the stage that populates them. Nothing about Stage 4's schema needs to change for Stage 7 to land.

**What is missing.** Nearly everything else: an Identity/users table, a PIN mechanism of any kind, a Session model, a Role/Permission model, a Security Sub-Library, a security event log, and Driver/External Viewer access boundaries (every Portal route is reachable by anyone who can reach the process).

**What can be reused.** The HMAC token verification code (as a secondary layer, not primary auth), `PORTAL_SECRET_KEY` (as the future session-signing key, once sessions exist to sign), the free-text actor fields already threaded through the domain model (`approved_by`, `entered_by`, `author`, `uploaded_by`, `confirmed_by`) as the exact map of where a real `user_id` foreign key needs to reach, and the IFTA approval-gate's mailed-link UX pattern as a proven interaction model worth preserving.

**What should remain unchanged.** Stage 4's `approval_events` schema (already correct — this stage populates it, does not redesign it). The HMAC token mechanics' code quality. Business-entity identity models (`Driver`, `BrokerContact`) — these are fleet/business records, not security identities, and must not be conflated with a future Identity table without a separate, explicit doctrine decision.

---

## 2. Security Sub-Library Integration

`LIBRARY_INGESTION_RULE.md` §6 requires a distinct Security sub-library within Library, gated by a **separate PIN re-check at the moment of access** (distinct from the general Portal session login PIN), with a governed PIN reset capability, and a hard boundary preventing Publisher/Intelligence/Driver/External Viewer from ever reading its contents.

**Current state:** `portal/models/library.py` has no sub-section/scoping concept beyond its existing `SECTIONS` list (`company, broker, customer, location_intelligence, operations, intelligence`) — no `security` section exists, and there is no PIN mechanism anywhere to gate it with even if the section existed.

**How it integrates:** the Security Sub-Library is structurally a **downstream consumer of this stage's own Identity/PIN foundation**, not a parallel concern needing its own PIN implementation. Its "separate PIN re-check" requirement is the same PIN-validation code a general Portal login would use, called a second time at a different trigger point (opening the sub-library) rather than a second, independently-built PIN system. Building it before Identity/PIN exist would mean building PIN validation twice.

**Classification:** Missing. **Reuse:** none yet exists to reuse. **Build New:** yes, but only after the general PIN mechanism exists — this is a sequencing finding, not a scope reduction.

---

## 3. Identity Mapping

Security Spec §2.1 defines a Dispatch identity as a controlled record: `user_id, display_name, role, status, pin_record_id, created_at, updated_at, last_login_at, permissions, authority_level`.

**Current Dispatch structures that are identity-*adjacent*, and why none of them are a security Identity:**

| Existing Structure | What It Actually Is | Why It Is Not a Security Identity |
|---|---|---|
| `Driver` model (`dispatch/models.py`) | A fleet resource record — name, license class/number, phone, email, employment status | Models a business entity (a driver Level 1 Transport employs), not an authenticated system actor. A `Driver` row has no relationship to who is logged into Portal. |
| `BrokerContact` model | A business contact record | Same category error risk — a broker contact is not a Portal user. |
| Free-text actor fields: `approved_by` (`IFTAReportApproval`), `entered_by` (`MilestoneEvent`), `author` (`LoadActivity`), `uploaded_by` (`EvidenceItem`, `IFTAFuelEvidence`), `confirmed_by` (`RateConfirmation`) | Unvalidated `TEXT` fields, populated today with values like the literal string `"reviewer"`, an email address, or whatever a dispatcher typed | No table backs them, no uniqueness constraint, no relationship to any session. They record a *claim* of who acted, not a *verified* identity. |

**The mapping finding:** none of the above becomes a security Identity by renaming or repurposing it — a real `users`/identities table is new construction (a future Stage 7 build concern, not this stage's). But the free-text actor fields are directly useful as a **map of exactly where a `user_id` foreign key needs to reach** once Identity exists — every one of those fields is a place doctrine's Audit requirement ("who acted") is currently unsatisfied, and every one is a natural, additive migration target later.

**Classification:** Missing (as a security concept). Partial Match (as a pre-existing map of where identity must be threaded through).

---

## 4. PIN Architecture

Security Spec §2.2, §4: managed creation, one-PIN-per-user assignment, validated login, change, Authority-gated reset, and revocation — never stored as plaintext.

**Current state:** zero PIN concept anywhere, confirmed by direct grep sweep (no matches for "PIN"/"pin_" as a concept; only coincidental substring hits inside unrelated words like "overlappING"). The nearest thing that could be mistaken for a PIN is `DISPATCH_EMAIL_SECRET` (`cin_lite/email_delivery.py`) and its `dispatch/notifications.py` counterpart — but this is a **server-side shared HMAC-signing secret**, not a credential a human enters. Flagging this distinction explicitly because it is an easy category error: a shared server secret used to sign a token is architecturally nothing like a per-user PIN, even though both involve the word "secret"/"key."

**Relationship to the Security Sub-Library:** the PIN mechanism this stage would eventually build is the *same* mechanism the Security Sub-Library's separate access-check calls a second time — one PIN system, two trigger points, not two PIN systems.

**Classification:** Missing.

---

## 5. PIN Reset and Recovery

Security Spec §4.5: reset requires Authority approval or an approved reset workflow; Driver/External Viewer resets must never grant new permissions.

**Current state:** no reset mechanism exists because no PIN mechanism exists. There is no directly reusable code. The closest *pattern* (not code) in the current system is IFTA's finalization gate: a sensitive state change (sealing a quarter) requires a second, distinct confirmation step (the mailed HMAC link) beyond the initial action (submission). A PIN reset workflow has the same shape — a sensitive credential change should require a second confirming step beyond the request itself — and IFTA's gate is worth studying as a proven interaction pattern when Stage 7 build designs the reset flow, without importing any of its code (which is IFTA-specific and does not generalize).

**Classification:** Missing.

---

## 6. Authority Events to Approval Events

Security Spec §7: an Authority Action requires an authenticated session, the Authority role, an active permissions snapshot, a Portal-mediated action, and an audit record.

**The mapping is already half-built.** Stage 4 (already implemented and merged to the `stage4-spine-schemas` branch) created the generic `approval_events` table with exactly the fields Security Spec §9 and Spine Spec §10 require, including `session_id`, `user_id`, and `role` — deliberately left **nullable**, with a test (`test_approval_event_interim_identity_gap_is_nullable`) asserting this explicitly so the gap cannot silently tighten or loosen without a conscious code change. Stage 4's own design document named this exact stage — Stage 7 — as the one that closes it.

**What this means for Stage 7:** a "Security Spec Authority Action" *is* an `approval_events` row where `role == "Authority"` and `session_id`/`user_id` are populated instead of null. No new schema is needed. Stage 7's job is to make those three fields real, not to design where they live.

**Classification:** Partial Match — the target schema exists and was purpose-built for this; the identity data required to populate it does not exist yet.

---

## 7. Existing HMAC Gates Mapped to Future Identity Controls

Three independent decision endpoints today, all following the identical pattern:

| Gate | Location | Verifies |
|---|---|---|
| CIN/SAM contract decision | `portal/routes/decisions.py` | `email_delivery.verify_token()` |
| Dispatch-load decision | `portal/routes/dispatch_api.py::dispatch_decision()` | `notifications.verify_token()` |
| IFTA quarter approval | `dispatch/services.py::approve_ifta_quarter()` | `email_delivery.verify_token()` (reused directly, not reimplemented) |

All three: HMAC-SHA256, `hmac.compare_digest` (correct — timing-safe), a shared secret with a hardcoded fallback default if `DISPATCH_EMAIL_SECRET` is unset (a stderr warning only, no refusal to start — a known, already-tracked risk, not a new finding).

**What this proves:** the *mechanics* are implemented correctly — proper signing, proper comparison, sound degradation behavior. What they verify is wrong for the claim made about them: `pipeline.py`'s own docstring calls the CIN/SAM route "session-authenticated," which is false — there is no session. The token proves a link was clicked, not who clicked it.

**How they map forward, without being discarded:** once session authentication exists, these become a **secondary confirmation layer**, not a replacement target. The email-approval UX (click a link from your phone, approve without opening Portal) is genuinely valuable and IFTA's walkthrough reports show it working correctly across five phases — the fix is requiring the token **and** a session belonging to the intended approver, not removing the token. This closes the actual gap (today, anyone who intercepts or is forwarded the email can act) without discarding working, tested code.

**Classification:** Partial Match — correct mechanics, insufficient claim. Not a Conflict, because nothing here contradicts doctrine outright; it under-delivers on an authentication claim the code itself (incorrectly) makes in one comment.

---

## 8. Security Specification to Current Code — Full Capability Table

| Security Capability | Doctrine Source | Current Asset | Current Fit | Reuse / Modify / Build New | Notes |
|---|---|---|---|---|---|
| Identity Doctrine | Security Spec §2.1 | None | Missing | Build New | Free-text actor fields (Section 3) show where `user_id` must reach |
| PIN Doctrine | Security Spec §2.2 | None | Missing | Build New | Do not conflate with `DISPATCH_EMAIL_SECRET` (Section 4) |
| Authority Doctrine | Security Spec §2.3 | `DECISION_LOG.md`'s owner-approval-per-phase process | Partial Match | Reuse (as a build-time process) / Build New (as a runtime role) | Governs code changes today, not runtime decisions — do not conflate the two |
| Audit Doctrine | Security Spec §2.4 | `audit_events` table (Stage 4) + free-text actor fields | Partial Match | Modify | Schema exists; "who" data to populate it does not |
| Authority role | Security Spec §3.1 | None | Missing | Build New | — |
| Driver role | Security Spec §3.2 | `Driver` model (business entity only) | Weak Match | Build New (role) / Reuse (link to existing `Driver` records) | `Driver` is fleet data, not a login identity — needs a role/session layer on top |
| External Viewer role | Security Spec §3.3 | None | Missing | Build New | No external/internal boundary exists at all today |
| System Service role | Security Spec §3.4 | Implicit — background jobs run as the app process itself | Weak Match | Build New | No formal distinction between human and system actors anywhere |
| PIN Creation | Security Spec §4.1 | None | Missing | Build New | — |
| PIN Assignment | Security Spec §4.2 | None | Missing | Build New | — |
| PIN Validation / login | Security Spec §4.3 | None (one false docstring claim of "session-authenticated") | Missing | Build New | See Section 7 |
| PIN Change | Security Spec §4.4 | None | Missing | Build New | — |
| PIN Reset | Security Spec §4.5 | None (IFTA's gate is a study pattern only, not reusable code) | Missing | Build New | See Section 5 |
| PIN Revocation | Security Spec §4.6 | None | Missing | Build New | — |
| Session Model | Security Spec §5 | `PORTAL_SECRET_KEY` configured, never used | Weak Match | Reuse (the config value) / Build New (the model) | The key exists; nothing signs anything with it yet |
| Permission Model | Security Spec §6 | None | Missing | Build New | — |
| Authority Actions | Security Spec §7 | `approval_events` table (Stage 4) | Partial Match | Modify | See Section 6 |
| Portal-Mediated Approval Flow | Security Spec §8 | The three HMAC gates | Partial Match | Modify | See Section 7 |
| Approval Event Schema | Security Spec §9 | `dispatch/spine/models.py::ApprovalEvent` (Stage 4, already built) | **Strong Match** | Reuse | Built specifically anticipating this stage |
| Authentication Context Schema | Security Spec §10 | `ApprovalEvent.authentication_context` field exists, unpopulated | Partial Match | Modify | Field exists (Stage 4); shape to populate it does not |
| Library and PIN Records | Security Spec §11 | `LIBRARY_INGESTION_RULE.md` §6 (doctrine only, no code) | Missing | Build New | See Section 2 |
| Security Boundaries by Function | Security Spec §12 | Partially true by accident — Publisher/Intelligence never touch PIN data because no PIN data exists | Weak Match | Build New | The boundary is currently satisfied only because there is nothing to violate |
| Driver Portal Security | Security Spec §13 | `Driver` model + driver-facing templates, no access boundary | Weak Match | Build New | Matrix row 3/18 from earlier reconciliation, restated here for Security-specific detail |
| External Viewer Security | Security Spec §14 | None | Missing | Build New | — |
| PIN Change/Review Reporting | Security Spec §15 | None (no Monday/Monthly report integration for security events) | Missing | Build New | — |
| Security Event Types | Security Spec §16 | None (`LOGIN_SUCCESS` etc. do not exist as a concept) | Missing | Build New | — |
| Forbidden Security Actions (as a live check) | Security Spec §18 | See notes | **Conflict** (one item) | Modify | "Allow unauthenticated approval" is not hypothetical — it is the literal current behavior of every Portal route and all three decision gates today |

---

## 9. What Already Exists

- HMAC-SHA256 token verification, correctly implemented (two independent copies: `cin_lite/email_delivery.py` and `dispatch/notifications.py`, same pattern, not shared code).
- `PORTAL_SECRET_KEY`, configured, currently inert.
- Free-text actor fields across the domain model, marking exactly where identity needs to reach.
- Stage 4's `approval_events`/`audit_events` schema, purpose-built with this stage in mind.
- `LIBRARY_INGESTION_RULE.md` §6's Security Sub-Library doctrine (specified, not built).
- `portal/routes/pages.py`'s `/settings` route, which currently exposes which secrets/keys are configured to any unauthenticated visitor — worth naming here specifically as a Security-relevant finding, since it's an information-disclosure surface that gets more dangerous, not less, the longer authentication is absent.

## 10. What Is Missing

Identity/users table; PIN mechanism (all six lifecycle stages); Session model; Role/Permission model; Security Sub-Library; security event log and event types; Driver Portal and External Viewer access boundaries; any per-user "who acted" data anywhere in the audit trail.

## 11. What Can Be Reused

- HMAC token verification code, as a secondary confirmation layer (Section 7).
- `PORTAL_SECRET_KEY`, as the future session-signing key.
- The free-text actor field locations, as an implementation map (Section 3).
- Stage 4's `ApprovalEvent`/`AuditEvent` schemas, unmodified (Section 6).
- The IFTA mailed-link approval UX, as a proven interaction pattern to preserve, layered with session auth rather than replaced.

## 12. What Should Remain Unchanged

- Stage 4's `approval_events`/`audit_events` schema and the `transition()`/`apply_transition()` guard — this stage populates fields, it does not redesign the Spine.
- The HMAC token mechanics' actual cryptographic implementation (signing, comparison) — sound and reusable as-is.
- `Driver`, `BrokerContact`, and other business-entity models — these must not be merged into or repurposed as a security Identity table without a separate, explicit doctrine decision from Mike (the same caution Stage 6 raised about not merging Archive scopes without explicit approval applies here to Identity scopes).

---

## 13. Open Questions for Mike

1. Does the initial Stage 7 build need to support only a single Authority user (Mike) at first, or does day-one scope include Driver and/or External Viewer roles as well?
2. Should the two independently-implemented HMAC token functions (`cin_lite/email_delivery.py`, `dispatch/notifications.py`) be consolidated into one shared implementation as part of a future Stage 7 build, or left as-is since both already work correctly and the duplication risk is low?
3. Should the Security Sub-Library's separate PIN re-check be built in the same implementation pass as general Portal login, or as an immediate follow-on once login exists (Section 2's sequencing finding)?
4. Does Mike want `/settings`'s current unauthenticated exposure of configured-secret flags addressed as an early, small fix ahead of full Security Foundation, given it's a live information-disclosure surface today?

## 14. Recommendation and Next Steps

This reconciliation confirms Stage 4's own design anticipated this exact stage correctly — the target schema for Authority Actions already exists and needs no redesign. The actual gap is uniformly the same gap named throughout every prior reconciliation pass (the Repo Reconciliation Matrix, the Integrated Blueprint, Stage 6): there is no identity, no PIN, no session, and no role model anywhere in the running application, and that gap is the single hard blocker on any network/VPS deployment, per `DEPLOY_VPS.md`'s own self-reported blocker.

**No implementation is authorized by this document.** When Mike is ready to move from reconciliation to build, the next artifact is a Stage 7 *build* launch package (matching the discipline used for Stage 4 and Stage 5) — not created here.

---

## Authority Closing

This is an architecture reconciliation document only.

No code was written. No file in the Dispatch repository was modified. No pull request was opened. No migration or database table was created. No Security Foundation capability was built or implemented.

Mike Zachary remains final authority.

**Mike decides.**
