from typing import Any, Dict

from shared.pricing_engine import PricingEngine


class PricingEngineV2:
    """Advanced pricing engine using the matrix LLPA grid when available."""

    def __init__(self):
        self.engine = PricingEngine()

    def calculate_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        result = self.engine.calculate_price(params, use_llpa_grid=True)
        result["version"] = 2
        result["pricing_model"] = "LLPA grid with published-tier fallback"
        result["rate"] = result["final_rate"]
        return result

    def price(
        self,
        loan_amount,
        fico,
        ltv,
        occupancy="primary",
        property_type="single_family"
    ):
        return self.calculate_price({
            "loan_amount": loan_amount,
            "fico": fico,
            "ltv": ltv,
            "occupancy": occupancy,
            "property_type": property_type,
        })