# DISPATCH_COPILOT_ARTIFACT_REFERENCE_REVIEW_v1

Program: Dispatch
Status: **Reference material only. Not authoritative. No code changes made or authorized by this
document.**
Origin: Mike located a list of artifacts built by Consumer Copilot-Task, stored locally at
`D:\level 1\All copilot-Task built Agents`, and asked whether any could help fill gaps identified
by this session's completeness reviews and the closed `DISPATCH_INTEGRITY_AND_DEPLOYMENT_
VERIFICATION_MISSION_v1`. Four CSV indexes (47 titles + dates total, no content) were reviewed
first and triaged by title; four of the highest-relevance HTML files were then uploaded directly
and reviewed for real content.

---

## 1. What Was Reviewed

**Title-only triage** (47 entries across four CSV exports): most are unrelated to the Dispatch
program — corporate formation/bylaws documents, VA disability and Medicare claims, a separate
SDVOSB insurance-carrier business line, FEMA capability statements, real estate parcel scans, and
merchandise design. Not re-examined here; flagged for the record only.

**Four HTML artifacts uploaded and read in full or by targeted search** (first batch):
1. `CIN_Contract_Intelligence_Network.html`
2. `L1_Transport_Planning_Intelligence_Dashboard.html`
3. `Hybrid_AI_Manager_Dashboard.html`
4. `L1_Transport_l1truck_Website.html`

**Second batch, five files uploaded**: three (`L1_Transport_l1truck_Website.html`,
`CIN_Contract_Intelligence_Network.html`, `Hybrid_AI_Manager_Dashboard.html`) confirmed
byte-identical to the first batch via `md5sum` — not re-reviewed, findings unchanged. Two new
files reviewed: `Level5_Autonomous_Intelligence_Master_Report_1.html`,
`Email_Sweep_Command_Center.html`. See Section 3.5 and 3.6.

## 2. Method

Each file was checked directly for real backend connectivity — `fetch(`, `XMLHttpRequest`,
`.ajax(`, `WebSocket(`, and `localStorage` usage — rather than assumed from title or appearance.

**Result: zero matches for any of the four, for any of those patterns.** All four are static,
client-side-only HTML/Tailwind/JS pages. None of them call a backend, persist state, or connect
to anything live. This is true even where a page's UI strongly implies live behavior (status
lights, "TEST CONNECTION" buttons, a scrolling terminal log) — those are hardcoded markup and
inline event handlers with no network call behind them, confirmed by the same grep across all
four files, not assumed from one.

## 3. Findings, By File

### 3.1 `CIN — Contract Intelligence Network`
A concept dashboard for the pipeline this whole program is named after: Sweep / Intel /
Incumbent / Proposal / Archive / Follow-Up "agents," a Command Dashboard with KPIs (142 active
contracts, 68.4% win rate, $34.7M pipeline — all fabricated demo values, not real data), NAICS
and set-aside filters, a data-flow diagram, and a competitor database. No real data, no backend.
**Relevance**: directly maps onto Operational Intelligence — the single largest gap this session
found (Intelligence Completeness Review: all 6 contract concepts absent; Track F of the closed
verification mission: Rule 16 unimplemented). Worth keeping as a design reference for that
department, not as anything closer to code.

### 3.2 `L1 Transport — Planning Intelligence Dashboard`
Freight/port-specific concept: real Jacksonville-area vessel and terminal references (Blount
Island, Dames Point, Talleyrand), rate-floor guidance, broker outreach windows, contracting prep,
decision gates, route validation. Also fabricated demo data, also no backend.
**Relevance**: maps directly onto Article VI's Operational Position Doctrine and, again,
Operational Intelligence. Two independently-built Copilot concepts both converge on the same gap
this session already identified through completely different means — worth noting as a signal,
not as evidence either concept is correct or complete.

### 3.3 `Hybrid AI Manager Dashboard`
A concept console built specifically around a human-approval-gate pattern — its own "Pending
Gates — YOUR DECISIONS" panel is a near-literal restatement of Constitution Rules 1 and 2 (Human
Final Authority, AI Decides Nothing), the same pattern this session's real `RESERVED_SYSTEM_
IDENTITIES` gate already enforces in code.
**Relevance**: Manager stays deliberately dormant per Mike's standing ruling
(`jax1313-outlook/Dispatch:docs/MANAGER.md`, Section 8). This document does not reopen that
decision. It is filed here as exactly the kind of reference material `MANAGER.md` Section 4
already anticipated being useful "for whenever implementation is reconsidered" — nothing more.

### 3.4 `L1 Transport — l1truck.com Website` — different in kind
Unlike the three above, this file's embedded data is **accurate**, not fabricated: the real VPS
IP (`159.198.41.164`), the real service name (`l2cos-portal.service`), a real `gunicorn`/`nginx`
setup description, and the real deployment path (`/opt/cin-hybrid`) — all independently confirmed
by Track A of the closed verification mission via commands run directly on the live server. This
file appears to be a Copilot-built deployment console/runbook referencing a real session, not an
invented scenario. Its "live" elements (status lights, terminal log, TEST CONNECTION button) are
still static markup with no real connection behind them, same as the other three — the accuracy
is in the reference data it embeds as text, not in any live function.

**New item surfaced, not previously checked by any track**: the file's embedded terminal log and
a "Configure Claude API Key" button both reference an intended `CLAUDE_API_KEY` variable in
`/opt/cin-hybrid/.env` on the live VPS.

**Resolved, follow-up finding — a real naming mismatch, not a security issue**: checked directly
in `jax1313-outlook/Dispatch`'s real code first (`cin_lite/agents/extractor.py`,
`proposal_writer.py`, `router.py`, `summarizer.py`, `receipt_vision.py`, `portal/routes/pages.py`)
— every one of them reads `ANTHROPIC_API_KEY`, never `CLAUDE_API_KEY`. The mockup's button used a
different variable name than the real code recognizes. Confirmed on the live VPS:
`grep -c "^CLAUDE_API_KEY=" /opt/cin-hybrid/.env` → `1` (set); `grep -c "^ANTHROPIC_API_KEY="
/opt/cin-hybrid/.env` → `0` (not set). **Someone followed the mockup's instructions and set a key
under the wrong name — the Claude-powered agents (extractor, proposal writer, router, summarizer,
receipt vision) have been running on deterministic fallback only this whole time, with no visible
in-app indicator that anything was misconfigured.** Not fixed here — Mike's call whether to enable
real Claude-agent behavior on the live VPS, since that has real cost/behavior implications beyond
a simple bugfix. If wanted, the fix is a rename, not a new value:
`echo "ANTHROPIC_API_KEY=$(grep '^CLAUDE_API_KEY=' /opt/cin-hybrid/.env | cut -d= -f2-)" >>
/opt/cin-hybrid/.env` (run entirely on the server; nothing sensitive touches chat), then restart
`l2cos-portal.service`.

**Decided — CLOSED**: Mike's ruling, verbatim: **leave it on fallback for now.** No rename
performed; `ANTHROPIC_API_KEY` stays unset on the live VPS by choice, not oversight. The
deterministic-fallback behavior in `cin_lite`'s agents remains the live, intended behavior until
Mike decides otherwise — this is a considered decision, not an unresolved item, and should not be
silently re-flagged in any future review without new evidence changing the picture.

**Status: check requested of Mike this session (relayed command sent). Output not yet received —
still open as of this document's last update.**

### 3.5 `Level 5 Autonomous Intelligence System — Master Report`
Reviewed on title alone in the earlier CSV triage as high-priority, given the "Intelligence"
name. Direct read finds **zero mentions** anywhere in the file of Level 1 Transport, Dispatch,
`cin_lite`, `l1truck`, SAM.gov, freight, or broker — confirmed by targeted search, not assumed.
This is a generic report on building a local, self-hosted LLM hardware stack: architecture layers,
GPU/VRAM hardware tiers, memory requirements, cost breakdowns, and a snapshot of recommended
open-source models as of June 2026.
**Relevance**: none to this program's actual gaps. A title-level false positive — flagged
explicitly as ruled out, not silently dropped, so it isn't mistakenly re-flagged as high-priority
again later. Retains general value only if a future, separate decision is ever made about running
AI infrastructure locally rather than via API — unrelated to anything scoped in Dispatch today.

### 3.6 `Email Sweep Command Center`
A concept inbox-automation console built around the real account addresses `jax1313@outlook.com`
and `admin@l1truck.com` — sweep/forward/trash rules, duplicate-action prevention, Outlook token
refresh handling, a whitelist system. Demo activity feed references DAT Freight, Uber Freight,
and Samsara vehicle-alert emails — plausible, freight-relevant, but still fabricated demo content,
not real data (no backend, confirmed by the same connectivity check as every other file here).
**One item worth surfacing, explicitly unconfirmed**: the hardcoded demo activity feed includes a
GitHub notification referencing a repository `l1truck/fleet-mgmt` ("PR #247 merged: Fix GPS
tracking module"). This repo is not among any found or accessible to this session (`Dispatch`,
`dispatch-old`, `Hold`, `Test-Grounds`, `Jules`/`Jules-2`/`Jules-3`, `Claude`/`Claude-2`). Because
it appears inside the same fabricated demo dataset as this file's other placeholder activity
entries, it is **not** treated as confirmed to exist — noted only in case it means something to
Mike, per the No-Fabrication rule against asserting an unverified claim as fact.
**Relevance**: adjacent to, but distinct from, Track E's `DISPATCH_EMAIL_SECRET` finding — that
finding concerns `cin_lite`'s outbound HMAC-signed decision-action email links, not inbox triage.
This concept addresses a different problem (managing what arrives in the inbox) than the one
already flagged (securing what Dispatch sends out).

## 4. Ruling: Reference Material, Not Authoritative

Consistent with the standing ruling already applied to `Hold` and the five doctrine-review repos
(`DISPATCH_INTEGRITY_AND_DEPLOYMENT_VERIFICATION_MISSION_v1.md`, Section 6.3): all artifacts
reviewed in this document are candidate design material, not automatically authoritative over
anything already built in `jax1313-outlook/Dispatch`. None of them contain working code. None of
them are authorized for use as-is. If any of them are to inform an actual change to Portal or to
Operational Intelligence, that requires its own separate scope document and go-ahead, per this
program's standing practice — not adoption by inclusion in this note.

## 5. Where Real Refinement Could Plausibly Help

Recorded as candidates only, not scoped, not started:

- **Operational Intelligence UI concept** — both the CIN dashboard and the Planning Intelligence
  Dashboard could inform what a real Intelligence department screen looks like once the
  underlying data model exists (it currently doesn't — Intelligence Completeness Review: all 6
  concepts absent). Design-first, but the actual object model has to be built before a screen
  showing it means anything.
- **A real Portal ops/deploy console** — the `l1truck.com` file's VPS Management concept, if
  rebuilt with a genuine backend, could become an actual admin view of the sort Track A/B had to
  reconstruct by hand this session (deployment identity, `.env` variable state, service status).
  This is the one with the clearest, most concrete path to real usefulness, precisely because its
  reference data was already accurate.
- **A Manager-style decision console** — only relevant if and when Manager is reactivated, which
  it is not.

None of these are scoped. Mike decides whether any becomes its own mission.

---

Mike decides.
