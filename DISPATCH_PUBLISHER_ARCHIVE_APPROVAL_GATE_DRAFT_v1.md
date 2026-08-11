# DISPATCH_PUBLISHER_ARCHIVE_APPROVAL_GATE_DRAFT_v1.md

Program: Dispatch
Status: **DRAFT ONLY — NOT APPLIED TO DISPATCH. Nothing in this document has been committed,
pushed, or merged anywhere.**
Purpose: Merge the Library approval-gate pattern (external, non-self reviewer identity required
before something becomes truth) into Dispatch's real Publisher and Archive code, per
`DISPATCH_CANONICAL_ARCHITECTURE_RECONCILIATION_MATRIX_v1`'s Hard Conflict List items 2 and 3.
Date: 2026-08-11

This document was produced instead of touching Dispatch because: (1) this session only has
**read** access to `jax1313-outlook/Dispatch`, and (2) the reconciliation matrix that prompted
this work states integration should wait for Mike's explicit approval — a real conflict with the
same message's closing instruction, which the user resolved by choosing "draft only" when asked.
Nothing here is authorized for application until Mike reviews it.

---

## 1. What Gate Is Being Merged, From Where

The pattern already proven in both tri-department Library (`ingestion.review_candidate()`) and
tri-department Publisher (`service.approve_review_package()`): a status transition to
"approved"/truth requires an explicit identity argument, and that argument is rejected if it's
empty or matches a reserved system identity (the approving system may not approve its own output).

Applying this to Dispatch's two real gaps identified in the reconciliation report:

- `portal/models/publisher.py::update_action_status()` — today accepts any status transition,
  including to `"APPROVED"`, with **no identity argument at all**.
- `portal/models/archive.py::archive_publisher_action()` — today archives whatever `action` dict
  it's given, with **no check that it was ever approved**.

---

## 2. Real Call-Site Investigation (Done Before Drafting, Not Guessed)

`portal/routes/api.py` lines 124-139 is the only real caller of both functions:

```python
@api_bp.route("/publisher/update", methods=["POST"])
def update_publisher_action():
    data = request.get_json(force=True)
    action_id = data.get("action_id")
    new_status = data.get("status")
    ...
    action = publisher.update_action_status(action_id, new_status)
    if new_status == "ARCHIVED":
        arc_model.archive_publisher_action(action)
```

Two important facts this uncovered, which change the shape of the fix from a naive first draft:

1. **The request body has no identity field at all today** — not `approved_by`, not a session
   user, nothing. Dispatch's Portal has no login/auth system (confirmed: no `flask_login`, no
   `current_user`, no session-based identity anywhere in `portal/`). This gate can only be as
   strong as "a string the caller supplies," the same posture the tri-department build itself
   uses for `approver_id`/`reviewed_by` — this is not a new weakness introduced by this draft, it
   matches the existing program-wide pattern.
2. **`archive_publisher_action()` is called *after* `update_action_status()` has already mutated
   `action["status"]` to `"ARCHIVED"`.** A naive gate checking `action["status"] == "APPROVED"`
   at archive time would be wrong — by the time the archive function runs, the status is already
   `"ARCHIVED"`, never `"APPROVED"`. The correct check is whether `approved_by` was ever recorded
   on the action (stamped once, during the `APPROVED` transition, and persisted forward), not
   what the current status string happens to be.

---

## 3. Proposed Diff — `portal/models/publisher.py`

