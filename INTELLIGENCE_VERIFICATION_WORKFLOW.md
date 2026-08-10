# INTELLIGENCE_VERIFICATION_WORKFLOW.md

**Document Type:** Intelligence Verification Workflow  
**Program:** Dispatch  
**Owner:** Mike Zachary / Level 1 Transport  
**Status:** Proposed Workflow / Architecture Hardening  
**Authority:** Mike Zachary remains final authority  

---

## 1. Purpose

This workflow defines how facts become usable by Publisher and Library.

The purpose is to enforce the No Fabrication Rule using the existing Intelligence function rather than creating a new compliance agent.

Facts must be verified before Publisher uses them as truth.

Unknown remains Unknown.

---

## 2. Core Flow

Raw information enters Dispatch through approved intake.

The flow is:

Raw Information
→ Collection Layer
→ Parsing Layer
→ Intelligence Verification
→ Verified Fact or Rejected Fact
→ Library if approved
→ Publisher use if verified or approved

---

## 3. Verification Classifications

Intelligence may classify a finding as one of the following:

### 3.1 Verified

The fact is supported by source material or approved Library material.

Verified facts may proceed to Library review or Publisher use according to workflow.

### 3.2 Partially Verified

Some support exists, but the fact has uncertainty or missing support.

Partially verified facts require notation and may not be treated as fully approved truth unless Mike approves the specific use.

### 3.3 Unverified

Source support is missing.

Unverified facts may not enter Library as approved truth.

Publisher may not use unverified facts as factual claims.

### 3.4 Rejected

The fact is determined unreliable, contradictory, stale, unsupported, or wrong.

Rejected facts may be archived as history if useful, but may not be used as truth.

---

## 4. Publisher Use Rule

Publisher may consume:

- Verified facts
- Approved Library facts
- Partially Verified facts only when clearly labeled and approved for use

Publisher may not present Unverified or Rejected facts as truth.

---

## 5. Source Grounding Rule

Every significant factual claim should point to one of:

- Source record
- Approved Library record
- Intelligence Verification record
- Mike-approved exception

If no source exists, the output must be marked:

- UNKNOWN
- MISSING
- NEEDS SOURCE
- NEEDS REVIEW
- NEEDS MIKE DECISION

---

## 6. Intelligence Responsibilities

Intelligence verifies:

- source presence
- source relevance
- source conflict
- source age if known
- source consistency
- operational meaning
- uncertainty level
- whether the item should go to Library, Publisher, Archive, Manager, or Portal

Intelligence does not approve final truth by itself.

Intelligence recommends classification.

Mike or approved workflow controls final promotion where required.

---

## 7. Library Relationship

Verified facts may be nominated for Library promotion.

Library promotion requires approval.

Library stores approved reusable facts, not raw Intelligence guesses.

---

## 8. Archive Relationship

Rejected, stale, superseded, or unverified material may be archived for history if useful.

Archive storage does not make a fact true.

---

## 9. Portal Relationship

Portal cards involving facts should identify whether information is:

- Verified
- Partially Verified
- Unverified
- Rejected
- Unknown

This lets Mike evaluate the reliability of presented information quickly.

---

## 10. Success Standard

The workflow succeeds when every major factual claim used by Publisher or shown in Portal can be traced to source, verification, Library, or Mike-approved exception.

The workflow fails when Publisher uses unverified claims, Intelligence guesses are treated as truth, or missing facts are silently filled in.

---

## 11. Authority Closing

Intelligence verifies and recommends.

Library stores approved truth.

Publisher drafts from approved or traceable inputs.

Mike decides.
