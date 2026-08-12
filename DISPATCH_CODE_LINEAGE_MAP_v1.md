# DISPATCH_CODE_LINEAGE_MAP_v1

Program: Dispatch
Status: **Synthesis complete. Reference document — reconciles naming and lineage, does not
authorize or change anything.**
Origin: Track C of `DISPATCH_INTEGRITY_AND_DEPLOYMENT_VERIFICATION_MISSION_v1.md`. Built from
evidence gathered and verified across this session — repo clones, file reads, checksums, and
live VPS verification (Tracks A and B) — not from memory or assumption.
Rule: No code changes authorized by this document. Every claim below cites where it was
verified; anything not directly verified is marked as such rather than asserted.

---

## 1. The Core Confusion This Document Resolves

This program has used at least seven names — L1-COS, SAM Sweeper, Hybrid v1, cin-hybrid, L2-COS,
Dispatch, Dispatch Matrix Group 1 — across at least twelve repositories and local folders, several
of which independently reused the same names for different things. Mike's own words apply
directly: "there are legacy names on these files. Design and building has taken faster than my
ability to keep a naming convention." This document is the reconciliation.

## 2. Timeline (Chronological, By Evidence Date)

| When | What | Where | Status now |
|---|---|---|---|
| Earliest | **L1-COS Prototype** — standalone Python package (`l1_cos/app.py`), raw `http.server`, own SQLite DB (`l1_cos.db`), SAM.gov sweep + `publisher_mvp.py` draft generation | Local folder, run via `py -m l1_cos.app` on Mike's Windows machine (uploaded as `L1COS_Prototype_v1_3_2_GOLD.zip`) | **Still actively run locally**, port 8000, via PowerShell. Confirmed by Mike: real SAM.gov sweeps, real Publisher drafts, records exist. |
| Jul 29 | **Hybrid v1** — minimal two-container Docker build (`hybrid-worker`, `hybrid-api`), deployed to the same VPS at `/opt/hybrid_v1` | Not a persistent git repo found this session — described only in an email transcript | Self-described in its own summary as "not the full multi-container architecture... no router/core/events/dashboard modules." Likely superseded; not found running on the VPS during Track A. |
| — (predates Jul 31) | **`dispatch-old`** (package name **`cin-hybrid`**, per its own `pyproject.toml`) — CLAUDE.md's Phases 1-2: `cin_lite/` core (acquisition, processing, rules, archive, control, proposal workflow) plus lightweight `manager.py`, `library.py`, `publisher.py`, `portal.py`, `dashboard.py` bolted directly onto it. `manager.py`'s ticket system is real and wired into `run.py`'s orchestrator — not dead code. | `github.com/jax1313-outlook/dispatch-old` | Reviewed in full this session. Superseded by the Phase 3 restructuring below — its `manager.py`/`library.py`/`publisher.py`/`portal.py`/`dashboard.py` did not carry forward. |
| Jul 31 | **`jax1313-outlook/Dispatch`** (package name **also `cin-hybrid`** — both repos independently chose this name) — CLAUDE.md's Phase 3: `cin_lite/` trimmed back to core responsibilities, a proper separate `portal/` Flask package (titled **"L2-COS Operations Portal"** in its own `base.html`), and a `dispatch/` freight-load engine. Commit `a753252`, "Add Library, Archive, Intelligence models and templates (#4)," is the version **currently live on the VPS** (Track A). | `github.com/jax1313-outlook/Dispatch` | **This is the production-intent repository** (Mike's explicit ruling). Everything this entire session built (Stages 3-5, the Approval Chain Safety Gate, Manager Preservation Decision, Stage 1, Stage 2, presentation-layer consolidation) is merged to its `main`, as of today — but not yet deployed; the live VPS is still frozen at `a753252`. |
| Aug 3-4 | **`Hold`** — "Dispatch Matrix Group 1": four lanes (Librarian, Manager, Receipt/IFTA, Reports), frozen contracts, 14-item Approval Register, all resolved Aug 4. **Verified zero application code** — every file under `src/`/`tests/`/`tools/` is an empty `.gitkeep`. | `github.com/jax1313-outlook/hold` | Seed-only. Mike's ruling: reference/candidate material, not automatically authoritative. Its Manager lane specifically: archived planning material, not grounds for reactivating the dormant Manager decision. |
| Aug 8 | **`Test-Grounds`** — a differently-numbered doctrine variant (`02`-`08` prefixed files), Agent Governance Law, Constitution v2 | `github.com/jax1313-outlook/test-grounds` | Docs only, no code. Reference material per the same ruling as `Hold`. |
| Aug 10 | **Five "clean review" repos** — `Jules`, `Jules-2`, `Jules-3`, `Claude`, `Claude-2`. Nine of ten baseline doctrine files are byte-identical across all five (confirmed by checksum) — a common bundle distributed for independent review, described by their own `SUPERSESSION_MAP.md` as "Round 2." `Jules-3`/`Claude-2` are the most elaborated round (Constitution v3, Spine Spec, Security/Auth spec, Decision Matrix, Stress Test Prompt). | `github.com/jax1313-outlook/{jules,jules-2,jules-3,claude,claude-2}` | Docs only, no code. Reference material, per the same ruling. |
| Pending | **Public site + Admin portal proposal** — static site proposed for Netlify hosting, built via an M365 Copilot Enterprise session (`Admin@l1truck.com`), plus a weekly SAM.gov Copilot task saving to OneDrive | Not a repo — described in an uploaded `.docx` | Per its own status table: hosting is "⏳ Your action," DNS not yet pointed. **Not live.** |
| Unclear | **Vanilla JS/HTML dashboard** — `index.html`, `layout.css`, `dashboard.js`, `builder.js`, `review.js`, `alerts.js`, `app.js` | Referenced only in a checklist `.docx`, alongside unrelated SAM.gov registration content | Location and current status genuinely unknown — flagged, not resolved. |

