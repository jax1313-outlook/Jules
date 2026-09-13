"""Tests for Bounded Workers (Joe, Intelligence, Publisher), Spine Watchdogs, & Outlook Connectors."""

import pytest
import datetime
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
    }
    packet = pub.draft_rate_confirmation_packet(trip_data)

    assert packet["load_number"] == "L1T-2026-9901"
    assert packet["status"] == "DRAFT"
    assert packet["requires_human_review"] is True
    assert "LEVEL 1 TRANSPORT RATE CONFIRMATION" in packet["content"]


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
    # Simulate active load with last status update 4 hours ago
    stale_time = (datetime.datetime.utcnow() - datetime.timedelta(hours=4)).isoformat() + "Z"
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
