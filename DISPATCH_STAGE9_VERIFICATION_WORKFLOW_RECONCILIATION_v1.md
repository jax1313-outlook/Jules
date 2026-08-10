# DISPATCH_STAGE9_VERIFICATION_WORKFLOW_RECONCILIATION_v1.md

**Document Type:** Architecture Reconciliation — Stage 9 (Intelligence Verification Workflow)
**Program:** Dispatch
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Reconciliation Draft — analysis only, no implementation authorized
**Authority:** Mike Zachary remains final authority

---

## Authority Notice

This document is Stage 9 of the Migration Plan (`DISPATCH_INTEGRATED_BLUEPRINT_v1.md` §16), delivered in the same **Architecture Reconciliation Mode** Mike specified for Stages 6, 7, and 8: no production code, no Dispatch repository modification, no pull request, no migrations, no new database tables, no Stage 9 build launch package. Discovery, mapping, reuse, alignment — not a redesign of the Intelligence Verification Workflow, and not a build.

`INTELLIGENCE_VERIFICATION_WORKFLOW.md` §1 is explicit that this doctrine exists to enforce the No Fabrication Rule **using the existing Intelligence function, not by creating a new compliance agent.** That constraint governs this reconciliation's findings throughout — nothing below recommends a new agent, service, or cognitive role.

**Mike Zachary is final authority. AI decides nothing. Mike decides.**

---

## 1. Executive Summary

**What Stage 9 originally scoped.** Formalize Verified / Partially Verified / Unverified / Rejected classification for cognitively-derived candidates, and add an `origin` field to Library ingestion so Publisher-generated/Intelligence-nominated/Archive-nominated candidates route through the promotion workflow instead of the human-ingestion path `LIBRARY_INGESTION_RULE.md` establishes.

**What already exists.** Two genuinely strong, independent seeds for this doctrine already run in production, built for reasons unrelated to this stage:
1. **IFTA's `extraction_confidence` + suspect-entries threshold** (Phase 6b/7) — a real, working confidence score attached to vision-extracted data, with a threshold-based "suspect" flag.
2. **The nine `cin_lite/rules/*.py` deterministic modules** — pure regex/keyword extraction against source text, explicitly marked `deterministic: true` in every `RuleResult`, with zero LLM involvement.

**What's missing.** `portal/models/intelligence.py` — the object that should be the natural home for verification classification — has none. It is a plain CRUD store with no confidence field, no source-grounding field, no classification of any kind. `portal/models/library.py` has no `origin` field distinguishing a human-placed document from a cognitively-derived one, which is the specific, narrow gap that lets a future Publisher/Intelligence integration accidentally reuse Library's ungated human-ingestion path.

