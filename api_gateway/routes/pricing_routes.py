import json
import math
import os
import tempfile
import time

from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, StrictFloat, StrictInt, StrictStr

from shared.engine_registry import get_engines, MatrixActivationError, replace_matrix_and_refresh
from shared.borrower_rules import validate_borrower, BorrowerValidationError
from shared.matrix_loader import resolve_matrix_path, validate_matrix
from api_gateway.middleware.auth_middleware import require_admin_or_owner
from api_gateway.services.activity_store import record_activity


router = APIRouter(tags=["Pricing"])



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
        engine_v1, engine_v2 = get_engines()
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
        engine_v1, engine_v2 = get_engines()
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

class BaseRateUpdate(BaseModel):
    product_type: StrictStr
    base_rate: StrictFloat | StrictInt


def _base_rate_matrix():
    """Read the active matrix using the shared path and validation rules."""
    from shared.matrix_loader import load_matrix

    path = resolve_matrix_path()

    try:
        return path, load_matrix(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Pricing matrix file not found.")
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Pricing matrix validation failed: {exc}",
        )
    except OSError:
        raise HTTPException(status_code=500, detail="Unable to read pricing matrix.")


def _record_base_rate_event(user, status):
    """Record metadata only; logging must never change the API response."""
    try:
        record_activity(
            action="BASE_RATE_UPDATE",
            module="PRICING",
            actor_role=user.get("role", "UNKNOWN"),
            actor_id=user.get("user_id"),
            details={"section": "baseRates"},
            status=status,
        )
    except Exception:
        pass


@router.get("/base-rates")
def get_base_rates(
    _user: dict = Depends(require_admin_or_owner),
):
    """Return editable base rates to authorized administrators."""
    _, matrix = _base_rate_matrix()

    return [
        {"product_type": key, "base_rate": value}
        for key, value in matrix["baseRates"].items()
    ]


@router.put("/base-rates")
def update_base_rate(
    update: BaseRateUpdate,
    user: dict = Depends(require_admin_or_owner),
):
    """Safely update one existing base rate in the active pricing matrix."""
    rate = update.base_rate

    try:
        numeric_rate = float(rate)
    except (OverflowError, TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="base_rate must be a finite positive number.",
        )

    if isinstance(rate, bool) or not math.isfinite(numeric_rate) or numeric_rate <= 0:
        raise HTTPException(
            status_code=422,
            detail="base_rate must be a finite positive number.",
        )

    matrix_path, matrix = _base_rate_matrix()

    if update.product_type not in matrix["baseRates"]:
        raise HTTPException(
            status_code=404,
            detail="Unknown product_type. Existing base rates were not changed.",
        )

    matrix["baseRates"][update.product_type] = numeric_rate

    try:
        validate_matrix(matrix)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Updated pricing matrix failed validation: {exc}",
        )

    temp_path = None

    try:
        matrix_path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            prefix="pricing_matrix_",
            dir=str(matrix_path.parent),
            delete=False,
        ) as temp_file:
            json.dump(matrix, temp_file, indent=4, ensure_ascii=False)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        replace_matrix_and_refresh(temp_path, matrix_path)
        temp_path = None
        _record_base_rate_event(user, "SUCCESS")

        return {
            "status": "ok",
            "product_type": update.product_type,
            "base_rate": matrix["baseRates"][update.product_type],
        }

    except (OSError, MatrixActivationError):
        _record_base_rate_event(user, "FAILURE")
        raise HTTPException(
            status_code=500,
            detail="Unable to save the updated base rate.",
        )

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
