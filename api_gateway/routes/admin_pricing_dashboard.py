from fastapi import APIRouter, HTTPException, Depends
from api_gateway.middleware.auth_middleware import require_admin_or_owner

from shared.pricing_engine import PricingEngine
from shared.borrower_rules import validate_borrower, BorrowerValidationError
from api_gateway.routes.matrix_routes import MATRIX_PATH, load_matrix

router = APIRouter(tags=["Admin Pricing Dashboard"], dependencies=[Depends(require_admin_or_owner)])
engine = PricingEngine()


@router.get("/matrix")
def admin_get_matrix():
    return load_matrix()


@router.post("/test-scenario")
def admin_test_scenario(payload: dict):
    try:
        borrower = validate_borrower(payload)
        params = {**payload, **borrower}
        result = engine.calculate_price(params)
        return {"valid": True, "pricing": result}
    except BorrowerValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/summary")
def admin_summary():
    return {
        "service": "GenXBaby Pricing Engine",
        "matrix_file": str(MATRIX_PATH),
    }