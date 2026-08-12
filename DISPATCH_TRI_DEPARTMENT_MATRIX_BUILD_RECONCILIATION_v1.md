# DISPATCH_TRI_DEPARTMENT_MATRIX_BUILD_RECONCILIATION_v1

Program: Dispatch
Status: **Reconciliation complete. Reference document — reconciles what exists, does not authorize
or change anything.** No scoping decision made by this document; the Operational Intelligence
scoping request that surfaced this is on hold pending Mike's ruling below.
Origin: "start Operational Intelligence scoping" surfaced that a separate, already-completed
"Tri-Department Matrix Build" (Intelligence/Library/Publisher, three standalone repos) exists and
was never cross-referenced against this session's own Intelligence/Library/Publisher Completeness
Reviews or the tri-department wiring (Stage 1/Stage 2) already merged into `jax1313-outlook/
Dispatch`. Mike directed: reconcile first, same treatment as `Hold`/`Test-Grounds`, before deciding
how to scope anything. Built from three parallel investigations run this session — read the
originals for full detail; this document synthesizes for a decision, not a duplicate.

---

## 1. What Actually Exists

Three GitHub repos — `jax1313-outlook/l2-intelligence-agent.`, `jax1313-outlook/library`,
`jax1313-outlook/publisher` — each independently implement a real, tested Python package
(`dispatch_intel`, `dispatch_library`, `dispatch_publisher`) against
`DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`'s exact field-level schemas. This is genuinely
substantial, verified work, not a stub:

| Repo | Object model | Service layer | Tests (actually re-run this session) | Storage |
|---|---|---|---|---|
| `l2-intelligence-agent.` | 6 objects: `IntelligenceFinding`, `OperationalConsideration`, `SpecialRequirement`, `PublisherRequirement`, `LibraryCandidate`, `ManagerDecisionSupportNote` | `service.py`: `create_finding`, `build_finding_from_analysis`, `route_to_publisher`, `route_to_library`, `create_decision_support_note` | 33 passing (confirmed via own `MERGE_READINESS_REPORT.md`; the Claude-3 aggregator doc's "32" is stale by one CLI-wiring test) | In-memory `IntelligenceStore` only |
| `library` | 3 objects: `LibraryObject`, `LibraryCandidate`, `PublisherRecipe`; 15-value closed collection taxonomy | `LibraryService`: `current`, `list_current`, `resolve_packet`, `register_recipe`, `ingest_human_document`, `submit_candidate`, `review_candidate`, `pending_candidates` | **24/24 re-run and confirmed passing this session** | In-memory `ObjectRegistry`/`CandidateQueue`/`RecipeRegistry` only |
| `publisher` | 9 objects (all named in `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` §5): `PublisherRequest`, `Workspace`, `ReadinessPacket`, `PartsInventory`, `MissingItemNotice`, `DraftReviewPackage`, `ArchiveHandoffPackage`, `VisibilityPackage`, `PODEvidenceBundle` | 11 functions covering the full pipeline: `create_request → pull_libraries → create_readiness_packet → create_inventory → create_missing_notice → create_review_package → approve_review_package → create_archive_handoff`, plus `create_visibility_package`/`create_pod_bundle` | **19/19 re-run and confirmed passing this session** | Fully stateless — every function returns objects, caller holds them; no storage at all |

Plus a genuine **live cross-repo integration walkthrough**
(`integration/cross_repo_walkthrough.py`, Claude-3 repo, already read in full this session): a
real run — not simulated — proving Intelligence's `LibraryCandidate` and Library's
`LibraryCandidate` are field-identical at runtime with zero translation code, that a candidate
stays `PENDING_REVIEW` until a real `review_candidate(approve=True, reviewed_by="Mike Zachary")`
call, that Publisher's self-approval block and no-fabrication behavior hold when actually wired
to a live `LibraryService` (via a `LiveLibraryAdapter`, not just a stub), and that Archive handoff
is genuinely blocked pre-approval.

**Total: 76 tests (33+24+19) plus one passing live integration walkthrough, all independently
re-verified this session, not taken on the repos' own word.**

## 2. Status Per The Repos' Own Documentation

All three: **"Integration-ready candidate. Not merged into Dispatch. Not deployed. Not
production-promoted."** Each cites a promotion flow via `07_DISPATCH_REPO_PLACEMENT_PLAN.md` —
which does not exist as a committed file in any of the three repos, only as a reference. Its
actual content was located in this session's own upload folder (not durably committed anywhere):

```
Intell / Library / Publisher repos
  -> Integration-ready candidate
  -> Claude Code review
  -> Hold / Test-Grounds
  -> Mike approval
  -> Dispatch merge candidate
  -> Dispatch main
  -> Separate deployment decision
```

**This build sits at "integration-ready candidate" — the step before Claude Code review, which
this document now constitutes.** Every one of its own reports ends with "Mike decides" and
authorizes no merge, deployment, or promotion.

## 3. Relationship to `Hold` / "Dispatch Matrix Group 1" — Confirmed Separate, Parallel Initiative

This is the most important finding for framing any decision. **These are not the same effort,
and Hold's own planning explicitly argued against building this now:**

- `Hold`'s own pre-coding audit (`DISPATCH_BUILD_MATRIX_AUDIT_v1.md`, dated Aug 3-4) explicitly
  excluded Intelligence and Publisher from "Matrix Group 1," in these words: *"Five or more lanes
  (adding Publisher or Intelligence) is past the line."* And: *"Intelligence (needs deep-source
  inspection design; needs the decision queue to exist; highest vagueness = highest drift risk if
  built early)... stay in the waiting room behind their named tripwires."*
- The Tri-Department Matrix Build proceeded anyway, about **one week later** (integration-ready
  deliverables dated Aug 11), building exactly the two departments Hold's audit had flagged as
  highest-risk to build early.
- Zero cross-references exist in either direction: Hold's `contracts/`/`library_seed/`/`docs/`
  contain no trace of `IntelligenceFinding`/`LibraryCandidate`/`PublisherRequirement` or any of
  the three repos' class names. The three matrix-build repos mention "Hold/Test-Grounds" only as
  an abstract future promotion step, never as a reference to Group 1's actual four lanes.
  Confirmed via full-text search across all repos.
- **Never staged.** No evidence this build ever passed through `Hold` or `Test-Grounds` at any
  point — both remain exactly as this session's earlier investigation found them (Hold: `.gitkeep`
  placeholders only; Test-Grounds: doctrine files only, no code).

