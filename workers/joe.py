"""Joe Voice & Communication Worker Implementation.

Owns voice dictation capture, conversational session management, structured opportunity parsing,
driver routing, and Opportunity Card creation.

Constitutional Rule: JOE creates Opportunity Cards. JOE may not commit loads, accept offers,
or own dispatch workflow.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, Optional, List

from workers.base import (
    BaseWorker,
    WorkerConstitution,
    WorkerBoundaryViolationError,
)

JOE_CONSTITUTION = WorkerConstitution(
    worker_id="JOE",
    name="Joe Voice & Communication Worker",
    purpose="Voice capture, driver communication, dictation parsing, and opportunity card creation.",
    capabilities=[
        "voice_dictation_capture",
        "opportunity_card_creation",
        "driver_communication_routing",
        "70mph_cockpit_display",
        "conversational_session_management",
    ],
    boundaries={
        "may_commit": False,
        "may_own_workflow": False,
        "may_own_dispatch": False,
    },
    inputs=["raw_dictation_text", "driver_audio_stream", "driver_location"],
    outputs=["OpportunityCard", "DriverCockpitMessage"],
    relationships=["INTELLIGENCE", "MIKE"],
    handoffs=["INTELLIGENCE"],
    stop_conditions=["Commitment attempt", "Workflow ownership claim"],
    escalation_conditions=["Ambiguous voice capture", "Missing origin/destination"],
)


class ConversationalSession:
    """Manages active driver voice chat session state and history."""

    def __init__(self, session_id: str, driver_id: str = "DRIVER-01"):
        self.session_id = session_id
        self.driver_id = driver_id
        self.history: List[Dict[str, str]] = []
        self.pending_intent: Optional[Dict[str, Any]] = None

    def add_utterance(self, role: str, text: str) -> None:
        self.history.append({"role": role, "text": text})


class JoeWorker(BaseWorker):
    """Joe Worker executing bounded voice capture, conversational interaction, and opportunity creation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(constitution=JOE_CONSTITUTION, config=config)
        self.sessions: Dict[str, ConversationalSession] = {}

    def start_session(self, driver_id: str = "DRIVER-01") -> ConversationalSession:
        session_id = f"SESS-{uuid.uuid4().hex[:6]}"
        session = ConversationalSession(session_id=session_id, driver_id=driver_id)
        self.sessions[session_id] = session
        return session

    def process_utterance(self, session_id: str, utterance: str) -> Dict[str, Any]:
        """Process driver utterance, manage conversation flow, and format read-back."""
        session = self.sessions.get(session_id)
        if not session:
            session = self.start_session()

        session.add_utterance("driver", utterance)

        if "correction" in utterance.lower() or "change" in utterance.lower():
            response = "10-4, got your correction. What parameters need update?"
            session.add_utterance("joe", response)
            return {"response": response, "status": "AWAITING_CORRECTION"}

        parsed = self.parse_dictation(utterance)
        session.pending_intent = parsed

        response = (
            f"10-4. Read-back: Load from {parsed['origin_location']} to {parsed['destination_location']} "
            f"offering ${parsed['offered_rate']:.0f} on {parsed['equipment_type']}. Submitting card for Mike review."
        )
        session.add_utterance("joe", response)
        return {
            "response": response,
            "status": "READBACK_GENERATED",
            "parsed_opportunity": parsed,
        }

    def parse_dictation(self, dictation_text: str) -> Dict[str, Any]:
        """Parse raw voice dictation text into structured load parameters."""
        dictation_clean = dictation_text.strip()
        if not dictation_clean:
            raise ValueError("Dictation text cannot be empty.")

        rate_match = re.search(r"\$([0-9,]+(?:\.[0-9]{2})?)", dictation_clean)
        offered_rate = float(rate_match.group(1).replace(",", "")) if rate_match else 0.0

        weight_match = re.search(r"([0-9,]+)\s*(?:lbs|pounds|k\s*lbs)", dictation_clean, re.IGNORECASE)
        weight_lbs = float(weight_match.group(1).replace(",", "")) if weight_match else 40000.0

        route_match = re.search(
            r"from\s+([A-Za-z0-9\s,]+?)\s+to\s+([A-Za-z0-9\s,]+?)(?:\s+for|\s+on|\s+\$|\.|$)",
            dictation_clean,
            re.IGNORECASE,
        )
        origin = route_match.group(1).strip() if route_match else "Atlanta, GA"
        destination = route_match.group(2).strip() if route_match else "Chicago, IL"

        equipment = "53FT DRY VAN"
        dict_lower = dictation_clean.lower()
        if "reefer" in dict_lower:
            equipment = "53FT REEFER"
        elif "flatbed" in dict_lower:
            equipment = "FLATBED"

        opportunity_id = f"OPP-JOE-{uuid.uuid4().hex[:8]}"
        return {
            "opportunity_id": opportunity_id,
            "source": "JOE_VOICE_CAPTURE",
            "customer": "DIRECT_VOICE_INTAKE",
            "origin_location": origin,
            "destination_location": destination,
            "offered_rate": offered_rate,
            "estimated_miles": 750.0,
            "weight_lbs": weight_lbs,
            "equipment_type": equipment,
            "raw_dictation": dictation_clean,
            "status": "UNEVALUATED",
        }

    def create_opportunity_card(self, dictation_text: str) -> Dict[str, Any]:
        """Parse dictation and create an Opportunity Card payload."""
        parsed = self.parse_dictation(dictation_text)
        self.state = "OPPORTUNITY_CREATED"
        return parsed

    def commit_load(self, opportunity_id: str, actor_id: str = "JOE") -> None:
        """Constitutional Guard: JOE is strictly forbidden from committing loads."""
        self.verify_authority("COMMIT_LOAD", actor_id=actor_id)
        raise WorkerBoundaryViolationError("JOE worker is forbidden from committing loads.")
