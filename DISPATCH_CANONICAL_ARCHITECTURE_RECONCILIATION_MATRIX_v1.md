# DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1

Program: Dispatch
Owner: Mike / Level 1 Transport
Purpose: Determine which existing implementation becomes canonical before any Dispatch integration, merge, import, or replacement work.
Status: Decision-support matrix — ratified as the canonical record
Rule: No code changes. No merge. No deployment. Mike decides.

---

## 1. Executive Decision

The correct next step is not direct integration.

The correct next step is canonical reconciliation.

Reason:

Dispatch already contains independently-built implementations of Intelligence, Library, Publisher, and Archive. The tri-department build also contains independently-built implementations of Intelligence, Library, and Publisher. These implementations overlap, conflict, and in some cases solve different parts of the same problem.

Therefore, Dispatch must choose a canonical architecture before any code is merged or imported.

---

## 2. Canonical Reconciliation Matrix

| Area | Existing Dispatch Implementation | Tri-Department Implementation | Conflict / Gap | Canonical Decision | Keep | Replace | Merge / Adapt | Retire | Rationale |
|---|---|---|---|---|---|---|---|---|---|
| Intelligence | Existing Dispatch implementation in `portal/models/` according to reconciliation finding | New structured Intelligence repo with Finding, Operational Consideration, Special Requirement, Publisher Requirement, Library Candidate, Manager Decision Support Note | Different schemas and likely different object expectations | Tri-Department Intelligence becomes canonical object producer | Keep Dispatch intelligence only as legacy reference until mapped | Replace Dispatch intelligence schema where it conflicts | Adapt Dispatch-facing intake/output to consume tri-department objects | Retire conflicting duplicate models after migration | Tri-department Intelligence was built around shared object contracts and produces downstream Library and Publisher objects. |
| Library | `portal/models/library.py`, 6-section taxonomy, `add_record()` auto-stamps `status: "approved"` | New Library repo with taxonomy, versioned object registry, current resolver, candidate review path, human-ingestion path, recipe registry | Dispatch Library auto-approves all records, including machine-nominated candidates, which violates the no-fabrication / no-auto-truth doctrine | Tri-Department Library governance becomes canonical | Keep useful existing taxonomy labels as aliases or legacy categories | Replace auto-approval behavior for machine-generated candidates | Merge Dispatch Portal access/UI with tri-department Library service logic | Retire direct `add_record()` approval path unless restricted to human-ingested documents | Human-placed documents can be accepted, but machine-generated candidates need review/promotion controls. |
| Publisher Workflow | Existing Dispatch Publisher/action queue with `human_approval_required: True` flag | New Publisher repo with request/workspace/readiness/inventory/review/handoff pipeline and enforced self-approval block | Dispatch uses a flag that appears advisory, not an enforced gate | Tri-Department Publisher workflow becomes canonical | Keep Dispatch queue only if it becomes a front-end queue or adapter | Replace unenforced approval behavior | Merge Dispatch UI/queue with tri-department `approve_review_package()` style gate | Retire any publisher path that can hand off or archive without approval status check | Tri-department Publisher has stronger governance enforcement and no-self-approval protection. |
| Publisher Content Generation | `cin_lite/agents/proposal_writer.py` and `workflows/proposal.py` already provide proposal drafting | Tri-department Publisher has packet shell/governance but no content-generation layer | Tri-department Publisher governs packet assembly but does not draft content | Dispatch proposal writer becomes canonical content engine under Publisher governance | Keep `proposal_writer.py` and `workflows/proposal.py` | Do not replace with tri-department shell | Adapt proposal writer to operate as a Publisher content-generation worker | Retire none yet | Best hybrid: Dispatch already has content generation, tri-department Publisher supplies governance, readiness, review, and approval. |
| Archive | `cin_lite/archive.py` with SHA-256 verification, fail-closed tamper behavior, 26 dedicated tests; also `portal/models/archive.py` duplicate | Tri-department Publisher has archive handoff package logic, not full archive engine | Dispatch has duplicate Archive implementations. `portal/models/archive.py` appears weaker. Existing `archive_publisher_action()` lacks approval-status precondition | `cin_lite/archive.py` becomes canonical Archive engine | Keep `cin_lite/archive.py` | Replace `portal/models/archive.py` where behavior conflicts | Merge tri-department archive handoff gate before calling canonical Archive engine | Retire or downgrade `portal/models/archive.py` to adapter/view only | Strongest component found. Keep the fail-closed, hash-verified archive. Add approval gate before archive handoff. |
| Archive Handoff | Dispatch has live Publisher to Archive handoff with no approval-status precondition | Tri-department Publisher blocks archive handoff until approval | Dispatch may archive unapproved Publisher action | Tri-department approval gate becomes canonical precondition | Keep Dispatch archive storage mechanism | Replace direct unaudited handoff | Insert approval-status gate before `archive_publisher_action()` | Retire any no-gate handoff path | Archive should preserve approved history, not become an escape route around review. |
| Approval Model | Dispatch uses approval-like flags in Library, Publisher, Archive paths | Tri-department uses enforced external non-self approval checks | Dispatch flags may not be enforced | Tri-department enforced approval model becomes canonical | Keep flag labels only as UI/status indicators | Replace advisory-only gates | Merge approval status into Dispatch Portal/work item display | Retire paths where flag exists but is never checked | Governance must be structural, not decorative. |
| Shared Object Contracts | Dispatch uses existing local schemas in `portal/models/` | Tri-department uses shared contracts across Intelligence, Library, Publisher | Schemas are non-interoperable | Tri-department shared contracts become canonical cross-department contracts | Keep Dispatch models only as adapters during transition | Replace conflicting field models over time | Map existing Dispatch records to canonical object contract | Retire duplicate object definitions after migration | Cross-department object flow is the reason the tri-department build succeeded. |
| Taxonomy | Dispatch Library has 6 sections: company, broker, customer, location_intelligence, operations, intelligence | Tri-department Library has broader collection model | Taxonomies differ | Tri-department taxonomy becomes canonical, Dispatch taxonomy becomes legacy alias layer | Keep existing 6 labels as supported entry categories | Replace as source-of-truth taxonomy | Map 6-section taxonomy into canonical collections | Retire only after migration completed | Avoid breaking existing Dispatch data while moving toward stronger canonical Library structure. |
| Manager / Spine | No named Manager code found. Closest equivalents: `sandbox.py` work-item/card state machine and `conflict.py` Conflict Notice implementation | Tri-department build produces Manager Decision Support Notes but no Manager implementation | Manager exists doctrinally but not as named implementation | Dispatch `sandbox.py` and `conflict.py` become seed components for future Manager integration | Keep sandbox and conflict logic | Do not replace yet | Adapt tri-department outputs into Work Items, Cards, and Conflict Notices | Retire none yet | These are likely the real receiving surfaces for Manager behavior. |
| Portal | Dispatch Portal exists and has screens/cards/state | Tri-department build does not include Portal implementation | Tri-department objects need presentation layer | Dispatch Portal remains canonical presentation layer | Keep Portal | Do not replace | Adapt Portal to display canonical objects, approvals, missing items, and work items | Retire placeholder screens only after mapping | Portal is already the presentation surface. Departments should feed it, not replace it. |
| Proposal / Government Packet Flow | Dispatch has proposal drafting agent and workflow | Tri-department Publisher has governed packet assembly shell | Capabilities are complementary | Hybrid canonical model: Publisher governs, Proposal Writer drafts | Keep proposal writer | Do not replace | Attach proposal writer as content worker inside Publisher workflow | Retire standalone proposal generation only if it bypasses Publisher review | This is the cleanest path to real packet production without losing governance. |
| No-Fabrication Behavior | Some Dispatch paths may auto-approve or move records without review | Tri-department explicitly surfaces missing items instead of inventing content | Dispatch may not structurally prevent fabricated completeness | Tri-department no-fabrication behavior becomes canonical | Keep any existing missing asset checks, especially `library_missing_asset` in conflict logic | Replace silent or auto-complete behavior | Connect Missing Item Notice to Portal/Conflict Notices | Retire any path that fills missing facts automatically | Missing information must become a visible decision item, not generated filler. |
| Persistence / Runtime | Dispatch likely has the actual application runtime pieces | Tri-department repos were integration-ready candidates, not production persistence systems | Tri-department may be stronger logically but weaker operationally | Dispatch runtime remains canonical host | Keep Dispatch runtime | Do not replace runtime with department repos | Import/adapt department services into Dispatch integration branch | Retire none until import decisions are made | Dispatch is production-intent. Department repos are source packages. |

