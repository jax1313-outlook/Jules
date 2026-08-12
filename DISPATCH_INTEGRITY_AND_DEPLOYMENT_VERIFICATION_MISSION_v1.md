# DISPATCH_INTEGRITY_AND_DEPLOYMENT_VERIFICATION_MISSION_v1

Program: Dispatch
Status: **All six tracks (A-F) closed.** Findings recorded per track; no code changes made under
this mission except where a track's own scope explicitly named one (Track F made none).
Origin: Direct request ("Scope this as a formal review mission"), following the `dispatch-old`
code-lineage discovery and the confirmed finding that the Portal has no authentication. Framed
by Mike as establishing "a new starting point from where I am now" before any further deployment
work.
Rule: No code changes authorized by this document. No track begins without its own separate
go-ahead, matching every prior stage this session.

---

## 1. What This Mission Is

Before any further deployment work, verify — with evidence, not assumption — that what has been
built actually operates end to end, that its real relationship to the live VPS is understood, and
that its security and doctrine posture is known rather than inferred from paraphrase. Six tracks,
split by who can act on them.

## 2. Tracks Requiring Mike (server/live access this session doesn't have)

### Track A — Live Deployment Identity Check — **CLOSED**
**Purpose**: settle definitively which codebase and commit is actually running on `l1truck.com`
right now — `portal.app:create_app` (the real Flask app) or `cin_lite.portal` (the old dashboard),
and which version.
**Action**: on the VPS, `systemctl status portal.service` and `cat /etc/systemd/system/
portal.service` — the `ExecStart` and `WorkingDirectory` lines answer this in one look. If it's a
git checkout, `git -C <dir> log -1` pins the exact commit.
**Produces**: one factual line — entry point, directory, commit/version.

**Finding, verified live on the VPS by Mike:**
- The actual systemd unit is `l2cos-portal.service` (not `portal.service`, the name assumed from
  `dispatch-old`'s deployment scripts — that assumption was wrong, and the mismatch itself was
  informative).
- `ExecStart=/opt/cin-hybrid/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8080 ...` — gunicorn,
  a real WSGI server. `dispatch-old`'s `cin_lite.portal`/`dashboard.py` is built on Python's raw
  `http.server.ThreadingHTTPServer`, not WSGI-compatible — gunicorn could not serve it. **This is
  the real `jax1313-outlook/Dispatch` Flask app (`portal.app:create_app`), not the old dashboard.**
- `WorkingDirectory=/opt/cin-hybrid` is a genuine git checkout of `jax1313-outlook/Dispatch`
  (`origin/main` confirmed via `git -C /opt/cin-hybrid log -1`).
- **Commit: `a7532529` — "Add Library, Archive, Intelligence models and templates (#4)," dated
  July 31, 2026.** The checkout shows `HEAD -> main, origin/main, origin/HEAD` with no
  divergence — not because it's current, but because nothing has fetched since July 31, so its
  own idea of `origin/main` is exactly as stale as its `HEAD`.

**Conclusion: the live site is ~12 days stale, sitting at PR #4 in the repo's history.** It
predates "IFTA Phase 7" and whatever else landed natively on `main` since July 31, and it
predates everything built this session — Stage 1, Stage 2, the Approval Chain Safety Gate, the
Manager Preservation Decision, the presentation-layer consolidation panel, and PRs #82/#83
merged today. None of that is reaching `l1truck.com`. Redeploying (`git pull` + service restart
on the VPS) is a separate, not-yet-authorized action.

### Track B — Live Data Reality Check — **CLOSED**
**Purpose**: confirm what's actually live in the deployed instance versus static/seed content.
Mike already confirmed the live instance doesn't scan SAM.gov live the way the local L1-COS
prototype did — this track pins down the rest: which subsystems (freight/dispatch entry,
Publisher queue, Library, Archive) are live-fed versus placeholder data in that specific
deployment.
**Produces**: a clear live-vs-static list for the deployed instance specifically.

**Finding, verified live on the VPS by Mike** (commands tailored against the exact code at
commit `a753252`, checked first — `portal/models/__init__.py::get_data_dir()`,
`portal/helpers.py::load_and_process_sam()`, `cin_lite/acquisition.py`'s
`CIN_LITE_SAM_API_KEY` fallback):

