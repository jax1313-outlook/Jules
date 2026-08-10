# DISPATCH_SPINE_OVERVIEW.md

**Program:** Dispatch  
**Document Type:** Spine Definition  
**Status:** Clean Repo Replacement Draft - Round 2  
**Authority:** Mike Zachary remains final authority  

## 1. Purpose

The Dispatch Spine is the deterministic operating backbone of Dispatch.

The Spine exists so routine system operation does not depend on probabilistic reasoning. It handles the boring but critical machinery that keeps Dispatch reliable.

## 2. What the Spine Handles

The Dispatch Spine handles:

- Workflow state
- Routing mechanics
- Queue management
- Validation
- Required field checks
- Storage operations
- Audit logs
- Event records
- Scoring formulas
- Automation triggers
- Status transitions

## 3. What the Spine Does Not Do

The Dispatch Spine does not:

- Reason about business meaning
- Draft documents
- Interpret solicitations
- Decide what Mike should do
- Approve anything
- Replace Manager
- Replace Portal
- Replace Mike
- Create doctrine
- Alter authority

## 4. Spine Relationship to Manager

Manager watches the office and protects attention.

The Spine executes deterministic routing mechanics and records workflow status.

Manager may recommend or explain. The Spine records, routes, validates, and tracks.

## 5. Spine Relationship to Portal

Portal displays Dispatch output to humans.

The Spine supplies structured state, statuses, cards, events, and outputs to the Portal.

Portal is the window. Spine is the machinery.

## 6. Spine Relationship to Cognitive Functions

The Spine calls cognitive functions only when cognition is actually needed.

Examples:

- Call Intelligence Analyst when interpretation is required.
- Call Publisher when drafting is required.
- Call Manager reasoning when prioritization, escalation, or attention filtering is required.

## 7. Spine First-Pass Components

Round 2 defines the Spine at concept level only.

First-pass components:

| Component | Purpose |
|---|---|
| State Registry | Track work item status |
| Routing Table | Define deterministic routing paths |
| Queue | Hold pending work |
| Validation Layer | Check required fields and schemas |
| Storage Layer | Save files, metadata, and records |
| Scoring Engine | Run formula-driven scores |
| Event Log | Record system events |
| Audit Trail | Preserve traceability |
| Automation Hooks | Trigger approved routine actions |

## 8. Success Standard

The Spine succeeds when routine work moves reliably without asking an AI to guess what should happen next.

The Spine fails when routine operation depends on conversational routing, hidden reasoning, or manual Mike intervention.
