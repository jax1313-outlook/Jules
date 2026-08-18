"""
Dispatch Spine Engine & Data Models for Level 1 Transport
Aligned with DISPATCH_SPINE_SPECIFICATION_v1.md, ALERT_GOVERNANCE_DOCTRINE.md, and PORTAL_DESCRIPTION.md.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Consequence Levels
LEVEL_0_SILENT_LOG = 0
LEVEL_1_STATUS = 1
LEVEL_2_REVIEW = 2
LEVEL_3_DECISION = 3
LEVEL_4_CONFLICT = 4
LEVEL_5_AUTHORITY = 5

CONSEQUENCE_LABELS = {
    0: "Silent Log",
    1: "Status",
    2: "Review",
    3: "Decision",
    4: "Conflict",
    5: "Authority"
}

# Required closing for Portal Cards
REQUIRED_CARD_CLOSING = "This is a recommendation only. No action is authorized. Mike decides."

# State List
VALID_STATES = [
    "CREATED", "VALIDATION_PENDING", "VALIDATION_FAILED", "VALIDATED",
    "SCORING_PENDING", "SCORED", "COGNITIVE_REVIEW_PENDING", "COGNITIVE_REVIEW_COMPLETE",
    "ROUTING_PENDING", "ROUTED_TO_MANAGER", "ROUTED_TO_INTELLIGENCE", "ROUTED_TO_PUBLISHER",
    "ROUTED_TO_LIBRARY_REVIEW", "ROUTED_TO_ARCHIVE", "PORTAL_CARD_PENDING",
    "PORTAL_CARD_CREATED", "WAITING_FOR_MIKE", "MIKE_APPROVED", "MIKE_REJECTED",
    "MIKE_REQUESTED_REVISION", "DEFERRED", "CONFLICT_RAISED", "CONFLICT_RESOLVED",
    "COMPLETED", "ARCHIVED"
]

@dataclass
class PortalCard:
    card_id: str
    work_item_id: str
    created_at: str
    card_level: int
    card_type: str  # e.g., 'DECISION', 'CONFLICT', 'REVIEW', 'STATUS'
    title: str
    summary: str
    source_refs: List[str]
    recommendation: str
    decision_needed: str
    allowed_actions: List[str]
    required_closing: str = REQUIRED_CARD_CLOSING

@dataclass
class COMICommunicationCard:
    comi_id: str
    load_number: str
    channel: str  # e.g., 'SMS', 'Portal Alert', 'Stakeholder Notification'
    recipient_role: str  # e.g., 'Broker', 'Shipper', 'Driver', 'Mike'
    subject: str
    message_body: str
    timestamp: str
    status: str  # e.g., 'QUEUED_FOR_MIKE', 'SENT', 'ARCHIVED'
    consequence_level: int = LEVEL_1_STATUS

@dataclass
class ActiveTrip:
    load_number: str
    status: str  # e.g., 'IN_TRANSIT', 'AT_PICKUP', 'DELIVERED', 'PENDING'
    shipper_name: str
    pickup_location: str
    pickup_window: str
    pickup_notes: str
    consignee_name: str
    delivery_location: str
    delivery_window: str
    delivery_notes: str
    broker_name: str
    broker_contact_phone: str
    broker_reference: str
    cargo_description: str
    weight_lbs: int
    piece_count: int
    route_notes: str
    route_risk_level: str  # 'LOW', 'MODERATE', 'HIGH'
    route_risk_summary: str
    pod_status: str  # 'PENDING_UPLOAD', 'UPLOADED', 'APPROVED_BY_MIKE'
    bol_status: str  # 'VERIFIED', 'PENDING'
    invoice_packet_status: str  # 'DRAFTING', 'READY_FOR_REVIEW', 'APPROVED'

@dataclass
class WorkItem:
    work_item_id: str
    created_at: str
    updated_at: str
    source_type: str
    source_id: str
    current_state: str
    priority: str
    consequence_level: int
    assigned_function: str
    required_action: str
    source_confidence: str
    due_date: Optional[str] = None
    related_files: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)
    validation_status: str = "PENDING"
    scoring_status: str = "NOT_REQUIRED"
    cognitive_status: str = "NOT_STARTED"
    portal_card_id: Optional[str] = None
    final_disposition: Optional[str] = None


class DispatchSpineDataStore:
    """In-memory Dispatch Spine repository holding state and cards."""
    def __init__(self):
        self.active_trip = ActiveTrip(
            load_number="L1T-2026-8804",
            status="IN_TRANSIT",
            shipper_name="Jacksonville Marine Terminal Pier 4",
            pickup_location="2050 Talleyrand Ave, Jacksonville, FL 32206",
            pickup_window="07:00 - 08:30 EST (Completed)",
            pickup_notes="Gate 3 entry, TWIC required, High-value machinery parts",
            consignee_name="Savannah Industrial Distribution Center",
            delivery_location="500 Gateway Blvd, Savannah, GA 31407",
            delivery_window="13:30 - 15:00 EST",
            delivery_notes="Dock 12, Check in at Guard Shack upon arrival.",
            broker_name="Southeast Logistics Partners",
            broker_contact_phone="(904) 555-0199",
            broker_reference="SE-88941-X",
            cargo_description="High-Precision CNC Spare Assemblies (4 Pallets)",
            weight_lbs=8400,
            piece_count=4,
            route_notes="I-95 Northbound. Construction delays near Kingsland, GA (MP 3).",
            route_risk_level="MODERATE",
            route_risk_summary="Heavy rain band moving through Glynn County between 11:30 and 13:00. 15 min estimated delay.",
            pod_status="PENDING_UPLOAD",
            bol_status="VERIFIED",
            invoice_packet_status="DRAFTING"
        )

        self.past_loads = [
            {
                "load_number": "L1T-2026-8804",
                "status": "IN_TRANSIT",
                "origin": "Jacksonville, FL",
                "destination": "Savannah, GA",
                "broker": "Southeast Logistics Partners",
                "pickup_time": "2026-08-18 07:15 EST",
                "est_delivery": "2026-08-18 14:15 EST",
                "sanitized_route_risk": "Rain band on I-95 N near Glynn County. Driver briefed."
            },
            {
                "load_number": "L1T-2026-8801",
                "status": "DELIVERED",
                "origin": "Brunswick, GA",
                "destination": "Jacksonville, FL",
                "broker": "Coastal Freight Direct",
                "pickup_time": "2026-08-16 09:00 EST",
                "est_delivery": "2026-08-16 12:30 EST",
                "sanitized_route_risk": "Clear"
            },
            {
                "load_number": "L1T-2026-8798",
                "status": "DELIVERED",
                "origin": "Orlando, FL",
                "destination": "Jacksonville, FL",
                "broker": "Sunshine Regional Logistics",
                "pickup_time": "2026-08-14 06:00 EST",
                "est_delivery": "2026-08-14 10:45 EST",
                "sanitized_route_risk": "Clear"
            }
        ]

        self.work_items: Dict[str, WorkItem] = {}
        self.portal_cards: Dict[str, PortalCard] = {}
        self.comi_cards: List[COMICommunicationCard] = []
        self._bootstrap_sample_data()

    def _bootstrap_sample_data(self):
        # Work item 1: Rate Confirmation Review (Level 3 - Decision)
        wi1_id = "wi-101"
        card1_id = "card-101"
        self.work_items[wi1_id] = WorkItem(
            work_item_id=wi1_id,
            created_at="2026-08-18T08:15:00Z",
            updated_at="2026-08-18T08:15:00Z",
            source_type="rate_confirmation",
            source_id="RC-SE-88941",
            current_state="WAITING_FOR_MIKE",
            priority="HIGH",
            consequence_level=LEVEL_3_DECISION,
            assigned_function="Manager",
            required_action="Approve detention rate terms in Rate Confirmation",
            source_confidence="SOURCE_PRESENT",
            portal_card_id=card1_id
        )
        self.portal_cards[card1_id] = PortalCard(
            card_id=card1_id,
            work_item_id=wi1_id,
            created_at="2026-08-18T08:15:00Z",
            card_level=LEVEL_3_DECISION,
            card_type="DECISION",
            title="Rate Confirmation Approval - Load L1T-2026-8804",
            summary="Southeast Logistics sent updated Rate Con ($1,450 base + $75/hr detention after 2 hrs).",
            source_refs=["doc_rc_88941.pdf"],
            recommendation="Approve rate confirmation terms. Detention clause aligns with standard carrier agreement.",
            decision_needed="Approve Rate Confirmation or Request Revision",
            allowed_actions=["APPROVE_RATE_CON", "REJECT_RATE_CON", "REQUEST_REVISION"]
        )

        # Work item 2: Conflict Card - Missing Lump Sum Receipt (Level 4 - Conflict)
        wi2_id = "wi-102"
        card2_id = "card-102"
        self.work_items[wi2_id] = WorkItem(
            work_item_id=wi2_id,
            created_at="2026-08-18T07:45:00Z",
            updated_at="2026-08-18T07:45:00Z",
            source_type="invoice_packet",
            source_id="INV-8798",
            current_state="CONFLICT_RAISED",
            priority="CRITICAL",
            consequence_level=LEVEL_4_CONFLICT,
            assigned_function="Publisher",
            required_action="Resolve missing lumper receipt for Load L1T-2026-8798",
            source_confidence="SOURCE_MISSING",
            portal_card_id=card2_id
        )
        self.portal_cards[card2_id] = PortalCard(
            card_id=card2_id,
            work_item_id=wi2_id,
            created_at="2026-08-18T07:45:00Z",
            card_level=LEVEL_4_CONFLICT,
            card_type="CONFLICT",
            title="Conflict: Missing Lumper Receipt - Load L1T-2026-8798",
            summary="Publisher attempted packet assembly for Invoice L1T-8798. Lumper fee of $120 listed on BOL but scan is missing.",
            source_refs=["bol_8798.pdf"],
            recommendation="Request lumper receipt photo from driver or waive fee on invoice.",
            decision_needed="Choose resolution path for missing documentation",
            allowed_actions=["PROMPT_DRIVER_PHOTO", "WAIVE_LUMPER_FEE", "MANUAL_OVERRIDE"]
        )

        # Work item 3: System Authority / Key Rotation Prompt (Level 5 - Authority)
        wi3_id = "wi-103"
        card3_id = "card-103"
        self.work_items[wi3_id] = WorkItem(
            work_item_id=wi3_id,
            created_at="2026-08-18T06:00:00Z",
            updated_at="2026-08-18T06:00:00Z",
            source_type="security_audit",
            source_id="SEC-KEY-2026-08",
            current_state="WAITING_FOR_MIKE",
            priority="HIGH",
            consequence_level=LEVEL_5_AUTHORITY,
            assigned_function="Manager",
            required_action="Authorize JAXPORT API Key Secret Renewal",
            source_confidence="SOURCE_PRESENT",
            portal_card_id=card3_id
        )
        self.portal_cards[card3_id] = PortalCard(
            card_id=card3_id,
            work_item_id=wi3_id,
            created_at="2026-08-18T06:00:00Z",
            card_level=LEVEL_5_AUTHORITY,
            card_type="AUTHORITY",
            title="System Authority: JAXPORT API Key Secret Renewal",
            summary="JAXPORT terminal gateway secret expires in 7 days. Renewal payload prepared.",
            source_refs=["sec_spec_v1.md"],
            recommendation="Authorize API Key rotation for JAXPORT integration.",
            decision_needed="Final Mike authorization required to apply new API secret",
            allowed_actions=["AUTHORIZE_KEY_ROTATION", "DEFER_SECURITY_KEY"]
        )

        # Work item 4: Library Candidate Review (Level 2 - Review)
        wi4_id = "wi-104"
        card4_id = "card-104"
        self.work_items[wi4_id] = WorkItem(
            work_item_id=wi4_id,
            created_at="2026-08-17T16:00:00Z",
            updated_at="2026-08-17T16:00:00Z",
            source_type="library_candidate",
            source_id="LIB-CAND-2026-04",
            current_state="ROUTED_TO_LIBRARY_REVIEW",
            priority="LOW",
            consequence_level=LEVEL_2_REVIEW,
            assigned_function="Intelligence Analyst",
            required_action="Review standard TWIC gate entry protocol template for JAXPORT",
            source_confidence="SOURCE_PRESENT",
            portal_card_id=card4_id
        )
        self.portal_cards[card4_id] = PortalCard(
            card_id=card4_id,
            work_item_id=wi4_id,
            created_at="2026-08-17T16:00:00Z",
            card_level=LEVEL_2_REVIEW,
            card_type="REVIEW",
            title="Library Candidate: JAXPORT Pier 4 Entry SOP",
            summary="Intelligence Analyst compiled verified TWIC entry procedures into reusable Library asset.",
            source_refs=["jaxport_sop_v1.txt"],
            recommendation="Promote SOP to Library active store for driver route notes.",
            decision_needed="Approve Library Promotion or Archive Candidate",
            allowed_actions=["APPROVE_LIBRARY_PROMOTION", "ARCHIVE_CANDIDATE"]
        )

        # Work item 5: Archive Retention Prompt (Level 2 - Review)
        wi5_id = "wi-105"
        card5_id = "card-105"
        self.work_items[wi5_id] = WorkItem(
            work_item_id=wi5_id,
            created_at="2026-08-17T18:00:00Z",
            updated_at="2026-08-17T18:00:00Z",
            source_type="archive_review",
            source_id="ARC-2026-07-BATCH",
            current_state="ROUTED_TO_ARCHIVE",
            priority="LOW",
            consequence_level=LEVEL_2_REVIEW,
            assigned_function="Manager",
            required_action="Review July 2026 completed trip records for Archive lock",
            source_confidence="SOURCE_PRESENT",
            portal_card_id=card5_id
        )
        self.portal_cards[card5_id] = PortalCard(
            card_id=card5_id,
            work_item_id=wi5_id,
            created_at="2026-08-17T18:00:00Z",
            card_level=LEVEL_2_REVIEW,
            card_type="REVIEW",
            title="Archive Review: July 2026 Completed Trip Records",
            summary="18 trip records for July 2026 have passed 30-day operational retention window.",
            source_refs=["archive_index_2026_07.json"],
            recommendation="Lock July 2026 batch into immutable Archive.",
            decision_needed="Confirm Archive Lock",
            allowed_actions=["CONFIRM_ARCHIVE_LOCK", "EXTEND_RETENTION"]
        )

        # COMI Cards
        self.comi_cards = [
            COMICommunicationCard(
                comi_id="comi-201",
                load_number="L1T-2026-8804",
                channel="SMS / Portal",
                recipient_role="Driver",
                subject="Route Risk Update: Rain Band on I-95 N",
                message_body="Heavy rain reported MP 25-40 on I-95 N. Speed reduced to 55 MPH. ETA adjusted +15 min.",
                timestamp="2026-08-18 10:15 EST",
                status="SENT",
                consequence_level=LEVEL_1_STATUS
            ),
            COMICommunicationCard(
                comi_id="comi-202",
                load_number="L1T-2026-8804",
                channel="Stakeholder Portal",
                recipient_role="Broker",
                subject="ETA Update - Load L1T-2026-8804",
                message_body="Load in transit on schedule. Revised delivery ETA 14:15 EST due to rain band.",
                timestamp="2026-08-18 10:20 EST",
                status="QUEUED_FOR_MIKE",
                consequence_level=LEVEL_2_REVIEW
            ),
            COMICommunicationCard(
                comi_id="comi-203",
                load_number="L1T-2026-8801",
                channel="Email via Publisher",
                recipient_role="Broker",
                subject="POD & Invoice Packet - L1T-2026-8801",
                message_body="POD signed and verified. Final invoice packet prepared for Southeast Freight.",
                timestamp="2026-08-16 14:00 EST",
                status="SENT",
                consequence_level=LEVEL_1_STATUS
            )
        ]

    def get_cards_by_consequence(self, min_level: int = 0) -> List[PortalCard]:
        return [card for card in self.portal_cards.values() if card.card_level >= min_level]

    def search_loads(self, query: str) -> List[Dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return self.past_loads
        results = []
        for load in self.past_loads:
            if (q in load["load_number"].lower() or
                q in load["broker"].lower() or
                q in load["origin"].lower() or
                q in load["destination"].lower() or
                q in load["status"].lower()):
                results.append(load)
        return results


# Global singleton store
spine_store = DispatchSpineDataStore()