- **SAM.gov: not live.** `grep -c "CIN_LITE_SAM_API_KEY" /opt/cin-hybrid/.env` → `0`. SAM cards
  shown are `cin_lite`'s bundled `sample_data/`, not real acquisitions.
- **Only two data files exist on disk**, in `/opt/cin-hybrid/portal/data/`: `conflicts.json` and
  `sandbox.json`. `archive.json`, `intelligence.json`, `library.json`, `publisher_queue.json` are
  entirely absent — not empty, never created. Archive, Intelligence, Library, and Publisher have
  never had a single record written on this deployment. Matches the screenshot's "0 Publisher
  Queue / 0 Archived Records / 0 Intelligence Records" exactly, confirmed at the file-existence
  level, not just the displayed count.
- **`sandbox.json`: real but frozen.** 4 entries, matching the snapshot Mike uploaded earlier
  exactly (same 2 SAM opportunities, 2 Dispatch loads). Last modified Aug 9 — no new cards since.
- **`conflicts.json`: 95 records, up from 5 in the earlier-uploaded snapshot — a likely bug, not
  organic growth.** Sandbox stayed flat at 4 entries the entire time; conflict count grew ~19x
  against that same tiny set. The original 5 all traced to one load
  (`SBX-DISPATCH-LOAD-20260729-002`, the Flatbed equipment mismatch). Consistent with a
  non-idempotent conflict-check re-firing and re-creating duplicate notices on repeated runs
  rather than skipping when an equivalent one is already open — flagged as a real anomaly worth
  checking directly, not confirmed as root cause without reading the actual 95 records.

**Conclusion**: the live deployment has genuine, if narrow, real usage (Sandbox cards, Conflict
Notices) — it is not purely static placeholder data — but four of seven departments have never
been touched at all, SAM.gov is confirmed not live, and the Conflict Notices count shows signs
of a duplication bug rather than 95 distinct real issues. No fix applied — investigation only.

## 3. Tracks Claude Can Execute Directly (source-code and local-run based)

### Track C — Code Lineage Reconciliation — **CLOSED**
**Purpose**: one authoritative document tracing L1-COS → Hybrid v1 → `dispatch-old`/`cin-hybrid`
(CLAUDE.md's Phases 1-2) → `jax1313-outlook/Dispatch` (Phase 3, now merged to `main` via PR #82)
— reconciling every name this program has used (L1-COS, L2-COS, Hybrid v1, cin-hybrid, Dispatch)
into one map, so future sessions don't have to reconstruct this from scattered uploads again.
**Produces**: `DISPATCH_CODE_LINEAGE_MAP_v1.md` — done. Timeline, naming glossary, authority
hierarchy, and a cross-reference to Tracks A/B's live-verification findings, all cited to
evidence gathered and verified this session.

### Track D — End-to-End Functional Verification — **CLOSED**
**Purpose**: this session's tri-department work (Stage 1, Stage 2, the Approval Chain Safety
Gate, the presentation-layer panel) has only ever been verified by `pytest` — never by actually
running the Flask app and clicking through it as a user would. Tests prove the code is correct;
they don't prove the feature works end to end. Close that gap.
**Scope**: run `jax1313-outlook/Dispatch`'s real Flask app locally (`main`, post-merge) and walk
real flows: create a broker-type Intelligence record → promote → approve → confirm a Publisher
action actually appears in the rendered `/publisher` page; create a `GovCon Proposal Draft
Required` action → generate a draft → confirm the approval gate genuinely blocks an unapproved
`APPROVED` transition through the real UI, not just via a direct API call; confirm the "Attention
Needed Across Departments" panel actually renders real cross-department items on `/home`.
**Produces**: a report of what was actually run and observed (real HTTP responses / rendered
HTML), distinct from and in addition to the existing test suite's green result.

