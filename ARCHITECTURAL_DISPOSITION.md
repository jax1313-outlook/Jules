# ARCHITECTURAL_DISPOSITION.md

**Program:** Dispatch  
**Document Type:** Architectural Disposition Register  
**Status:** Clean Repo Replacement Draft - Round 2  
**Authority:** Mike Zachary remains final authority  

## 1. Purpose

This document explains what happened to prior Dispatch roles, components, or concepts that no longer appear as organizational functions in the clean Round 2 architecture.

No component should silently disappear.

## 2. Current Organizational Functions

The current organizational functions are:

- Manager
- Publisher
- Intelligence Analyst
- Library
- Archive
- Portal

Portal is the Presentation Layer. Library and Archive begin as deterministic services. Manager, Publisher, and Intelligence Analyst include cognitive functions where cognition is useful.

## 3. Disposition Register

| Prior Element | Status | Disposition |
|---|---|---|
| Research Scout | Removed from Dispatch architecture | Separate external discovery program. May feed material into approved intake paths. No Dispatch authority. |
| Refinement Analyst | Retired | Replaced by invoked-only Quality Control Review when needed. No standing adversarial agent. |
| Dispatcher Agent | Not used | Dispatch is the platform name. Future load or route reasoning may exist, but not under Dispatcher Agent naming. |
| Automation Agent | Removed as cognitive role | Reassigned to deterministic Dispatch Spine automation triggers and hooks. |
| Acquisition Agent | Removed as cognitive role | Reassigned to deterministic Intelligence collection and intake layer. |
| Processing / Rules Agent | Removed as cognitive role | Reassigned to deterministic parsing, scoring, validation, and rules modules. |
| Controlled Aggression Agent | Not used | Controlled aggression is urgency and review posture, not a standing role. |
| Generic Improvement Bot | Deferred | May be reconsidered later as a recommendation-only improvement process, not self-modifying authority. |

## 4. Important Clarifications

### 4.1 Dispatcher Naming

Dispatch is the software/platform identity.

Do not create a cognitive role named Dispatcher Agent in the current clean architecture. If load or route reasoning is needed later, name it according to its actual function, such as Load Evaluation or Route Position Support.

### 4.2 Automation

Automation remains important, but it is deterministic machinery, not a cognitive agent.

### 4.3 Acquisition

Acquisition remains important, but it is collection and intake machinery feeding Intelligence. It is not the Intelligence Analyst.

### 4.4 Rules and Processing

Rules and processing remain important, but formulaic scoring, deterministic parsing, required field checks, and validation belong to the Dispatch Spine.

## 5. Success Standard

This disposition is successful when reviewers can clearly tell what is current, what is retired, what is reassigned, and what is outside Dispatch.
