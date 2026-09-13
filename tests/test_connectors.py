"""Tests for Bounded Workers (Joe, Intelligence, Publisher), Spine Watchdogs, IFTA, Settlements, & Outlook Connectors."""

import pytest
from datetime import datetime, timedelta, timezone
from workers.base import WorkerBoundaryViolationError, HumanCommitmentRequiredError
from workers.joe import JoeWorker
from workers.intelligence import IntelligenceWorker
from workers.publisher import PublisherWorker
from adapters.outlook_connectors import OutlookConnector, ConnectorStatus
from dispatch_spine import spine_store


def test_joe_worker_dictation_parsing():
    joe = JoeWorker()
    dictation = "Got a load from Jacksonville, FL to Savannah, GA for $1,800 on 53ft reefer 42,000 lbs"
    card = joe.create_opportunity_card(dictation)

    assert card["origin_location"] == "Jacksonville, FL"
    assert card["destination_location"] == "Savannah, GA"
    assert card["offered_rate"] == 1800.0
    assert card["equipment_type"] == "53FT REEFER"
    assert card["weight_lbs"] == 42000.0
    assert card["status"] == "UNEVALUATED"


def test_joe_worker_commit_guard():
    joe = JoeWorker()
    with pytest.raises((WorkerBoundaryViolationError, HumanCommitmentRequiredError)):
        joe.commit_load("OPP-123")


def test_intelligence_worker_scoring():
    intel = IntelligenceWorker()
    card_data = {
        "opportunity_id": "OPP-99",
        "offered_rate": 2000.0,
        "estimated_miles": 500.0,
    }
    scored = intel.evaluate_capacity_and_score(card_data)

    assert scored["rpm"] == 4.0
    assert scored["score"] == 100.0
    assert scored["status"] == "SCORED"
    assert "rate_rpm_score" in scored["scoring_breakdown"]
    assert "Mike decides" in scored["notice"]


def test_intelligence_worker_commit_guard():
    intel = IntelligenceWorker()
    with pytest.raises((WorkerBoundaryViolationError, HumanCommitmentRequiredError)):
        intel.commit_opportunity("OPP-99")


def test_publisher_worker_packet_drafting():
    pub = PublisherWorker()
    trip_data = {
        "load_number": "L1T-2026-9901",
        "offered_rate": 2500.0,
        "detention_fee": 150.0,
    }
    packet = pub.draft_rate_confirmation_packet(trip_data)

    assert packet["load_number"] == "L1T-2026-9901"
    assert packet["total_rate"] == 2650.0
    assert packet["status"] == "DRAFT"
    assert packet["requires_human_review"] is True
    assert "LEVEL 1 TRANSPORT RATE CONFIRMATION" in packet["content"]


def test_publisher_driver_settlement_drafting():
    pub = PublisherWorker()
    settlement_input = {
        "driver_id": "DRIVER-88",
        "load_number": "L1T-2026-8804",
        "gross_pay": 1200.0,
        "fuel_deduction": 250.0,
        "other_deductions": 50.0,
    }
    stmt = pub.draft_driver_settlement(settlement_input)

    assert stmt["driver_id"] == "DRIVER-88"
    assert stmt["gross_pay"] == 1200.0
    assert stmt["fuel_deduction"] == 250.0
    assert stmt["net_pay"] == 900.0
    assert stmt["status"] == "DRAFT_PENDING_APPROVAL"
    assert stmt["requires_mike_approval"] is True


def test_publisher_broker_invoice_verification():
    pub = PublisherWorker()
    packet_meta = {
        "load_number": "L1T-2026-8804",
        "has_rate_con": True,
        "has_bol": True,
        "has_pod": False,
    }
    res = pub.verify_broker_invoice_packet(packet_meta)

    assert res["is_complete"] is False
    assert "PROOF_OF_DELIVERY" in res["missing_documents"]
    assert res["status"] == "INCOMPLETE_MISSING_DOCS"


def test_spine_driver_settlement_payroll_processing():
    res = spine_store.process_driver_settlement_payroll("DRIVER-01", 1500.0, 300.0)

    assert res["settlement_statement"]["net_pay"] == 1200.0
    assert res["portal_card"].card_level == 2
    assert "Driver Settlement Approval" in res["portal_card"].title


def test_publisher_ifta_receipt_parsing():
    pub = PublisherWorker()
    receipt_data = {
        "gallons": 120.5,
        "jurisdiction_state": "GA",
        "total_cost": 450.0,
        "fuel_type": "DIESEL",
        "tax_paid": True
    }
    parsed = pub.parse_ifta_receipt(receipt_data)

    assert parsed["jurisdiction_state"] == "GA"
    assert parsed["gallons"] == 120.5
    assert parsed["status"] == "PARSED_FOR_IFTA_REVIEW"
    assert parsed["requires_mike_approval"] is True


def test_ifta_summary_aggregation():
    spine_store.ifta_fuel_log.append({
        "jurisdiction_state": "FL",
        "gallons": 50.0
    })
    summary = spine_store.aggregate_ifta_summary("Q3-2026")

    assert summary["quarter"] == "Q3-2026"
    assert summary["total_miles"] == 355.0
    assert summary["total_gallons"] == 50.0
    assert "portal_card_id" in summary


def test_detention_time_calculation():
    now = datetime.now(timezone.utc)
    arr = (now - timedelta(hours=4, minutes=30)).isoformat()
    dep = now.isoformat()

    spine_store.active_trip.arrival_timestamp = arr
    spine_store.active_trip.departure_timestamp = dep

    det = spine_store.calculate_detention()
    assert det["billable_hours"] == 2.5
    assert det["detention_fee"] == 187.50
    assert det["status"] == "BILLABLE_DETENTION"


def test_publisher_pod_exception_detection():
    pub = PublisherWorker()
    pod_meta = {
        "filename": "pod_l1t_8798.pdf",
        "has_signature": True,
        "has_lumper_fee": True,
        "lumper_receipt_attached": False
    }
    finding = pub.detect_pod_exceptions(pod_meta)

    assert finding["status"] == "EXCEPTION_DETECTED"
    assert "MISSING_LUMPER_RECEIPT_SCAN" in finding["exceptions"]
    assert finding["consequence_level"] == 4
    assert finding["requires_mike_adjudication"] is True


def test_stalled_load_watchdog():
    now = datetime.now(timezone.utc)
    stale_time = (now - timedelta(hours=4)).isoformat()
    spine_store.active_trip.last_status_update = stale_time
    stalled_cards = spine_store.check_stalled_loads(timeout_minutes=180)

    assert len(stalled_cards) > 0
    assert "Stalled Load Warning" in stalled_cards[0].title
    assert stalled_cards[0].card_level == 2


def test_publisher_worker_submit_guard():
    pub = PublisherWorker()
    with pytest.raises((WorkerBoundaryViolationError, HumanCommitmentRequiredError)):
        pub.submit_packet("PKT-123")


def test_outlook_connector_unconfigured_boundary():
    connector = OutlookConnector()
    res = connector.fetch_emails()

    assert res["status"] == ConnectorStatus.UNCONFIGURED.value
    assert "not configured" in res["reason"]


def test_outlook_connector_offline_queueing():
    connector = OutlookConnector()
    evt = {"type": "EMAIL_RECEIVED", "id": "MSG-001"}
    q_res = connector.queue_webhook_event(evt)

    assert q_res["status"] == "success"
    assert q_res["queue_depth"] == 1

    processed = connector.process_offline_queue()
    assert len(processed) == 1
    assert processed[0]["status"] == "PROCESSED"
    assert len(connector.offline_queue) == 0
