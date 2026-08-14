# DISPATCH_DEPLOYMENT_CRITICAL_PATH_v1

Program: Dispatch
Status: **Active — governs prioritization for all future work until superseded.**
Origin: Mike's verbatim "BUILD CONTEXT UPDATE," delivered mid-session after the "larger
discussion" (multi-user auth, dashboard reset, IFTA data entry, broker/shipper email) had been
opened but not resolved. Recorded here in full because it redefines what "done" means for the
whole program, not just one department — the same reason `DECISION_LOG.md` exists.

## 1. The Update, Verbatim

> The convergence experience revealed that future department builds require:
> 1. Governance Context
> 2. Architecture Context
> 3. Integration Context
> 4. End-State Context
>
> All future Intelligence work should be designed knowing:
> - Dispatch exists
> - Archive exists
> - Acquisition exists
> - Portal exists
> - Library partially exists
> - Publisher partially exists
>
> Intelligence is being built as the final major missing department inside an existing
> ecosystem, not as a standalone product.
>
> IMPORTANT ARCHITECTURAL DECISION
>
> I have clarified the finish line for Dispatch. Dispatch is considered COMPLETE when I can run
> a real load through the system end-to-end. The goal is no longer to implement every
> enhancement idea before deployment. The goal is operational usability.
>
> For purposes of build prioritization:
>
> DEPLOYMENT CRITICAL
> - Intelligence
> - Library integration
> - Publisher integration
> - SAM configuration
> - SMTP configuration
> - Operational workflow completion
>
> NOT DEPLOYMENT CRITICAL
> - Future enhancements
> - Quality-of-life improvements
> - Nice-to-have refinements
> - Multi-user expansion
> - Future Manager functionality
>
> When evaluating work: Ask "Does this prevent me from running a real load through Dispatch?"
> If yes: treat as priority. If no: record as enhancement backlog and continue toward
> operational completion.

## 2. What This Changes

Before this update, "what's left" was being tracked against the full contract shape from
`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1.md` — all six Intelligence concepts,
Library/Publisher's full target shape, Manager, multi-user auth, etc. That's now explicitly
**not** the finish line. The finish line is: a real load, run end-to-end, for real.

This also changes how Intelligence gets built. Every prior department build this session
(Intelligence's own extend-to-integration-ready pass, Library, Publisher) was scoped somewhat
independently, then reconciled against each other afterward — that reconciliation is what
surfaced the duplicate tri-department build in the first place
(`DISPATCH_TRI_DEPARTMENT_MATRIX_BUILD_RECONCILIATION_v1.md`). Mike's framing here is explicit
correction: Intelligence must now be designed *against* the existing ecosystem (Dispatch,
Archive, Acquisition, Portal real; Library/Publisher partial) from the start, not standalone and
reconciled later.

## 3. Reclassifying Everything Open From "The Larger Discussion"

Applying Mike's own test ("does this prevent running a real load through Dispatch end-to-end?")
to every item that was paused:

| Item | Classification | Why |
|---|---|---|
| Multi-user registration/recovery/login redesign | **NOT critical** — explicit ("Multi-user expansion") | A real load can run today under the single-Authority login already live. |
| Manager module | **NOT critical** — explicit ("Future Manager functionality") | Already 0% built by design; stays parked. |
| Dashboard reset/refresh button | **NOT critical** | Doesn't block running a load — the underlying duplicate-accumulation bug it was meant to work around is already fixed (PR #86). Backlog. |
| IFTA data-entry mechanism / rate-table currency | **NOT critical for running a load** — but flagged | Running a load doesn't require a correct quarterly IFTA filing. Real compliance risk if left unaddressed before an actual filing, just not on the load-execution critical path. Worth revisiting before quarter-end, not before first load. |
| SAM.gov API key | **CRITICAL** | On Mike's own list. Needs Mike's signup (I can't create the account) — can happen in parallel with engineering work. |
| SMTP account | **CRITICAL** | On Mike's own list. Same — needs Mike's signup, can run in parallel. |
| Intelligence (5 remaining contract concepts) | **CRITICAL** | Explicit — "the final major missing department." |
| Library integration | **CRITICAL** | Explicit. |
| Publisher integration | **CRITICAL** | Explicit, and includes the one confirmed break already found: `promote_to_candidate()` has no HTTP route. |

## 4. Open Question Before Building Starts

Intelligence is the largest single build item in the whole program (5 of 6 contract concepts
still fully absent) and is now explicitly required to be designed against the real existing
ecosystem using all four context categories Mike specified. Every governed-capability change
this session (IFTA phases 1-7) went through a launch-package proposal before implementation —
whether Intelligence gets the same treatment, given its size, is Mike's call, raised in chat
rather than assumed here.

Mike decides.