**What was actually done**: `main` (commit `502adf2`, post PR #82/#83) run locally as a real
Flask dev server on `127.0.0.1:5099`, in an isolated scratch data directory. Every step below is
a real `curl` HTTP request against that live server, not a `pytest` assertion.

**Finding 1 — a real gap, found immediately**: `intelligence.promote_to_candidate()` has **zero
callers anywhere in `portal/routes/`**. There is no HTTP route for it. A human using the real,
running app has no way to trigger Stage 1's Intelligence→Library promotion at all — it's only
reachable via direct Python call, which is exactly what the test suite does and exactly what a
real user cannot do. Confirmed via `grep`, then worked around for the rest of this walkthrough
by invoking it directly against the same live data store (clearly separated from the real HTTP
steps below).

**Stage 1 chain — fully confirmed working, end to end, via real HTTP:**
1. `POST /api/intelligence/add` → real `INT-BRO-0001` record created; confirmed rendered on the
   real `/intelligence` page.
2. `promote_to_candidate()` (direct call — see Finding 1) → `LIB-BRO-0001`, `pending_review`.
3. Checked `/library`'s real rendered HTML for a review/approve control — **confirms** the
   earlier Library Completeness Review finding: none exists. The only "review"/"approve" text on
   the page is unrelated static prose and the *Publisher* page's shared JS (present because
   `base.html` is included everywhere) — not a Library-specific control.
4. `POST /api/library/review` (the only path, since no UI one exists) → `LIB-BRO-0001` approved.
5. Confirmed `PUB-0001` ("Broker Packet Required") now genuinely appears on the real, rendered
   `/publisher` page with the correct trigger reason.

**Stage 2 chain — fully confirmed working, end to end, via real HTTP, including real archived
output:**
1. Staged a real `cin_lite` pending decision using the actual `acquisition`/`processing`
   pipeline (not test fixtures) against `cin_lite/sample_data/sample_contract.json`.
2. `POST /api/publisher/create` with `contract_id` → `PUB-0002` created, sandbox lookup correctly
   skipped (`GOVCON-CIN-TRACKD-VERIFY` marker).
3. `POST /api/publisher/update` (`PENDING→DRAFT`) → real `proposal_reference_id`
   (`PROP-20260812-66DF1F97`) returned. **Verified on disk**, not just in the response: the full
   `cin_lite` archive tree was actually written — `Raw/`, `Processed/`, `Intelligence/`,
   `Summaries/`, `Routing/`, `Proposals/` (with `.sha256` hash sidecars), and an `Outbox/` kickoff
   email. Read the actual drafted `.md` outline — real generated content, not a stub.
4. `POST /api/publisher/update` (`APPROVED`, no `approved_by`) → **real 400**, correct error,
   gate genuinely blocks it through the actual HTTP path, not just in a unit test.
5. `POST /api/publisher/update` (`APPROVED`, `approved_by: "Mike Zachary"`) → succeeds.

**Attention Needed panel — confirmed working correctly, including correct exclusion logic:**
`/home`'s real rendered HTML showed exactly one item — `PUB-0001` (still `PENDING`), with its
real trigger note. `PUB-0002` (now `APPROVED`) was correctly **excluded** — the panel only shows
items still awaiting action. Not just "renders something," genuinely correct filtering behavior
observed live.

**Conclusion**: every piece of this session's tri-department work that has an HTTP entry point
is confirmed genuinely functional end to end, not just passing isolated tests — with one real,
concrete gap found: Stage 1's promotion step has no UI/API path at all. No fix applied here;
Track D is verification only.

### Track E — Security Posture Review — **CLOSED**
**Purpose**: consolidate the two concrete findings already surfaced this session — no
authentication anywhere in the Portal, and a live SAM.gov API key exposed in an uploaded `.env`
— into one findings record, plus a fresh scan of both `jax1313-outlook/Dispatch` and `dispatch-old`
for any other exposed secrets or credentials in source control.
**Produces**: a findings list with severity and recommended next action per item. Rotating the
exposed key and deciding on an authentication approach are both Mike's calls, not implemented
here.

**Findings, verified this pass (broad regex scan of current tree + full git history in both
repos, plus targeted reads):**

| # | Finding | Severity | Evidence | Recommended action |
|---|---|---|---|---|
| 1 | Portal has no authentication of any kind | High | Established earlier this session — no `/login` route, no `flask_login`, no `before_request` gate, no reverse-proxy `auth_basic` in any deployment script found | Mike's call — decide an approach, then scope as its own mission |
| 2 | Live SAM.gov API key exposed in chat | High | Uploaded twice in plaintext this session (`.env`/`.env.example`, and again pasted directly). **Not found committed to any git history in either repo** — the exposure channel was direct upload to this conversation, not GitHub | Rotate at SAM.gov |
| 3 | `DISPATCH_EMAIL_SECRET` defaults to a hardcoded, publicly-known string (`"dispatch-dev-secret"`) if unset | High, if unresolved on the live deployment | `cin_lite/email_delivery.py:38,90`. This HMAC secret signs the tokens gating `cin_lite`'s email decision-action links (`approve_proposal`, `approve_archive`, etc., verified in `portal/routes/decisions.py`). If the live `.env` hasn't overridden it, anyone who knows this public default (published in this open-source repo) could forge a valid token and trigger a real decision action without ever receiving the actual email — bypassing that approval gate entirely. **Status on the live VPS is unconfirmed** — same one-line check pattern Mike already ran for the SAM key would settle it: `grep -c "DISPATCH_EMAIL_SECRET" /opt/cin-hybrid/.env` | Mike to check directly; set a real value if unset |
| 4 | `dispatch-old`'s `.gitignore` doesn't list `.env` | Low (hygiene only) | Confirmed via full history search: no real `.env` was ever actually committed to that repo — this is a missing safety net, not an active exposure | Add `.env` to `.gitignore` if that repo is touched again |

