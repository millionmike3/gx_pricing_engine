import json
import os

class PricingEngineV2:
    """
    Advanced pricing engine with additional risk-layering logic.
    """

    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        llpa_path = os.path.join(base_path, "llpa.json")

        with open(llpa_path, "r") as f:
            self.llpa_table = json.load(f)

    def _lookup_llpa(self, fico, ltv):
        fico_key = str(fico)
        ltv_key = str(ltv)

        if fico_key not in self.llpa_table:
            raise ValueError(f"FICO {fico} not found in LLPA table")

        if ltv_key not in self.llpa_table[fico_key]:
            raise ValueError(f"LTV {ltv} not found in LLPA table")

        return self.llpa_table[fico_key][ltv_key]

    def _risk_layering(self, fico, ltv, occupancy, property_type):
        adjustments = 0.0

        if occupancy == "investment":
            adjustments += 1.25

        if property_type == "2_unit":
            adjustments += 0.375

        if fico < 660 and ltv > 80:
            adjustments += 0.50

        return adjustments

    def price(self, loan_amount, fico, ltv, occupancy="primary", property_type="single_family"):
        base_rate = 6.25

        llpa = self._lookup_llpa(fico, ltv)
        risk_adj = self._risk_layering(fico, ltv, occupancy, property_type)

        final_rate = base_rate + llpa + risk_adj

        return {
            "loan_amount": loan_amount,
            "fico": fico,
            "ltv": ltv,
            "llpa": llpa,
            "risk_adjustments": risk_adj,
            "rate": round(final_rate, 4)
        }
