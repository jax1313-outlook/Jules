# DISPATCH_DEPARTMENT_RECONCILIATION_v1.md

Program: Dispatch
Status: Reconciliation Report only — no code modified, no code merged, no deployment
Scope: Dispatch's existing `cin_lite/`, `dispatch/`, `portal/` subsystems vs. the tri-department
build's Intelligence, Library, Publisher repos
Date: 2026-08-11

Do not modify code. Do not merge code. Do not deploy. Mike decides.

---

## 0. A Correction Baked Into This Report's Method

Every claim below is grounded in files actually read this session (paths cited throughout), not
inferred from doctrine or from the tri-department build's own documentation. This report also
surfaces something not visible in `DISPATCH_INTEGRATION_RECONSTRUCTION_v1.md` (the previous
turn's shallower pass): **Dispatch is not one existing implementation of each department — it is
three loosely-connected subsystems, and at least Archive is duplicated *within* Dispatch itself,
before the tri-department build is even considered.**

| Dispatch subsystem | What it is | Files |
|---|---|---|
| `cin_lite/` | A mature, tested, real government-contract intelligence pipeline: live SAM.gov acquisition, 10 deterministic compliance/risk rule modules, a Claude-backed routing-recommendation agent (with deterministic fallback), a Claude-backed proposal-drafting agent (with deterministic fallback), email-based human-decision checkpoints (HMAC-token action links), and a hash-verified file-tree Archive | `cin_lite/acquisition.py`, `rules/*.py` (10 modules), `agents/router.py`, `agents/proposal_writer.py`, `agents/summarizer.py`, `agents/extractor.py`, `agents/receipt_vision.py`, `workflows/proposal.py`, `archive.py`, `control.py`, `email_delivery.py`, `pending.py`, `pipeline.py`, `processing.py` |
| `dispatch/` | A separate "Dispatch Data Engine" for the load-operations lifecycle (create→dispatch→pickup→transit→deliver→POD→archive) — freight/trucking operations, not contract intelligence | `dispatch/models.py` ("canonical data models for the seven dispatch objects"), `scoring.py`, `services.py`, `acquisition.py`, `store.py`, `db.py`, `notifications.py` |
| `portal/` | The Flask web UI, with its own independent flat-JSON-file models for Intelligence, Library, Publisher, Archive, Sandbox (work-item/card state), and Conflict (notice) — none of which import from or share code with `cin_lite/` | `portal/models/{intelligence,library,publisher,archive,sandbox,conflict}.py`, `portal/routes/{api,pages,decisions,pipeline}.py`, `portal/templates/*.html` |

`portal/models/archive.py` and `cin_lite/archive.py` are two independently-written Archive
implementations with different ID formats, different storage layouts, and no shared code —
confirmed by reading both in full. This predates and is unrelated to the tri-department build.

---

## 1. Intelligence

### What already exists?

Two Dispatch implementations, doing different jobs:

- **`cin_lite/` pipeline** — real: live SAM.gov acquisition (`acquisition.py`, falls back to
  local sample data offline), 10 deterministic government-contract rule modules
  (`rules/{cyber_compliance,foreign_influence,jv_mp_structure,naics_sin,past_performance,
  pricing_anomaly,set_aside,subcontractor_dominance,vendor_network}.py`), a Claude-backed
  routing-recommendation agent (`agents/router.py::decide()`, deterministic fallback when no API
  key), tested (`tests/test_archive.py` imports `cin_lite.archive` directly; the walkthrough
  reports at Dispatch's repo root — `PHASE2_IFTA_WALKTHROUGH_REPORT_v1.md` through
  `PHASE7_...md` — document further hardening passes, though those are IFTA/fleet-focused, not
  this pipeline specifically).
- **`portal/models/intelligence.py`** — a much simpler flat JSON-record store across six intel
  types (`location`, `broker`, `customer`, `route`, `position`, `market`), no rule engine, no
  routing logic, no risk detection — just create/read/update records.

### What overlaps with Tri-Department Intelligence?

Conceptually, all three (`cin_lite`, `portal`, tri-department) do "turn raw contract/opportunity
text into structured findings a human can act on." Mechanically, they overlap almost nowhere:

- Tri-department's `dispatch_intel` classifies **10 general opportunity types** (load board,
  SAM.gov, federal, state, county, FEMA, DOT, GSA, port/agency, mixed-text) with **15+ generic
  operational risk rules** (rate missing, deadhead risk, staffing burden, etc.) — built for a
  one-truck regional carrier's *fit* decision.
