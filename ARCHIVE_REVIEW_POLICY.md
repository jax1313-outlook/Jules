# ARCHIVE_REVIEW_POLICY.md

**Document Type:** Archive Review and Retention Policy  
**Program:** Dispatch  
**Owner:** Mike Zachary / Level 1 Transport  
**Status:** Proposed Policy / Architecture Hardening  
**Authority:** Mike Zachary remains final authority  

---

## 1. Purpose

Archive exists to preserve completed history, source records, decision records, audit bundles, completed packets, and retention material.

Archive is preserve-by-default.

Archive is not keep-forever-by-default.

Archive review is designed to keep useful history while preventing uncontrolled accumulation of stale prior versions.

---

## 2. Version Retention Rule

All documents and significant records are versioned under Dispatch Version Doctrine.

Dispatch retains automatically:

- Current Version
- Three Previous Versions

Example:

- Current: Ver: 10
- Retained automatically: Ver: 9, Ver: 8, Ver: 7
- Older than Ver: 7 enters Archive Review Queue

---

## 3. Archive Review Queue

Versions older than the current version plus three previous versions are placed into the Archive Review Queue.

Archive Review Queue does not delete items automatically.

Archive Review Queue prepares items for Mike's review.

---

## 4. Monthly Archive Review Report

Archive Review Queue items appear in the monthly report for Mike.

Each item should present a simple disposition control:

- Keep
- Delete

The report should show:

- object name
- version number
- current version
- age or relative history position
- last change summary
- reason for review
- suggested disposition if available

Mike decides.

---

## 5. Critical Record Rule

Critical records do not wait for the monthly report if human review is needed sooner.

Critical records may appear on the Monday Report.

Critical records may include:

- compliance-sensitive documents
- government packet records
- high-value opportunity records
- authority approval history
- broker/customer documents
- load or route records with business consequence
- security or PIN-related audit records
- records tied to active disputes, claims, or unresolved issues

---

## 6. Delete Rule

No Archive material may be permanently deleted without Mike approval.

Delete means an approved retention or purge action, not a silent system cleanup.

A delete action must record:

- who approved
- what was deleted
- version number
- reason
- timestamp
- related work item if any
- audit event

---

## 7. Keep Rule

If Mike selects Keep, the record remains in Archive and should be marked as retained by human decision.

A Keep decision should record:

- who approved retention
- version number
- reason if provided
- timestamp
- next review status if any

---

## 8. Relationship to Library

Archive does not create Library truth.

Archived material may be nominated for Library review.

A record may only become Library material through approved Library promotion workflow.

---

## 9. Success Standard

Archive Review Policy succeeds when Dispatch preserves useful history, prevents uncontrolled clutter, and gives Mike simple Keep/Delete controls without requiring manual file archaeology.

Archive Review Policy fails when old versions accumulate without review, critical records are buried, or deletion occurs without Mike approval.

---

## 10. Authority Closing

This policy does not authorize automatic deletion.

This policy does not approve purge actions.

Mike decides.
