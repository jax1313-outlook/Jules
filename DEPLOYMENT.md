# DISPATCH PRESENTATION LAYERS & WEBSITE - DEPLOYMENT & WIRING GUIDE

## Overview
This document provides complete wiring, deployment, testing, and operational guidance for the three presentation layers and public website developed for **Level 1 Transport (Jacksonville Regional Micro-Response Carrier™)**.

---

## A. Files Created or Changed

| File Path | Description | Status |
|-----------|-------------|--------|
| `dispatch_spine.py` | Core Dispatch Spine data models (`WorkItem`, `ActiveTrip`, `COMICommunicationCard`, `PortalCard`), consequence levels (L0-L5), and mock data store. | **Created** |
| `app.py` | Main Flask web application handling website, portal routes, and REST APIs. | **Created** |
| `templates/base.html` | Master Jinja layout template containing global head, navigation, and footer. | **Created** |
| `templates/index.html` | Marketing homepage for Level 1 Transport. | **Created** |
| `templates/capabilities.html` | Service capabilities page (Same Day, Next Day, Dedicated, Emergency). | **Created** |
| `templates/about.html` | About page detailing company vision and Jacksonville focus. | **Created** |
| `templates/contact.html` | Contact & Service Request dispatch form page. | **Created** |
| `templates/driver.html` | Driver Portal (truck-cab operational cockpit). | **Created** |
| `templates/operations.html` | Operations / Management Portal (digital backroom office). | **Created** |
| `templates/stakeholder.html` | External Stakeholder Portal (broker/shipper confidence window). | **Created** |
| `static/style.css` | High-contrast, dark-theme cockpit CSS styling. | **Created** |
| `tests/test_portals.py` | Pytest test suite validating routes, APIs, search, uploads, and security isolation. | **Created** |
| `DEPLOYMENT.md` | Deployment, wiring, rollback, and governance instructions. | **Created** |

---

## B. Routes Added

| Route | HTTP Method | Layer | Description |
|-------|-------------|-------|-------------|
| `/` | GET | Public Website | Homepage detailing micro-response carrier positioning. |
| `/capabilities` | GET | Public Website | Service capabilities matrix & specifications. |
| `/about` | GET | Public Website | Jacksonville regional focus and company story. |
| `/contact` | GET | Public Website | Direct contact / service request dispatch form. |
| `/driver` | GET | Driver Portal | Truck-cab operational cockpit view. |
| `/operations` | GET | Operations Portal | Digital backroom office view with decision cards. |
| `/stakeholder` | GET | External Portal | Public/Broker confidence window for shipment tracking. |

---

## C. REST API Endpoints Added

| API Endpoint | HTTP Method | Target Layer | Description |
|--------------|-------------|--------------|-------------|
| `/api/v1/driver/active-trip` | GET | Driver Portal | Returns active trip, pickup, delivery, risk, and BOL/POD status. |
| `/api/v1/driver/search-loads` | GET | Driver Portal | Fast load lookup by reference/load number. |
| `/api/v1/driver/upload-pod` | POST | Driver Portal | Simulates uploading POD/BOL scan for an active trip. |
| `/api/v1/operations/cards` | GET | Operations Portal | Returns filtered decision cards (L3, L4, L5) and work queue items. |
| `/api/v1/operations/action` | POST | Operations Portal | Submits human decision actions (e.g. Approve, Reject) to Dispatch Spine. |
| `/api/v1/stakeholder/shipment/<load_number>` | GET | External Portal | Publicly safe, filtered milestone view (sanitized of internal scoring & data). |

---

## D. Models, Services, and Integrations

* **`dispatch_spine.py`**:
  * `ConsequenceLevel`: L0 (Silent Log), L1 (Status), L2 (Review), L3 (Decision), L4 (Conflict), L5 (Authority).
  * `WorkItem`: Represents raw system tasks (`waiting_for_mike`, `conflict_raised`, etc.).
  * `ActiveTrip`: Stores trip details, pickup/delivery windows, Route Risk alerts, and document statuses (`BOL`, `POD`, `Invoice`).
  * `COMICommunicationCard`: Workflow cards for tracking SMS/Email notifications sent to drivers/brokers without replacing transport email/SMS services.
  * `PortalCard`: High-contrast decision card presented to Mike for authoritative action.

---

## E. Connection to Existing Dispatch Architecture