**This is not a violation of anything — it's simply a second, independent track that ran in
parallel to Hold's more cautious, deferred approach, and never merged with it.** Worth naming
plainly rather than leaving implicit.

## 4. A Doctrine Variant, Not The Primary Constitution

`l2-intelligence-agent.`'s `01_DISPATCH_CONSTITUTION.md` — the doctrine this build was built
against — is **not byte-identical** to `dispatch-old/CONSTITUTION.md`, the primary-source
Constitution this whole session has otherwise treated as supreme law (per its own Article 0).
Different checksum, roughly half the length, flat numbered sections instead of Articles. Two
substantive differences, not just formatting:

- **Amendment rule differs.** Primary: *"This Constitution may change only by deliberate human
  approval"* (amendment permitted, gated). Variant: *"No amendments. Rewrite and replace the
  governing file when doctrine changes"* (amendment forbidden outright, replacement only).
- **An extra department not in the primary Constitution's Article III table**: "Refinement
  Analyst" — appears in the variant, absent from the primary Constitution's nine-department list.

In substance, the core doctrine this build actually followed — Human Final Authority, AI Decides
Nothing, No Fabrication, no self-approval, Library/Archive/Publisher role boundaries — matches the
primary Constitution's principles closely, and the build's own Hard Rule verification (Section 5
of each MERGE_READINESS_REPORT.md) demonstrates real compliance with those principles in code.
**But it was built against a variant document, not the primary source**, which matters given
Article 0's own supremacy claim. Flagged for the record, not treated as invalidating the work —
this is a governance-provenance note, not a code defect.

## 5. Compatibility With `jax1313-outlook/Dispatch`'s Real Code — Not A Drop-In