- `cin_lite`'s 10 rule modules are **narrower and deeper on one axis**: set-aside eligibility,
  NAICS/SIN extraction, cyber-compliance framework/CMMC level detection, foreign-influence and
  JV/MP structure red flags, pricing anomaly detection, subcontractor dominance, vendor network —
  all specific to *federal contract pursuit viability*, a dimension tri-department Intelligence
  does not touch at all.
- `portal/models/intelligence.py` overlaps with neither in mechanism — it's a passive record
  store, not an analysis engine.

### What is duplicated?

The *concept* of "Intelligence department" is triplicated (cin_lite, portal, tri-department) with
almost no code-level redundancy — each does a genuinely different analysis. The one true
duplication: **routing/recommendation logic exists three separate times**
(`cin_lite/agents/router.py::decide()`, tri-department's `dispatch_intel/routing.py`, and
implicitly whatever surfaces `portal/models/sandbox.py`'s `decision` field), each with its own
action vocabulary and none aware of the others.

### What conflicts?

- **Determinism posture.** Tri-department Intelligence is explicitly, doctrinally offline/rule-
  only (`docs/ARCHITECTURE.md`: "No live web-scraping, third-party API calls... AI/Agent retains
  zero authority"). `cin_lite/agents/router.py` is Claude-backed by default when
  `ANTHROPIC_API_KEY` is set — a materially different position on whether AI may generate the
  routing recommendation itself (with a deterministic fallback, and the human still clicks the
  final action link, but the *recommendation text* is LLM output, not rule output). Neither is
  "wrong" per Constitution Section 4 (AI may recommend; only the human decides) — but they are two
  different interpretations of how far "recommend" may go, and would produce different-looking
  output for the same input.
- **No-fabrication enforcement mechanism.** Tri-department enforces no-fabrication structurally
  (`is_final_decision`/`library_truth` fixed False at the dataclass level, never a string in a
  prompt). `cin_lite`'s equivalent is a system-prompt instruction ("Do not invent facts" /
  "Ground every point in the provided data; do not invent requirements") — real, but a request to
  the model, not a code-enforced guarantee. These are different strengths of the same doctrine.

### What is stronger?

- `cin_lite`: **live data acquisition** (tri-department Intelligence has none — it only reads
  local files a human already placed), **domain depth** on federal-contract-specific risk
  (set-aside, CMMC, NAICS/SIN — tri-department has zero equivalent), and **real test coverage
  tied to a live archive** (26 tests in `test_archive.py` alone).
- Tri-department: **structural, code-enforced no-fabrication/no-final-decision guarantees**
  (`init=False` fields, not prompt text) and a **broader, carrier-fit-oriented risk vocabulary**
  (staffing, positioning, deadhead, equipment) that `cin_lite` doesn't cover at all — `cin_lite` is
  federal-pursuit-only, tri-department is fit-for-a-one-truck-carrier-only. Genuinely different
  scope, not a strictly-better/worse pair.

### What is weaker?

- `cin_lite`: no code-level guarantee equivalent to tri-department's `is_final_decision`/
  `library_truth` fixed-False fields — its no-fabrication posture rests on prompt engineering plus
  a deterministic fallback path, which is real but not as hard a guarantee.
- Tri-department: no live acquisition, no federal-contract-specific rule depth, and — per the
  previous audit — its own CLI didn't call its object-model layer until a follow-up fix; `cin_lite`
  has no equivalent gap (its pipeline is one continuous, exercised path from acquisition to
  archive).

### What should stay?

`cin_lite`'s acquisition, rule modules, and archive integration — they are live, tested,
federal-contract-specific, and nothing in the tri-department build replaces that domain depth.

### What should be replaced?

Nothing here is a byte-for-byte replacement candidate — the two Intelligence implementations solve
different problems (federal pursuit viability vs. one-truck carrier fit) and neither doctrinally
covers the other's ground.

### What should be merged?

The **object-model discipline** (structural finding/candidate schemas with fixed truth/decision
fields) is the one piece of tri-department Intelligence worth carrying into `cin_lite`'s output
shape — `cin_lite` currently returns plain dicts (`{action, reason, priority, recipient, notes}`
from `router.py`, `{module_name: rule_json}` from `processing.py`) with no equivalent to
`IntelligenceFinding.is_final_decision` being unsettable. That's a reconciliation direction, not a
design — no schema change is proposed here.

### What should be retired?

Tri-department's own `routing.py` label vocabulary, *if* `cin_lite`'s router ever became the
single routing authority — but only one of the two routing engines should survive long-term, since
maintaining two independently-evolving action taxonomies (`ALLOWED_ROUTING_LABELS` vs.
`cin_lite.control.ACTIONS`) for the same underlying concept is the kind of duplication this program
warns against creating.

---

## 2. Library

### What already exists?

`portal/models/library.py` only — no `cin_lite` equivalent exists (confirmed by search: no
`library.py`, no library-shaped module anywhere under `cin_lite/`). Six sections: `company`,
`broker`, `customer`, `location_intelligence`, `operations`, `intelligence`. Every record gets
`status: "approved"` hardcoded at creation time in `add_record()` — there is no pending/review
state anywhere in this file. `get_missing_company_assets()` diffs against a fixed 10-item
`COMPANY_ASSETS` list (W-9, Insurance, Authority, Business Card, Rate Sheets, Terms, Capabilities,
Compliance Documents, Fleet/Equipment, Driver Qualifications).

### What overlaps with Tri-Department Library?

The core idea — "approved reusable facts and production parts, not temporary workspace" — is
identical in intent (Dispatch's own docstring: "Library is not temporary workspace," verbatim
matching Constitution Section 7.4's language). The `company` section maps closely onto
tri-department's `Company`/`Publisher_Parts` collections; `broker`/`customer`/
`location_intelligence` map onto tri-department's `Broker`/`Customer`/`Location_Intelligence`
collections by name.

### What is duplicated?

The *concept* and even several *collection names* overlap almost one-to-one on the business-data
side (broker, customer, location intelligence). Underneath, they are two separate storage engines
with two separate taxonomies (6 sections vs. 15 collections) and no shared schema.

### What conflicts?

**This is the sharpest doctrine conflict found in this whole reconciliation.** Dispatch's real
Library (`portal/models/library.py::add_record()`) auto-approves every record on creation — no
review, no candidate queue, no external approver check. The tri-department build's Library repo
was built specifically to enforce the opposite: human-placed documents are accepted directly (that
part matches), but **machine-nominated candidates must go through `submit_candidate()` →
`review_candidate(..., reviewed_by=<external human>)` before becoming truth** — a gate Dispatch's
existing Library has no equivalent of at all. Since `add_record()` doesn't distinguish
human-placed from machine-generated content, **Dispatch's real Library today would auto-approve a
machine-nominated candidate exactly like a human-placed document** — which is the forbidden path
tri-department Library was built to structurally prevent (System Relationship Matrix §11:
"Intelligence Finding -> Library Truth Automatically"). This is not a hypothetical: it's the
literal behavior of the code that exists right now.

### What is stronger?

Tri-department Library, unambiguously, on governance: real `PENDING_REVIEW`/`APPROVED`/`REJECTED`
lifecycle, an external-non-self `reviewed_by` check enforced in code, versioned
`CURRENT`/`SUPERSEDED` objects with automatic supersession, and a 15-collection taxonomy that
matches the System Relationship Matrix exactly (verified in a prior audit this session, section 4
of `TRI_DEPARTMENT_BUILD_RECEIPT_AND_QUALITY_AUDIT_v1.md`). Dispatch's real Library has none of
this.

### What is weaker?

Tri-department Library has zero live storage (in-memory only) and zero real usage — nothing
outside its own tests and the cross-repo walkthrough has ever called it. Dispatch's real Library,
weaker on governance, is at least **live**: it's imported by `portal/routes/api.py` and
`portal/routes/pages.py`, has a rendered template (`portal/templates/library.html`), and backs a
real `check_library_assets()` conflict-notice check in `portal/models/conflict.py`.

### What should stay?

Dispatch's real Library's **storage wiring and UI** (routes, templates, the file-backed
persistence pattern via `get_data_dir()`) — none of that exists in tri-department Library at all.

### What should be replaced?

`add_record()`'s auto-approve-everything behavior. Per the conflict above, this is the one place
in this whole reconciliation where the tri-department build's stricter behavior is not just
"different" but doctrinally *correct* relative to Dispatch's current, weaker implementation.

### What should be merged?

Tri-department's candidate-review gate logic (`submit_candidate`/`review_candidate`, the
external-reviewer check, the `CURRENT`/`SUPERSEDED` versioning) is the strongest merge candidate
in this entire report — it's a direct doctrine-compliance upgrade to a real, live gap in Dispatch's
current code, not a speculative improvement.

### What should be retired?

Nothing should be deleted outright — Dispatch's 6-section taxonomy has real data in production
shape (company assets, location fields) that the tri-department's 15-collection taxonomy doesn't
structurally preclude holding, just doesn't currently model identically.

---

## 3. Publisher

### What already exists?

Two real pieces, working together:

- **`portal/models/publisher.py`** — a JSON action queue over 8 fixed action types (Broker
  Packet Required, Direct Shipper Packet Required, Rate Sheet Request, Rate Confirmation Package
  Required, DocuSign Package Ready, Arrival Notice Draft, POD/BOL Document Package Draft,
  Detention Evidence Draft), status flow `PENDING → DRAFT → READY → APPROVED → ARCHIVED`, a
  `human_approval_required: True` field on every action, and hardcoded manifests per action type
  (e.g. `BROKER_PACKET_MANIFEST = ["Business Card", "W-9", "Insurance", "Authority", "Rate
  Sheet", "Terms"]`).
- **`cin_lite/agents/proposal_writer.py` + `cin_lite/workflows/proposal.py`** — a real,
  **content-generating** proposal-drafting capability: `draft_outline()` produces an actual
  Markdown proposal outline (Technical/Management/Past-Performance/Price volumes, a compliance
  matrix, win themes), Claude-backed with a deterministic fallback template when no API key is
  set. `workflows/proposal.py::trigger()` assembles a structured brief (milestones, requirements
  checklist), calls the writer, persists both to `archive.store_proposal()`, and emails a kickoff
  — fired only after a human clicks "approve_proposal" through the HMAC-token-verified email
  link in `portal/routes/decisions.py`.

### What overlaps with Tri-Department Publisher?

Materially, on the governance side: `human_approval_required: True` plus the
`PENDING→DRAFT→READY→APPROVED→ARCHIVED` flow is the same shape of idea as tri-department's
`DraftReviewPackage` status lifecycle and its "Publisher may not approve itself" rule. On the
content side: `proposal_writer.py`'s system prompt ("Ground every point in the provided data; do
not invent requirements") is the same No-Fabrication doctrine tri-department Publisher's
`KNOWN_GAPS.md` explicitly said it could not implement without missing source templates.

### What is duplicated?

The packet-manifest concept exists twice with different content: Dispatch's
`BROKER_PACKET_MANIFEST`/`DIRECT_SHIPPER_MANIFEST`/`RATE_CONFIRMATION_MANIFEST` (hardcoded lists
of document names) vs. tri-department's `PublisherRecipe.required_library_object_codes`
(deliberately left empty, scaffold-only, per its own docs, pending
`publisher_recipes.json` which was never found). **Dispatch already has the real manifest content
tri-department Publisher's recipe registry was missing.**

### What conflicts?

- **Approval enforcement mechanism**, same pattern as Library: Dispatch's `human_approval_required`
  is a static boolean field on the action record — nothing in `update_action_status()` checks it or
  enforces who may set `status="APPROVED"`. Tri-department's `approve_review_package()` is a real
  code gate that rejects a `PUBLISHER`/system-identity `approver_id`. Dispatch's version could, as
  written, have `update_action_status(action_id, "APPROVED")` called by anything, including
  automated code, with no identity check — the same class of gap as Library's auto-approve issue,
  though less severe here because the action still requires a human to have clicked the email link
  that triggered the workflow in the first place (`decisions.py` + `email_delivery.verify_token()`).
- **Content-generation authority.** `proposal_writer.py` generates real prose via Claude by
  default. Tri-department Publisher's doctrine (`PUBLISHER.md` Section 12, this build's own
  `README.md`) treats content generation as out of scope for a rule-based repo and explicitly
  defers it. Neither is wrong per Constitution Section 4, but they represent different design
  decisions about how much of "drafting" an LLM should do directly versus how much should stay
  template/rule-based — unreconciled between the two.

