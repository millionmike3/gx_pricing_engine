import math
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LoanScenario:
    loan_amount: float
    fico: int
    dti: float
    ltv: float
    occupancy: str
    state: str
    product: str


class PricingEngine:
    """
    Simple mortgage pricing engine used by the FastAPI backend.
    Produces a base rate, adjustments, and final price.
    """

    def __init__(self):
        # Base rate table (example values)
        self.base_rates = {
            "30yr_fixed": 6.50,
            "15yr_fixed": 5.75,
            "10yr_arm": 6.10,
        }

        # FICO adjustments
        self.fico_adj = {
            760: -0.10,
            740: -0.05,
            720: 0.00,
            700: 0.10,
            680: 0.25,
            660: 0.50,
            640: 0.75,
            620: 1.00,
        }

        # LTV adjustments
        self.ltv_adj = {
            60: -0.05,
            70: 0.00,
            80: 0.15,
            90: 0.35,
            95: 0.60,
        }

        # Occupancy adjustments
        self.occ_adj = {
            "primary": 0.00,
            "second_home": 0.25,
            "investment": 0.75,
        }

    def _lookup_adj(self, value: float, table: Dict[float, float]) -> float:
        """
        Finds the closest adjustment bucket.
        """
        keys = sorted(table.keys())
        for k in keys:
            if value <= k:
                return table[k]
        return table[keys[-1]]

    def price(self, scenario: LoanScenario) -> Dict[str, Any]:
        """
        Main pricing function.
        Returns a dict with base rate, adjustments, and final rate.
        """

        if scenario.product not in self.base_rates:
            raise ValueError(f"Unknown product: {scenario.product}")

        base_rate = self.base_rates[scenario.product]

        fico_adj = self._lookup_adj(scenario.fico, self.fico_adj)
        ltv_adj = self._lookup_adj(scenario.ltv, self.ltv_adj)
        occ_adj = self.occ_adj.get(scenario.occupancy, 0.50)

        total_adj = fico_adj + ltv_adj + occ_adj
        final_rate = round(base_rate + total_adj, 3)

        return {
            "base_rate": base_rate,
            "fico_adj": fico_adj,
            "ltv_adj": ltv_adj,
            "occupancy_adj": occ_adj,
            "total_adj": total_adj,
            "final_rate": final_rate,
        }
