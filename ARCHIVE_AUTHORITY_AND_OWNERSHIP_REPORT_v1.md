# ARCHIVE_AUTHORITY_AND_OWNERSHIP_REPORT_v1

Program: Dispatch
Mission Type: Architecture Review and Boundary Reconciliation
Status: **Analysis only. No code changed. No branch created. No file touched, deleted, or
migrated. No implementation authorized by this document.**
Method: Every claim below is backed by a real grep/read against Dispatch `main`, performed this
session. Where a component has zero real producer, that is stated as a finding, not assumed.
Date: 2026-08-11

---

## Phase 1 — Archive Inventory

### ARCHIVE COMPONENT INVENTORY

**Component:** Portal Archive (`portal/models/archive.py`)
**Authority:** Portal-native decision/publisher/history archive. Backed by one flat JSON file
(`archive.json`, path from `get_archive_dir()`).
**Data Stored:** Five defined sections (`ARCHIVE_SECTIONS`): `load`, `decision`, `publisher`,
`location_history`, `broker_history`.
**Produced By:** `portal/routes/api.py` — `arc_model.archive_from_sandbox(entry)` (2 call sites:
`card_action()` on `PASS`, and `mark_inquiry_sent()`-adjacent flow at line 293); `arc_model.
archive_publisher_action(action)` (1 call site, `update_publisher_action()`, gated since the
Approval Chain Safety Gate fix).
**Consumed By:** `portal/routes/pages.py::archive_view()` (renders `sections` on `/archive`);
`portal/app.py` and `pages.py` (`total_count()` for a dashboard stat).
**Comments:** Only `load`, `decision`, and `publisher` sections have a real producer.
**`location_history` and `broker_history` are defined in `ARCHIVE_SECTIONS`/`SECTION_LABELS` but
have zero call sites writing to them anywhere in the codebase** — confirmed by grep for
`section="location_history"`/`section="broker_history"` across the entire repo, matching only
the definitions themselves. These two sections are dead code paths today: reachable in the
schema and rendered (as empty) on the Archive page, never populated.

---

**Component:** CIN-Lite Pipeline Archive (`cin_lite/archive.py`)
**Authority:** Canonical store for the government-contract-pursuit pipeline. Hash-verified
(SHA-256 sidecar per artifact), fail-closed on tamper (`ArchiveIntegrityError`). File-tree
storage under `ARCHIVE_ROOT` with subdirectories `Raw/Processed/Intelligence/Summaries/Routing/
Pending/Outbox/Proposals`.
**Data Stored:** Contract metadata, raw/processed contract payloads, rule-module intelligence
output, human-readable summaries, routing decisions, drafted proposals.
**Produced By:** `cin_lite/pipeline.py` (`make_id`, `store`, `record_routing` — the core
acquisition→processing→archive path); `cin_lite/workflows/proposal.py::trigger()`
(`store_proposal`).
**Consumed By:** `portal/routes/pages.py::archive_view()` (`cin_archive.list_contracts()`,
rendered as "DISPATCH Pipeline Archive"); `portal/routes/pipeline.py` (`list_contracts()`,
`load_artifact()` for the `/pipeline` and `/queues` pages); `cin_lite/email_delivery.py`.
**Comments:** 26 dedicated tests (`tests/test_archive.py`). The only component of the four with
active integrity verification.

---

**Component:** Pending Decision Staging (`cin_lite/pending.py`)
**Authority:** Not an archive itself — a pre-decision staging buffer. Notably, it physically
lives *inside* `cin_lite/archive.py`'s own directory tree (`archive.ARCHIVE_ROOT / "Pending"`),
which is almost certainly the component referred to as "additional archive-related storage used
by Dispatch workflows" in this mission's context — it is storage, it is archive-adjacent (shares
the archive's root path), but it is not itself a system of record for completed history.
**Data Stored:** Full context needed to complete a human decision later: contract, intelligence
output, summary, draft routing recommendation, flags.
**Produced By:** The pipeline, when a contract is routed to a human-decision queue (email
checkpoint).
**Consumed By:** `portal/routes/decisions.py` (loads the pending record when a human clicks an
email action link, then completes archival via `cin_lite.pipeline.resolve_decision()`).
**Comments:** Once a decision is made, the record's terminal state moves into
`cin_lite/archive.py` proper (`Routing/`, `Proposals/`, etc.) — this is a staging area with a
one-way handoff into the real archive, not a competing store.

