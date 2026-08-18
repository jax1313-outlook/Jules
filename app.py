"""
Dispatch Presentation Layer Flask Application
Integrates Driver Portal, Operations Portal, External Stakeholder Portal, and Public Website.
"""

from flask import Flask, render_template, request, jsonify
from dispatch_spine import spine_store, CONSEQUENCE_LABELS, LEVEL_0_SILENT_LOG
import os

app = Flask(__name__)

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
# Broker / Shipper confidence-building window
# ---------------------------------------------------------

@app.route("/stakeholder")
def stakeholder_portal():
    # Sanitized view: load number search or active shipment progress
    load_ref = request.args.get("ref", "L1T-2026-8804")
    trip = spine_store.active_trip

    # Sanitized data extraction (strictly NO internal scores, raw cognitive notes, or database access)
    sanitized_shipment = {
        "load_number": trip.load_number,
        "status": trip.status,
        "shipper_name": trip.shipper_name,
        "pickup_location": "Jacksonville, FL",
        "consignee_name": trip.consignee_name,
        "delivery_location": "Savannah, GA",
        "delivery_window": trip.delivery_window,
        "cargo_description": trip.cargo_description,
        "route_visibility_status": "On Route - Normal Transit",
        "route_risk_public_notice": trip.route_risk_summary if trip.route_risk_level != "LOW" else "Clear weather and traffic along route.",
        "pod_availability": "Available upon delivery completion",
        "bol_status": trip.bol_status,
        "invoice_packet_status": "Pending Delivery Confirmation",
        "contact_support": "Level 1 Transport Dispatch Direct: (904) 555-0100"
    }

    return render_template("stakeholder.html", shipment=sanitized_shipment)


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
    # Mock POD upload trigger
    spine_store.active_trip.pod_status = "UPLOADED"
    # Create COMI notification for Operations
    return jsonify({
        "status": "success",
        "message": "POD uploaded successfully and queued for Publisher review.",
        "pod_status": "UPLOADED"
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
    if load_number == spine_store.active_trip.load_number:
        trip = spine_store.active_trip
        return jsonify({
            "load_number": trip.load_number,
            "status": trip.status,
            "origin": trip.pickup_location.split(",")[1].strip() if "," in trip.pickup_location else "Jacksonville",
            "destination": trip.delivery_location.split(",")[1].strip() if "," in trip.delivery_location else "Savannah",
            "est_delivery": trip.delivery_window,
            "public_route_notice": trip.route_risk_summary if trip.route_risk_level != "LOW" else "On schedule",
            "pod_available": trip.pod_status == "APPROVED_BY_MIKE"
        })
    else:
        loads = spine_store.search_loads(load_number)
        if loads:
            load = loads[0]
            return jsonify({
                "load_number": load["load_number"],
                "status": load["status"],
                "origin": load["origin"],
                "destination": load["destination"],
                "est_delivery": load["est_delivery"],
                "public_route_notice": load["sanitized_route_risk"],
                "pod_available": load["status"] == "DELIVERED"
            })
        return jsonify({"status": "error", "message": "Load reference not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