## 3. Naming Glossary

| Name | Refers to |
|---|---|
| **L1-COS** | The standalone local SAM.gov sweep tool (`l1_cos/app.py`), run via PowerShell on Mike's machine. Not a VPS-deployed service. |
| **SAM Sweeper** | Doctrine name for the same L1-COS function, per `CONSTITUTION.md`'s "Applies To" line. |
| **Hybrid v1** | The abandoned/superseded minimal Docker experiment from Jul 29. Not the same as the ongoing "cin-hybrid" project despite the similar name. |
| **cin-hybrid** | The actual `pyproject.toml` project name shared by *both* `dispatch-old` and `jax1313-outlook/Dispatch` — the source of the `/opt/cin-hybrid` directory name in every deployment script found this session. Not a third codebase. |
| **L2-COS / L2-COS Operations Portal** | The real Flask app's own self-declared title, confirmed in `jax1313-outlook/Dispatch`'s `portal/templates/base.html`. This is "the Loadboard portal" in Mike's terms — what's actually deployed on the VPS. |
| **Dispatch / Dispatch program** | The overall production-intent repository, `jax1313-outlook/Dispatch`, and this whole effort's umbrella name. |
| **Dispatch Matrix Group 1** | `Hold`'s separate, unstarted four-lane initiative (Librarian/Manager/Receipt-IFTA/Reports) — not the tri-department (Intelligence/Library/Publisher) work this session executed. |
| **Loadboard portal** | Mike's term for the VPS-deployed `l2cos-portal.service` (port 8080) — the real Flask `Dispatch` app. |
| **SAM portal** | Mike's term for the locally-run L1-COS tool (port 8000) — confirmed separate from the VPS. |

## 4. Authority Hierarchy (As Established, Not Assumed)

1. **`CONSTITUTION.md`** (Level 1 Transport Inc. master constitution) — supreme law per its own
   Article 0. Maintained outside every repo reviewed this session (per `Hold`'s own README);
   copied for reference into `dispatch-old`.
2. **`jax1313-outlook/Dispatch`** — the current production-intent repository (Mike's explicit
   ruling, this session).
3. **Everything else found this session** — `dispatch-old`, `Hold`, `Test-Grounds`, the five
   clean-review repos, the Netlify proposal, the vanilla JS dashboard — candidate architecture,
   scaffolding, and reference material. Not automatically authoritative over item 2 (Mike's
   explicit ruling, this session).

## 5. What's Actually Running Right Now (Cross-Reference To Tracks A/B)

- **`https://l1truck.com`** → `l2cos-portal.service` → gunicorn → `/opt/cin-hybrid`, a checkout
  of `jax1313-outlook/Dispatch` frozen at commit `a753252` (Jul 31) — ~12 days stale relative to
  `main` today, missing all of this session's work.
- **Port 8000, local, PowerShell-run** → `l1_cos/app.py` — real SAM.gov sweeps, real Publisher
  drafts, unrelated to the VPS.
- **Hybrid v1's Docker containers** — not confirmed running during Track A's `systemctl`/nginx
  checks; likely dormant or removed.
- **Everything else in Section 2** — not deployed anywhere, by its own documentation's admission.

Mike decides what happens with any of this next.