---

**Component:** Dispatch Retention Archive (`dispatch/store.py`'s `retention` table, exposed via
`dispatch/services.py::archive_load()`/`list_retentions()`)
**Authority:** System of record for completed freight-load compliance/financial retention.
Relational (SQLite), not file-based — a different storage technology from all three above.
**Data Stored:** `RetentionArchive` (`dispatch/models.py`): `archive_id`, `load_id`,
`final_status`, `pod_package_id` (a *reference* into the separate `pod_packages` table, not the
POD data itself), `evidence_index` (references into the separate `evidence` table),
`financial_summary`, `archive_location`, `retention_status`.
**Produced By:** `dispatch/services.py::archive_load(load_id)` (single call site), itself invoked
from `portal/routes/dispatch_api.py::archive_load()` (line ~492-494) — a Portal API route
distinct from anything Publisher- or contract-pursuit-related.
**Consumed By:** `dispatch/services.py::list_retentions()` → `portal/routes/pages.py::
archive_view()` (rendered as "Dispatch Retention Archive").
**Comments:** `pod_packages`, `evidence`, `rate_confirmations`, `settlements`, `expenses`,
`activities`, `detention_events` are **separate sibling tables** in the same SQLite database
(confirmed via `dispatch/store.py::delete_load()`'s child-table list), each with its own create/
list functions in `dispatch/services.py`. Retention does not store POD/evidence data directly —
it stores a completion marker plus references into those tables. This means "POD records" and
"Retention records" are not the same system of record even within this one component (see Phase
2).

---

**Component:** Sandbox — Archive Candidates view (`portal/models/sandbox.py`, filtered)
**Authority:** None as an archive — this is **not archived data**. It is the live, still-mutable
`sandbox.json` store, filtered at render time (`portal/routes/pages.py::archive_view()`) to
entries whose `status` is `PASS`, `CLOSED`, `EXPIRED`, or `BOOKED`.
**Data Stored:** Same shape as any other sandbox entry (`STATUSES`, `card_data`, `intelligence`,
`decision`, `events`, etc.) — nothing archive-specific.
**Produced By:** `sandbox.create_entry()`/`update_status()`, same as every other sandbox record.
**Consumed By:** `archive_view()` for the "Sandbox — Archive Candidates" section.
**Comments:** The label is accurate and honest — "candidates," not "archive." This is a
correctly-scoped design choice (surfacing what *could* be archived), not a duplication bug.

---

**Component:** Operational Intelligence (`portal/models/intelligence.py`) — *not an archive,
included for ownership-boundary adjacency to `location_history`/`broker_history`*
**Authority:** Reusable, current, non-archival knowledge ("Experience becomes an asset," per its
own docstring). Six `INTEL_TYPES`: `location`, `broker`, `customer`, `route`, `position`,
`market`.
**Data Stored:** Free-text subject/content records with a `source` field and metadata.
**Produced By:** `portal/routes/api.py::create_inquiry()` — one automated call site
(`intel_type="broker"`, fired when an inquiry is drafted); `POST /api/intelligence/add` (a
generic human-facing route, any of the 6 types).
**Consumed By:** `portal/routes/pages.py::intelligence_view()` (`/intelligence` page).
**Comments:** Grep for `intel_type="location"` found **zero** producers — no code path, human or
automated, currently writes a `location` intelligence record, despite it being a defined type.

---

**Component:** Library (`portal/models/library.py`) — *not an archive, included for
ownership-boundary adjacency to `broker_history`/`location_history`*
**Authority:** Approved current reusable facts and production parts. Six `SECTIONS`: `company`,
`broker`, `customer`, `location_intelligence`, `operations`, `intelligence`.
**Data Stored:** Named records with content/metadata, `status` (now `approved`/`pending_review`/
`rejected` after the Approval Chain Safety Gate fix — see that branch).
**Produced By:** `POST /api/library/add` only — a generic human-facing route. **Zero automated/
agent-driven call sites found anywhere in the codebase** for any Library section, confirmed by
grep.
**Consumed By:** `portal/routes/pages.py::library_view()` (`/library` page);
`get_available_company_assets()`/`get_missing_company_assets()` (Conflict Notice checks,
Publisher action creation).
**Comments:** Everything in Library today is human-placed by construction (there is no other
entry point) — directly relevant to why the Approval Chain Safety Gate's `submitted_by="human"`
default was safe to make the unconditional default.

---

**Component:** Sync Engine (`sync/engine.py`, `SyncEngine` class) — *cross-cutting transport,
included because it can write directly into the `archive`/`library`/`intelligence` local
directories from an external source*
**Authority:** None over content — a pull-only file transport/staging mechanism (own docstring:
"core pull-only synchronization logic"), not a system of record. Defines `SYNC_SUBDIRS`
including `library`, `archive`, `publisher`, `locations`, and six `intelligence/<type>`
subdirectories, mirroring the domain taxonomy of the components above almost exactly.
**Data Stored:** Nothing of its own — staging/conflict/log/report directories plus whatever it
mirrors from the configured remote transport into the local per-domain folders.
**Produced By:** External transport source (configuration-dependent — `sync_config.example.json`,
not investigated in depth this pass).
**Consumed By:** Local `staging` → `_validate_record()` → `_commit_record()` into the matching
local data type folder; conflicts go to `_save_conflict()`.
**Comments:** Flagged, not fully investigated — if this mechanism is active in a given
deployment, it is a fifth entry point capable of writing into Library/Archive/Intelligence data
from outside the Portal application entirely. Whether it is currently wired to a live transport
was not determined this pass. Recommend a dedicated look before treating any consolidation
decision as complete, since this pass optimized for archive-labeled components specifically.

---

## Phase 2 — Record Ownership Matrix

### RECORD OWNERSHIP MATRIX

**Record Type:** Publisher actions
**System of Record:** `portal/models/publisher.py` (live queue) → `portal/models/archive.py`
`publisher` section (completed).
**Why:** Only component with a producer for Publisher-shaped data; matches the Approval Chain
Safety Gate's scope exactly.
**Evidence:** `portal/routes/api.py::update_publisher_action()`, `archive_publisher_action()`.

**Record Type:** Library records
**System of Record:** `portal/models/library.py`.
**Why:** Sole store for approved reusable facts; no other component claims this data.
**Evidence:** `SECTIONS` list, `POST /api/library/add`/`/library/review`.

**Record Type:** Intelligence products (operational, reusable)
**System of Record:** `portal/models/intelligence.py`.
**Why:** Sole store for the six `INTEL_TYPES`; conceptually distinct from Library (raw/ongoing
notes vs. approved facts) even though `broker`/`location`-shaped content could plausibly belong
in either — see Phase 3.
**Evidence:** `INTEL_TYPES`, `create_record()` call sites above.

**Record Type:** Manager decisions
**System of Record:** **No dedicated store exists.** The closest real data is `sandbox.py`'s
`decision` field (set inline on a sandbox entry) and `cin_lite`'s routing-decision agent output
(`agents/router.py::decide()`, persisted as part of the pending/archive payload, not as its own
record type).
**Why:** No named "Manager" module exists in Dispatch (confirmed in the earlier reconciliation
pass and re-confirmed this pass — no `manager.py` anywhere).
**Evidence:** `sandbox.py::create_entry()`'s `decision` parameter; `cin_lite/agents/router.py`.

**Record Type:** Contract pipeline history
**System of Record:** `cin_lite/archive.py`.
**Why:** Purpose-built, hash-verified, and the only component with this domain's actual shape
(`Raw/Processed/Intelligence/Summaries/Routing`).
**Evidence:** `cin_lite/pipeline.py::process_contract`-equivalent flow (`make_id`/`store`/
`record_routing`).

**Record Type:** Email approval history
**System of Record:** Split across two places, by design: the pending decision context lives in
`cin_lite/pending.py` until resolved; the resolved outcome (action taken, whether it matched the
recommendation) is written via `cin_lite/archive.py::record_routing()`.
**Why:** This is the same pipeline as "Contract pipeline history" — email approval is how a
human resolves a pending pipeline decision, not a separate domain.
**Evidence:** `portal/routes/decisions.py::process_decision()` → `cin_lite.pipeline.
resolve_decision()`.

**Record Type:** Freight loads
**System of Record:** `dispatch/store.py`'s `loads` table.
**Why:** The `dispatch/` subsystem ("Dispatch Data Engine... canonical data models for the seven
dispatch objects," per `dispatch/models.py`'s own docstring) is purpose-built for this domain;
nothing else in the repo models a freight load.
**Evidence:** `dispatch/models.py`, `dispatch/store.py`.

**Record Type:** POD records
**System of Record:** `dispatch/store.py`'s `pod_packages` table — **not** the `retention` table.
**Why:** `RetentionArchive.pod_package_id` is a reference field, not the POD data itself; the
actual POD content lives and is queried (`list_pods()`) separately.
**Evidence:** `dispatch/store.py::delete_load()`'s child-table list; `dispatch/services.py::
list_pods()`.

**Record Type:** Compliance records
**System of Record:** No single owner — split across `dispatch/store.py`'s `exceptions` table
(load-level compliance flags) and `cin_lite/rules/*.py` output (contract-level compliance
findings: `cyber_compliance.py`, `set_aside.py`, etc.), which are two different domains
(freight-operations compliance vs. federal-contract-eligibility compliance) that happen to share
the word "compliance."
**Why:** No investigation found a unifying "compliance" store; each domain's compliance concern
is native to that domain's own system.
**Evidence:** `dispatch/store.py::delete_load()`'s `exceptions` table; `cin_lite/rules/`
directory listing.

**Record Type:** Financial retention records
**System of Record:** `dispatch/store.py`'s `retention.financial_summary` field, sourced from
`get_financials()`/`settlements` at archive time.
**Why:** Freight-load-specific financial closeout; no overlap with any other component.
**Evidence:** `dispatch/services.py::archive_load()` (constructs `fin_summary` from
`get_financials()` and `store.get_settlement()`).

**Record Type:** Route intelligence
**System of Record:** **Ambiguous — no clear single owner.** `portal/models/intelligence.py`
defines a `route` `INTEL_TYPE` with zero confirmed producers (not checked as thoroughly as
`location`/`broker` this pass — flagged for the future mission, not claimed empty with the same
confidence as `location`). No `route_intelligence` section exists in Library (Library has
`location_intelligence` but no `route_intelligence` equivalent) or in Archive.
**Why:** This is a real gap, not a duplication — the doctrine concept (tri-department Library's
canonical taxonomy has an explicit `Route_Intelligence` collection) has no confirmed live
Dispatch producer.
**Evidence:** `portal/models/intelligence.py::INTEL_TYPES`; absence confirmed by grep, not by
assumption alone (though route specifically deserves a second, dedicated grep pass before this
is treated as fully settled).

**Record Type:** Location history
**System of Record:** **None — defined but unpopulated.** `portal/models/archive.py`'s
`location_history` section exists in schema only (see Phase 1). `portal/models/library.py`'s
`location_intelligence` section is the closest live analog, but it is *current* facility data
(gate notes, dock notes, security requirements — per `LOCATION_FIELDS`), not *historical* data
in the archival sense.
**Why:** This is the clearest example in this whole report of a schema/doctrine concept
(archived location history) that has no actual implementation behind it today.
**Evidence:** Phase 1 finding above; `LOCATION_FIELDS` in `library.py`.

**Record Type:** Broker history
**System of Record:** **None — defined but unpopulated**, same finding as Location History.
`portal/models/intelligence.py`'s `broker` intel_type (system-generated, on inquiry creation) and
`portal/models/library.py`'s `broker` section (human-placed) are both *current*, not *historical*
— see Phase 3 for whether these two count as duplication of each other.
**Evidence:** Phase 1 finding above; `create_inquiry()` call site.

---

## Phase 3 — Duplication Analysis

**A) True duplication (same record stored in multiple locations): NONE FOUND.**

No evidence of any single triggering event writing the same record into two different stores.
Specifically checked and ruled out: the "broker" three-way naming overlap (intelligence.py /
library.py / archive.py) — traced every producer and found each populated by a distinct,
non-overlapping trigger (system-auto-generated on inquiry vs. human-submitted vs. never-written).
No shared write path exists.

**B) Shared presentation (different records displayed together): CONFIRMED, by design.**

The `/archive` page (`portal/routes/pages.py::archive_view()`) deliberately renders four
components together — Portal Archive, CIN-Lite Pipeline Archive, Dispatch Retention Archive,
Sandbox Archive Candidates — each in its own clearly labeled section (`h2` headers: "DISPATCH
Pipeline Archive," "Dispatch Retention Archive," "Sandbox — Archive Candidates," plus the looped
Portal sections). This is honest shared presentation, not conflation — confirmed by reading the
template directly (`portal/templates/archive.html`), not by assumption.

**C) Related but independent records: the majority of what this inventory found.**

- Intelligence's `broker`/`location` intel_types and Library's `broker`/`location_intelligence`
  sections: related concepts (both concern brokers/locations), independent stores, independent
  and non-overlapping producers. Not duplication.
- `dispatch/store.py`'s `retention` table and its own sibling tables (`pod_packages`, `evidence`,
  `settlements`): related (retention *references* the others), independent tables, no data
  copied between them — reference, not duplication.
- Sync Engine's local folder structure mirrors the domain taxonomy of Library/Archive/
  Intelligence but does not itself store canonical data — a transport layer over independent
  stores, not a fifth copy of the data (pending confirmation of live transport wiring, per Phase
  1 comment).

**Genuinely new finding this pass, not previously reported: two `portal/models/archive.py`
sections (`location_history`, `broker_history`) and at least one `portal/models/intelligence.py`
type (`location`) are not duplicated — they are unimplemented.** This is a materially different
problem than duplication and should not be filed under "consolidate the archives."

---

## Phase 4 — Archive Authority Review

**1. Should freight-load retention remain entirely separate?**
Yes. Evidence: `dispatch/store.py`'s relational schema (11 sibling tables under `loads`) has no
conceptual or code-level relationship to contract-pursuit or Portal-decision archival. Its
producer (`archive_load()`) and consumers (`list_retentions()`, `list_pods()`, `list_evidence()`)
are entirely internal to the `dispatch/` subsystem. No shared record type, no shared trigger, no
shared storage technology (SQL vs. file-based) with any of the other three.

**2. Should Portal archival remain separate from CIN-Lite archival?**
Evidence supports separation remaining the default, but with a caveat: both are genuinely
Publisher/decision-adjacent in a way freight retention is not — `portal/models/archive.py`'s
`publisher` section and `cin_lite/archive.py`'s `Proposals`/`Routing` both ultimately trace back
to "did Mike approve this output." That shared *concept* (not shared *storage*) is exactly what
the Approval Chain Safety Gate branch addressed on the Portal side. Whether that's sufficient, or
whether the *presentation* of "all Publisher-adjacent approval history in one place" would serve
Mike better, is a legitimate open question — but it is a UX question (Phase 5), not evidence that
the storage layers must merge.

**3. Is any consolidation justified?**
Narrowly, yes — but not the consolidation the original Hard Conflict List item 4 proposed.
Evidence: `location_history` and `broker_history` are unimplemented, not competing with anything.
The actual justified action here is **implement or remove these two dead sections**, not merge
two live, actively-diverging archive engines. No evidence supports merging `cin_lite/archive.py`
and `portal/models/archive.py`'s live sections (`load`, `decision`, `publisher`) — they store
different domains with different producers.

**4. Does any component currently violate Dispatch department boundaries?**
One candidate, flagged for further review rather than asserted as confirmed: `portal/routes/
api.py::create_inquiry()` writes an Intelligence record (`intel_model.create_record(intel_
type="broker", ...)`) as a side effect of a Portal API action, without going through any review
or approval step — this is the same *shape* of gap the Approval Chain Safety Gate fixed for
Library, just for Intelligence instead. Not in this mission's scope to fix (that would be
implementation), but the boundary question — should system-generated Intelligence records be
subject to the same human-origin-vs-machine-origin distinction Library now has? — is real and
evidenced, not speculative.

**5. Does the Approval Chain Safety Gate already eliminate the primary operational risk?**
For the risk it targeted, yes: `portal/models/archive.py::archive_publisher_action()` can no
longer archive a Publisher action with no valid `approved_by`, confirmed by the regression test
added on that branch (`test_publisher_cannot_archive_without_approval`). It does **not** address
the two newly-found gaps in this report (unimplemented `location_history`/`broker_history`
sections, or the unreviewed Intelligence auto-write in question 4) — those are different risks
the safety gate was never scoped to cover, not failures of that fix.

---

## Phase 5 — Presentation Layer (Usability Only)

**Would a four-section archive view be the preferred long-term design even if storage systems
remain separate?**

Evaluated on usability grounds only, per the instruction not to evaluate storage technology:

- **Human cognitive load:** Four clearly labeled, honestly-scoped sections is more legible than
  a single blended list would be — Mike can immediately tell "this came from the contract
  pipeline" vs. "this came from a freight load" without inferring it from record shape. The
  current design does not hide the sprawl; it discloses it. That is the right instinct.
  Four is not obviously too many for one page, but the two dead Portal sections
  (`location_history`, `broker_history` — currently rendering as permanently-empty tables per
  Phase 1) add visual noise without adding information; removing empty sections from the *view*
  (not the schema) would reduce load without touching storage.
- **Department separation:** Consistent with Constitution-level department boundaries (Archive
  preserves history per-department, not as one undifferentiated pool) — the four-section
  structure actually reflects real department boundaries (Publisher/decision history vs.
  contract-pursuit history vs. freight-load history vs. live-sandbox candidates) reasonably well
  already.
- **Retrieval simplicity:** Untested this pass — no evidence gathered on whether Mike (or anyone)
  has ever needed to search *across* all four sections at once (e.g., "find everything related to
  Broker X regardless of which archive it's in"). If that access pattern matters, four separate
  sections with no cross-index is a real usability gap; if it doesn't, it isn't. This report has
  no evidence either way and should not guess.
- **Manager doctrine / Library doctrine / Archive doctrine:** The current split maps cleanly onto
  "Archive is not Library" (Constitution §7.5) and onto per-department ownership generally.
  Nothing here suggests the four-section split *violates* doctrine; if anything it makes
  department boundaries more visible than a merged view would.

**Assessment: the four-section split is a defensible long-term presentation choice on usability
grounds alone**, independent of whatever happens to the underlying storage systems. The
strongest usability improvement available today that requires no storage change at all: hide (or
visibly mark as "not yet in use") the two dead sections, so the page reflects what's actually
populated.

---

## Final Deliverable Summary

### 1. Archive Inventory — see Phase 1 (8 components catalogued: 4 true archives, 1 staging
buffer, 1 live-filtered view, 2 adjacent current-truth stores included for boundary context,
plus 1 cross-cutting transport mechanism flagged for further review).

### 2. Ownership Matrix — see Phase 2 (12 record types mapped; 2 have no implemented owner at
all — Location History, Broker History; 1 is ambiguous — Route Intelligence; 1 has no dedicated
store — Manager Decisions).

### 3. Duplication Analysis — see Phase 3. **No true duplication found.** Confirmed shared
presentation (by design, honestly labeled) and confirmed related-but-independent records
throughout. The apparent "duplication" in the original Hard Conflict List item 4 does not hold
up under call-site-level evidence.

### 4. Authority Findings — see Phase 4. Freight retention should stay separate (strong
evidence). Portal/CIN-Lite archival separation is defensible but the shared "Publisher approval"
concept across both is worth a UX look. The only evidence-backed consolidation candidate is
implementing-or-removing two dead sections, not merging live systems. One possible boundary
concern flagged (Intelligence auto-write bypassing review) but not confirmed as a violation,
only as evidence-worthy for a future look.

### 5. UX Findings — see Phase 5. Four sections is usability-defensible. Dead sections should be
hidden or clearly marked, independent of any storage decision.

### 6. Recommended Decision Options

**OPTION A — Maintain Separation**
*Benefits:* Matches the evidence best — no true duplication exists to consolidate. Lowest risk;
preserves `cin_lite/archive.py`'s integrity guarantees untouched. No migration risk to any of the
11 dispatch tables, the file-tree archive, or the Portal JSON store.
*Risks:* The two dead sections and the ambiguous Route Intelligence ownership remain unresolved
unless separately addressed. Mike continues navigating four sections on one page indefinitely.
*Dependencies:* None.
*Required Future Missions:* A small, separately-scoped "Archive Schema Cleanup" mission (resolve
or remove `location_history`/`broker_history`, resolve Route Intelligence ownership) — much
smaller in scope than the originally-proposed consolidation.

**OPTION B — Partial Consolidation**
*Benefits:* Could resolve the two dead sections *by* deciding they belong in an existing live
system (e.g., decide Location/Broker History is actually just Library's `location_intelligence`/
`broker` sections with a "historical" flag, rather than a separate Archive section) — addressing
the real gap found in Phase 1/3 without touching the two systems that have no duplication problem
(`cin_lite/archive.py`, `dispatch/store.py`).
*Risks:* Requires a real design decision (does "history" belong in Library, which this report
found is current-truth-only by doctrine, or does it need a genuinely new home?) before any code
change — exactly the kind of decision this report is not authorized to make.
*Dependencies:* Resolves cleanly only after Mike decides what "Location/Broker History" is
supposed to mean, doctrinally, since no implementation currently defines it.
*Required Future Missions:* A "Location/Broker History Definition" mission (doctrine-level,
before any implementation mission) — narrower and more tractable than a full archive merge.

**OPTION C — Full Consolidation**
*Benefits:* One archive engine, one integrity model (`cin_lite/archive.py`'s), theoretically
simpler long-term maintenance.
*Risks:* Not supported by the evidence in this report. Would require redesigning `cin_lite/
archive.py`'s section model to absorb Portal-native domains (Publisher/decision) and inventing an
entirely new relationship to `dispatch/store.py`'s relational schema (a SQL-to-file-tree
migration, or vice versa) for data this report found has no actual overlap with contract-pursuit
data. Highest risk, least justified by real findings, touches the one component
(`cin_lite/archive.py`) with active integrity guarantees and 26 dependent tests.
*Dependencies:* Would require its own full migration-planning mission, explicitly out of this
report's scope, and — per the evidence above — would be solving a problem (duplication) this
investigation did not find.
*Required Future Missions:* Not recommended based on current evidence. If pursued anyway, would
need: a dedicated Archive Data Migration mission, a `dispatch/store.py` relational-to-file-tree
(or reverse) design decision, and a full regression pass against all four components' existing
test coverage.

---

No code was produced. No implementation steps were produced. No migration plan was produced. No
deletion is recommended anywhere in this report — every "should be removed" observation (the two
dead sections) is reported as a finding for Mike's decision, not executed or scheduled.

Human review required before any architecture change is authorized.

Mike decides.
