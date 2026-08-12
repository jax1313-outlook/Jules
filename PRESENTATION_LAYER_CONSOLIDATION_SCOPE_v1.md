# PRESENTATION_LAYER_CONSOLIDATION_SCOPE_v1

Program: Dispatch
Status: **Scope only. No implementation authorized by this document.**
Origin: Named as a suggested next step in `DISPATCH_END_TO_END_DEPLOYMENT_PLAN_v1.md`'s "Beyond
Stage 2" section, grounded in `DISPATCH_STAGE6_OBJECT_FLOW_SCOPING_v1.md` Link 10's finding that
Portal already fragments "Card/Work Item/History" across three unrelated views on one page.
Sharpened into a concrete task ("start the presentation-layer consolidation").
Rule: No code changes authorized by this document. Scoping only, matching the discipline used
for Stage 1 and Stage 2 before their implementation go-aheads.

---

## 1. Confirmed Fragmentation (Fresh Evidence, Not Re-Derived From Memory)

Re-read `portal/routes/pages.py` this session to confirm current state:

- **`/archive`** (`archive_view()`, line 743) already renders three separate sources on one
  page: `portal/models/archive.py` sections, `cin_lite/archive.py`'s `list_contracts()`, and
  `dispatch/store.py`'s `list_retentions()` — clearly labeled, already reasonably consolidated
  as a single page. Lower priority for this pass.
- **Queue-like views are the clearest unsolved fragmentation**: `/publisher`
  (`publisher_view()`, line 709 — Publisher's own action queue), `/pipeline`
  (`pending_decisions()`, line 800 — `cin_lite`'s pending decisions), and `/queues` (`queues()`,
  line 833 — `cin_lite`'s `routing_history()` by filter) are three separate pages for "things
  awaiting action," with no shared view.
- **`/home`** (`home()`, line 24) already aggregates *counts* from every department
  (`publisher_count`, `pending_count`, `archive_count`, `intel_count`, `conflict_count`) into one
  dashboard — but renders zero actual *items* from the queue-like sources, only numbers. This is
  the natural extension point.

## 2. Explicit Boundary — What This Is Not

This is presentation-layer only, per Stage 6 Link 10's own framing ("a presentation-layer
consolidation, not a new data-flow"). It is **not** Manager: `MANAGER_ORCHESTRATION_REVIEW_v1`'s
Preservation Decision stands untouched — no orchestration, no routing, no decision logic, no
module resembling Manager gets built here, and nothing in this scope should be named "manager"
in any form. It is **not** Archive consolidation — Option A stands, `/archive`'s three sources
stay separate and owned by their existing departments. It does not touch storage or ownership
anywhere — every function called is an existing read.

## 3. Scope Questions

1. **Which fragmented views are in scope for this first pass?** Recommend: the queue-like
   fragmentation only (`/publisher`, `/pipeline`, `/queues`) — the clearest unsolved case.
   `/archive` is already reasonably consolidated; leave it alone.
2. **What does "consolidation" mean here — route restructuring, or composition?** Recommend:
   composition, not restructuring. Keep `/publisher`, `/pipeline`, `/queues` exactly as they are
   — bookmarkable, familiar, unbroken — and add a small composed preview elsewhere, rather than
   merging routes or changing URLs anyone currently relies on.
3. **Minimum viable target?** Extend `/home`'s existing aggregation from counts to a small
   preview: a few real items (not just numbers) from `publisher.get_queue()` (pending/draft
   actions), `pending.list_pending()`, and `routing_history(route_filter="HUMAN_REVIEW")` —
   turning three separate counts into one small "Attention Needed" panel with links out to each
   full page.
4. **Does this touch data/storage?** No — strictly read-composition over existing functions
   already used elsewhere in `pages.py`. No new writes, no new fields, no new storage.
5. **Where does new composition logic live?** `portal/helpers.py` (already the home for
   cross-cutting Portal helpers — `card_visual`, `format_score` are passed into `home.html` the
   same way today) or inline in `home()` itself. Explicitly not a new module resembling
   "manager.py" — kept small enough that a dedicated module isn't warranted, and named to avoid
   any confusion with the dormant Manager capability.
6. **Which routes/templates get touched?** Only `pages.py::home()` and `home.html`. `/publisher`,
   `/pipeline`, `/queues` (routes and templates) are untouched — no removal, no URL change,
   nothing existing breaks.
7. **What test proves it works?** A test asserting `/home` renders at least one real item's
   identifying text (not just a count) from each of the three sources when one exists in each —
   mirroring how existing home-page tests already assert counts.
8. **What does a real user actually see differently?** A new small panel on `/home` surfacing a
   few pending items across departments, with links to their full pages. This is the first stage
   this session that changes what appears on a page a user already looks at, rather than a
   backend-only change — flagged explicitly since Stage 1 and Stage 2 didn't carry this kind of
   visible change and didn't need this kind of sign-off.

## 4. What This Scope Does Not Include

Does not touch `/archive`, `/publisher`, `/pipeline`, or `/queues` themselves. Does not build any
orchestration, routing, or decision logic. Does not reopen Manager or Archive consolidation. Does
not restructure any existing route or URL. Does not go beyond the `/home` panel described in
question 3 without a separate future scope.

No implementation authorized yet. Awaiting approval of this scope, per this program's standing
practice, before any code changes.

Mike decides.