---

## 3. Canonical Winners By Department

| Department | Canonical Winner | Decision Type | Explanation |
|---|---|---|---|
| Intelligence | Tri-Department Intelligence | Replace / Adapt | Stronger structured object producer. Dispatch intelligence should be mapped or retired after compatibility review. |
| Library | Tri-Department Library | Replace governance, adapt taxonomy | Tri-department Library has stronger control over candidates, review, supersession, and current-object resolution. Dispatch taxonomy can be preserved as legacy labels. |
| Publisher | Hybrid | Merge | Tri-department Publisher should govern workflow, readiness, missing-item logic, review, and approval. Dispatch proposal writer should provide content generation. |
| Archive | Dispatch `cin_lite/archive.py` | Keep / Strengthen | Strongest component found. Preserve it as canonical Archive engine. Add tri-department approval gate before handoff. |
| Portal | Dispatch Portal | Keep / Adapt | Portal remains the user-facing presentation layer. It should consume canonical objects after integration. |
| Manager | Not yet canonicalized | Build later from existing seeds | Use `sandbox.py` and `conflict.py` as real Dispatch seeds for Work Items, Cards, and Conflict Notices. Do not invent Manager blindly. |

---

## 4. Hard Conflict List

| Conflict | Severity | Canonical Rule |
|---|---|---|
| Dispatch Library auto-approves every record | Critical | Machine-generated Library Candidates must not become approved truth without review/promotion. |
| Publisher approval flag exists but is not enforced | Critical | Approval must be enforced by code, not represented only as metadata. |
| Archive handoff lacks approval-status precondition | Critical | Publisher outputs must not be archived as completed history unless approved. |
| Duplicate Archive engines inside Dispatch | High | `cin_lite/archive.py` becomes canonical. `portal/models/archive.py` must become adapter/view or be retired. |
| Dispatch and tri-department schemas differ | High | Tri-department shared object contracts become canonical. Dispatch schemas are mapped to them. |
| Proposal writer exists outside Publisher governance | Medium | Proposal writer should become a Publisher content worker, not an independent bypass path. |
| Manager not implemented as named code | Medium | Do not fake Manager. Use existing Work Item/Card/Conflict components as seeds. |

