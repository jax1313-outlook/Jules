# DISPATCH_VERSION_DOCTRINE.md

**Document Type:** System-Wide Version Doctrine  
**Program:** Dispatch  
**Owner:** Mike Zachary / Level 1 Transport  
**Status:** Proposed Doctrine / Architecture Hardening  
**Authority:** Mike Zachary remains final authority  

---

## 1. Purpose

Dispatch shall use explicit version identification across the ecosystem to reduce cognitive load, improve recognition, prevent repeated review of materially unchanged information, and make operational changes visible at a glance.

Versioning is not only a Library feature.

Versioning is Dispatch doctrine.

---

## 2. Core Rule

Every significant Dispatch object should display a human-readable version marker.

Version numbers should be easier to interpret than timestamps when Mike is operating under time pressure.

A timestamp answers:

- When did this happen?

A version answers:

- Have I seen this before?
- How many times has this changed?
- Is this a repeat item?
- Is this worth looking at again?

Dispatch prioritizes version visibility for operational decision-making.

---

## 3. Display Standard

The standard display language is:

**Ver: X**

Examples:

- SAM Opportunity — Ver: 4
- Load Board Match — Ver: 9
- Carrier Packet — Ver: 3
- Broker Packet — Ver: 6
- Route Risk Review — Ver: 2
- Decision Card — Ver: 5
- Library Asset — Ver: 7
- Archive Record — Ver: 10
- Monday Report Item — Ver: 2

---

## 4. Operational Example

Preferred Portal display:

**HIGH VALUE MATCH**  
**Score: 97%**  
**Ver: 9**  
**Last Change: Rate Updated**

This is more useful operationally than requiring Mike to read a timestamp such as:

**Updated: 8/10/2026 10:41:15**

The version number tells Mike immediately that this item has appeared or changed multiple times.

---

## 5. System-Wide Application

Version Doctrine applies to:

- Portal cards
- Intelligence findings
- Library assets
- Archive records
- Publisher drafts
- packet drafts
- carrier packets
- broker packets
- shipper packets
- opportunity evaluations
- load board matches
- route reviews
- Manager reports
- Monday Reports
- monthly reports
- driver-facing documents
- customer or broker visibility artifacts

---

## 6. Version Meaning

Version number increases when there is a meaningful change to the object.

Meaningful changes may include:

- rate changed
- deadline changed
- route changed
- requirement changed
- document revised
- score changed
- source updated
- status changed
- Packet draft changed
- Library asset updated
- Archive review disposition changed

A version should not increase for meaningless system noise unless the object record itself materially changes.

---

## 7. Last Change Label

Where practical, version display should include a plain-language change label.

Examples:

- Last Change: Rate Updated
- Last Change: Deadline Changed
- Last Change: New Attachment Added
- Last Change: Score Increased
- Last Change: Route Risk Added
- Last Change: Mike Requested Revision

This allows fast triage without reading a full history log.

---

## 8. Relationship to Archive and Library

Library assets must retain version history.

Archive records must preserve completed versions according to the Archive Review Policy.

The current version and prior versions must be distinguishable.

---

## 9. Portal Rule

Portal should display version information prominently for review, decision, conflict, and authority cards.

Portal should not hide version information behind metadata panels when the version is operationally relevant.

---

## 10. Success Standard

Version Doctrine succeeds when Mike can determine within seconds:

- Is this new?
- Have I seen this before?
- How many times has this changed?
- What changed last?
- Is this worth opening again?

Version Doctrine fails when Mike must read timestamps, compare file names, or remember prior appearances to understand whether an item is worth attention.

---

## 11. Authority Closing

This doctrine does not authorize deployment.

This doctrine does not approve implementation.

This doctrine does not change Mike's final authority.

Mike decides.
