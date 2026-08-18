# DISPATCH PRESENTATION LAYERS & PORTAL WIRING MANIFEST
**Level 1 Transport (`L1truck.com`) • Jacksonville Regional Micro-Response Carrier™**

This document provides explicit wiring instructions, route manifests, URL path maps, startup procedures, and before/after verification notes for the Dispatch Presentation Layers.

---

## 1. Route Manifest (Added or Modified Routes)

| URL Path | HTTP Method | Route Name | Layer / Target | Function & Wiring |
|----------|-------------|------------|----------------|-------------------|
| `/` | GET | `index` | Public Website | Marketing homepage featuring tagline *"From Boxes To Pallets"* and direct links to all portals. |
| `/capabilities` | GET | `capabilities` | Public Website | Precision Micro-Response fleet capabilities matrix. |
| `/about` | GET | `about` | Public Website | Company background and Jacksonville regional operational focus. |
| `/contact` | GET | `contact` | Public Website | Direct dispatch hotline and service request form (`dispatch@L1truck.com`). |
| `/driver` | GET | `driver_portal` | Driver Portal | Truck-cab operational cockpit for active trips, load retrieval, route risk, and POD uploads. |
| `/operations` | GET | `operations_portal` | Operations Portal | Command backroom office surfacing decision cards (L3-L5), COMI queue, Library/Archive prompts, and state tracker. |
| `/stakeholder` | GET | `stakeholder_portal` | External Portal | Role-based confidence window (`Customer`, `Shipper`, `Broker`) for Mission Visibility™ and Route Risk™. |
| `/portal`, `/l2-cos`, `/cos`, `/dashboard`, `/admin` | GET | `legacy_portal_redirect` | Legacy Wire | Redirects legacy portal and L2-COS entry URLs directly to `/operations`. |
| `/api/v1/driver/active-trip` | GET | `api_driver_active_trip` | REST API | Returns active trip, pickup, delivery, risk, and BOL/POD status. |
| `/api/v1/driver/search-loads` | GET | `api_driver_search_loads` | REST API | Fast load lookup by reference/load number. |
| `/api/v1/driver/upload-pod` | POST | `api_driver_upload_pod` | REST API | Multi-part file upload handler saving POD scans to `uploads/` disk directory. |
| `/api/v1/operations/cards` | GET | `api_operations_cards` | REST API | Returns filtered decision cards (L3-L5) and auto-sync queue items. |
| `/api/v1/operations/action` | POST | `api_operations_action` | REST API | Submits human decision actions (e.g. Approve, Reject) under Mike's final authority. |
| `/api/v1/stakeholder/shipment/<load>` | GET | `api_stakeholder_shipment` | REST API | Publicly safe, sanitized milestone data boundary formatted by stakeholder role. |

---

## 2. Explicit Application Wiring & Legacy Compatibility

* **Single Source Entry Point**: The entire application is wired via `app.py`, which binds all Jinja HTML templates, CSS styles (`static/style.css`), and REST API endpoints.
* **Legacy Portal Integration**: To ensure operators launching old or legacy L2-COS bookmarks hit the new Dispatch presentation layers, `app.py` includes explicit redirect wiring:
  ```python
  @app.route("/portal")
  @app.route("/cos")
  @app.route("/l2-cos")
  @app.route("/dashboard")
  @app.route("/admin")
  def legacy_portal_redirect():
      return redirect(url_for("operations_portal"))
  ```

---

## 3. URL Paths for Operator Access

To access each screen on a running instance (e.g., `http://localhost:5000` or production host):

1. **Driver Cockpit**: `http://localhost:5000/driver`
2. **Operations / Backroom Portal**: `http://localhost:5000/operations`
3. **External Stakeholder Window (Broker View)**: `http://localhost:5000/stakeholder?ref=L1T-2026-8804&role=Broker`
4. **External Stakeholder Window (Shipper View)**: `http://localhost:5000/stakeholder?ref=L1T-2026-8804&role=Shipper`
5. **External Stakeholder Window (Customer View)**: `http://localhost:5000/stakeholder?ref=L1T-2026-8804&role=Customer`
6. **Public Homepage**: `http://localhost:5000/`
7. **Capabilities Page**: `http://localhost:5000/capabilities`
8. **About Page**: `http://localhost:5000/about`
9. **Contact Page**: `http://localhost:5000/contact`

---

## 4. One-Command Startup Procedure

An operator can launch and verify the complete Dispatch Presentation Layer using the included executable script:

```bash
./run_portal.sh
```

### What `run_portal.sh` executes automatically:
1. Inspects and clears any existing process bound to port `5000`.
2. Verifies Python dependencies (`flask`, `pytest`, `gunicorn`).
3. Launches `app.py` under Python in the background.
4. Performs an automated local health check (`curl http://127.0.0.1:5000/`) and outputs active URL access points.

---

## 5. Portal Navigation & Discoverability Updates

All 7 UI screens feature a top-level navigation bar in `templates/base.html`:

```html
<nav class="nav-links">
  <a href="/">Public Home</a>
  <a href="/capabilities">Capabilities</a>
  <a href="/about">About</a>
  <a href="/contact">Contact</a>
  <a href="/driver">Driver Cockpit</a>
  <a href="/operations">Operations Portal</a>
  <a href="/stakeholder">Stakeholder Window</a>
</nav>
```

Every new screen is discoverable and accessible from any other screen with a single click.

---

## 6. Before / After Visual & Architectural Comparison

| Dimension | Before (Legacy / Unwired State) | After (Dispatch Presentation Layers) |
|-----------|----------------------------------|-------------------------------------|
| **Navigation** | Isolated text links or missing routes. | Universal, responsive top navigation header across all 7 UI pages. |
| **Driver Interface** | No dedicated cockpit view for quick phone inquiries. | Operational Driver Cockpit (`/driver`) with instant search, Route Risk, and POD uploads. |
| **Backroom View** | Generic administration view. | Consequence-Filtered Operations Portal (`/operations`) with L3-L5 decision cards ("Mike Decides"). |
| **External Window** | Unrestricted or missing external view. | Role-Restricted Stakeholder Window (`/stakeholder`) with Customer, Shipper, and Broker filters. |
| **Branding & Domain** | `level1transport.com` / generic fleet text. | `L1truck.com` & Jacksonville Regional Micro-Response Carrier™. |
| **Startup Process** | Manual multi-step configuration. | Single command launcher `./run_portal.sh`. |

---

## 7. Runtime Verification Evidence

* **Automated Unit Tests**:
  ```bash
  PYTHONPATH=. pytest tests/test_portals.py
  # Result: 8 passed in 0.41s
  ```
* **Endpoint Health Verification**:
  ```bash
  curl -I http://127.0.0.1:5000/operations
  # Result: HTTP/1.1 200 OK
  ```
