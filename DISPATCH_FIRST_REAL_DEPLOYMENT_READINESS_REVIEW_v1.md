# DISPATCH_FIRST_REAL_DEPLOYMENT_READINESS_REVIEW_v1

Program: Dispatch
Status: **Review only. No code changed.**
Origin: Mike asked for an end-to-end review of `jax1313-outlook/Dispatch` (commit `5274d47`,
now live on `l1truck.com` as of Aug 12's redeploy) — what has placeholder data, what needs
human-supplied information, and what needs templates created, ahead of first real (non-demo)
use. Four parallel research passes (config/secrets, placeholder/seed data, templates, Manager
module + a live dashboard discrepancy) against the local clone. Nothing was fixed — this is the
inventory Mike asked for; every "needs" item below is his call on priority and timing.

---

## 1. Needs Human-Supplied Information

These are documented in `.env.example` at the repo root, which is accurate and complete — no
undocumented credential dependency was found anywhere in `dispatch/`, `portal/`, or `cin_lite/`.

| Item | Env var(s) | Without it | To go live |
|---|---|---|---|
| SAM.gov API key | `DISPATCH_SAM_API_KEY` | Falls back to `cin_lite/sample_data/` (2 fake contracts). Logged to stdout each run — not silent. | Free signup at api.data.gov. |
| Anthropic API key | `ANTHROPIC_API_KEY`, `DISPATCH_MODEL` | All 4 content agents (summarizer, router, proposal_writer, extractor) return deterministic templated output, structurally identical in shape to real Claude output, **with no in-band flag distinguishing fake from real** — only visible via source review, not a UI badge. (The 5th, receipt vision, is honest: returns `{"available": false}`.) | Anthropic API credits + key. |
| SMTP relay | `DISPATCH_SMTP_HOST`, `_PORT`, `_USER`, `_PASSWORD` | Emails write to `.eml` files in `Archive/Outbox/` instead of sending — explicit, non-silent. | SendGrid/SES/etc. account. |
| Email HMAC secret | `DISPATCH_EMAIL_SECRET` | Defaults to the literal string `"dispatch-dev-secret"` — forgeable by anyone reading the source. **Warned only when SMTP is configured; zero warning if SMTP stays unconfigured**, which is the more likely first-deploy state. | Generate a random secret regardless of SMTP status. |
| Portal session key | `PORTAL_SECRET_KEY` | Defaults to hardcoded `"dev-portal-key-change-in-production"` — Flask session cookies forgeable. Already set correctly on the live VPS (Track E fix). | Random 64-char value (already done). |
| Company info | `DISPATCH_COMPANY_NAME/ADDRESS/PHONE/EMAIL`, `DISPATCH_MC_NUMBER`, `DISPATCH_DOT_NUMBER` | Template omits blank fields cleanly (no fake placeholder text) — but a rate confirmation sent to a real broker without an MC/DOT number is an incomplete legal document. | Mike's actual FMCSA-registered business info. |
| Load board API | `DISPATCH_LOAD_API_URL`, `DISPATCH_LOAD_API_KEY` | Falls back to `portal/sample_dispatch_data/` — see §2, this is the one fallback that's a real risk, not just a dev convenience. | A real load-board contract (DAT/Truckstop-style). |
| IFTA tax rate table | N/A — hardcoded in `dispatch/models.py:738-803` | Not placeholder junk — realistic, currently-plausible per-state/province diesel rates. But **no comment records what quarter/year they were pulled from**, and IFTA rates are republished quarterly. Wrong-but-plausible rates are the most dangerous kind of stale data, since nothing will flag them as wrong. | Not a one-time input — Mike needs to verify against the current official IFTA quarterly rate matrix before any real filing, and establish who updates it each quarter. |

## 2. Placeholder / Sample Data — Real Risk vs. Harmless

**Real risk — these are the *default* data sources, not obviously-fake demo screens:**
- `portal/sample_dispatch_data/` (2 fake loads, brokers "Southeast Freight Partners" /
  "National Trucking Solutions") is what actually renders on the live load board if
  `DISPATCH_LOAD_SOURCE` is never set — `dispatch/acquisition.py:27,51-55` →
  `portal/helpers.py:55-67`. The give-away details (`*.example.com` emails,
  `loadboard.example.com`) are subtle; the company names and rates read as plausible. **No "DEMO"
  banner anywhere in the UI.**
- `cin_lite/sample_data/` (2 fake SAM contracts) is the equivalent default for the SAM/contract
  pages absent `DISPATCH_SAM_API_KEY` — same lack of a visual demo indicator, only a stdout log.
- Action: before treating anything on the live site as real, explicitly confirm
  `DISPATCH_LOAD_SOURCE` / SAM key are set to real sources — this is worth checking on the VPS
  specifically now that it's live, since the redeploy didn't set either.

**Harmless:**
- `portal/data/` — not tracked in git, doesn't exist until first run, starts genuinely empty.
- `dispatch/notifications.py`'s `_SAMPLE_LOAD` fixture ("Acme Logistics") — only reachable from
  the admin email-template-preview page, never a live notification.
- `DEFAULT_SUSPECT_CONFIDENCE_THRESHOLD = 0.75` in `dispatch/services.py:1744` — explicitly
  commented as "Hold's own placeholder... not yet calibrated." Only affects which IFTA fuel
  purchases get *flagged* for review, not any filed number — worth calibrating with real data
  over time, not a launch blocker.
- No hardcoded fake data found in `portal/templates/` or served pages beyond the two sample
  directories above; no TODO/FIXME/lorem-ipsum anywhere in application code.

## 3. Templates — Better News Than Expected: Nothing Is a Stub

Every template inspected, including the ones that looked suspiciously small
(`publisher.html` at 105 lines, `intelligence.html` at 42) turned out to be a real, functional
view over working backend models — small because they're list/loop markup, not because content
is missing.

- **`rate_confirmation_print.html`** — fully env-driven (`{% if company.name %}` guards, no
  hardcoded business info), real freight boilerplate terms/signature blocks. **Only gap: no logo
  image** — not broken, just never attempted. Needs the company env vars populated (§1), not a
  template edit.
- **`email_templates.html` / `dispatch/notifications.py`** — 9 fully-written internal
  operational-alert templates (dispatched, exception, delivered, POD, archived, invoice,
  payment received/overdue, stalled), real copy, HMAC-signed action links, HTML + plain-text.
  **Gap: these are internal ops alerts only — there are no outbound broker/customer sales or
  outreach email templates.** If Mike wants those, that's a new feature, not a placeholder to
  fill in.
- **`publisher.html`, `intelligence.html`, `library.html`** — all real, all wired to working
  models (`portal/models/publisher.py`, `intelligence.py`). `library.html`'s
  `status-placeholder` CSS class is a real feature (flags a missing company asset like a W-9),
  not template placeholder text.
- **`login.html`** — no hardcoded fake branding, just the generic internal system name
  "L2-COS Operations Portal." Cosmetic question for Mike: keep the internal system name, or
  brand it with his own company name/logo?

## 4. Two Findings Outside the Original Three Questions

**The Manager module is not "built but unwired" — it's a design doc with no implementation at
all.** `docs/MANAGER.md` says so explicitly: *"authorizes no code, no route, no data model, and
no runtime behavior."* A repo-wide search found zero Manager class/route/template — the only
related real code is `conflict.check_library_assets()`, which exists and is tested but has no
call sites anywhere. Activating it is not a flip-a-switch; it requires Mike's explicit
authorization to actually build against `MANAGER.md`'s Section 4 design, because there's no
route to flip yet.

**The 95-conflicts-vs-flat-sandbox pattern flagged after the redeploy is a confirmed bug, not
expected behavior.** The dashboard's count is *unresolved* notices
(`conflict.get_unresolved()`), and a resolve path exists and works end-to-end
(`conflicts.html` → `/api/conflict/resolve` → `conflict.resolve_notice()`). The bug is on
creation: `conflict.create_notice()` (`portal/models/conflict.py:63-86`) has **no dedup check**
against existing notices for the same `sandbox_id` + `conflict_type` — unlike
`sandbox.create_entry()`, which dedupes by a deterministic `sid` and is why Sandbox stays flat.
Every refresh/sweep that re-detects the same missing field on the same load creates a brand-new
`CN-####` record, even if an identical one was already resolved earlier. Over ~2 weeks of
repeated sweeps, that's unbounded duplicate accumulation — this is a real, fixable bug, not a
permanent-log-by-design pattern. Not fixed here; flagging for Mike's call on priority.

---

## 5. Summary For Go-Live

**Must do before treating the live site as real (not demo) data:** confirm `DISPATCH_LOAD_SOURCE`
and the SAM data source are pointed at real sources, not the sample directories — this wasn't
part of the Aug 12 redeploy and needs an explicit check.

**Must do before sending a real document to a real counterparty:** populate the
`DISPATCH_COMPANY_*` / MC / DOT env vars.

**Must do before real users hit it over the open internet with email links in play:** set
`DISPATCH_EMAIL_SECRET` to a random value regardless of whether SMTP is configured yet — the
current silent-insecure-default is the one item in this review with no warning at all.

**Must do before any real IFTA filing:** verify `IFTA_TAX_RATES` against the current quarter's
official matrix.

**Worth fixing but not blocking:** the conflict-notice dedup bug (§4).

**Deliberately not done, needs a decision not an engineer:** Manager module activation (§4),
outbound broker/sales email templates (§3), rate confirmation logo (§3).

Mike decides.
