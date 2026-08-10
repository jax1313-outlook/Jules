# DISPATCH_STAGE8_VERSION_DOCTRINE_RECONCILIATION_v1.md

**Document Type:** Architecture Reconciliation — Stage 8 (Version Doctrine Retrofit)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Reconciliation Draft — analysis only, no implementation authorized
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document is Stage 8 of the Migration Plan (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16), delivered in the same **Architecture Reconciliation Mode** Mike specified for Stages 6 and 7: no production code, no Dispatch repository modification, no pull request, no migrations, no new database tables, no Stage 8 build launch package. Discovery, mapping, reuse, alignment — not a redesign of Version Doctrine, and not a build.

**Mike Zachary is final authority. AI decides nothing. Mike decides.**

---

## 1. Executive Summary

**What Stage 8 originally scoped.** Per the Migration Plan, Stage 8 extends `Ver: X` / `Last Change:` display to Library and Archive records and IFTA records — Sandbox and Conflict Notices are already done (Stage 5).

**What already exists to build from.** Stage 5 is a working, tested precedent, not a hypothesis: `portal/models/sandbox.py` proves a lightweight pattern — a `version` integer, a `last_change` plain-language label, bumped only on a detected meaningful change, backfilled at read time for legacy records — that satisfies Version Doctrine without requiring full historical snapshot storage. This pattern is directly reusable for Library.

**What's genuinely different for Archive.** Archive's version *display* is architecturally coupled to Archive's version *retention*, in a way Library and Sandbox are not. You cannot meaningfully show "Ver: 2" for an archived artifact unless a Ver: 1 still exists somewhere to have been superseded — and none of the three existing archives (`cin_lite/archive.py`, `portal/models/archive.py`, IFTA's compliance archive) currently retain prior versions of anything; each overwrites in place. This means Archive's half of Stage 8 cannot be usefully separated from Stage 6's already-identified, already-deferred retention/Review-Queue gap. They are one build, not two.

**What's genuinely different for IFTA.** Most IFTA records (`IFTATripLeg`, `IFTAFuelPurchase`, `IFTAException`) are **append-only by design** — created once, never mutated. Version Doctrine exists to answer "has this changed since I last saw it," which is not a question an append-only record can ever raise. Retrofitting a `version` field onto them would be motion without purpose. `IFTAReportApproval` is the one IFTA record with real state change (`draft` → `sealed`), but its existing status field already answers Version Doctrine's underlying question as well as a numeric version would — an explicit `sealed` status label is arguably clearer than "Ver: 2" for a two-state record. This is a finding, not an assumption: Stage 8 should not retrofit version fields where nothing changes, and should consider whether IFTA's own status semantics already satisfy the doctrine's intent before adding a field on top of them.

---

## 2. Version Doctrine Requirements (Recap)

