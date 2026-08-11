# DISPATCH_STAGE13_TESTING_HOLD_REVIEW_BUILD_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 13 Build Design — Testing and Hold Review
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code, config, or CI change made yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Approve Stage 13 build." Governed by `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`'s Stage 13 section ("Testing and Hold Review") and `DISPATCH_FINAL_BLUEPRINT_v1.md` §22 (Testing and Validation Plan).

---

## 0. What Kind Of "Build" This Is

Stage 13 is not a feature stage. Its cross-reference row says "No new code, full regression" — its job is to run everything built in Stages 4–12 together as one suite, confirm the existing coverage standard actually holds, and produce the most comprehensive Mike walkthrough in the whole plan. Consistent with that, this design proposes **no new product code, no new Manager/Portal/Spine behavior.** What it does propose, based on findings below, is two small, corrective changes to test *infrastructure* (a CI command and a config file) — not because Stage 13 wants to be a build stage, but because the investigation surfaced infrastructure that was silently not doing its job, and that is squarely what a Hold Review exists to catch.

## 1. Investigation Findings

### 1.1 The integration branch already exists — `stage12-manager-m7-policy-hook`

None of the five most recent stage branches were ever merged into `main` — every build simply branched forward from the previous one and stopped there (`stage7-security-foundation` → `stage12-manager-foundation` → `stage6-archive-review-queue` → `stage12-manager-archive-wiring` → `stage12-manager-m7-policy-hook`). Verified by ancestry check: `main`, and every one of `stage2` through `stage12-manager-archive-wiring`, is an ancestor of the current tip. **`stage12-manager-m7-policy-hook` is the full, real aggregate of Stages 2 through 12** — nothing is missing from it, nothing needs to be cherry-picked or reassembled. It is 64 files and ~8,941 lines ahead of `main`, none of it merged.

### 1.2 The full regression suite is clean: 2,489 tests, 0 failures

Re-run from a clean checkout of the aggregate tip. Matches the running total already recorded at the end of every prior build pass — no drift, no interaction effects between stages' test suites.

### 1.3 CI's coverage gate has a real gap: it has only ever measured `cin_lite`

`.coveragerc`'s `[run] source` lists both `cin_lite` and `dispatch` — but `.github/workflows/ci.yml` invokes pytest with `--cov=cin_lite` only, no `--cov=dispatch`, no `--cov=portal`. Confirmed empirically: running the exact CI command produces a coverage report containing only `cin_lite/*` files — `dispatch/` and `portal/` do not appear in the report at all, and the reported "96.77%" is `cin_lite`'s coverage alone, not the whole codebase's. This means **the 90% CI gate has never actually measured or enforced anything against `dispatch/` (10,129 lines) or `portal/` (5,500 lines)** — roughly three-quarters of the codebase built since Stage 4 — despite Stage 7's own launch package language ("Existing CI already enforces 90% coverage on `cin_lite` + `dispatch`") assuming otherwise. That assumption was wrong; it was never checked until this stage.

`portal` was never even listed in `.coveragerc`'s `source` — so this isn't only a CI command bug, it's also a config gap.

### 1.4 The real, measured coverage — once `dispatch` and `portal` are actually included

Ran the full suite with `--cov=cin_lite --cov=dispatch --cov=portal`. Result: **8,816 statements, 421 missed, 95.22% aggregate — clears the existing 90% bar even correctly measured.** Per-module, most files are well above 90% (many at 97–100%). Eleven modules fall below 90%:

| Module | Coverage | Note |
|---|---|---|
| `portal/app.py` | 69% | App factory / startup wiring — largely non-branching bootstrap code |
| `dispatch/acquisition.py` | 71% | |
| `portal/routes/security.py` | 76% | **Security-relevant** — exposes the Stage 7 security event log |
| `portal/auth_helpers.py` | 83% | **Security-relevant** — this is the `authority_required` decorator itself |
| `dispatch/manager/classify.py` | 81% | |
| `portal/helpers.py` | 81% | |
| `dispatch/spine/store.py` | 86% | |
| `dispatch/manager/priority.py` | 86% | |
| `dispatch/scoring.py` | 86% | |
| `dispatch/security/store.py` | 88% | **Security-relevant** — Stage 7's own event store |
| `dispatch/manager/stage_gate.py` | 89% | |

Three of these (`portal/routes/security.py`, `portal/auth_helpers.py`, `dispatch/security/store.py`) are directly part of the Security Foundation Stage 7 claimed as "approved & executed" — worth Mike's attention specifically because of what they gate, not just because of the number.

### 1.5 `DISPATCH_FINAL_BLUEPRINT_v1.md` §22's sixteen named test categories