### What is stronger?

`cin_lite`'s proposal pipeline: it actually produces a document. Tri-department Publisher, per its
own `KNOWN_GAPS.md`, produces "the governed assembly shell around a packet, not the packet
itself" — this reconciliation confirms that gap was real and that Dispatch already has a working
answer to it, just not integrated with tri-department's stricter approval-gate code.

### What is weaker?

`cin_lite`'s proposal/publisher approval path has no code-enforced non-self-approval check
comparable to tri-department's; tri-department's `create_archive_handoff()` refuses to run unless
`review.status == APPROVED_BY_MIKE` — Dispatch's `archive_publisher_action()`
(`portal/models/archive.py`) has no equivalent precondition; it archives whatever status an action
is in when called.

### What should stay?

`cin_lite`'s proposal-writer/workflow pair as the actual content-generation engine — nothing in
tri-department Publisher does this job, and rebuilding it would duplicate real, tested,
already-working code.

### What should be replaced?

Nothing wholesale. The manifest hardcoding in `portal/models/publisher.py` is a candidate for
replacement *by* tri-department's recipe-registry pattern (data-driven, versioned,
`resolve_packet()`-resolved) rather than the reverse, since tri-department's mechanism is more
flexible — but the *content* of Dispatch's manifests (the actual document names) is real and
should populate tri-department's currently-empty recipe registry, not be discarded.

