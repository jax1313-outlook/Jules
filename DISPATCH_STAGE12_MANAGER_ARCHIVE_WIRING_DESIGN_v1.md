# DISPATCH_STAGE12_MANAGER_ARCHIVE_WIRING_DESIGN_v1.md

**Program:** Dispatch
**Document Type:** Stage 12 Build Design — Wiring Manager to the Archive Review Queue (completes M5)
**Owner:** Mike Zachary / Level 1 Transport
**Status:** Design only. No code written yet. Requires "Approve design" before implementation, per `DISPATCH_CONSTITUTION_v3.md` §20 and the same discipline every prior build in this plan has followed.
**Authority:** Mike Zachary remains final authority. AI decides nothing.

**Responds to:** "Wire Manager to the new Archive Review Queue" — the follow-on task both `DISPATCH_STAGE6_ARCHIVE_BUILD_DESIGN_v1.md` and the Stage 12 tracking explicitly deferred once Stage 6's Archive Review Queue shipped (`portal/models/archive.py::list_review_queue()`, `jax1313-outlook/Dispatch` commit `9a9889b`).

---

## 1. What This Completes

`DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §11 defines Manager's relationship to Archive: *"Archive review needs — once the Archive Review Queue exists (a future build), Manager prepares an Archive Review Card **per item**, Keep/Delete choice presented to Mike, never decided by Manager."* The Archive Review Queue now exists. This design wires it in as an eighth signal source, completing the Archive half of Phase M5 that Stage 12's second build pass (M5 IFTA half + M6) explicitly left open pending this exact prerequisite.

## 2. Per-Item, Not Aggregated — Following Doctrine's Own Language, Flagged As A Real Tradeoff

The buildout design's Portal Card Model (§7) lists "Archive Review Card," card level 2, source trigger "Archive Review Queue entry" (singular), and §11 says "per item" explicitly. This design follows that literally: each Archive Review Queue item becomes its own signal, flowing through the exact same classify → priority → dedup → materialize pipeline as the other seven sources — no new aggregation module, no day-keyed summary card (unlike `security_monitor.py`, where aggregation was necessary because a security *pattern* only exists as a relationship across multiple raw events; an Archive Review Queue item is already one discrete, addressable thing, same as a stalled load or an open exception).

**The tradeoff, named rather than silently decided:** if the queue ever grows large, this produces one card per item, all landing at the same priority tier. Manager's own ranking already sorts everything by tier — Archive/cleanup items land at Tier 7, below anything more urgent — so this isn't a *ranking* problem, but it could become a *volume* problem on the `/manager` page itself if the queue grows into the hundreds. No cap or aggregation is proposed here, because doctrine explicitly calls for per-item cards and the current queue is realistically small (items only enter it after 180 unreviewed days). If volume becomes a real issue later, that's exactly the kind of thing to solve in a future enrichment/pagination pass, not something to prematurely design around now against doctrine's explicit instruction.

## 3. A Bug Found Before Writing Any New Code

`dispatch/manager/classify.py`'s `_CARD_LEVEL_BY_CLASS` maps `ARCHIVE: 1` — below `REVIEW_BAR_CARD_LEVEL = 2`. This class has been defined since the M2+M3 build but was never reachable by any signal source until now. Had this wiring gone in without correcting it, every Archive Review card would have silently classified below the review bar and never materialized — a real, previously-latent bug about to go live. **This design corrects `ARCHIVE` to card_level 2**, matching the buildout design's own Portal Card Model table exactly (Archive Review Card = Level 2), not a new judgment call.

## 4. Design

- **`dispatch/manager/signals.py`** — new source type `ARCHIVE_REVIEW_ITEM = "archive_review_item"`. Reads `portal.models.archive.list_review_queue()` (already read-only, already tested, already used directly by `/archive`'s own rendering). `source_id` = the archive record's own `id` (e.g. `ARC-LOA-0001`). Already-reviewed items are excluded automatically — `list_review_queue()` only ever returns `review_status == "pending"` items, so a Keep/Delete decision made through `/archive` naturally stops that item from being read as a new signal on the next Manager pass.
- **`dispatch/manager/classify.py`** — fixes `ARCHIVE: 1` → `ARCHIVE: 2` (§3). New classifier: every Archive Review item classifies uniformly as `ARCHIVE` — no severity sub-tiering, matching the buildout design's single fixed card level for this card type (unlike, say, stalled loads, which do split Status vs. Decision Needed by how far past threshold they are). Summary text explicitly points to `/archive`: *"In the Archive Review Queue, N days old. Review and record a Keep/Delete decision at /archive — Manager does not action this itself."*
- **`dispatch/manager/priority.py`** — new tier function: fixed **Tier 7** ("Library, Archive, or cleanup work"), the exact tier `DISPATCH_MANAGER_BUILDOUT_DESIGN_v1.md` §8 names for this category — not a judgment call the way some other tier assignments in this build have been.
- **`dispatch/manager/staff_report.py`** — no changes. The orchestrator remains source-type-agnostic, the same result every prior extension (Pass 2's IFTA exceptions + security patterns, Pass 3's Stage Gate) has already confirmed.
- **What Manager never does with this data:** call `portal.models.archive.mark_reviewed()`, or anything else that would record a Keep/Delete decision. Manager's card is read-only and points at the existing, Authority-gated `/archive` page — it never performs the action itself, matching every hard constraint this whole engagement has carried since the original Manager mission ("Manager does not approve... AI decides nothing").

## 5. Files In Scope

| File | Action | Purpose |
|---|---|---|
| `dispatch/manager/signals.py` | Modify | Add `ARCHIVE_REVIEW_ITEM` source + collection via `list_review_queue()` |
| `dispatch/manager/classify.py` | Modify | Fix `ARCHIVE` card_level (1→2); add classifier + title/summary for the new source |
| `dispatch/manager/priority.py` | Modify | Add Tier 7 mapping for the new source |
| `tests/test_manager_foundation.py` | Modify | New tests — see §6, plus a regression test proving the `ARCHIVE` card-level fix (an Archive-classified signal now clears the review bar) |

No file under `portal/models/archive.py`, `portal/routes/api.py`, or any other already-shipped Stage 6/12 file is modified — this build only adds a new read path into Manager, it does not touch the Archive Review Queue's own mechanics.

## 6. Test Plan

- A pending, aged Archive Review Queue item is detected as a signal and correctly classified `ARCHIVE`, card_level 2 — clears the review bar (the direct regression test for §3's fix).
- An item already marked `kept`/`deleted` via `/archive` is correctly excluded from a fresh signal collection.
- Priority tier is exactly 7, every time, regardless of the item's age or section.
- Dedup: a second Manager pass over the same still-pending item does not create a duplicate Work Item; the card remains visible.
- Structural guard: `dispatch/manager/` never calls `mark_reviewed` anywhere.
- Portal rendering: the card appears on `/manager` with a summary pointing to `/archive`, and — matching the fixed closing sentence every Manager card carries — "This is a recommendation only. No action is authorized. Mike decides."
- Full regression suite re-run clean.

## 7. Walkthrough Requirements

Required, live, matching every prior build's convention:
1. Seed a backdated Archive record (as Stage 6's own walkthrough did), confirm it appears on `/manager` as an Archive-classified, Tier 7 card pointing to `/archive`.
2. Use `/archive`'s existing Keep/Delete action (Stage 6, unmodified) to resolve it; confirm a fresh `/manager` signal collection no longer detects it as a new signal, while its already-materialized card knowingly persists — the same accepted, already-documented limitation carried forward from every prior Manager pass ("no enrichment of existing Work Items"), not a new one.
3. Confirm no other Manager-produced card or the rest of `/manager`'s output changed.
4. Full regression suite re-run clean.

## 8. Stop/Go

Go once the `ARCHIVE` card-level fix is proven by test (an Archive signal actually clears the review bar), the read-only boundary against `portal/models/archive.py` is confirmed (no call to `mark_reviewed` anywhere in `dispatch/manager/`), and the live walkthrough shows a real, backdated Archive record correctly surfacing on `/manager` and correctly stopping once resolved through `/archive`.

Mike decides.

---

*End of DISPATCH_STAGE12_MANAGER_ARCHIVE_WIRING_DESIGN_v1.md.*
