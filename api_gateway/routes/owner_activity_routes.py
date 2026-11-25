import logging

from fastapi import APIRouter, Depends, HTTPException

from api_gateway.middleware.auth_middleware import require_admin_or_owner
from api_gateway.services.activity_store import (
    fetch_activity_overview,
    fetch_recent_activity,
)


logger = logging.getLogger("genxbaby-pricing-engine.owner-activity")

router = APIRouter(
    tags=["Owner Pricing Activity"],
    dependencies=[Depends(require_admin_or_owner)],
)


def _load_overview(days=30):
    try:
        return fetch_activity_overview(days=days)
    except Exception as exc:
        logger.error(
            "Owner activity overview unavailable (%s).",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Pricing activity data is currently unavailable.",
        )


@router.get("/owners/revenue/summary")
def owner_revenue_summary(days: int = 30):
    """Report quote activity without misrepresenting it as realized revenue."""

    overview = _load_overview(days)

    return {
        "period_days": overview["period_days"],
        "total_quote_requests": overview["quote_requests"],
        "successful_events": overview["successful_events"],
        "failed_events": overview["failed_events"],
        "estimated_revenue_available": False,
        "estimated_margin_available": False,
        "revenue_note": (
            "The pricing engine records quote activity, not funded loans "
            "or realized revenue."
        ),
    }


@router.get("/owners/fraud/summary")
def owner_pricing_controls_summary(days: int = 30):
    """Report observed validation and pricing-control events only."""

    overview = _load_overview(days)

    control_actions = {
        "QUOTE_VALIDATION_FAILED",
        "QUOTE_REJECTED",
        "MATRIX_VALIDATION_FAILED",
    }

    observed_controls = [
        item
        for item in overview["by_action"]
        if item["action"] in control_actions
    ]

    return {
        "period_days": overview["period_days"],
        "control_events": sum(
            item["event_count"] for item in observed_controls
        ),
        "observed_control_actions": observed_controls,
        "fraud_scores_available": False,
        "note": (
            "These are recorded pricing-control events, not fraud "
            "determinations or borrower risk scores."
        ),
    }


@router.get("/owners/behavior/summary")
def owner_pricing_behavior_summary(days: int = 30):
    """Summarize actual pricing-engine activity by action and module."""

    overview = _load_overview(days)

    return {
        "period_days": overview["period_days"],
        "total_events": overview["total_events"],
        "by_action": overview["by_action"],
        "by_module": overview["by_module"],
    }


@router.get("/owners/execution/summary")
def owner_pricing_execution_summary(days: int = 30):
    """Report observed pricing API performance and matrix activity."""

    overview = _load_overview(days)

    return {
        "period_days": overview["period_days"],
        "total_events": overview["total_events"],
        "successful_events": overview["successful_events"],
        "failed_events": overview["failed_events"],
        "quote_requests": overview["quote_requests"],
        "matrix_events": overview["matrix_events"],
        "average_duration_ms": overview["average_duration_ms"],
        "p95_duration_ms": overview["p95_duration_ms"],
        "by_module": overview["by_module"],
        "performance_note": (
            "These measurements describe recorded pricing-engine "
            "operations, not secondary-market execution or P&L."
        ),
    }


@router.get("/pricing/audit-log/recent")
def recent_pricing_activity(limit: int = 50):
    """Return recent activity records to authorized administrators/owners."""

    try:
        return fetch_recent_activity(limit=limit)
    except Exception as exc:
        logger.error(
            "Recent pricing activity unavailable (%s).",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Pricing audit activity is currently unavailable.",
        )