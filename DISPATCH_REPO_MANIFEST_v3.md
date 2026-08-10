# DISPATCH_REPO_MANIFEST_v3.md

**Document Type:** Active Repository Manifest  
**Program:** Dispatch  
**Status:** Current Architecture Package Manifest  
**Authority:** Mike Zachary remains final authority  

---

## 1. Purpose

This manifest identifies the active Dispatch architecture, governance, and review files that should be loaded into current clean review repositories such as Claude-2 and Jules-2.

This manifest replaces older Round 2 manifest files for active review purposes.

The purpose is to prevent document drift, duplicate-version confusion, and review contamination from archived or superseded files.

---

## 2. Active Repo Rule

The active review repository should contain only current governing, architecture, specification, and review-control documents.

Old drafts, prior reviews, old agent-mesh files, obsolete context documents, prototype outputs, and historical experiments should remain outside the active review repo unless Mike explicitly includes them for historical comparison.

---

## 3. Current Active Files

The following files are the current active Dispatch review package:

1. `README.md`
2. `DISPATCH_CONSTITUTION_v3.md`
3. `CONTEXT_MASTER.md`
4. `ARCHITECTURE.md`
5. `MANAGER.md`
6. `PUBLISHER.md`
7. `INTELLIGENCE_ANALYST.md`
8. `COGNITIVE_FUNCTIONS.md`
9. `PORTAL_DESCRIPTION.md`
10. `DISPATCH_SPINE_OVERVIEW.md`
11. `DISPATCH_SPINE_SPEC_v1.md`
12. `ARCHITECTURAL_DISPOSITION.md`
13. `SUPERSESSION_MAP.md`
14. `REFINEMENT_ANALYST_REMOVAL.md`
15. `DISPATCH_DECISION_MATRIX.md`
16. `DISPATCH_FINAL_ARCHITECTURE_STRESS_TEST_PROMPT.md`
17. `DISPATCH_REPO_MANIFEST_v3.md`

---

## 4. File Roles

### 4.1 Governance and Authority

- `DISPATCH_CONSTITUTION_v3.md`  
  Current controlling Dispatch Constitution. Aligns the governing law with the current architecture.

- `SUPERSESSION_MAP.md`  
  Identifies which documents and concepts are current, superseded, retired, historical, or controlling.

- `ARCHITECTURAL_DISPOSITION.md`  
  Explains what happened to prior roles and concepts such as Dispatcher, Automation, Acquisition, Processing / Rules, Research Scout, and Refinement Analyst.

### 4.2 Context and Architecture

- `CONTEXT_MASTER.md`  
  Plain-language explanation of what Dispatch is, what Dispatch is not, and the business reality it serves.

- `ARCHITECTURE.md`  
  Current architecture model showing Authority, Presentation, Organizational, Deterministic, and Cognitive layers.

- `COGNITIVE_FUNCTIONS.md`  
  Defines bounded cognitive functions: Manager reasoning, Publisher drafting, and Intelligence analysis.

### 4.3 Organizational Functions

- `MANAGER.md`  
  Defines Manager as the event-driven and exception-driven Run Office function.

- `PUBLISHER.md`  
  Defines Publisher as the document and packet production function.

- `INTELLIGENCE_ANALYST.md`  
  Defines Intelligence Analyst as the cognitive interpretation function and includes load / route evaluation ownership.

- `PORTAL_DESCRIPTION.md`  
  Defines Portal as the required Presentation Layer and human-facing decision cockpit.

### 4.4 Deterministic Runtime

- `DISPATCH_SPINE_OVERVIEW.md`  
  Plain-language overview of the Dispatch Spine as deterministic runtime machinery.

- `DISPATCH_SPINE_SPEC_v1.md`  
  Build-readiness specification for the Spine, including schemas, states, transitions, routing, validation, audit, and approval-event requirements.

### 4.5 Retired Concepts and Review Control

- `REFINEMENT_ANALYST_REMOVAL.md`  
  Retires the standing Refinement Analyst role and replaces it with limited Quality Control Review where appropriate.

- `DISPATCH_DECISION_MATRIX.md`  
  Working matrix for sorting findings into KEEP, MODIFY, REJECT, and DEFER buckets.

- `DISPATCH_FINAL_ARCHITECTURE_STRESS_TEST_PROMPT.md`  
  Prompt used to stress test the final architecture before build authorization.

- `DISPATCH_REPO_MANIFEST_v3.md`  
  This active document inventory.

---

## 5. Files Not To Include In Clean Review Repos

Do not include the following in Claude-2 or Jules-2 unless Mike explicitly requests historical comparison:

- `DISPATCH_CLEAN_REPO_ROUND_2_MANIFEST.md`
- `DISPATCH_CONSTITUTION_v2.md`
- old Context Master versions
- old README variants such as `README_CLAUDE_2.md` or `README_JULES_2.md`
- old governance stack files from prior architecture phases
- old 11-agent mesh documents
- old review reports
- old program map proposals
- prototype scaffold code from prior reviewers
- archived experiments
- superseded agent charters
- historical draft files

---

## 6. Filename Cleanup Rule

The active review repo should use current-truth filenames, not version-history filenames, except where the file itself is a controlled numbered spec or Constitution.

Recommended active filenames:

- `DISPATCH_CONSTITUTION_v3.md`
- `DISPATCH_SPINE_SPEC_v1.md`
- `INTELLIGENCE_ANALYST.md`

Do not upload `INTELLIGENCE_ANALYST_v2.md` as an active filename. Rename its contents to `INTELLIGENCE_ANALYST.md` before loading into the clean repo.

Version history belongs in Archive, not in the active review file name unless the document is intentionally version-controlled as a formal specification.

---

## 7. Active Review Repo Structure

The active repo may remain flat for review clarity.

Recommended clean layout:

- `README.md`
- all active `.md` governing and architecture files listed in Section 3

Do not create unnecessary folders unless the repo later moves into implementation planning.

For review repositories, clarity matters more than folder complexity.

---

## 8. Promotion Path

Current review and build promotion path:

1. **Holding**  
   Local working collection of current architecture files.

2. **Claude-2 / Jules-2**  
   Clean independent review repositories.

3. **Decision Matrix**  
   Findings are sorted into KEEP, MODIFY, REJECT, and DEFER.

4. **Final Blueprint**  
   Approved KEEP items and corrected MODIFY items become the next blueprint.

5. **Test-Grounds**  
   Experimental build and prototype testing.

6. **Hold**  
   Stabilization and review lane.

7. **Dispatch**  
   Production-intent repository after Mike approval.

---

## 9. Review Readiness Checklist

Before running a stress test, confirm:

- Constitution v3 is present.
- Constitution v2 is not active.
- Context Master is current.
- Supersession Map is present.
- Architectural Disposition is present.
- Publisher has its own file.
- Intelligence Analyst includes load / route evaluation ownership.
- Dispatch Spine Spec v1 is present.
- Decision Matrix is present.
- Stress Test Prompt is present.
- No old program maps or old reviewer outputs are included.
- No duplicate README variants are included.

---

## 10. Authority Closing

This manifest is a document-control tool.

It does not authorize deployment.
It does not alter doctrine.
It does not approve implementation.
It does not merge code.

Mike decides.
