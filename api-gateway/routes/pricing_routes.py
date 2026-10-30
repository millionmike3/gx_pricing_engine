from fastapi import APIRouter
from shared.pricing_engine import PricingEngine

router = APIRouter()
engine = PricingEngine()

@router.post("/quote")
def get_quote(payload: dict):
    return engine.calculate(payload)