Doctrine names sixteen specific test categories. Several (Fact grounding, Publisher no-fabrication, Intelligence verification, Load evaluation) target cognitive-layer behavior (Publisher/Intelligence output generation) that doctrine itself has repeatedly noted is not yet built to that depth — `portal/models/publisher.py` and `intelligence.py` exist and are well-covered (96–98%) but as data models, not as the fact-grounded generation pipeline §22 describes. Mapping which of the sixteen categories are fully exercised today, partially exercised, or not yet applicable given current build scope is proposed as part of this stage's walkthrough deliverable (§4 below) rather than resolved here — it is exactly the kind of comprehensive inventory Stage 13 exists to produce, not a decision this design document should pre-empt.

## 2. Proposed Scope

1. **Fix the CI coverage command** (`.github/workflows/ci.yml`) to measure `cin_lite`, `dispatch`, and `portal` together, matching what a "full regression" gate should have been checking all along.
2. **Fix `.coveragerc`** to add `portal` to `[run] source`, so the config and the CI invocation agree, and so a bare `pytest --cov` (no explicit `--cov=` flags) also measures the whole codebase correctly.
3. **Keep the aggregate 90% bar, not a per-module bar** — the aggregate is already met (95.22%), and picking winners/losers module-by-module isn't something this design proposes to decide unilaterally (see Open Question 1).
4. **Produce the §22 test-category inventory** described in §1.5, as part of the walkthrough report.
5. **No product code changes.** No new tests are written to close the eleven modules' individual gaps as part of this pass — that is Open Question 2, not a default.

## 3. Explicitly Not In Scope

- **Merging `stage12-manager-m7-policy-hook` (or any stage branch) into `main`.** This is a real, load-bearing question this investigation surfaced — nothing has ever been merged — but it is a repository-structure decision with its own blast radius (rewrites what "current" means for anyone looking at `main`), and the Migration Plan's own Stage 14 is a *decision*, not a merge action either. Raised as Open Question 3, not decided here.
- **Writing new tests to raise any of the eleven sub-90% modules.** Flagged, not silently fixed — see Open Question 2.
- Any new Manager, Portal, Spine, or Security behavior. None is proposed by this stage.
- A physical re-walk of `DEPLOY_VPS.md`'s blocker checklist — that is Stage 14's own open question, not this stage's.

## 4. Test Plan / Walkthrough Requirements

- Full suite re-run on the corrected CI command, confirming the 90% gate now actually evaluates against the real, full codebase (not just `cin_lite`), and still passes.
- A `git diff --stat main..stage12-manager-m7-policy-hook`-derived summary of everything Stage 13 is certifying, cited in the walkthrough report so "full regression" is traceable to an actual diff, not just a test count.
- The §22 test-category inventory (§1.5), delivered as a table: category → representative existing test file(s) → status (Exercised / Partially exercised / Not yet applicable at current build scope).
- No live dev-server walkthrough is proposed for this stage — there is no new user-facing behavior to click through. If Mike wants one anyway (e.g., a full click-through of every page built across Stages 4–12 as a final integration smoke test), that can be added; flagged as Open Question 4.

## 5. Open Questions For Mike

1. **Coverage bar: aggregate (as today, already met at 95.22%) or per-module minimum?** Recommended default: keep aggregate — it's the existing standard, it's met, and it doesn't require Mike to adjudicate eleven modules individually right now. If Mike wants a per-module floor, the three security-relevant modules (`portal/auth_helpers.py` 83%, `portal/routes/security.py` 76%, `dispatch/security/store.py` 88%) are the ones worth prioritizing first.
2. **Should new tests be written now to close the eleven modules' gaps, or logged as a known-and-accepted gap for a future pass?** Recommended default: log them (this design document itself, plus the walkthrough report) rather than open new test-writing scope inside a stage whose own charter says "no new code." A follow-on instruction ("close coverage gaps in X") can be issued separately if Mike wants it done now instead.
3. **Should Stage 13 merge the aggregate branch into `main`, or leave `main` as-is and treat `stage12-manager-m7-policy-hook` as the de facto current branch until Stage 14's promotion decision?** This has no clean default — it's a real structural choice with consequences either way, and no prior stage decided it. Flagged for an explicit answer, not defaulted.
4. **Does Mike want a live full-suite click-through walkthrough (every page, every stage's feature) in addition to the automated regression, or is the automated suite plus the walkthrough report sufficient for this Hold Review?** Recommended default: automated suite + report is sufficient — every individual feature already had its own live walkthrough at build time; Stage 13's value-add is aggregation and the coverage-gate fix, not re-walking already-walked features.

## 6. Effect If Approved

The CI gate starts actually measuring what it has claimed to measure since Stage 7. The full aggregate test suite (2,489 tests) is certified clean in one place, traceable to one branch and one diff against `main`. Stage 14 (Production-Intent Promotion Decision) has a real, documented Hold Review to point to — including, honestly, the branch-merge question it may need to account for, since this document does not resolve that for it.

---

*End of DISPATCH_STAGE13_TESTING_HOLD_REVIEW_BUILD_DESIGN_v1.*