**Clean, worth stating explicitly**: both repos' `.env.example` templates contain only comments
and placeholders, no real values. No AWS-style keys, private-key blocks, or hardcoded passwords
found anywhere in either repo's current tree or full commit history via broad pattern scan.
`jax1313-outlook/Dispatch`'s own `.gitignore` does correctly cover `.env`.

No fixes applied — findings and severities only, per this track's own scope.

### Track F — Doctrine Compliance Audit Against the Primary Constitution — **CLOSED**
**Purpose**: `dispatch-old`'s `CONSTITUTION.md` is the actual primary-source governing document —
read directly for the first time this session, rather than operated on via secondhand paraphrase
the way it was for everything prior. Run a proper rule-by-rule pass: does `jax1313-outlook/
Dispatch`'s real implementation hold up against the 17 Building Rules and Article III's
department table?
**Produces**: a rule-by-rule compliance table with evidence, not assumption, for each rule.

**What was actually done**: read `dispatch-old/CONSTITUTION.md` in full (Article 0 through
Article XII, all 17 Building Rules, the Article III department table). Every verdict below cites
either evidence already established this session (the three Completeness Reviews, the Manager
Preservation Decision, Tracks D and E) or a fresh check run for this track specifically — none is
asserted from memory or paraphrase.

**Fresh checks run for this track**:
1. `ls docs/` in `jax1313-outlook/Dispatch` → `CANONICAL_RECONCILIATION_INTEGRATION.md`,
   `MANAGER.md` — confirms process/governance documentation exists inside Dispatch itself, not
   only in the Claude-3 planning repo (relevant to Rules 5 and 6).
2. `grep -rln "class Automation\|def automation\|Automation department" --include="*.py" .` →
   **no matches**. Confirms no dedicated "Automation" module or class exists anywhere, relevant to
   Article III's ninth department row.

**Findings — the 17 Building Rules:**

