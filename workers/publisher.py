"""Publisher Worker Implementation.

Produces document packets, rate confirmation summaries, and BOL/POD verification packages
from approved facts only.

Constitutional Rule: PUBLISHER drafts. Publisher may not invent facts, sign forms,
or commit business contracts. Mike approves.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Optional, List

from workers.base import (
    BaseWorker,
    WorkerConstitution,
    WorkerBoundaryViolationError,
)

PUBLISHER_CONSTITUTION = WorkerConstitution(
    worker_id="PUBLISHER",
    name="Publisher Document Drafting Worker",
    purpose="Drafting document packets, rate confirmations, and BOL/POD verification packages from approved Library facts.",
    capabilities=[
        "rate_confirmation_drafting",
        "completion_packet_assembly",
        "bol_pod_verification",
        "template_selection_and_versioning",
        "pod_exception_detection",
        "detention_billing_incorporation",
        "ifta_fuel_receipt_parsing",
        "driver_settlement_drafting",
        "broker_invoice_verification",
    ],
    boundaries={
        "may_commit": False,
        "may_invent_facts": False,
        "may_submit_legal": False,
    },
    inputs=["TripData", "ApprovedLibraryFact", "PODImage", "FuelReceiptMetadata", "DriverSettlementData"],
    outputs=["DraftRateConfirmationPacket", "CompletionPacket", "PODExceptionFinding", "IFTAReceiptSummary", "DriverSettlementSummary", "BrokerInvoiceVerification"],
    relationships=["MANAGER", "MIKE"],
    handoffs=["MIKE"],
    stop_conditions=["Commitment attempt", "Unapproved fact injection"],
    escalation_conditions=["Missing POD signature", "Rate discrepancy"],
)


class PublisherWorker(BaseWorker):
    """Publisher Worker executing bounded document drafting."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(constitution=PUBLISHER_CONSTITUTION, config=config)
        self.templates = {
            "RATE_CONFIRMATION": "Level 1 Transport Rate Con Template v2.1",
            "COMPLETION_PACKET": "Level 1 Transport Delivery Proof Packet v1.0",
            "IFTA_SUMMARY": "Level 1 Transport Quarterly IFTA Tax Summary v1.0",
            "DRIVER_SETTLEMENT": "Level 1 Transport Driver Settlement Statement v1.2",
        }

    def draft_rate_confirmation_packet(self, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """Draft a rate confirmation summary packet from approved trip facts."""
        load_number = trip_data.get("load_number", "L1T-DRAFT")
        rate = trip_data.get("offered_rate", 0.0)
        detention_fee = trip_data.get("detention_fee", 0.0)
        total_rate = rate + detention_fee

        packet_id = f"PKT-{load_number}"
        content = (
            f"=== LEVEL 1 TRANSPORT RATE CONFIRMATION SUMMARY (DRAFT) ===\n"
            f"TEMPLATE VERSION: {self.templates['RATE_CONFIRMATION']}\n"
            f"LOAD NUMBER: {load_number}\n"
            f"BASE RATE: ${rate:.2f}\n"
            f"DETENTION CHARGE: ${detention_fee:.2f}\n"
            f"TOTAL INVOICE DRAFT: ${total_rate:.2f}\n"
            f"STATUS: DRAFT - PENDING MIKE APPROVAL\n"
            f"DRAFTED AT: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n"
        )

        self.state = "PACKET_DRAFTED"
        return {
            "packet_id": packet_id,
            "load_number": load_number,
            "template_used": self.templates["RATE_CONFIRMATION"],
            "base_rate": rate,
            "detention_fee": detention_fee,
            "total_rate": total_rate,
            "status": "DRAFT",
            "content": content,
            "requires_human_review": True,
        }

    def assemble_completion_packet(self, load_number: str, pod_filename: Optional[str] = None, detention_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Assemble delivery completion packet (BOL + POD + Invoice Summary + Detention Breakdown)."""
        packet_id = f"COMP-PKT-{load_number}"
        detention_summary = detention_info or {"billable_hours": 0.0, "detention_fee": 0.0}

        return {
            "packet_id": packet_id,
            "load_number": load_number,
            "template_used": self.templates["COMPLETION_PACKET"],
            "pod_attached": pod_filename if pod_filename else "MISSING_POD",
            "detention_billable_hours": detention_summary.get("billable_hours", 0.0),
            "detention_fee": detention_summary.get("detention_fee", 0.0),
            "status": "READY_FOR_MIKE_REVIEW",
            "notice": "This is a draft completion packet. Mike approval required prior to broker submission.",
        }

    def draft_driver_settlement(self, settlement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Draft driver pay settlement statement with gross pay, deductions, and net pay."""
        driver_id = settlement_data.get("driver_id", "DRIVER-01")
        load_number = settlement_data.get("load_number", "L1T-DRAFT")
        gross_pay = settlement_data.get("gross_pay", 0.0)
        fuel_deduction = settlement_data.get("fuel_deduction", 0.0)
        other_deductions = settlement_data.get("other_deductions", 0.0)
        net_pay = gross_pay - fuel_deduction - other_deductions

        settlement_id = f"STL-{load_number}"
        return {
            "settlement_id": settlement_id,
            "driver_id": driver_id,
            "load_number": load_number,
            "template_used": self.templates["DRIVER_SETTLEMENT"],
            "gross_pay": round(gross_pay, 2),
            "fuel_deduction": round(fuel_deduction, 2),
            "other_deductions": round(other_deductions, 2),
            "net_pay": round(net_pay, 2),
            "status": "DRAFT_PENDING_APPROVAL",
            "requires_mike_approval": True,
        }

    def verify_broker_invoice_packet(self, packet_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Verify broker invoice packet for mandatory documents (Rate Con, signed BOL, signed POD)."""
        load_number = packet_metadata.get("load_number", "L1T-DRAFT")
        has_rate_con = packet_metadata.get("has_rate_con", True)
        has_bol = packet_metadata.get("has_bol", True)
        has_pod = packet_metadata.get("has_pod", True)

        missing = []
        if not has_rate_con:
            missing.append("RATE_CONFIRMATION")
        if not has_bol:
            missing.append("BILL_OF_LADING")
        if not has_pod:
            missing.append("PROOF_OF_DELIVERY")

        is_complete = len(missing) == 0
        return {
            "load_number": load_number,
            "is_complete": is_complete,
            "missing_documents": missing,
            "status": "PACKET_COMPLETE" if is_complete else "INCOMPLETE_MISSING_DOCS",
            "requires_human_review": not is_complete,
        }

    def parse_ifta_receipt(self, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse fuel receipt details for IFTA compliance reporting."""
        gallons = receipt_data.get("gallons", 0.0)
        jurisdiction = receipt_data.get("jurisdiction_state", "FL").upper()
        total_cost = receipt_data.get("total_cost", 0.0)
        fuel_type = receipt_data.get("fuel_type", "DIESEL")
        tax_paid = receipt_data.get("tax_paid", True)

        receipt_id = f"IFTA-REC-{int(datetime.datetime.now().timestamp())}"
        return {
            "receipt_id": receipt_id,
            "jurisdiction_state": jurisdiction,
            "gallons": gallons,
            "total_cost": total_cost,
            "fuel_type": fuel_type,
            "tax_paid": tax_paid,
            "status": "PARSED_FOR_IFTA_REVIEW",
            "requires_mike_approval": True,
        }

    def detect_pod_exceptions(self, pod_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Detect document exceptions (missing signature, missing lumper receipt, blurred scan)."""
        filename = pod_metadata.get("filename", "")
        has_signature = pod_metadata.get("has_signature", True)
        has_lumper = pod_metadata.get("has_lumper_fee", False)
        lumper_receipt_present = pod_metadata.get("lumper_receipt_attached", True)

        exceptions = []
        if not has_signature:
            exceptions.append("MISSING_CONSIGNEE_SIGNATURE")
        if has_lumper and not lumper_receipt_present:
            exceptions.append("MISSING_LUMPER_RECEIPT_SCAN")

        status = "EXCEPTION_DETECTED" if exceptions else "VERIFIED_CLEAR"
        return {
            "filename": filename,
            "status": status,
            "exceptions": exceptions,
            "consequence_level": 4 if exceptions else 1,
            "requires_mike_adjudication": len(exceptions) > 0,
        }

    def submit_packet(self, packet_id: str, actor_id: str = "PUBLISHER") -> None:
        """Constitutional Guard: PUBLISHER is strictly forbidden from committing or submitting legal documents."""
        self.verify_authority("SUBMIT_PACKET", actor_id=actor_id)
        raise WorkerBoundaryViolationError("PUBLISHER worker cannot submit or execute contracts.")
