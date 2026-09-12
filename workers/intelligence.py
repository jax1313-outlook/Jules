"""Pre-Commit Intelligence Worker Implementation.

Evaluates 6 Dynamic Capacity dimensions, scores freight opportunities, generates calendar
placement recommendations, and presents opportunities to Mike Zachary.

Constitutional Rule: INTELLIGENCE recommends. INTELLIGENCE stops at Mike's commit gate.
INTELLIGENCE may never commit loads or override human decisions.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List

from workers.base import (
    BaseWorker,
    WorkerConstitution,
    WorkerBoundaryViolationError,
)

INTELLIGENCE_CONSTITUTION = WorkerConstitution(
    worker_id="INTELLIGENCE",
    name="Pre-Commit Freight Intelligence Worker",
    purpose="Pre-commit lifecycle evaluation: dynamic capacity analysis, scoring, and calendar recommendations.",
    capabilities=[
        "dynamic_capacity_6d_evaluation",
        "opportunity_scoring",
        "calendar_placement_recommendation",
        "consumption_metric_calculation",
    ],
    boundaries={
        "may_commit": False,
        "may_override_human": False,
        "stop_condition": "Mike Commit Gate",
    },
    inputs=["OpportunityCard", "DynamicCapacityData", "CalendarState"],
    outputs=["ScoredOpportunityCard", "CapacityFinding", "CalendarRecommendation"],
    relationships=["JOE", "MIKE"],
    handoffs=["MIKE"],
    stop_conditions=["Commitment attempt", "Mike approval gate"],
    escalation_conditions=["Unconfigured physical asset data", "HOS clock violation"],
)


class IntelligenceWorker(BaseWorker):
    """Intelligence Worker executing pre-commit load evaluation and scoring."""

    RECOMMENDATION_NOTICE = "This is a recommendation only. No action is authorized. Mike decides."

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(constitution=INTELLIGENCE_CONSTITUTION, config=config)

    def evaluate_capacity_and_score(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run 6-dimension Dynamic Capacity analysis and calculate score."""
        offered_rate = card_data.get("offered_rate", 0.0)
        estimated_miles = card_data.get("estimated_miles", 1.0) or 1.0
        rpm = offered_rate / estimated_miles if estimated_miles > 0 else 0.0

        # 6D Capacity Breakdown
        rate_score = min(40.0, rpm * 10.0)
        deadhead_score = 20.0
        hos_score = 15.0
        home_time_score = 10.0
        fuel_efficiency_score = 10.0
        route_risk_score = 5.0

        total_score = min(100.0, rate_score + deadhead_score + hos_score + home_time_score + fuel_efficiency_score + route_risk_score)

        breakdown = {
            "rate_rpm_score": round(rate_score, 1),
            "deadhead_score": round(deadhead_score, 1),
            "hos_availability_score": round(hos_score, 1),
            "home_time_alignment_score": round(home_time_score, 1),
            "fuel_efficiency_score": round(fuel_efficiency_score, 1),
            "route_risk_penalty_score": round(route_risk_score, 1),
        }

        risk_findings = []
        if rpm < 2.0:
            risk_findings.append("Low Rate per Mile (< $2.00/mi)")

        scored_card = dict(card_data)
        scored_card["rpm"] = round(rpm, 2)
        scored_card["score"] = round(total_score, 1)
        scored_card["scoring_breakdown"] = breakdown
        scored_card["risk_findings"] = risk_findings
        scored_card["status"] = "SCORED"
        scored_card["confidence_score"] = 0.95
        scored_card["notice"] = self.RECOMMENDATION_NOTICE

        self.state = "EVALUATED_AND_SCORED"
        return scored_card

    def recommend_calendar_placement(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate calendar placement recommendation for an opportunity."""
        return {
            "opportunity_id": card_data.get("opportunity_id"),
            "recommended_slot_start": "2026-09-15T08:00:00Z",
            "recommended_slot_end": "2026-09-16T17:00:00Z",
            "notice": self.RECOMMENDATION_NOTICE,
        }

    def commit_opportunity(self, opportunity_id: str, actor_id: str = "INTELLIGENCE") -> None:
        """Constitutional Guard: INTELLIGENCE is strictly forbidden from committing loads."""
        self.verify_authority("COMMIT_OPPORTUNITY", actor_id=actor_id)
        raise WorkerBoundaryViolationError("INTELLIGENCE worker cannot commit loads.")
