# DISPATCH_STAGE12_MANAGER_M4_MIRROR_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 12 Build Design — Phase M4 Cross-Repo Mechanism
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 and the same discipline every prior Stage 12 pass has followed.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Design the dispatch/docs/ mirror approach for M4" — resolving the open question `DISPATCH_STAGE12_MANAGER_M4_M6_BUILD_DESIGN_v1.md` §1 raised and deliberately did not answer unilaterally: how Manager can know Claude-3's stage status without becoming a live cross-repo integration.

**Correction to that prior document's own prose:** it referred to "Stage 2's `dispatch/docs/` mirror." The actual, correct location — confirmed by direct inspection — is `docs/` at the Dispatch repository root, not `dispatch/docs/`. This document uses the correct path throughout.

---

## 1. What M4 Actually Needs, Restated Precisely

`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §16: Manager should track current stage, dependencies, open questions, approval status, test status, walkthrough reports, blocked items, and next recommended stage. Manager may *recommend* the next stage. Manager may not *approve* it.

All of that state lives in two Claude-3 files: `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md` (per-stage detail) and `DISPATCH_BLUEPRINT_DECISION_LOG.md` (verbatim approval record). Both are long, prose-heavy governance documents — exactly right for a human to read, exactly wrong for code to parse. Attempting to have Manager parse Markdown prose to extract "is Stage 6 blocked" would mean Manager *interpreting* governance text to determine system state — closer to a judgment call than a deterministic read, and a real risk of silently misreading a stage's status as prose evolves. That's not a risk this design accepts.

## 2. Why Not a Live Integration

A live fetch (Dispatch code reaching out to GitHub at runtime to read Claude-3) was already ruled out in the prior design and stays ruled out here: it needs network egress and credentials to a private repository from inside what's supposed to be a narrow, read-only monitor, and it introduces a live external dependency into a Portal page that today works entirely offline. Nothing about M4's actual need (a periodic status check, not real-time sync) justifies that risk.

## 3. The Mirror: Extending, Not Inventing

Stage 2 already established the pattern this design reuses: `docs/` at the Dispatch repo root is a mirror of specific Claude-3 files, refreshed periodically, marked "do not edit here" (`docs/README.md`, current five files: `DISPATCH_CONSTITUTION_v3.md`, `DISPATCH_FINAL_BLUEPRINT_v1.md`, `SECURITY_AND_AUTHENTICATION_SPECIFICATION_v1.md`, `DISPATCH_SPINE_SPECIFICATION_v1.md`, `LIBRARY_INGESTION_RULE.md`).

**This design adds one new file to that same mirror: `docs/STAGE_STATUS.json`.** Not a copy of the prose documents — a small, structured, hand-authored snapshot containing only the fields Manager actually needs to read, refreshed at the same moments the Claude-3 tracking documents themselves are updated.

### Schema

```json
{
  "schema_version": 1,
  "last_synced": "2026-08-10T23:55:00Z",
  "synced_from": "jax1313-outlook/Claude-3: DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md, DISPATCH_BLUEPRINT_DECISION_LOG.md",
  "stages": [
    {
      "number": 12,
      "name": "Manager Reconciliation and Build",
      "status": "approved_executed_narrowed",
      "depends_on": [11],
      "blocked": false,
      "blocked_reason": null,
      "open_questions": [
        "M4: cross-repo read mechanism -- resolved by this design",
        "M5 Archive half: blocked on Stage 6 Archive Review Queue"
      ],
      "test_status": "2444 tests, 0 failures",
      "walkthrough_reports": [
        "STAGE12_MANAGER_FOUNDATION_WALKTHROUGH_REPORT_v1.md",
        "STAGE12_MANAGER_M4_M6_WALKTHROUGH_REPORT_v1.md"
      ]
    }
  ],
  "next_recommended_stage": 6,
  "next_recommended_reason": "Archive Review Queue unblocks Stage 6 itself and M5's Archive half."
}
```

**`status` vocabulary** (fixed, matching the exact language `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md` already uses for every stage, so the mirror never invents a new taxonomy):
`approved` · `approved_executed` · `approved_executed_narrowed` · `redefined_analysis_only_delivered` · `pending` · `blocked`

**JSON, not YAML — a deliberate, flagged choice.** YAML would read slightly more naturally by hand, but this codebase has zero YAML dependency today (`pyproject.toml`: `flask`, `paramiko`, optional `anthropic`, dev `pytest` — nothing else). JSON needs no new dependency; the stdlib `json` module is already used throughout `dispatch/`. Worth a look if Mike prefers YAML enough to accept a new dependency for it — not assumed here.

**One entry per stage, not just the current one** — so Manager can answer "what's blocked" and "what are the dependencies" across the whole plan, not only the most recent stage, matching §16's full requirement list.

### Refresh Discipline

**Not a new automated job.** Every stage action in this engagement so far has ended with the same two-step habit: update `DISPATCH_STAGE_LAUNCH_PACKAGES_v1.md`, then update `DISPATCH_BLUEPRINT_DECISION_LOG.md`, both in the same turn the stage action completes. This design adds a third step to that same existing habit: update `docs/STAGE_STATUS.json` in the Dispatch repository to match. No new agent, no scheduled sync, no cron job — the same manual discipline already governing every other tracking-document update, extended by one file. This is also why `next_recommended_stage`/`next_recommended_reason` are hand-authored fields, not computed: the recommendation is whoever is doing the stage work saying so explicitly, the same way every prior stage's "Findings" section has recommended a next step in prose — Manager surfaces that recommendation, it doesn't generate its own.

### Staleness

`last_synced` lets Manager flag (not block on) a mirror that's gone stale — e.g., if the newest `synced_from` timestamp is more than 14 days old, that's worth one low-priority Status note, not a Conflict. A stale mirror means "nobody has run a stage action recently," which is often just true and fine — not an error condition to escalate hard on.

## 4. Manager-Side Design

**New file: `dispatch/manager/stage_gate.py`.** Reads `docs/STAGE_STATUS.json` from disk (resolved relative to the repo root the same way `docs/README.md` is referenced elsewhere in this codebase). Read-only — this module never writes to `docs/`, never writes to any Spine table, never touches Claude-3 or GitHub in any way.

**Deliberately does not join the existing signal pipeline.** The six/seven signals Manager already handles (`signals.py`, `security_monitor.py`) are discrete, countable events — a stalled load either exists or it doesn't, a security pattern either crossed the threshold or it didn't — which is exactly what the classify → rank → dedup → materialize pipeline was built for. Stage status is not that shape: it's one standing snapshot, always present, that gets *replaced* on each refresh rather than *appearing once and needing dedup*. Forcing it through the existing per-signal machinery would mean inventing a fake "source_id" for something that isn't really an event, and either re-materializing a new Work Item on every single stage-tracking-file update (noisy) or never updating an existing one (stale, contradicts the whole point of tracking current status). **Simpler and more honest: a Stage Gate summary is computed fresh on every `/manager` page load and rendered in its own section, separate from the ranked signal cards.** No Work Item, no Portal Card, no dedup logic needed for this piece.

**Card level:** informational by default (comparable to Level 1/Status) — bumped to Level 2/Review only when the file reports at least one `blocked: true` stage, since a blocked stage is something Mike could plausibly unblock with a decision. Never higher than that; Stage Gate status alone is never a Level 3+ item — an actual blocking decision, if urgent enough to need one, would already be surfacing through one of Manager's other signal sources (e.g., a Conflict Notice or a Decision Card), not through this summary panel.

**Fails soft, always.** If `docs/STAGE_STATUS.json` is missing, malformed, or fails `schema_version` validation, `/manager`'s core function (the six/seven-source signal pipeline, already shipped and working) must render exactly as it does today — the Stage Gate panel simply doesn't appear, with no exception raised and no dependency introduced from the rest of `/manager` on this file existing. Manager's existing, proven functionality must never become fragile because of an optional file that a human forgot to refresh.

## 5. What This Design Does Not Do

- Does not give Manager (or anything else) write access to Claude-3, ever, in any form.
- Does not auto-generate the mirror file from prose — a human (or Claude, acting on Mike's explicit stage-approval instructions, exactly as today) writes it by hand, the same way every other governance record in this system is written.
- Does not let Manager approve, recommend-and-execute, or otherwise act on any stage transition — `next_recommended_stage` is read and displayed, never acted on.
- Does not resolve M5's Archive half — a separate, still-blocked item, untouched by this design.

## 6. Files In Scope (Future Build, Not Authorized By This Document)

| File | Action |
|---|---|
| `docs/STAGE_STATUS.json` | New — hand-authored initial snapshot, refreshed going forward per §3's discipline |
| `docs/README.md` | Modify — document the new file, matching the existing five-file listing's style |
| `dispatch/manager/stage_gate.py` | New — read-only parser + summary builder, per §4 |
| `portal/templates/manager.html` | Modify — add the separate Stage Gate panel, additive only |
| `tests/test_manager_foundation.py` | Modify — missing-file/malformed-file fail-soft tests, blocked-stage card-level bump test, structural guard confirming zero writes to `docs/` |

## 7. Test Plan (For a Future Build)

- Well-formed file with no blocked stages → Status-level summary panel renders, no crash.
- Well-formed file with ≥1 `blocked: true` stage → Review-level summary panel, blocked stage(s) named.
- Missing file → `/manager` renders exactly as it does today (verified against the current, already-tested signal-pipeline output), no exception, no Stage Gate panel.
- Malformed JSON / wrong `schema_version` → same fail-soft behavior as missing file.
- Structural guard: `stage_gate.py` contains no file-write call anywhere (`open(..., "w")`, or any `docs/`-path write).

## 8. Stop/Go (For a Future Build)

Go once fail-soft behavior is proven (the existing, shipped Manager pipeline must be provably unaffected by this file's presence or absence), the blocked-stage card-level rule is confirmed, and a live walkthrough shows the panel rendering correctly against a real, hand-authored `docs/STAGE_STATUS.json` reflecting this plan's actual current state.

Mike decides.

---

*End of DISPATCH_STAGE12_MANAGER_M4_MIRROR_DESIGN_v1.md.*