| # | Rule | Verdict | Evidence |
|---|---|---|---|
| 1 | Human Final Authority | **Compliant** | Every implementation this session (Stage 1, Stage 2, the presentation-layer panel, the merge to `main`) proceeded only after Mike's own explicit approval instruction, recorded turn-by-turn and in each scope document's own status line. |
| 2 | AI Decides Nothing | **Compliant** | This session's own scope-then-approve pattern directly enacts this rule. In code, the `RESERVED_SYSTEM_IDENTITIES` gate (Library/Publisher/Archive) exists specifically to stop an AI/automation identity from self-approving — verified in the Publisher and Library Completeness Reviews. |
| 3 | Software Automates Administration | **Partial** | Stage 1/2's hooks (`promote_to_candidate`, `_trigger_publisher_on_approval`, `_trigger_govcon_draft`) are exactly the approved administrative automation this rule describes, but Track D found `promote_to_candidate()` has zero HTTP callers — real automation a human cannot yet trigger through the running app. |
| 4 | No Spec, No Prompt. No Prompt, No Build. No Approval, No Implementation. | **Compliant** | The most strongly evidenced rule this session — every implementation (Stage 1, Stage 2, presentation-layer, `docs/MANAGER.md`) has a named, dated scope document with an explicit approval step preceding any code, no exceptions; Manager was directly refused implementation for lacking exactly this (`MANAGER.md` Section 3). |
| 5 | Process Before Tool | **Compliant** | Each scope document (`STAGE_1_...`, `STAGE_2_...`, `PRESENTATION_LAYER_...`) defines the business process before any tool/code decision; `docs/CANONICAL_RECONCILIATION_INTEGRATION.md` and `docs/MANAGER.md` exist inside Dispatch itself as the process record (fresh check #1, above). |
| 6 | Governance Before Automation | **Partial** | Where automation exists (Publisher/Library approval gates) it has purpose, trigger, and accountability (`RESERVED_SYSTEM_IDENTITIES`). The Intelligence department (all 6 contract concepts absent, per its Completeness Review) has neither automation nor governance yet — unproven there, not violated. |
| 7 | Roles Before Agents | **Compliant** | Publisher/Library/Intelligence/Archive remain distinct, bounded models with distinct ownership per the three Completeness Reviews; no department performs another's job — Manager stays dormant rather than absorbing routing work from elsewhere. |
| 8 | Reuse Before Create | **Compliant** | Stage 2 explicitly reused `cin_lite.pipeline.resolve_decision()` instead of a new GovCon decision path; `MANAGER.md` Section 4 reasons explicitly from reuse-first principles (compose over Conflict Notices, don't subsume it); the presentation-layer panel composed existing data rather than creating new storage. |
| 9 | Deterministic First | **Partial / not fully verifiable this session** | The `RESERVED_SYSTEM_IDENTITIES` check and the Publisher approval-gate's real 400 response (Track D, Stage 2 step 4) are genuine deterministic gates, verified live. Article VI's freight-scoring/radius-band logic was not reviewed by any track this session — marked unknown, not assumed either way. |
| 10 | No Architecture Drift | **Compliant, strongly evidenced** | The Manager Preservation Decision (`MANAGER.md` Section 8) is the clearest instance: Mike explicitly refused to let a discovered `MANAGER_CONSTITUTION_v1.md` in `Hold` reopen the dormant-Manager decision. The `Hold`/`Test-Grounds`/five-repo ruling (Section 6.3, this document) applies the same principle at the repository level. |
| 11 | No Fabrication | **Compliant in this session's own conduct; one open question on live data** | This session consistently marked unverified claims as unknown rather than asserting them (the port-8080 retraction, the `conflicts.json` growth flagged "unconfirmed," Tracks A/B relying only on relayed real command output). Open, not resolved: Track B found Sandbox data is real SAM.gov data only when `CIN_LITE_SAM_API_KEY` is set — whether the live UI clearly labels an unset-key state as sample/placeholder data, versus presenting it as live, was not directly verified. |
| 12 | Library Stores Approved Reusable Knowledge | **Partial** | Library Completeness Review: 4/6 contract concepts absent, no `library.current(object_code)` lookup, no versioning/supersession. The core approve/reject lifecycle (`review_candidate()`, identity-gated) does work — the gap is data richness, not an ungated write path. |
| 13 | Archive Stores Completed History | **Compliant, with a known nuance** | `reconciliation/` adapters are confirmed read-only (Stage 4); the Archive Dead Section Validation Mission established the current split as deliberate design, "split by design, not drift," not an unrecorded gap. |
| 14 | Publisher Produces From Approved Inputs Only | **Partial, one violation found and fixed** | Publisher Completeness Review: 4/6 contract concepts absent. More directly on-rule: the live "Mark Approved" button bug (not sending `approved_by`) was a real instance of the UI permitting an approval transition without a genuine human identity attached — found and fixed this session (commit `f5a42dd`); Track D confirmed it now correctly blocks (real HTTP 400). |
| 15 | Portal Reduces Cognitive Load | **Partial** | The presentation-layer panel is a direct, Track-D-verified implementation of this rule. Set against it: Track E Finding 1 (no Portal authentication at all) is a direct violation of Article X's own explicit stop-trigger ("expose Portal publicly without approved authentication") — undermining the precondition for a cockpit meant to be trusted. |
| 16 | Capture Once, Use Many / Experience Becomes An Asset | **Not implemented — the most significant gap tied to any single rule** | Operational Intelligence, the department this rule most directly names, has zero implementation (Intelligence Completeness Review: all 6 contract concepts absent). No mechanism exists for "the tenth trip" to consume anything "the first trip" captured. |
| 17 | Protect Position And HOS-Aware Operations | **Not assessed this session** | No track reviewed `dispatch/`'s freight-load/HOS/radius-band logic. Marked unknown rather than assumed compliant. |

**Summary**: 9 of 17 rules compliant on direct evidence, 6 partial (real gaps or unproven areas,
not active violations), 1 outright not-yet-implemented (Rule 16), 1 not assessed this session
(Rule 17). Exactly one concrete in-code rule violation was found this session at all — the
Publisher approval button bypassing `approved_by` (Rule 14) — and it was found and fixed before
this audit ran. The two most consequential open items (Article X's authentication stop-trigger,
and Rule 16/Operational Intelligence's total absence) are not new discoveries; this track's
contribution is tying both explicitly to the primary Constitution's own text rather than leaving
them as standalone review findings.

**Findings — Article III department table:**

| Department | Constitution's Passed Product | Current State | Evidence |
|---|---|---|---|
| Acquisition | Raw source record, source link, acquisition log | Real, exists | `cin_lite`'s acquisition module, carried from `dispatch-old` into `jax1313-outlook/Dispatch`; Track B confirmed the local L1-COS tool performs real SAM.gov sweeps. |
| Processing / Rules | Rule JSON, score, flags, normalized record | Real, exists — not independently re-verified this session | `cin_lite/processing`, `cin_lite/rules` present in the repo structure; no track this session re-tested its scoring/flagging logic directly. |
| Manager / Control | Decision request, routing task, Conflict Notice | **Deliberately dormant** | `MANAGER.md` Sections 2-3; zero Manager code confirmed twice (Manager Orchestration Review Phase 1, and this track's fresh grep finding no Automation/Manager module). The routing/Conflict-Notice function is currently covered ad hoc by `portal/models/conflict.py`, not by a Manager/Control department. |
| Publisher | Brief, draft, packet, inquiry, checklist, document package | Real, partial | Publisher Completeness Review: 4/6 concepts absent; live approval-gate bug found and fixed. |
| Library | Approved fact, packet component, current asset | Real, partial | Library Completeness Review: 4/6 concepts absent, no review UI. |
| Archive | Retrievable audit bundle | Real, split by design | `reconciliation/` adapters, confirmed read-only and structurally incapable of writes. |
| Portal / Presentation | Operator-facing display card | Real, functioning, unauthenticated | Track D confirmed the Attention Needed panel renders correctly and filters correctly; Track E Finding 1: no authentication of any kind. |
| Operational Intelligence | Reusable intelligence record | **Zero implementation** | Intelligence Completeness Review: all 6 contract concepts absent — the most severe finding of any department reviewed this session. |
| Automation | Execution log, completed workflow | **No distinct department exists** | Fresh check this track: no `class Automation`, `def automation`, or "Automation department" match anywhere in the tree. Automation logic exists only ad hoc, embedded inside other departments' models (Stage 1/2's `_trigger_*` hooks inside Library/Publisher) — there is no dedicated Automation department with its own purpose/input/output boundary as Article III names it. |

No code changes made in this track — findings and citations only, per this track's own scope.

## 4. What This Mission Is Not

Not an authorization to fix anything found — no auth implementation, no key rotation, no code
changes of any kind. Not a re-scope of any already-decided item (Manager stays dormant, Archive
stays Option A). Investigation and verification only.

## 5. Sequencing Note

Tracks C, D, E, and F are investigation/verification work Claude can start directly, each on its
own separate go-ahead per this program's standing practice. Tracks A and B need Mike's server
access first and don't block the others — they can run in parallel with C/D/E/F, not before them.

Mike decides which track(s) to start, and in what order.

---

## 6. Update: Repo Discovery Findings and Rulings

Substantially expands Track C's scope. Mike granted broad explore-as-you-see-fit access across
the full `jax1313-outlook` account; seven additional repos were found and surveyed:
`Jules`, `Jules-2`, `Jules-3`, `Claude`, `Claude-2`, `Test-Grounds`, `Hold`.

### 6.1 Repo Matrix

| Repo | Role (per its own `DISPATCH_REPO_MANIFEST_v3.md` promotion path) | Content | Last commit | Finding |
|---|---|---|---|---|
| `Jules` | Round 2 clean review copy | 13 docs, baseline bundle only | Aug 10 | Baseline doctrine, Constitution v2 |
| `Jules-2` | Clean review repo | Baseline + Decision Matrix, Repo Manifest v3, Spine Spec v1, Constitution v3, Publisher.md | Aug 10 | First "active" round per Manifest v3 |
| `Jules-3` | Clean review repo (most complete) | Baseline + Security/Auth spec, Alert Governance, Archive Review Policy, Version Doctrine, Intelligence Verification Workflow | Aug 10 | Latest, most elaborated round |
| `Claude` | Clean review repo | Baseline + Build Proposal, Program Map, Constitution v2, Context Master v2 | Aug 10 | Parallel round, earlier Constitution |
| `Claude-2` | Clean review repo | Baseline + Decision Matrix, two Spine Spec copies, Stress Test Prompt, Constitution v3, Publisher.md | Aug 10 | Matches Jules-2/3's active set |
| `Test-Grounds` | Pipeline stage 5, "experimental build and prototype testing" | Numbered doctrine series (02-08), Agent Governance Law, Constitution v2 | Aug 8 | Different, numbered doctrine variant |
| `Hold` | Pipeline stage 6, "stabilization and review lane" — code scaffold, not docs | `config/`, `contracts/`, `docs/`, `library_seed/`, `src/`, `tests/`, `tools/`, 68 files | Aug 4 | See 6.2 |
| `dispatch-old` | Predecessor ("cin-hybrid," Phases 1-2 of the CLAUDE.md roadmap) | Real working code | earlier | Already fully reviewed this session |
| `Dispatch` | Pipeline stage 7, "production-intent repository after Mike approval" | Real working code, tri-department work merged | today | What this whole session built |

Nine of the ten baseline doctrine files (`ARCHITECTURAL_DISPOSITION.md`, `ARCHITECTURE.md`,
`COGNITIVE_FUNCTIONS.md`, `CONTEXT_MASTER.md`, `MANAGER.md`, `PORTAL_DESCRIPTION.md`,
`REFINEMENT_ANALYST_REMOVAL.md`, `SUPERSESSION_MAP.md`, `DISPATCH_SPINE_OVERVIEW.md`) are
byte-identical (confirmed by checksum) across all five doctrine-review repos — a common bundle
distributed for independent review, not five diverging drafts.

### 6.2 `Hold` — Verified: Zero Application Code

`Hold`'s README describes a separate initiative, "Dispatch Matrix Group 1": four lanes
(Librarian, Manager, Receipt/IFTA, Reports), frozen data contracts, a 14-item Approval Register
(all resolved as of Aug 4), six validation gates per lane, strict merge-order branch discipline.

Checked `src/`, `tests/`, `tools/` directly: **every file in all three is a `.gitkeep`
placeholder.** Zero lines of application code exist anywhere in the repository. This confirms,
rather than contradicts, the README's own claim ("no lane session has been opened... nothing
yet — seed only"). The only real content is `library_seed/Constitutions/` (per-lane governance
documents: `LIBRARIAN_CONSTITUTION_v1.md`, `MANAGER_CONSTITUTION_v1.md`,
`RECEIPT_CONSTITUTION_v1.md`, `IFTA_CONSTITUTION_v1.md`, `REPORTS_CHARTER_v1.md`, plus shared
`DISPATCH_BASE_CONSTITUTION_v1.md`, `APPROVAL_REGISTER.md`, `MEMORY_DOCTRINE_v1.md`) and one
data file, `expense_vocabulary.v1.json`.

Matrix Group 1's four lanes (Librarian/Manager/Receipt-IFTA/Reports) are not the same
decomposition as this session's tri-department work (Intelligence/Library/Publisher) — a
different, complementary feature set, not duplicate or competing work on the same features.

### 6.3 Ruling: `Hold` Is Reference Material, Not Authoritative

Mike's ruling, verbatim in substance: **`Hold` is a staging and stabilization repository —
candidate architecture, scaffolding, and work intended for evaluation before promotion.
`Dispatch` is the current production-intent repository. The `Hold` architecture should be
treated as prior design work and reference material, not automatically as the authoritative
replacement for `Dispatch`.** Applies to all seven newly-found repos, not `Hold` alone.

### 6.4 Ruling: Manager Queue Reinforcement

Mike's ruling, verbatim: **Manager Queue remains dormant. Treat `Hold`'s Manager lane as
archived planning material unless explicitly reactivated. Do not implement Manager
functionality based solely on the existence of `MANAGER_CONSTITUTION_v1.md`.**

This reinforces, does not modify, the existing Manager Preservation Decision
(`MANAGER_ORCHESTRATION_REVIEW_v1.md`, `jax1313-outlook/Dispatch:docs/MANAGER.md`). Recorded in
both places.

Mike decides.
