"""Joe Voice & Communication Worker Implementation.

Owns voice dictation capture, structured opportunity parsing, driver routing, and
Opportunity Card creation.

Constitutional Rule: JOE creates Opportunity Cards. JOE may not commit loads, accept offers,
or own dispatch workflow.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, Optional

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


class JoeWorker(BaseWorker):
    """Joe Worker executing bounded voice capture and opportunity creation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(constitution=JOE_CONSTITUTION, config=config)

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
        elif r"\bvan\b" in dict_lower:
            equipment = "53FT DRY VAN"

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