### What should be merged?

Two clear candidates: (1) Dispatch's manifest content → tri-department's `PublisherRecipe.
required_library_object_codes` (closes the "recipe content is scaffold" gap noted in this
session's earlier audit); (2) tri-department's enforced `approve_review_package()`/
`create_archive_handoff()` gating → Dispatch's `update_action_status()`/`archive_publisher_action()`
(closes the static-flag-not-a-gate weakness noted above).

### What should be retired?

Nothing. Both the manifest data and the proposal-writer agent are live, working, and not
duplicated by anything in tri-department Publisher.

---

## 4. Archive

### What already exists?

Two independent, real implementations (see Section 0):

- **`cin_lite/archive.py`** — file-tree storage (`Raw/Processed/Intelligence/Summaries/Routing/
  Pending/Outbox/Proposals` subdirectories under a configurable root), deterministic
  `CIN-YYYYMMDD-<hash>` IDs, **SHA-256 content-hash sidecars with fail-closed integrity
  verification** (`ArchiveIntegrityError`, `_read_verified()`), and a
  `record_integrity_exception()` path that escalates a corrupted-artifact read to the same
  human-review routing queue as any other exception — deliberately never overwriting the original
  record. 26 dedicated tests (`tests/test_archive.py`).
- **`portal/models/archive.py`** — flat JSON records across 5 sections (`load`, `decision`,
  `publisher`, `location_history`, `broker_history`), `ARC-XXX-0001` IDs, no integrity
  verification of any kind, `archive_from_sandbox()` and `archive_publisher_action()` as its two
  real ingestion paths.

### What overlaps with Tri-Department Publisher's Archive-adjacent object?

Tri-department Publisher's `ArchiveHandoffPackage` (`review_id`, `bundle_manifest`,
`retention_class`) is a *pointer/manifest* object — it doesn't implement storage itself, by
design (Section 5.7 of `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md`: "Publisher creates; Archive
receives"). Both Dispatch Archive implementations overlap with it at the concept level (receiving
a completed Publisher output) but neither has a corresponding "handoff package" object with an
approval-status precondition — they just accept whatever is passed to `store()`/
`archive_publisher_action()`.