```diff
 PUBLISHER_STATUSES = ["PENDING", "DRAFT", "READY", "APPROVED", "ARCHIVED"]
 
+# Identities that may never be used as an approver -- Publisher may not approve itself.
+# Mirrors dispatch_library.models.RESERVED_SYSTEM_IDENTITIES / dispatch_publisher.models
+# .RESERVED_SYSTEM_IDENTITIES from the tri-department build.
+RESERVED_SYSTEM_IDENTITIES = {"PUBLISHER", "SYSTEM", "AUTOMATION", "INTELLIGENCE", "LIBRARY"}
+
+
+class PublisherApprovalError(ValueError):
+    """Raised when an action is moved to APPROVED without a valid external approver identity."""
+
+
 BROKER_PACKET_MANIFEST = ["Business Card", "W-9", "Insurance", "Authority", "Rate Sheet", "Terms"]
@@
-def update_action_status(action_id: str, new_status: str) -> dict:
+def update_action_status(action_id: str, new_status: str, approved_by: str | None = None) -> dict:
     if new_status not in PUBLISHER_STATUSES:
         raise ValueError(f"Invalid publisher status: {new_status}")
+
+    if new_status == "APPROVED":
+        if not approved_by or approved_by.strip().upper() in RESERVED_SYSTEM_IDENTITIES:
+            raise PublisherApprovalError(
+                "Publisher action cannot be marked APPROVED without an external, non-system "
+                "approved_by identity (Publisher may not approve itself)."
+            )
+
     queue = _load()
     for action in queue:
         if action["id"] == action_id:
+            if new_status == "APPROVED":
+                action["approved_by"] = approved_by
+                action["approved_at"] = _utc_now()
             action["status"] = new_status
             action["updated_at"] = _utc_now()
             _save(queue)
             return action
     raise KeyError(f"Publisher action not found: {action_id}")
```

Backward-compatible for every transition except `-> "APPROVED"`, which now requires
`approved_by`. `PENDING`/`DRAFT`/`READY`/`ARCHIVED` transitions are unaffected by this diff in
isolation (see Section 4 for why `ARCHIVED` still needs a change elsewhere).

---

## 4. Proposed Diff — `portal/models/archive.py`

```diff
+class ArchiveApprovalError(ValueError):
+    """Raised when attempting to archive a Publisher action that was never approved by an
+    external, non-system identity. Mirrors the tri-department Publisher repo's
+    create_archive_handoff() precondition (blocked unless status == APPROVED_BY_MIKE)."""
+
+
 def archive_publisher_action(action: dict) -> dict:
-    """Archive a completed publisher action."""
+    """Archive a completed publisher action.
+
+    Hard Rule: Publisher outputs must not become Archive history unless a human approved
+    them first. Checks `approved_by` rather than the current `status` string, because by the
+    time this is called the caller (portal/routes/api.py) has already transitioned status to
+    "ARCHIVED" -- approved_by is stamped once during the APPROVED transition and persists
+    forward, so it is the only reliable signal here.
+    """
+    if not action.get("approved_by"):
+        raise ArchiveApprovalError(
+            f"Publisher action {action.get('id')!r} cannot be archived: no approved_by "
+            f"identity recorded. Publisher outputs must be approved before archival."
+        )
+
     return create_record(
         section="publisher",
         source_id=action["id"],
         title=f"{action['action_type']} — {action.get('sandbox_id', '')}",
         record_data=action,
-        decision_summary=f"Publisher action completed: {action['status']}",
+        decision_summary=(
+            f"Publisher action approved by {action['approved_by']} and archived: "
+            f"{action['status']}"
+        ),
     )
```

---

## 5. Proposed Diff — `portal/routes/api.py` (required for the above to be reachable at all)

Without this, nothing in the UI/API layer could ever supply `approved_by`, making the gate
unreachable rather than enforced:

```diff
 @api_bp.route("/publisher/update", methods=["POST"])
 def update_publisher_action():
     data = request.get_json(force=True)
     action_id = data.get("action_id")
     new_status = data.get("status")
+    approved_by = data.get("approved_by")
 
     if not action_id or not new_status:
         return jsonify({"error": "action_id and status required"}), 400
 
     try:
-        action = publisher.update_action_status(action_id, new_status)
+        action = publisher.update_action_status(action_id, new_status, approved_by=approved_by)
         if new_status == "ARCHIVED":
             arc_model.archive_publisher_action(action)
         return jsonify({"status": "ok", "action": action})
     except (KeyError, ValueError) as exc:
         return jsonify({"error": str(exc)}), 400
```

