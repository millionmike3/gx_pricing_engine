import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.pricing_engine import PricingEngine
from shared.pricing_engine_v2 import PricingEngineV2
from shared.borrower_rules import validate_borrower, BorrowerValidationError
from api_gateway.services.activity_store import record_activity


router = APIRouter(tags=["Pricing"])

engine_v1 = PricingEngine()
engine_v2 = PricingEngineV2()


class PricingRequest(BaseModel):
    fico: int
    ltv: float
    loan_amount: float
    investor: str | None = "SubstantialFunding"
    property_type: str | None = None
    occupancy: str | None = None
    purpose: str | None = "purchase"
    state: str | None = None
    dti: float | None = None
    dscr: float | None = None
    product_type: str | None = None
    rate_type: str | None = "30yr_fixed"
    first_time_homebuyer: bool = False
    bankruptcy_seasoning_under_2_years: bool = False
    foreclosure_seasoning_under_3_years: bool = False
    version: int = 1


def _record_event(action, status, started_at, details=None):
    """Record safe activity metadata without affecting pricing responses."""

    duration_ms = max(
        0,
        int((time.perf_counter() - started_at) * 1000),
    )

    try:
        record_activity(
            action=action,
            module="PRICING",
            actor_role="ANONYMOUS",
            actor_id=None,
            details=details or {},
            status=status,
            duration_ms=duration_ms,
        )
    except Exception:
        # Activity logging must never change quote behavior.
        pass


def normalized_params(req: PricingRequest):
    params = req.model_dump(exclude_none=True)

    try:
        borrower = validate_borrower(params)
    except BorrowerValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {**params, **borrower}


@router.post("/quote")
def get_quote(req: PricingRequest):
    started_at = time.perf_counter()

    if req.version not in (1, 2):
        _record_event(
            action="QUOTE_REJECTED",
            status="FAILURE",
            started_at=started_at,
            details={"reason": "INVALID_ENGINE_VERSION"},
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid version; must be 1 or 2"
        )

    try:
        params = normalized_params(req)
    except HTTPException as exc:
        action = (
            "QUOTE_VALIDATION_FAILED"
            if exc.status_code == 422
            else "QUOTE_REJECTED"
        )
        _record_event(
            action=action,
            status="FAILURE",
            started_at=started_at,
            details={"stage": "REQUEST_VALIDATION"},
        )
        raise

    try:
        if req.version == 1:
            result = engine_v1.calculate_price(params)
        else:
            result = engine_v2.calculate_price(params)

        _record_event(
            action="QUOTE_REQUEST",
            status="SUCCESS",
            started_at=started_at,
            details={"engine_version": req.version},
        )

        return {"version": req.version, "result": result}

    except (ValueError, FileNotFoundError) as exc:
        _record_event(
            action="QUOTE_REJECTED",
            status="FAILURE",
            started_at=started_at,
            details={
                "engine_version": req.version,
                "stage": "PRICE_CALCULATION",
            },
        )
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/quote/compare")
def compare_quote(req: PricingRequest):
    started_at = time.perf_counter()

    try:
        params = normalized_params(req)
    except HTTPException as exc:
        action = (
            "QUOTE_VALIDATION_FAILED"
            if exc.status_code == 422
            else "QUOTE_REJECTED"
        )
        _record_event(
            action=action,
            status="FAILURE",
            started_at=started_at,
            details={"stage": "REQUEST_VALIDATION"},
        )
        raise

    try:
        result_v1 = engine_v1.calculate_price(params)
        result_v2 = engine_v2.calculate_price(params)

    except (ValueError, FileNotFoundError) as exc:
        _record_event(
            action="QUOTE_REJECTED",
            status="FAILURE",
            started_at=started_at,
            details={
                "engine_versions": [1, 2],
                "stage": "PRICE_COMPARISON",
            },
        )
        raise HTTPException(status_code=422, detail=str(exc))

    _record_event(
        action="QUOTE_COMPARE",
        status="SUCCESS",
        started_at=started_at,
        details={"engine_versions": [1, 2]},
    )

    return {
        "v1": result_v1,
        "v2": result_v2,
        "delta": {
            "final_rate_diff": round(
                result_v2["final_rate"] - result_v1["final_rate"], 4
            )
        }
    }