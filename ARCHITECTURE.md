# ARCHITECTURE.md

**Program:** Dispatch  
**Document Type:** Clean Architecture Model  
**Status:** Clean Repo Replacement Draft - Round 2  
**Authority:** Mike Zachary remains final authority  

## 1. Core Architecture Statement

Dispatch is a governed digital office built on a deterministic Dispatch Spine with bounded cognitive functions attached only where reasoning, interpretation, drafting, or judgment support is required.

Dispatch is not an 11-agent mesh. Dispatch is not a free-roaming AI system. Dispatch is not a chatbot. Dispatch is not a fully autonomous operator.

Dispatch is a practical business system designed to reduce owner/operator cognitive load and produce human-useful deliverables.

## 2. Architecture Layers

```text
Authority Layer
    Mike Zachary

Presentation Layer
    Portal

Organizational Layer
    Manager
    Publisher
    Intelligence Analyst
    Library
    Archive

Deterministic Layer
    Dispatch Spine

Cognitive Layer
    Manager reasoning
    Publisher drafting
    Intelligence analysis
```

## 3. Authority Layer

Mike Zachary is final authority.

All final decisions, approvals, external submissions, business commitments, doctrine changes, and deployment approvals remain under Mike's control.

## 4. Presentation Layer

Portal equals Presentation Layer.

Portal is required because Dispatch must produce human-useful output.

Mike interacts with Dispatch through the Portal. Driver and external visibility views may be phased, but the architecture must preserve them.

## 5. Organizational Layer

The organizational layer defines business functions.

- Manager runs the office.
- Publisher drafts and assembles documents.
- Intelligence Analyst interprets collected data.
- Library stores approved reusable material.
- Archive stores completed history.

These are business functions, not necessarily all cognitive agents.

## 6. Deterministic Layer: Dispatch Spine

The Dispatch Spine is deterministic machinery.

It handles:

- State
- Routing mechanics
- Validation
- Storage
- Queues
- Scoring formulas
- Automation triggers
- Audit records
- Event records

The Spine should be reliable, auditable, quiet, and boring.

## 7. Cognitive Layer

Cognitive functions are used only where reasoning is required.

Primary cognitive functions:

- Manager reasoning
- Publisher drafting
- Intelligence analysis

Cognitive functions do not own deterministic routing, storage, scoring formulas, approval gates, or audit trail mechanics.

## 8. Deterministic vs Cognitive Separation

| Work Type | Owner |
|---|---|
| Final decision | Mike |
| Human-facing presentation | Portal |
| Workflow state | Dispatch Spine |
| Routing mechanics | Dispatch Spine |
| Required field validation | Dispatch Spine |
| Formula scoring | Dispatch Spine |
| Source collection | Sweeper or acquisition module |
| Parsing where structured | Parsing module |
| Meaning interpretation | Intelligence Analyst |
| Packet drafting | Publisher |
| Attention filtering | Manager |
| Completed history | Archive |
| Approved reusable assets | Library |

## 9. Manager Architecture

Manager is not a direct LLM router and not a direct Mike chat interface.

Manager is an office-control function that becomes active through scheduled reviews, workflow events, exception conditions, and Portal-mediated human actions.

Dispatch Spine performs deterministic routing mechanics. Manager performs cognitive attention protection and office coordination.

## 10. Intelligence Architecture

```text
Sweepers
    ↓
Acquisition
    ↓
Parsing and Extraction
    ↓
Scoring Engine
    ↓
Intelligence Analyst
    ↓
Manager / Publisher / Library / Archive / Portal
```

## 11. Library and Archive Architecture

Library and Archive begin as deterministic services.

Library stores approved reusable material.

Archive stores completed history and source records.

Cognitive assistance may be added later, but the base services must be reliable first.

## 12. Portal and Multi-User Reality

Portal is critical.

Portal must support the Mike cockpit. The architecture must preserve future driver, customer, broker, and shipper visibility where useful.

Portal is not optional because human-useful deliverables are the purpose of the system.

## 13. Removed or Reassigned Elements

The disposition of removed or reassigned elements is controlled by `ARCHITECTURAL_DISPOSITION.md`.

## 14. Document Authority

Current and superseded documents are controlled by `SUPERSESSION_MAP.md`.

## 15. Success Standard

Dispatch succeeds when it produces useful human deliverables, reduces Mike's cognitive load, preserves human authority, and makes Level 1 Transport more capable.

Dispatch fails when it becomes elegant machinery that Mike cannot see, use, trust, or benefit from.