This is the practical crux for any scoping decision. Dispatch's real, live, merged-to-`main`
models (`portal/models/intelligence.py`, `library.py`, `publisher.py`) and the candidate build are
**structurally incompatible, not just incomplete relative to each other**:

| | Dispatch's real code (live, merged) | Candidate build |
|---|---|---|
| Storage | Flat JSON files (`portal/data/*.json`), same pattern as `conflicts.json`/`sandbox.json` | In-memory only, no persistence anywhere — all three repos' own `KNOWN_GAPS.md` name this as their top architectural gap |
| Library shape | `SECTIONS` = 6 open strings; record has `id, section, name, content, metadata, status, submitted_by, reviewed_by` | `collection` = 15-value closed taxonomy enum; `LibraryObject`/`LibraryCandidate` have `object_code, proposed_title, proposed_body_or_reference`, versioned with automatic supersession |
| Publisher shape | Flat action queue: `ACTION_TYPES`, `PUBLISHER_STATUSES`, one `create_action()`/`update_action_status()` pair | 9-object pipeline (Request→Workspace→ReadinessPacket→PartsInventory→MissingItemNotice→DraftReviewPackage→ArchiveHandoffPackage/VisibilityPackage/PODEvidenceBundle), 11 service functions |
| IDs | Human-readable, prefixed (`LIB-BRO-0001`, `PUB-0001`) | Opaque `uuid.uuid4()` strings throughout |
| Already wired to | This session's own Stage 1 (Intelligence→Library promotion) and Stage 2 (GovCon proposal bridge), both merged, both built directly against the shapes in the left column | Nothing in Dispatch — never integrated |

**The practical consequence, stated plainly**: adopting the candidate build's object model would
not be an additive integration — it would mean **replacing** Dispatch's real, live
`library.py`/`publisher.py` shapes, which this session's own Stage 1/Stage 2 work is built
directly on top of. That wiring (already merged, already verified via real HTTP in Track D) would
need to be reconciled or rebuilt against the new shapes, not simply left in place alongside them.
This is a materially bigger decision than "add the missing Intelligence department" — it's closer
to a foundational object-model replacement across three departments at once.

## 6. What The Candidate Build Gets Right That Dispatch's Real Code Doesn't

Worth stating plainly, since it's the whole reason this is worth taking seriously rather than
setting aside as reference-only:

- All six Intelligence contract concepts exist and are tested — Dispatch's real Intelligence has
  zero, confirmed by this session's own Completeness Review.
- Library's candidate/version/supersession model is real and enforced in code (`ObjectRegistry`
  guarantees exactly one `CURRENT` version per object, automatically), not the thin flag Dispatch's
  real Library has.
- Publisher's full 9-object pipeline, including a genuine `MissingItemNotice`/`ReadinessPacket`
  distinction Dispatch's real Publisher only approximates with plain string lists.
- Structural (AST-scanned, not just tested) proof Publisher can never send anything externally —
  stronger than anything in Dispatch's real code.
- A live-verified cross-repo contract, not just three independently-plausible designs.

## 7. Decision Needed From Mike

This document reconciles; it does not decide. Three real options, each with a genuinely different
cost:

1. **Treat as reference material only, same as `Hold`** — informs future design, doesn't change
   what's live. Lowest risk, keeps Stage 1/Stage 2's existing wiring untouched, leaves Dispatch's
   real Intelligence gap exactly where the Completeness Review found it.
2. **Scope a genuine integration/replacement** — a real, large mission: reconciling three object
   models, adding persistence, rewiring Stage 1/Stage 2 against the new shapes, and only then
   closing the actual Intelligence gap. Gets the most complete result, costs the most, touches
   already-merged work.
3. **Scope Operational Intelligence narrowly against Dispatch's real code, as originally
   framed before this discovery** — smaller, faster, consistent with Stage 1/Stage 2's own
   "narrow first slice" precedent, but leaves this well-built candidate work unused and requires
   inventing a smaller Intelligence Finding shape from scratch inside Dispatch, duplicating some of
   what the candidate build already solved.

No scoping document will be written until Mike picks a direction here.

Mike decides.
