# REFINEMENT_ANALYST_REMOVAL.md

**Program:** Dispatch  
**Document Type:** Retirement Notice and Replacement Doctrine  
**Status:** Clean Repo Replacement Draft - Round 2  
**Authority:** Mike Zachary remains final authority  

## 1. Decision

The Refinement Analyst role is retired from the Dispatch architecture.

The concept of review remains useful, but the dedicated Refinement Analyst role creates unnecessary complexity and risks turning review into an argument loop.

## 2. Controlled Aggression Clarification

Controlled aggression is not a standing doctrine requiring a permanent adversarial agent.

In Dispatch, controlled aggression means urgency, challenge pressure, and refusal to accept weak work when review is appropriate.

It is a review posture, not a full-time role.

## 3. Replacement Model

If review is needed, Dispatch may use limited Quality Control Review.

Quality Control Review is invoked by context. It is not a standing agent with authority.

Appropriate uses:

- Architecture review
- High-risk packet review
- Major doctrine review
- Deployment readiness review
- Drift review
- Critical government opportunity review
- High-value operational decision review

Inappropriate uses:

- Routine file movement
- Simple formatting
- Deterministic validation
- Every draft
- Every output
- Minor wording preference
- Low-risk status updates

## 4. Preferred Validation Method

Where possible, Dispatch should prefer deterministic validation over cognitive debate.

Examples:

- Schema validation
- Required field checks
- File existence checks
- Approval status checks
- Version checks
- Mathematical scoring checks
- Audit log checks

## 5. Success Standard

The removal succeeds when Dispatch avoids unnecessary argument loops while preserving strong review where it truly matters.