---

## 5. Canonical Architecture Direction

The future Dispatch architecture should not be:

Dispatch wins all.

or:

Tri-Department wins all.

The correct architecture is selective reconciliation:

```
Dispatch Runtime
    +
Dispatch Portal
    +
Dispatch Proposal Writer
    +
cin_lite Archive
    +
Tri-Department Intelligence Objects
    +
Tri-Department Library Governance
    +
Tri-Department Publisher Workflow Gates
    +
Manager routing over Work Items / Cards / Conflict Notices
```

---

## 6. Recommended Canonical Import Strategy

**Stage 1: Stop all direct merge/import attempts**
No more git merge attempts between unrelated repos.

**Stage 2: Declare canonical winners**
Use this matrix to decide what survives.

**Stage 3: Create Dispatch-side integration branch**
Branch name suggestion: `dispatch/canonical-reconciliation-integration`

**Stage 4: Build adapters before replacing code**
Create object mapping adapters from Dispatch models into canonical shared contracts.

**Stage 5: Fix critical governance gaps first**
Priority order:
1. Library candidate approval gate
2. Publisher approval enforcement
3. Archive approval precondition
4. Archive duplication resolution
5. Proposal writer under Publisher governance

**Stage 6: Integrate object flow**
Target object flow:

```
Intelligence Finding
    ↓
Library Candidate
    ↓
Library Review / Promotion
    ↓
Publisher Requirement
    ↓
Publisher Workspace
    ↓
Proposal Writer / Content Worker
    ↓
Draft Review Package
    ↓
Human Approval
    ↓
Archive Handoff
    ↓
cin_lite Archive
    ↓
Portal Card / Work Item / History
```

**Stage 7: Only then consider Dispatch main**
No Dispatch main merge until reconciliation branch passes tests and Mike approves.

---

## 7. Do Not Touch Yet

Do not replace `cin_lite/archive.py`.

Do not delete `proposal_writer.py`.

Do not force tri-department Publisher to generate proposal content.

Do not let Dispatch Library auto-approve machine-generated candidates.

Do not wire Publisher directly to Archive without approval gate.

Do not build Manager until the receiving objects are canonical.

---

## 8. Final Recommendation

Canonical decision:

- Intelligence: Tri-Department wins as canonical object producer.
- Library: Tri-Department wins as governance and truth-management foundation.
- Publisher: Hybrid wins. Tri-Department governs. Dispatch proposal writer drafts.
- Archive: Dispatch `cin_lite/archive.py` wins as canonical archive engine.
- Portal: Dispatch Portal remains canonical presentation layer.
- Manager: Not ready for full build. First map tri-department objects into existing Work Item/Card/Conflict Notice surfaces.

Final status:

Do not integrate yet.

Create a Dispatch-side reconciliation integration branch only after Mike approves this canonical matrix.

Mike decides.

---

## 9. Editorial Note (Session Record)

This matrix was authored by Mike, building on the factual findings in
`DISPATCH_DEPARTMENT_RECONCILIATION_v1.md` (same repo). Its factual premises were cross-checked
against that report and match: the 6-section Library taxonomy, `add_record()`'s unconditional
`status: "approved"` stamp, `cin_lite/archive.py`'s SHA-256/fail-closed verification, the absence
of any named Manager/Spine module, and the rest all confirmed accurate against the actual code
read this session. This document adds the decision layer (canonical winners, severities, the
do-not-touch list, the staged import strategy) on top of that factual base.

A follow-up instruction pasted alongside an earlier copy of this matrix ("merge the Library
approval gate fix into Publisher and Archive") was identified by Mike as accidental and is not
part of this record. No code has been changed, merged, or deployed anywhere as a result of this
document. Per Section 8, Stage 3 and beyond (creating a Dispatch-side integration branch,
building adapters, applying the governance-gap fixes) require a separate, explicit go-ahead —
this document ratifies the decision, it does not itself authorize execution.

Mike decides.
