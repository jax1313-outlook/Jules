"""
Dispatch Presentation Layer Flask Application
Integrates Driver Portal, Operations Portal, External Stakeholder Portal, and Public Website.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from dispatch_spine import spine_store, CONSEQUENCE_LABELS, LEVEL_0_SILENT_LOG
import os

app = Flask(__name__)

# Legacy Alias & Redirect Routes to wire legacy L2-COS / Portal URLs
@app.route("/portal")
@app.route("/cos")
@app.route("/l2-cos")
@app.route("/dashboard")
@app.route("/admin")
def legacy_portal_redirect():
    """Redirects legacy portal URLs seamlessly to the Dispatch Operations Portal."""
    return redirect(url_for("operations_portal"))

# ---------------------------------------------------------
# PUBLIC WEBSITE ROUTES (Presentation Layer v2)
# Positioning: Jacksonville Regional Micro-Response Carrier™
# ---------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/capabilities")
def capabilities():
    return render_template("capabilities.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------------------------------------------------
# PRESENTATION LAYER #1: DRIVER PORTAL
# Truck-cab operational cockpit
# ---------------------------------------------------------

@app.route("/driver")
def driver_portal():
    trip = spine_store.active_trip
    # Driver cards: filter out silent logs, prioritize active operational alerts
    cards = spine_store.get_cards_by_consequence(min_level=1)
    comi_cards = [c for c in spine_store.comi_cards if c.recipient_role in ['Driver', 'All']]
    return render_template("driver.html", trip=trip, cards=cards, comi_cards=comi_cards)


# ---------------------------------------------------------
# PRESENTATION LAYER #2: OPERATIONS / MANAGEMENT PORTAL
# Digital backroom office view
# ---------------------------------------------------------

@app.route("/operations")
def operations_portal():
    work_items = list(spine_store.work_items.values())
    all_cards = list(spine_store.portal_cards.values())
    comi_queue = spine_store.comi_cards

    # Categorize cards by level
    decision_cards = [c for c in all_cards if c.card_level == 3]
    conflict_cards = [c for c in all_cards if c.card_level == 4]
    authority_cards = [c for c in all_cards if c.card_level == 5]
    review_cards = [c for c in all_cards if c.card_level == 2]
    status_cards = [c for c in all_cards if c.card_level == 1]

    return render_template("operations.html",
                           work_items=work_items,
                           decision_cards=decision_cards,
                           conflict_cards=conflict_cards,
                           authority_cards=authority_cards,
                           review_cards=review_cards,
                           status_cards=status_cards,
                           comi_queue=comi_queue,
                           consequence_labels=CONSEQUENCE_LABELS)


# ---------------------------------------------------------
# PRESENTATION LAYER #3: EXTERNAL STAKEHOLDER PORTAL
# Role-Based External Visibility Window (Customer, Shipper, Broker)
# ---------------------------------------------------------

def sanitize_stakeholder_shipment(trip, role="Broker"):
    role_clean = role.strip().capitalize() if role else "Broker"
    if role_clean not in ["Broker", "Shipper", "Customer"]:
        role_clean = "Broker"

    base = {
        "load_number": trip.load_number if hasattr(trip, 'load_number') else trip.get("load_number"),
        "status": trip.status if hasattr(trip, 'status') else trip.get("status"),
        "consignee_name": trip.consignee_name if hasattr(trip, 'consignee_name') else "Savannah Distribution",
        "delivery_location": "Savannah, GA",
        "delivery_window": trip.delivery_window if hasattr(trip, 'delivery_window') else trip.get("est_delivery", "Pending"),
        "route_visibility_status": "On Route - Normal Transit",
        "pod_availability": "Available upon delivery completion" if getattr(trip, 'pod_status', '') != "APPROVED_BY_MIKE" else "POD Verified & Available",
        "role": role_clean,
        "contact_support": "Level 1 Transport Dispatch Direct: (904) 555-0100"
    }

    if role_clean in ["Broker", "Shipper"]:
        base["shipper_name"] = getattr(trip, 'shipper_name', 'Jacksonville Terminal')
        base["pickup_location"] = "Jacksonville, FL"
        base["cargo_description"] = getattr(trip, 'cargo_description', 'Industrial Cargo')
        base["route_risk_public_notice"] = getattr(trip, 'route_risk_summary', 'Clear transit') if getattr(trip, 'route_risk_level', 'LOW') != "LOW" else "Clear weather and traffic along route."
        base["bol_status"] = getattr(trip, 'bol_status', 'VERIFIED')

    if role_clean == "Broker":
        base["invoice_packet_status"] = "Pending Delivery Confirmation"
        base["broker_reference"] = getattr(trip, 'broker_reference', 'SE-88941-X')

    return base

@app.route("/stakeholder")
def stakeholder_portal():
    load_ref = request.args.get("ref", "L1T-2026-8804")
    role = request.args.get("role", "Broker")
    trip = spine_store.active_trip

    sanitized_shipment = sanitize_stakeholder_shipment(trip, role=role)
    return render_template("stakeholder.html", shipment=sanitized_shipment, role=sanitized_shipment["role"])


# ---------------------------------------------------------
# REST API ENDPOINTS
# Connecting presentation layers to Dispatch Spine
# ---------------------------------------------------------

@app.route("/api/v1/driver/active-trip", methods=["GET"])
def api_driver_active_trip():
    return jsonify(spine_store.active_trip.__dict__)

@app.route("/api/v1/driver/search-loads", methods=["GET"])
def api_driver_search_loads():
    query = request.args.get("q", "")
    results = spine_store.search_loads(query)
    return jsonify({"query": query, "count": len(results), "results": results})

@app.route("/api/v1/driver/upload-pod", methods=["POST"])
def api_driver_upload_pod():
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    saved_filename = None
    if "pod_file" in request.files:
        file = request.files["pod_file"]
        if file and file.filename:
            saved_filename = secure_filename(file.filename)
            file.save(os.path.join(upload_dir, saved_filename))

    spine_store.active_trip.pod_status = "UPLOADED"
    return jsonify({
        "status": "success",
        "message": "POD uploaded successfully and queued for Publisher review.",
        "pod_status": "UPLOADED",
        "file_saved": saved_filename if saved_filename else "Simulated upload"
    })

@app.route("/api/v1/operations/cards", methods=["GET"])
def api_operations_cards():
    min_level = int(request.args.get("min_level", 0))
    cards = spine_store.get_cards_by_consequence(min_level)
    return jsonify([c.__dict__ for c in cards])

@app.route("/api/v1/operations/action", methods=["POST"])
def api_operations_action():
    data = request.json or {}
    card_id = data.get("card_id")
    action = data.get("action")
    comments = data.get("comments", "")

    if not card_id or card_id not in spine_store.portal_cards:
        return jsonify({"status": "error", "message": "Card not found"}), 404

    card = spine_store.portal_cards[card_id]
    if action not in card.allowed_actions:
        return jsonify({"status": "error", "message": f"Action {action} not allowed for this card"}), 400

    # Process action
    work_item = spine_store.work_items.get(card.work_item_id)
    if work_item:
        if "APPROVE" in action:
            work_item.current_state = "MIKE_APPROVED"
            work_item.final_disposition = f"Approved by Mike: {action}"
        elif "REJECT" in action:
            work_item.current_state = "MIKE_REJECTED"
        elif "REQUEST_REVISION" in action:
            work_item.current_state = "MIKE_REQUESTED_REVISION"
        elif "PROMPT_DRIVER" in action:
            work_item.current_state = "ROUTED_TO_MANAGER"

    # Remove resolved card from active queue
    del spine_store.portal_cards[card_id]

    return jsonify({
        "status": "success",
        "message": f"Action '{action}' processed for Card '{card_id}'. Mike remains final authority.",
        "card_id": card_id,
        "new_work_item_state": work_item.current_state if work_item else "N/A"
    })

@app.route("/api/v1/stakeholder/shipment/<load_number>", methods=["GET"])
def api_stakeholder_shipment(load_number):
    # Strict Security Guardrail: Exclude internal scoring, internal notes, databases
    role = request.args.get("role", "Broker")
    if load_number == spine_store.active_trip.load_number:
        trip = spine_store.active_trip
        return jsonify(sanitize_stakeholder_shipment(trip, role=role))
    else:
        loads = spine_store.search_loads(load_number)
        if loads:
            load = loads[0]
            return jsonify(sanitize_stakeholder_shipment(load, role=role))
        return jsonify({"status": "error", "message": "Load reference not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
