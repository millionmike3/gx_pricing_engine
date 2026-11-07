from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LoanScenarioV2:
    loan_amount: float
    fico: int
    dti: float
    ltv: float
    occupancy: str
    state: str
    product: str
    loan_term: int
    loan_type: str


class PricingEngineV2:
    """
    Advanced pricing engine with expanded adjustments.
    """

    def __init__(self):
        # Base rates by product
        self.base_rates = {
            "conventional_fixed": 6.50,
            "conventional_arm": 6.10,
            "fha_fixed": 6.25,
            "va_fixed": 6.15,
            "jumbo_fixed": 7.00,
        }

        # FICO adjustments
        self.fico_adj = {
            780: -0.20,
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
            60: -0.10,
            70: 0.00,
            80: 0.20,
            90: 0.45,
            95: 0.75,
        }

        # Occupancy adjustments
        self.occ_adj = {
            "primary": 0.00,
            "second_home": 0.25,
            "investment": 1.00,
        }

        # Loan term adjustments
        self.term_adj = {
            10: -0.25,
            15: -0.15,
            20: -0.05,
            30: 0.00,
        }

        # Loan type adjustments
        self.type_adj = {
            "conforming": 0.00,
            "jumbo": 0.50,
            "non_qm": 1.25,
        }

    def _lookup_adj(self, value: float, table: Dict[float, float]) -> float:
        keys = sorted(table.keys())
        for k in keys:
            if value <= k:
                return table[k]
        return table[keys[-1]]

    def price(self, scenario: LoanScenarioV2) -> Dict[str, Any]:
        if scenario.product not in self.base_rates:
            raise ValueError(f"Unknown product: {scenario.product}")

        base_rate = self.base_rates[scenario.product]

        fico_adj = self._lookup_adj(scenario.fico, self.fico_adj)
        ltv_adj = self._lookup_adj(scenario.ltv, self.ltv_adj)
        occ_adj = self.occ_adj.get(scenario.occupancy, 0.50)
        term_adj = self.term_adj.get(scenario.loan_term, 0.10)
        type_adj = self.type_adj.get(scenario.loan_type, 0.75)

        total_adj = fico_adj + ltv_adj + occ_adj + term_adj + type_adj
        final_rate = round(base_rate + total_adj, 3)

        return {
            "base_rate": base_rate,
            "fico_adj": fico_adj,
            "ltv_adj": ltv_adj,
            "occupancy_adj": occ_adj,
            "term_adj": term_adj,
            "type_adj": type_adj,
            "total_adj": total_adj,
            "final_rate": final_rate,
        }