`PublisherApprovalError`/`ArchiveApprovalError` both subclass `ValueError`, so they're already
caught by the existing `except (KeyError, ValueError)` and surfaced as a 400 with the error
message — no new exception handling needed in the route.

**Not addressed by this draft, flagged as a real prerequisite**: the Portal UI template that
POSTs to `/api/publisher/update` (not yet located/read — out of scope for this draft) would need
a form field for the approver to type their name, since there is no auth session to source it
from automatically. Until that exists, `approved_by` has to come from somewhere; this draft does
not invent that UI.

---

## 6. Real Test Impact (Found by Reading Dispatch's Existing Tests, Not Assumed)

Three tests in `tests/test_portal.py` exercise this exact code path today and would behave
differently under this diff:

| Test | Current behavior | What breaks | Why |
|---|---|---|---|
| `test_publisher_status_workflow` (line ~382) | POSTs `DRAFT`→`READY`→`APPROVED` with no `approved_by` in the JSON body; asserts each returns `"status": "ok"` | The `APPROVED` transition would now return a 400 (`PublisherApprovalError`) instead of `"ok"` | Test never supplies an approver identity, which is exactly the gap this fix closes |
| `test_archive_publisher_action` (line ~1207) | Calls `arc_model.archive_publisher_action(action)` directly with a hand-built dict that has `"status": "ARCHIVED"` but no `approved_by` key | Would now raise `ArchiveApprovalError` instead of returning a record | Same gap, exercised directly against the model function |
| `test_publisher_archive_on_status_change` (line ~1368) | POSTs `status: "ARCHIVED"` **directly, skipping `APPROVED` entirely**, and asserts the action successfully lands in the Archive's `publisher` section | Would now get a 400 and the archive assertion (`len(pub_archive) >= 1`) would fail | **This test currently asserts the exact forbidden path** (Publisher output archived with no approval ever recorded) that this whole reconciliation effort exists to close. Its current passing status is itself evidence for Hard Conflict List item 3 in the reconciliation matrix. |

**None of these three tests were changed as part of producing this draft.** They are reported
here as the necessary next step *if* this fix is ever applied — each would need updating to pass
a real `approved_by` value (for the two that should keep passing) or to assert the new rejection
(for `test_publisher_archive_on_status_change`, which should start asserting a 400/skip archival
when no approval was recorded, since that's the behavior change being deliberately introduced).

---

## 7. What This Draft Does Not Do

- Does not touch `portal/models/library.py`'s own auto-approve gap (`add_record()` stamping
  `status: "approved"` unconditionally) — the user's instruction was to merge the Library gate
  *pattern* into Publisher and Archive, not to fix Library's own remaining gap, which is a
  separate, not-yet-authorized piece of work.
- Does not touch `cin_lite/archive.py` (the other, stronger Dispatch Archive implementation) —
  the reconciliation report's Hard Conflict List item 3 specifically named
  `archive_publisher_action()` in `portal/models/archive.py`, which is what's addressed here.
- Does not locate or modify the Portal UI template/form that would need an `approved_by` input
  field — flagged as a real prerequisite in Section 5, not solved here.
- Does not commit, push, branch, or open a PR against Dispatch. No file in the Dispatch checkout
  at `/workspace/jax1313-outlook/dispatch` was modified while producing this document.

## 8. What Would Be Required To Actually Apply This

1. Write access to `jax1313-outlook/Dispatch` (this session currently has read-only).
2. A dedicated integration branch in Dispatch (not `main`) — the reconciliation matrix's own
   Stage 3 suggestion (`dispatch/canonical-reconciliation-integration`) is reasonable, pending
   Mike's naming preference.
3. Update the three tests in Section 6, per the behavior each should have after this fix.
4. Decide where `approved_by` comes from in the real UI (Section 5's open prerequisite) before
   this is anything more than an API-level gate nobody can reach.
5. Mike's explicit go-ahead to apply and push — not implied by this draft's existence.

Mike decides.