### What is duplicated?

The entire concept of "Archive" is duplicated within Dispatch itself — two ID schemes, two storage
layouts, two section/type vocabularies, zero shared code between `cin_lite/archive.py` and
`portal/models/archive.py`. This predates the tri-department build entirely and is a
Dispatch-internal reconciliation question independent of anything built this mission.

### What conflicts?

- `cin_lite/archive.py` is fail-closed on tampered data (raises `ArchiveIntegrityError` rather
  than silently returning corrupted content). `portal/models/archive.py` has no equivalent —
  reads whatever JSON is on disk with no verification. Two different reliability postures for the
  same doctrine concern ("Archive preserves completed history," Constitution Section 7.5) inside
  the same repository.
- Neither Dispatch Archive requires the referenced source object to be in an "approved" state
  before archiving it — `archive_publisher_action()` archives an action regardless of its
  `status` field. Tri-department's `create_archive_handoff()` explicitly blocks unless
  `APPROVED_BY_MIKE`. This is the Archive-side echo of the same approval-gate gap found in
  Section 3.

### What is stronger?

`cin_lite/archive.py`, decisively, on integrity: hash-verified reads, fail-closed on mismatch,
deterministic content-addressed-style IDs, dedicated test suite. Tri-department has no Archive
implementation at all to compare against on this axis — it only defines the handoff *contract*
(Section 5.7), never storage.