**The central nuance this reconciliation surfaces.** Verified/Partially Verified/Unverified/Rejected is not a label that belongs on everything — it belongs specifically at the boundary where cognitively-derived or externally-sourced data threatens to become Library truth or a Publisher factual claim without traceability. It does not apply to data a human directly entered (a dispatcher typing a rate, per the Library Ingestion Rule's own reasoning) and it does not apply, unmodified, to a deterministic rule module's raw match — a regex correctly finding the string "8(a)" in solicitation text is Verified as an *extraction claim* ("the text contains this"), which is a different, narrower claim than "this company is 8(a)-eligible" (a business judgment doctrine reserves for Mike). Conflating the two would let a correct text match silently become an unverified business claim — a subtle scope-creep risk worth naming explicitly.

---

## 2. Verification Workflow Requirements (Recap)

Per `INTELLIGENCE_VERIFICATION_WORKFLOW.md`: raw information flows Collection → Parsing → Intelligence Verification → Verified/Rejected → Library (if approved) → Publisher use (if verified/approved). Four classifications: **Verified** (source-supported, may proceed), **Partially Verified** (some support, needs explicit Mike approval for the specific use), **Unverified** (no support, may not enter Library or be used as fact), **Rejected** (unreliable/contradictory/stale, archivable as history only). Every significant claim must trace to a source record, approved Library record, Verification record, or Mike-approved exception — otherwise it's marked UNKNOWN/MISSING/NEEDS SOURCE.

---

## 3. Existing Verification-Adjacent Assets Assessment

### 3.1 The nine deterministic rule modules (`cin_lite/rules/*.py`)

Each outputs a `RuleResult` (`module, version, flags, findings, summary, score, deterministic`) via pure text matching — no LLM, no network, confirmed deterministic by both code inspection and the modules' own docstrings. **These are Verified-by-construction for the narrow claim they actually make** ("this text contains this pattern"), not for any downstream business conclusion drawn from that pattern. A future verification-classification layer should record the extraction as Verified while leaving the business interpretation of that extraction unclassified — that interpretation is Intelligence's cognitive job (`INTELLIGENCE_ANALYST.md` §7.2), not something a rule module's "Verified" tag should imply on its own.

### 3.2 The five Claude-backed cognitive agents (`cin_lite/agents/*.py`)

`extractor`, `summarizer`, `router`, `proposal_writer`, `receipt_vision` — all recommendation/interpretation outputs, never presented as factual claims in their own code (`router.py`'s own docstring: "This is a RECOMMENDATION — the human still makes the final call"). These map cleanly to `INTELLIGENCE_VERIFICATION_WORKFLOW.md` §4's Publisher Use Rule: usable as recommendations, never presentable as verified fact. No gap here — the code's existing behavior already matches doctrine's requirement without needing a classification field bolted onto agent output, because these outputs were never claims of fact to begin with.

### 3.3 IFTA's `extraction_confidence` + suspect-entries (Phase 6b/7)

The strongest working seed for **Partially Verified**. A real float, attached per-record, threshold-compared (`DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD = 0.75`, an admitted uncalibrated placeholder per the Phase 7 walkthrough report). **Critical difference from what Stage 9 needs:** suspect-entries is deliberately advisory-only — it never gates anything, by explicit design (Phase 7's resolved open question: suspect count does not affect readiness rollup). Real Verification classification, per doctrine, must actually **block** Unverified/Rejected facts from Library/Publisher use. Reusing the confidence-float *pattern* is sound; reusing its *non-blocking enforcement posture* is not — Stage 9's classification needs teeth that suspect-entries deliberately doesn't have.

### 3.4 `portal/models/intelligence.py`

`INTEL_TYPES = [location, broker, customer, route, position, market]`, `create_record()`/`update_record()`, no confidence field, no classification field, no source reference field of any kind. This is the object doctrine describes as Intelligence's storage layer, and it currently implements none of the verification doctrine.

### 3.5 `portal/models/library.py`'s missing `origin` field

Per the prior reconciliation (Reconciliation Matrix row 8, corrected by `LIBRARY_INGESTION_RULE.md`): `add_record()` correctly auto-approves human-placed documents, but has no field distinguishing that from a hypothetical future Publisher/Intelligence-sourced candidate. This is Stage 9's most concrete, narrowly-scoped finding (Jules item #6) — everything else in this section is about building classification; this is about making sure classification, once built, can't be bypassed by routing through the wrong ingestion path.

---

## 4. Source Grounding Assessment

`INTELLIGENCE_VERIFICATION_WORKFLOW.md` §5 requires every significant claim to point to a source record, approved Library record, Verification record, or Mike-approved exception. **Current state: no structured source-reference field exists anywhere in the Intelligence/Library/Publisher storage layer.** The closest analogues:

- IFTA's evidence linkage (`leg_ids`/`purchase_ids` provenance tracking in `_ifta_aggregate()`, Phase 5) — a real, working "this computed line traces to these specific source records" pattern, but scoped narrowly to IFTA's own tax computation, not generalized.
- `cin_lite/archive.py`'s `source_refs` concept doesn't formally exist either — contracts are identified by `contract_id`/`solicitation_number`, which is traceability by ID, not a structured source-reference object.

**Finding:** IFTA's `leg_ids`/`purchase_ids` provenance-tracking pattern (an array of source record IDs attached to a derived/computed value) is the one existing, proven implementation of "traceable to source" in this codebase, and is the strongest reusable template for what a general `source_refs` field should look like — closer to Stage 4's Spine schemas (`source_refs` already exists as a field name across `WorkItem`, `Event`, `PortalCard`, etc., per the Spine Specification) than to anything Intelligence-specific. This is a case where Stage 4's already-built Spine schema and Stage 9's verification need converge — worth naming as a direct dependency, not a coincidence.

---

## 5. Classification Mapping

| Classification | Doctrine Meaning | Closest Existing Analogue | Gap |
|---|---|---|---|
| **Verified** | Source-supported, may proceed to Library/Publisher use | The nine deterministic rule modules' raw extraction claims (Section 3.1) | No field records this classification explicitly today — it's implicit in "deterministic: true," not a stated verification status |
| **Partially Verified** | Some support, needs Mike's explicit approval for the specific use | IFTA `extraction_confidence` below threshold (Section 3.3) | Exists as a *signal*, not as an *enforced classification* — nothing currently requires Mike's approval before a low-confidence value is used |
| **Unverified** | No source support, may not enter Library or be used as fact | Nothing currently — no code path checks for or blocks this | Full gap |
| **Rejected** | Unreliable/contradictory/stale/wrong, archivable as history only | `cin_lite`'s `reject` control action (a human decision, not an automated classification) | Different mechanism — a human explicitly rejecting a contract via the email control gate is not the same as a system classifying a *fact* as Rejected |

---

## 6. Full Capability Table

| Verification Capability | Doctrine Source | Current Asset | Current Fit | Reuse / Modify / Build New | Notes |
|---|---|---|---|---|---|
| Core flow (Collection → Parsing → Verification → Library/Publisher) | Workflow §2 | `cin_lite` pipeline (Collection/Parsing halves only) | Partial Match | Modify | Verification step itself does not exist between parsing and storage |
| Verified classification | Workflow §3.1 | Deterministic rule modules (implicit) | Partial Match | Modify | Signal exists (`deterministic: true`); explicit classification field does not |
| Partially Verified classification | Workflow §3.2 | `extraction_confidence` + suspect threshold | Partial Match | Modify | Confidence signal exists; enforcement (Mike approval required for use) does not |
| Unverified classification | Workflow §3.3 | None | Missing | Build New | — |
| Rejected classification | Workflow §3.4 | `reject` control action (different mechanism — human decision, not fact classification) | Weak Match | Build New | Do not conflate contract-level human rejection with fact-level system classification |
| Source grounding / `source_refs` | Workflow §5 | IFTA's `leg_ids`/`purchase_ids` provenance tracking; Spine's `source_refs` field (Stage 4) | Partial Match | Reuse (Spine's field shape) + Modify (extend to Intelligence) | Stage 4 already defined the field shape doctrine needs |
| Publisher Use Rule (never present Unverified/Rejected as truth) | Workflow §4 | Cognitive agents already behave this way in practice (Section 3.2) | Strong Match (behaviorally) / Missing (structurally) | Modify | Correct behavior exists without a formal gate enforcing it — currently correct by convention, not by construction |
| Library promotion gate for non-human origin | Workflow §7; `LIBRARY_INGESTION_RULE.md` | None — no `origin` field | Missing | Build New | Jules item #6, most concrete finding in this document |
| Portal reliability display (Verified/Partially Verified/Unverified/Rejected/Unknown shown on cards) | Workflow §9 | None | Missing | Build New | Depends on the classification field existing first |
| No new compliance agent | Workflow §1 (constraint, not a capability) | N/A | N/A | N/A | Confirmed: nothing in this reconciliation recommends a new agent |

---

## 7. Relationship to Other Stages

- **Stage 4 (Spine schemas).** `source_refs` already exists as a field across every Spine schema. A future Verification build should extend that existing field shape into Intelligence/Library records rather than inventing a new source-reference format — this is a direct reuse opportunity, not a coincidental naming overlap.
- **Stage 6 (Archive/IFTA, deferred).** Rejected/stale facts "may be archived as history if useful" (Workflow §6) — this is a storage-destination decision for a future build, not a new requirement on Archive's own structure.
- **Stage 7 (Security, deferred).** Real enforcement of "Mike's explicit approval" for Partially Verified use requires the same identity/approval-event infrastructure Stage 7 reconciled — this is why the original Migration Plan sequenced Stage 9 after Stage 7, and this reconciliation confirms that sequencing is still correct, not incidental.
- **Stage 8 (Version Doctrine, delivered).** No direct coupling found — a fact's verification classification and its version number are independent axes, consistent with Stage 8's own finding that different doctrine concerns shouldn't be assumed to travel together without checking.

---

## 8. What Already Exists

Deterministic rule modules' implicit Verified-by-construction extraction claims; IFTA's confidence-float pattern; IFTA's `leg_ids`/`purchase_ids` provenance-tracking pattern; the cognitive agents' already-correct "recommendation, never fact" behavior; Stage 4's `source_refs` field shape, ready to be extended.

## 9. What Is Missing

An explicit classification field anywhere in the codebase; enforcement of any classification (nothing currently blocks Unverified/Rejected data from being used); the Library `origin` field; a Portal reliability display; a formal Unverified/Rejected pathway (only "human explicitly rejects a contract" exists, which is a different concept).

## 10. What Can Be Reused

IFTA's confidence-float-plus-threshold pattern (for deriving Verified/Partially Verified, not for its non-blocking enforcement posture — that part must change). IFTA's provenance-tracking (`leg_ids`/`purchase_ids`) as the template for general source grounding. Stage 4's `source_refs` field shape. The rule modules' `deterministic: true` field as the seed for automatic Verified-by-construction classification of extraction claims specifically.

## 11. What Should Remain Unchanged

The rule modules themselves (deterministic, correct, no LLM — nothing here found a reason to touch them). The cognitive agents' recommendation-only behavior. IFTA's suspect-entries panel's deliberately non-blocking design for its own stated purpose (informational triage) — Stage 9 needs a *separate*, blocking classification mechanism for Library/Publisher use, not a retrofit of suspect-entries into something it was explicitly designed not to be.

---

## 12. Open Questions for Mike

1. Should Verified-by-construction status for the nine rule modules' extraction claims be automatic (any deterministic rule match is Verified by default) or still require an explicit classification step, even for deterministic output? Automatic is simpler; explicit is more conservative and leaves no implicit trust rules embedded in code.
2. Should the existing `DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD = 0.75` (an admitted, uncalibrated placeholder) be reused as the Verified/Partially-Verified boundary for a future build, or does Mike want it recalibrated first, given it would now gate real Library/Publisher use rather than only an informational panel?
3. For source grounding, should Intelligence records reuse the Spine's `source_refs` field shape directly (Stage 4), or does Intelligence need something IFTA's `leg_ids`/`purchase_ids`-style record-ID-array pattern captures that a generic `source_refs` list does not?

## 13. Recommendation and Next Steps

This reconciliation confirms the direction was already right — Verification doctrine can be built entirely from existing patterns (confidence scoring, deterministic extraction, provenance tracking) without a new agent, exactly as the doctrine itself requires. The real work is enforcement, not invention: today's signals (confidence, `deterministic: true`, provenance arrays) exist but don't block anything. A future build closes that gap; this document does not.

**No implementation is authorized by this document.** A future Stage 9 build launch package — sequenced after Stage 7 (identity, for real approval enforcement) — is the next artifact, not created here.

---

## Authority Closing

This is an architecture reconciliation document only.

No code was written. No file in the Dispatch repository was modified. No pull request was opened. No migration or database table was created. No Intelligence Verification capability was built or implemented. No new agent is recommended anywhere in this document.

Mike Zachary remains final authority.

**Mike decides.**