Per `DISPATCH_VERSION_DOCTRINE.md` and `DISPATCH_FINAL_BLUEPRINT_v1.md` §11: every significant object displays `Ver: X`; version increases only on a *meaningful* change, never on noise; a plain-language `Last Change:` label accompanies it; the current version and prior versions remain distinguishable (Final Blueprint §8.2's "current pointer + retained prior versions"). Doctrine's own success standard (§10): Mike can tell, within seconds, whether an item is new, previously seen, how many times it's changed, and whether it's worth opening again — without reading timestamps.

---

## 3. The Sandbox Precedent (Stage 5) — What It Actually Proved

Stage 5 is not a design proposal; it is working, tested code (`stage5-portal-reconciliation` branch, 21 passing tests). What it proved, specifically:

- **Version tracking does not require full snapshot retention.** Sandbox entries carry a `version` int and a `last_change` string, not a history of every prior JSON blob. The `events` array (already existing, pre-Stage-5) retains a lightweight change log (`{action, from, to, note, timestamp}` entries), which is enough to answer "how many times has this changed and what changed last" without storing N full copies of the record.
- **Change detection must be deliberate, not automatic-on-every-write.** `_detect_change_label()` diffs specific fields (rate, schedule, score, summary, routing recommendation, flags) before bumping version — a same-data refresh (the common "hit refresh and re-run acquisition" case) does not create version noise. This was explicitly required by doctrine (§6: "should not increase for meaningless system noise") and explicitly tested.
- **Read-time backfill handles legacy records without a migration script.** Records written before the version fields existed get sane defaults computed on read (`_with_version_defaults()`), not a one-time batch migration.

This is the template. The question for Library and Archive is not "how should version tracking work" — Stage 5 already answered that — but "does each object's actual mutation pattern fit this template, or does it need something different."

---

## 4. Library Assessment

**Current state (`portal/models/library.py`):** `add_record()` sets `status: "approved"` unconditionally (confirmed correct for human-placed documents by `LIBRARY_INGESTION_RULE.md`). `update_record()` overwrites the stored content **in place, with no trace of the prior version** — strictly worse than pre-Stage-5 Sandbox, which at least had an `updated_at` timestamp and an `events` array. Library today has neither.

**Does the Sandbox pattern fit?** Better than it fits Archive, and more simply than it fits Sandbox itself. Per `LIBRARY_INGESTION_RULE.md` §8 ("immediate acceptance does not exempt a record from version tracking"), a human explicitly re-uploading/replacing a Library document is, by definition, already a deliberate human action — unlike Sandbox's `create_entry()`, which gets called on every routine data refresh regardless of whether anything actually changed. **Library does not need Sandbox's diffing logic (`_detect_change_label()`) at all** — every call to `update_record()` already represents an intentional human change, so a version bump can be unconditional on update, which is simpler than Sandbox's case, not harder.

**What's still an open design question (not this stage's to answer, but worth surfacing for a future build package):** does "retained prior versions" for Library mean keeping old content bodies retrievable, or is a version counter + `last_change` label (Sandbox's lighter-weight interpretation) sufficient for Library too? Final Blueprint §8.2 says "retained prior versions, distinguishable from the current at all times" — read literally, that implies old content must remain accessible, which Sandbox's implementation does not actually do (its `events` array logs *that* something changed and a label describing it, not the prior field values themselves). This is a real interpretation gap in how far Stage 5's precedent generalizes, flagged here rather than resolved unilaterally.

**Classification:** Missing (Library has zero version concept today — worse off than pre-Stage-5 Sandbox).

---

## 5. Archive Assessment

Per Stage 6's reconciliation, three separate archive-shaped assets exist, and **all three are uniformly missing version retention** — this stage's findings do not change that, they sharpen it specifically for the *display* half of the doctrine:

| Archive | Version Field Today | Can Version Display Be Added Without Retention? |
|---|---|---|
| `cin_lite/archive.py` | None — each write to a path overwrites the prior hash | **No.** A write to `Processed/{id}.json` replaces the file; there is no "Ver: 1" left anywhere once "Ver: 2" is written. Displaying a version number for an object with no retained history to count is not meaningful. |
| `portal/models/archive.py` | None — silently no-ops on duplicate `source_id` | **No**, for the same reason, and worse — a second archival attempt today isn't even recorded as a change, it's discarded outright. |
| IFTA compliance archive | None — sealed records are immutable, but there is only ever one sealed record per period (no re-sealing path exists) | **Partially** — since a sealed IFTA record is genuinely never superseded (re-submission of an already-submitted period is refused, not just discouraged), a static "Ver: 1 (Sealed)" label would be accurate and require no retention change. This is the one Archive case where version display could be added standalone. |

**The core finding:** for two of the three archives, Version Doctrine's display requirement and Archive Review Policy's retention requirement (Stage 6's already-deferred build scope) are **the same build, not two sequential ones.** You cannot show a meaningful version number for something that gets silently overwritten. Splitting "add version display" from "add retention" into separate build stages, as the original Migration Plan's Stage 6/Stage 8 split implied, does not hold up under closer inspection for `cin_lite/archive.py` and `portal/models/archive.py` specifically.

**Classification:** Missing (all three), with a note that IFTA's compliance archive is the sole exception where minimal version display could be added without also solving retention.

---

## 6. IFTA Records Assessment

| Record | Mutation Pattern | Version Doctrine Applicable? |
|---|---|---|
| `IFTATripLeg` | Create-only (no update path found in `dispatch/services.py`) | **No** — append-only, nothing to version |
| `IFTAFuelPurchase` | Create-only (evidence/`extraction_confidence` attach after the fact, but the core record itself isn't edited) | **No** — same reasoning |
| `IFTAException` | Explicitly documented as "persisted once... never updated or deleted after that" (`dispatch/models.py`) | **No** — immutable by explicit design, confirmed in Stage 4/prior reconciliation work |
| `IFTAReportApproval` | `draft` → `sealed`, one transition, then frozen | **Debatable, not obviously yes** — see below |

**On `IFTAReportApproval` specifically:** this is the one IFTA record that changes state at all, and Version Doctrine's underlying question — "have I seen this, how many times has it changed, is it worth looking at again" — is already answered by its existing `status` field (`draft` vs `sealed`) at least as clearly as a numeric `Ver: X` would answer it. Adding a `version` field here risks doctrine-compliance-by-checkbox rather than doctrine-compliance-by-purpose: the object would technically display `Ver: 2` on sealing, but a human reading "SEALED" already knows exactly what that means, arguably better than a bare version number would. This is a genuine open question, not a settled recommendation to skip it — see Section 9.

**Classification:** Not Applicable (three of four record types — append-only, no mutation to track), Weak Match / Question (the fourth — status already may satisfy doctrine's intent).

---

## 7. Version Doctrine vs Current Code — Full Capability Table

| Object Type | Doctrine Source | Current Asset | Current Fit | Reuse / Modify / Build New | Notes |
|---|---|---|---|---|---|
| Portal cards (Sandbox) | Version Doctrine §5 | `portal/models/sandbox.py` (Stage 5) | **Strong Match** | Reuse | Already built, tested, live |
| Conflict Notices | Version Doctrine §5 | `portal/models/conflict.py` `card_level` only, no version field | Weak Match | Build New | Stage 5 added `card_level` to conflicts but not `version`/`last_change` — a real, narrow gap Stage 5 left open, worth naming explicitly |
| Library assets | Version Doctrine §5, Final Blueprint §8.2 | None | Missing | Build New | Simpler than Sandbox — no diffing needed (Section 4) |
| Archive records (`cin_lite`) | Version Doctrine §5 | None | Missing | Build New — coupled to Stage 6's retention build | Cannot be built standalone (Section 5) |
| Archive records (`portal/models`) | Version Doctrine §5 | None | Missing | Build New — coupled to Stage 6's retention build | Same |
| Archive records (IFTA compliance) | Version Doctrine §5 | None | Missing (but standalone-addable) | Build New | The one Archive exception (Section 5) |
| IFTA trip legs / fuel purchases / exceptions | Version Doctrine §5 (arguably not applicable) | None | Not Applicable | None | Append-only; no mutation to version (Section 6) |
| `IFTAReportApproval` | Version Doctrine §5 | `status` field (`draft`/`sealed`) | Weak Match / Open Question | Investigate Further | Status may already satisfy doctrine's intent (Section 6) |
| Publisher drafts | Version Doctrine §5 | `portal/models/publisher.py` `PUBLISHER_STATUSES`, no version field | Missing | Build New | Out of Stage 8's originally scoped target — named here for completeness, not recommended for this stage |
| Manager/Monday/monthly reports, driver-facing documents, customer/broker artifacts | Version Doctrine §5 | None of these exist as concrete deliverables yet | Missing | Build New (later) | Explicitly out of scope — these objects don't exist yet to version |

---

## 8. Relationship to Other Stages

- **Stage 6 (Archive/IFTA Reconciliation, deferred build scope).** Section 5's finding means a future Archive build package should treat "add version retention" and "add version display" as one deliverable for `cin_lite/archive.py` and `portal/models/archive.py`, not two — this sharpens, rather than contradicts, Stage 6's own recommendation to build the retention pattern once and apply it to all three archives.
- **Stage 9 (Verification Workflow Retrofit).** Not directly coupled — Intelligence Verification classification (Verified/Partially Verified/Unverified/Rejected) is a different axis from version tracking (has this changed vs. is this trustworthy). Both can proceed independently once each is ready.
- **Stage 10 (Alert Governance Retrofit).** The Conflict Notice version-field gap found in Section 7 sits at the intersection of Stage 8 and Stage 5/10 — Conflict cards already got `card_level` (Stage 5) and will get governance controls (Stage 10); adding `version`/`last_change` to them is small and could reasonably ride with either a Stage 8 build or a Stage 10 build, whichever comes first.

---

## 9. Open Questions for Mike

1. **Library retention depth:** does "retained prior versions" for Library mean old content bodies must remain retrievable, or is a version counter + `last_change` label (Sandbox's lighter interpretation) sufficient? This changes how much a future Library version build actually has to do.
2. **Archive coupling:** given Section 5's finding that version display and version retention are the same build for two of the three archives, should a future build package merge Stage 6's deferred Archive Review Queue work and Stage 8's Archive version-display work into one combined launch package, rather than sequencing them as originally planned?
3. **`IFTAReportApproval`'s version field:** add a numeric `Ver: X` anyway for consistency with every other object type, or treat its existing `draft`/`sealed` status as already satisfying Version Doctrine's intent and skip it? Either is defensible; this is Mike's call, not an engineering default.
4. **Conflict Notice gap:** should the missing `version`/`last_change` fields on Conflict Notices (Section 7) be picked up as a small addition to a future Stage 8 build, or folded into Stage 10's Alert Governance work instead?

## 10. Recommendation and Next Steps

Stage 5 already proved the pattern works; this stage's job was to find out where it does and doesn't transfer cleanly, and it doesn't transfer uniformly. Library is a straightforward, arguably simpler application of the same pattern. Archive is not separable from Stage 6's already-deferred retention build for two of its three instances. Most of IFTA doesn't need version tracking at all, and its one mutable record raises a genuine judgment call rather than a mechanical retrofit.

**No implementation is authorized by this document.** A future Stage 8 build launch package — informed by Mike's answers to Section 9 — is the next artifact, not created here.

---

## Authority Closing

This is an architecture reconciliation document only.

No code was written. No file in the Dispatch repository was modified. No pull request was opened. No migration or database table was created. No Version Doctrine capability was built or implemented.

Mike Zachary remains final authority.

**Mike decides.**