```
                       +-----------------------------------+
                       |         MIKE ZACHARY               |
                       |       (Final Authority)            |
                       +-----------------------------------+
                                   ^           ^
                                   |           |
            +----------------------+           +----------------------+
            |                                                         |
+-----------------------+                                 +-----------------------+
|  DRIVER PORTAL (UI)   |                                 | OPERATIONS PORTAL(UI) |
| (Truck-Cab Cockpit)   |                                 | (Backroom Command)    |
+-----------------------+                                 +-----------------------+
            |                                                         |
            +---------------------------+-----------------------------+
                                        |
                                        v
                    +---------------------------------------+
                    |             DISPATCH SPINE            |
                    |  - Work Queue      - COMI Cards       |
                    |  - Active Trips    - Decision Engine  |
                    +---------------------------------------+
                                        ^
                                        |  (Sanitized Data Boundary)
                                        v
                    +---------------------------------------+
                    |      EXTERNAL STAKEHOLDER PORTAL      |
                    |   (Broker/Shipper Confidence Window)  |
                    +---------------------------------------+
```

* **Publisher Engine**: Receives status updates when POD/BOL packets are completed.
* **COMI Gateway**: Generates communication cards for driver/broker status notifications.
* **Library & Archive**: Surfaced in Operations Portal for promotion and retention confirmation.

---

## F. Environment Variables

| Variable Name | Default Value | Purpose |
|---------------|---------------|---------|
| `FLASK_ENV` | `production` | Controls Flask execution mode (`development` / `production`). |
| `SECRET_KEY` | `dev-key-change-in-prod` | Session and flash message signing key. |
| `PORT` | `5000` | Port for the web server to bind to. |

---

## G. Testing Commands & Execution

1. **Run Pytest Suite**:
   ```bash
   PYTHONPATH=. pytest tests/test_portals.py
   ```

2. **Run Endpoint Verification Tool**:
   ```bash
   python3 /home/jules/self_created_tools/verify_dispatch_app.py
   ```

3. **Run Playwright Screenshot Capture**:
   ```bash
   python3 /home/jules/verification/capture_screenshots.py
   ```

---

## H. Deployment Steps (Production Server / VPS)

Before executing deployment, perform reconnaissance on the target VPS:

1. **Reconnaissance & Pre-flight Inspection**:
   ```bash
   # Inspect running service and ports
   lsof -i :5000 || pgrep -af flask

   # Inspect current checkout path and git remote
   git remote -v
   git status
   git log -n 5 --oneline
   ```

2. **Backup Current Working State**:
   ```bash
   # Create a git tag or archive backup before pulling updates
   git tag pre-deploy-$(date +%Y%m%d%H%M%S)
   ```

3. **Pull Updates / Fresh Checkout**:
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   ```

4. **Install / Verify Dependencies**:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

5. **Restart Service**:
   ```bash
   # If running via systemd service:
   sudo systemctl restart dispatch-portal

   # If running via nohup/gunicorn:
   kill $(lsof -t -i :5000) 2>/dev/null || true
   gunicorn --bind 0.0.0.0:5000 app:app --daemon
   ```

6. **Verify Local & Public Endpoints**:
   ```bash
   curl -I http://127.0.0.1:5000/
   curl -I http://127.0.0.1:5000/driver
   curl -I http://127.0.0.1:5000/operations
   curl -I http://127.0.0.1:5000/stakeholder
   ```

---

## I. Rollback Steps

In the event of an issue on deployment:

1. **Identify Rollback Commit**:
   ```bash
   git log --oneline -n 10
   ```

2. **Revert Code Base**:
   ```bash
   git checkout <PREVIOUS_COMMIT_HASH_OR_TAG>
   ```

3. **Restart Service**:
   ```bash
   sudo systemctl restart dispatch-portal
   ```

4. **Verify Rollback**:
   ```bash
   curl -I http://127.0.0.1:5000/
   ```

---

## J. What Remains Intentionally Unbuilt

* **Direct Email Sending Engine**: Outlook remains the transport provider (COMI logs communication cards but does not directly deliver email).
* **Payment/Merchant Gateway**: Invoicing is queued and displayed, but credit card/ACH processing is not baked into the presentation layer.
* **ELD/GPS Live Hardware Integration**: Hardware telemetry feeds connect through API wrappers; raw device drivers are not implemented.

---

## K. Items Requiring Mike's Decision Before Production

1. **Production Domain & SSL Certificates**: Production domain confirmed as `L1truck.com`. SSL certificates to be configured for `L1truck.com` and subdomains.
2. **JAXPORT Terminal API Secret Renewal**: Current JAXPORT key active as placeholder. Renewal to be authorized by Mike after build sign-off.
3. **External Rate Visibility Policy**: Confirm whether rate confirmation totals should ever be exposed to authenticated shippers on the external stakeholder portal.
