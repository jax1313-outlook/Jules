# DISPATCH_INTELL_LIBRARY_PUBLISHER_BUILD_PACKAGE_v1.md

Program: Dispatch
Owner: Mike Zachary / Level 1 Transport
Status: Final Build Package — Tri-Department Matrix Build
Deliverable: Cross-Repo Relationship Report (Build Command Section 9 / Constitution-governed
final deliverable set)
Date: 2026-08-11

---

## 1. Mission Recap

Per `05_DISPATCH_TRI_DEPARTMENT_MATRIX_BUILD_COMMAND.md`: build Intelligence, Library, and
Publisher simultaneously as one dependency chain (not three isolated repos), to integration-ready
status, merge-ready candidate status, and deployment-capable architecture — without merging,
deploying, or promoting anything. Stage 13 certified the previously implemented codebase only;
it did not certify Publisher, Library, Intelligence, or full architecture completion. This
package is the result of that build.

## 2. Repositories Built

| Repo | Role | Branch | Status before this build | Status after |
|---|---|---|---|---|
| `jax1313-outlook/l2-intelligence-agent.` | Intelligence | `claude/dispatch-tri-department-build-899qjm` | Deterministic pipeline existed (classifier/extractors/risk/routing); `models.py` was an empty placeholder — no structured object model, no service surfaces | Integration-ready: object model + service layer added, 32 tests passing |
| `jax1313-outlook/Library` | Library | `claude/dispatch-tri-department-build-899qjm` | Governance docs only (repo was previously used as "Repo-3" for blueprint assembly); no code | Integration-ready: `dispatch_library` package built from scratch, 24 tests passing |
| `jax1313-outlook/Publisher` | Publisher | `claude/dispatch-tri-department-build-899qjm` | Governance docs only (README described "Test-Grounds"); no code | Integration-ready: `dispatch_publisher` package built from scratch, 19 tests passing |
| `jax1313-outlook/Claude-3` | Architecture/governance | `claude/dispatch-tri-department-build-899qjm` | Doctrine and matrices | + shared object contracts, this build package, cross-repo walkthrough |

None of these repos were merged into `jax1313-outlook/Dispatch`. None were deployed. All work is
on the designated build branch, pushed to `origin`, not to `main`.

## 3. Dependency Chain As Actually Built

```
Intelligence                    Library                        Publisher
─────────────                   ───────                        ─────────
IntelligenceFinding      ──►     (consumed only via
OperationalConsideration          Library Candidate path,
SpecialRequirement                never directly as truth)
PublisherRequirement      ──────────────────────────────►      ReadinessPacket
                                                                (INTELLIGENCE-sourced
                                                                 required_items)
LibraryCandidate           ──►   submit_candidate()
                                  review_candidate()
                                  (external approval only)
                                        │
                                        ▼
                                  LibraryObject (CURRENT)  ──►   library_client.current()/
                                  PublisherRecipe                resolve_packet()
                                                                        │
                                                                        ▼
                                                                  Workspace
                                                                  ReadinessPacket
                                                                  PartsInventory
                                                                  MissingItemNotice
                                                                  DraftReviewPackage
                                                                  (external approval only)
                                                                        │
                                                                        ▼
                                                                  ArchiveHandoffPackage
                                                                  (blocked pre-approval)
```

This was verified live, not just designed on paper — see `integration/
CROSS_REPO_WALKTHROUGH_REPORT.md` and `integration/cross_repo_walkthrough.py`. A real
`IntelligenceFinding` was produced from a real example document, its derived `LibraryCandidate`
was reconstructed on the Library side with a field-set equality assertion (proving no drift), was
submitted and approved through Library's review gate, became `LibraryObject` truth, was pulled by
Publisher through a live adapter wrapping the actual `LibraryService`, correctly reported a
deliberately-missing item instead of fabricating it, and was blocked from Publisher
self-approval before succeeding under an external Mike-identified approval.

## 4. Shared Object Model & Interface Contracts

Canonical source: `DISPATCH_SHARED_OBJECT_CONTRACTS_v1.md` (this repo). Every department repo's
`models.py` implements those schemas field-for-field; the walkthrough report is the evidence that
this held in practice, not just in the contract document.

## 5. Cross-Repo Relationship Summary

| Relationship | Governed By | Enforced By |
|---|---|---|
| Intelligence → Publisher (Publisher Requirement) | System Relationship Matrix §4 | `intell.route_to_publisher()` only fires for Publisher-relevant routing queues; `ReadinessPacket` consumes requirement types without fabricating presence |
| Intelligence → Library (Library Candidate, never truth automatically) | System Relationship Matrix §11 Forbidden Movements | `route_to_library()` always returns `PENDING_REVIEW`; Library's `review_candidate()` requires a non-system, non-self `reviewed_by` |
| Library → Publisher (current truth, recipe resolution) | System Relationship Matrix §4/§8 | `library.current()` / `library.resolve_packet()`, consumed via Publisher's `LibraryClient` Protocol; missing items reported, never invented |
| Publisher → Archive (handoff only after approval) | Agent Relationship Matrix §3/§4; Constitution §15 | `create_archive_handoff()` raises unless `review.status == APPROVED_BY_MIKE` |
| Publisher self-approval | Build Command §4.3 Hard Rule | `approve_review_package()` rejects system identities as `approver_id` |
| No external send anywhere | Constitution §15; Build Command §4.3 | No networking import exists in the Publisher repo — verified structurally by `tests/test_no_external_send.py` (AST scan) |

## 6. What Was Not Built (see Known Gap Report for full detail)

- No persistence layer (Dispatch Spine integration) in any of the three repos — all reference
  implementations are in-process/in-memory, by design, since Spine is a separate build.
- No live Manager/Portal card generation from any department.
- No Publisher content-drafting layer (actual packet/letter prose) — Publisher's *assembly and
  approval gate* machinery is complete; document authoring requires the still-missing
  `publisher_recipes.json`, templates, and prototype source.
- No Archive department implementation (out of scope — separate build phase).
- No Security department implementation (out of scope — separate build phase).

## 7. Recommendation

All three repos are recommended as integration-ready candidates for the next stage of the
Repository Placement Plan's promotion flow: Claude Code review (this package) → Hold/Test-Grounds
→ Mike approval → Dispatch merge candidate. This package does not itself authorize any of those
next steps.

This is a recommendation only. No merge, deployment, or promotion is authorized by this
document. Mike decides.
