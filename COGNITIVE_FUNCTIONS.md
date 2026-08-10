# COGNITIVE_FUNCTIONS.md

**Program:** Dispatch  
**Document Type:** Cognitive Function Design  
**Status:** Clean Repo Replacement Draft - Round 2  
**Authority:** Mike Zachary remains final authority  

## 1. Purpose

This document defines the cognitive functions of Dispatch.

Cognition is used only where reasoning, interpretation, drafting, judgment support, or analysis is needed.

Not every Dispatch function is an AI agent. Deterministic functions should be handled by code, schemas, queues, storage, validation, and workflow logic.

## 2. Core Cognitive Functions

Dispatch uses three primary cognitive functions:

- Manager reasoning
- Publisher drafting
- Intelligence analysis

These functions work with the Dispatch Spine and Portal. They do not replace the Dispatch Spine and do not replace Mike.

## 3. Manager Reasoning

Manager reasoning protects attention, interprets office state, identifies meaningful conflicts, prepares decision-ready cards, and helps coordinate work when judgment is required.

Manager reasoning is activated by scheduled reviews, workflow events, exception conditions, and Portal-mediated human actions.

Manager reasoning is not used for routine routing mechanics, file movement, storage, audit logging, or formula scoring.

## 4. Publisher Drafting

Publisher drafting assembles human-facing production materials from approved facts, source material, templates, and assigned requirements.

Publisher may draft packets, letters, reusable assets, customer materials, government packet sections, and production text.

Publisher may not approve facts, decide truth, submit documents, sign documents, change Library status, or bypass Mike approval.

## 5. Intelligence Analysis

Intelligence analysis interprets collected data, identifies operational meaning, detects risks, evaluates opportunity context, and routes useful insight.

Intelligence analysis is not basic scraping, file downloading, fixed parsing, formula scoring, database storage, or retention execution.

## 6. Boundaries

All cognitive functions must follow these boundaries:

- Recommend, do not decide.
- Draft, do not approve.
- Analyze, do not commit.
- Escalate, do not bypass.
- Explain uncertainty.
- Preserve source traceability.
- Respect role limits.
- Use Dispatch Spine for state, validation, storage, and routing mechanics.
- Use Portal for presentation.
- Defer final authority to Mike.

## 7. Success Standard

Cognitive functions succeed when they do the thinking deterministic systems cannot do.

They fail when they perform routine software tasks, create noise, or require Mike to manage the system manually.
