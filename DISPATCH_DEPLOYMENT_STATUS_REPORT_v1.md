# DISPATCH_DEPLOYMENT_STATUS_REPORT_v1

Program: Dispatch
Status: **Factual status report. No deployment action taken by this document or this session.**
Origin: Direct question — "Actually deployed and operating on the VPS?"
Rule: No fabrication. Every claim below is backed by evidence checked this session, not assumed.

---

## Direct Answer

**No. Nothing built or discussed this session is deployed or operating anywhere. There is no
known VPS.** Everything that happened is code committed to a git branch on GitHub. No server has
been provisioned, configured, deployed to, or verified as running, at any point in this program.

## What Actually Exists

- `dispatch/canonical-reconciliation-integration` — a branch in `jax1313-outlook/Dispatch`, **9
  commits ahead of `main`, not merged.** Confirmed via `git rev-list --count main..
  dispatch/canonical-reconciliation-integration` = 9.
- Every commit on that branch (Stages 3-5, the Approval Chain Safety Gate, the Publisher button
  fix, Manager's preservation doc, Stage 1, Stage 2, the presentation-layer consolidation) exists
  only there. `main` has none of it.
- The full test suite has been run **locally, inside this session's own sandboxed clone**, not
  against any deployed instance. "Full suite green" throughout this program has always meant
  `pytest` passing in this environment — never a live-server check.

## What Does Not Exist

- **No VPS.** No hostname, IP, SSH credential, or hosting provider has been referenced,
  mentioned, or accessed anywhere in this entire session. I have no knowledge of one existing for
  this program.
- **No deployment configuration in the repository.** Checked this session: no `Procfile`, no
  `Dockerfile`, no `docker-compose*`, no `.service` unit, no `wsgi.py`/`gunicorn` config anywhere
  in the repo tree.
- **No deploy step in CI.** `.github/workflows/ci.yml` exists and runs `pytest` with coverage on
  every push/PR (Python 3.11-3.13 matrix) — read in full this session. It installs dependencies,
  runs tests, uploads a coverage artifact. It does not SSH anywhere, does not build a container,
  does not push to any server. It is test-only.
- **No merge to `main` has been requested or performed.** Per this program's own standing
  practice ("No pending request to merge `dispatch/canonical-reconciliation-integration` into
  Dispatch main — explicitly stated as requiring a separate future decision"), that decision has
  never been made.

## What Would Actually Be Required To Deploy

None of the following has happened, and none is implied by anything reported as "done" earlier
in this session:

1. **A merge decision** — explicit approval to merge this branch into `main`, separate from
   every implementation go-ahead given so far.
2. **A real target server** — provisioning or identifying a VPS (or other host), with SSH/deploy
   access this session does not have.
3. **Environment and secrets configuration** — `cin_lite` alone references `ANTHROPIC_API_KEY`,
   `DISPATCH_SAM_API_KEY`, SMTP credentials, an email domain/secret, and more (per
   `tests/conftest.py`'s `_ENV_VARS` list, all deliberately scrubbed in tests to keep them
   deterministic and offline) — none of these have been set, discussed, or provisioned anywhere
   outside the test sandbox.
4. **A process manager and reverse proxy** — nothing currently defines how the Flask app would
   run continuously (gunicorn/uwsgi + systemd or equivalent) or be exposed publicly (nginx/Caddy
   or equivalent) — none of this exists in the repo.
5. **Post-deploy verification** — an actual live-traffic check, which by definition can't happen
   until 1-4 exist.

## Bottom Line

Every "done," "green," "implemented," and "verified" claim made this session refers to code on an
unmerged branch, tested locally in this sandbox. If Mike has a VPS already provisioned for
Dispatch from outside this session, I have no visibility into it and have made no assumptions
about it here. Treating anything built this session as "live" or "operating" would be
fabrication — this report exists specifically to not do that.

Mike decides what happens next — merge, deployment target, and go-live are all separate,
unmade decisions.

---

## Update: Live Deployment Confirmed

The original report above was accurate given what was known at the time it was written (no VPS
had been referenced anywhere in this session). It is now superseded on that one point by direct
evidence — everything else in it remains accurate and unchanged.

**Evidence**: a first-hand desktop screenshot, dated 8/11/2026 (taskbar clock), showing Microsoft
Edge navigated to `https://l1truck.com/home`, rendering a page titled "L2-COS Portal." The page's
navigation (Home, SAM, Dispatch, Publisher, Library, Archive, Intelligence, Conflict Notices,
Settings) and its five home-page summary-card labels (Active Cards, Conflict Notices, Publisher
Queue, Archived Records, Intelligence Records) match `portal/routes/pages.py` and
`portal/templates/home.html` exactly, as read and edited in this session. This is a structural
match to real application code, not a name coincidence.

**Conclusion: yes, a live Dispatch instance ("L2-COS Portal") is genuinely deployed and reachable
over HTTPS on a VPS at `l1truck.com`.** The "No VPS" line in the original report above is
corrected by this evidence.

**What remains true and unchanged**: which commit is running there is still unknown, and the
strong likelihood is that it predates this session's work entirely.
`dispatch/canonical-reconciliation-integration` — Stage 1, Stage 2, the Manager Preservation
Decision, the presentation-layer consolidation panel, the Approval Chain Safety Gate — is still
9 commits ahead of `main`, unmerged, as of this writing. Deployment here also appears to have
happened via manual `scp` (per the deployment guides reviewed alongside this evidence), not a
git-tracked pipeline, so the live instance's exact provenance can't be pinned to a commit hash
without direct server access. The screenshot's own data is consistent with this: Publisher Queue
reads 0, so there's no way to confirm from it whether the ninth `GovCon Proposal Draft Required`
action type exists there, and this session's new "Attention Needed Across Departments" panel
would not render regardless, since all three of its source queues are empty in the state shown.

**Next real decision, now that live infrastructure is confirmed to exist**: whether and when to
merge `dispatch/canonical-reconciliation-integration` into `main` and redeploy, so this session's
work actually reaches the live instance. Not decided by this document.

Mike decides.

---

## Update: Merged to `main`

Approved ("Approve the merge to main"). `dispatch/canonical-reconciliation-integration` merged
into `main` in `jax1313-outlook/Dispatch` via **PR #82**
(`https://github.com/jax1313-outlook/Dispatch/pull/82`), merge commit `be127ba`.

`main` was branch-protected — a direct `git push` was rejected (GH013, "Changes must be made
through a pull request"). Went through the proper PR path instead: opened PR #82, waited for the
repo's own CI (`pytest`, matrix py3.11/3.12/3.13) to go green on the merge — all three passed —
then merged via the GitHub API (merge commit, not squash, to preserve the individual stage
commits' history and the commit hashes already referenced throughout this program's tracking
documents).

`main` is now 11 commits ahead of where it was at session start, containing everything built this
session: Stage 3 (integration branch), Stage 4 (`reconciliation/` adapters), Stage 5 items 1-3
(the Approval Chain Safety Gate), the Publisher "Mark Approved" button fix, the Manager
Preservation Decision, Stage 1 (Intelligence → Library → Publisher, broker-type), Stage 2 (the
GovCon Proposal Integration Bridge), and the presentation-layer consolidation panel.

**This still does not mean the live instance at `l1truck.com` is running any of it.** Deployment
there has consistently been manual (`scp` + a setup script), not git-triggered — merging to
`main` on GitHub does not, by itself, push anything to the VPS. Getting this work onto the live
server is a separate, not-yet-requested action.

Mike decides.