### What is weaker?

`portal/models/archive.py` — no integrity verification, and (per above) no approval-status
precondition on what it accepts, making it the weakest of the three Archive-adjacent
implementations examined in this report on both axes that matter most to this program's doctrine
(tamper evidence and no-fabrication-via-premature-archival).

### What should stay?

`cin_lite/archive.py`'s hash-verification and fail-closed read path — it is the strongest
component found anywhere in this entire reconciliation, Dispatch-native or tri-department.

### What should be replaced?

`portal/models/archive.py`'s read path is the weakest link found in this report; if Dispatch ever
consolidates to one Archive implementation, `cin_lite/archive.py`'s integrity model is the one
that should survive, not `portal/models/archive.py`'s.

### What should be merged?

Tri-department's `ArchiveHandoffPackage` precondition ("only when the referenced review is
`APPROVED_BY_MIKE`") should be layered onto whichever Dispatch Archive implementation survives —
neither currently checks approval status before accepting a record, and Publisher's own
`portal/models/publisher.py::update_action_status()` has no equivalent block either, so today
nothing in Dispatch prevents archiving a non-approved Publisher action.

### What should be retired?

Between `cin_lite/archive.py` and `portal/models/archive.py`, one should eventually retire in
favor of the other — this reconciliation does not pick which (that is a design decision this
report is not authorized to make), but flags the duplication as real and pre-existing, not
something the tri-department build introduced or can resolve unilaterally.

---

## 5. Cross-Cutting Observations (Not New Sections — Consolidating What Appeared Repeatedly)

1. **The same doctrine gap recurs three times.** Library's `add_record()` (auto-approves),
   Publisher's `update_action_status()` (no gate behind `human_approval_required`), and Archive's
   `archive_publisher_action()` (no precondition on source status) are the same underlying issue —
   a status field that looks like a gate but isn't enforced in code — appearing independently in
   three different Dispatch files. Tri-department's pattern (external, non-self identity required
   to cross an approval boundary, enforced in the function itself) is the one mechanism in this
   whole reconciliation that would close all three at once if merged in.
2. **The same duplication pattern recurs twice.** Archive (cin_lite vs. portal) and, more loosely,
   routing/recommendation logic (cin_lite's router agent vs. tri-department's routing.py vs.
   portal's sandbox decision field) are each implemented more than once inside what should be one
   coherent program.
3. **Nothing found in this reconciliation was invented to make the report interesting.** Every
   file cited was read this session; every "stronger/weaker" claim is backed by a specific
   function or test file named above.

---

## 6. What This Report Does Not Do

Per the mission's hard constraints: no code was modified, no code was merged, nothing was
deployed. No file in `cin_lite/`, `dispatch/`, `portal/`, or any of the three tri-department repos
was changed as part of producing this document. Every "should merge/replace/retire" statement
above is a reconciliation-direction observation, not a spec, not a patch, and not authorization to
act on it.

Mike decides.
