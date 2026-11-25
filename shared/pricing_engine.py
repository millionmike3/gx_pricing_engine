import os
from pathlib import Path
from typing import Any, Dict, Optional

from shared.matrix_loader import load_matrix


class PricingEngine:
    """Matrix-driven mortgage pricing engine."""

    def __init__(self, matrix_path: Optional[str] = None):
        configured = matrix_path or os.getenv("MATRIX_FILE", "data/pricing_matrix.json")
        path = Path(configured)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[1] / path
        self.matrix_path = path
        self.matrix = self._load_matrix()

    def _load_matrix(self) -> Dict[str, Any]:
        """Load the active matrix through the shared schema validator."""
        return load_matrix(self.matrix_path)

    @staticmethod
    def _matches_range(value: float, label: str) -> bool:
        label = str(label).strip()
        if label.endswith("+"):
            return value >= float(label[:-1])
        if label.startswith("<="):
            return value <= float(label[2:])
        if label.startswith("<"):
            return value < float(label[1:])
        if "-" in label:
            low, high = label.split("-", 1)
            low = float(low)
            high = high.strip()
            if high.startswith("<"):
                return value >= low and value < float(high[1:])
            return value >= low and value <= float(high)
        return value == float(label)

    def _tier_adjustment(self, category: str, value: float) -> float:
        tiers = self.matrix.get("pricingTiers", {}).get(category, [])
        for tier in tiers:
            if self._matches_range(value, tier["range"]):
                return float(tier["adjustment"])
        raise ValueError(
            f"No {category} pricing tier found for value {value}."
        )

    def _grid_adjustment(self, fico: int, ltv: float):
        rows = self.matrix.get("llpa", {}).get("ficoLtvGrid", [])
        for row in rows:
            if self._matches_range(fico, row["fico"]):
                for label, adjustment in row["ltvAdjustments"].items():
                    if self._matches_range(ltv, label):
                        return float(adjustment)
                raise ValueError(f"No LLPA LTV tier found for LTV {ltv}.")
        return None

    def calculate_price(
        self,
        params: Dict[str, Any],
        use_llpa_grid: bool = False
    ) -> Dict[str, Any]:
        fico = int(params["fico"])
        ltv = float(params["ltv"])
        loan_amount = float(params["loan_amount"])
        investor = params.get("investor", "SubstantialFunding")
        occupancy = str(params.get("occupancy", "primary")).lower()
        property_type = str(params.get("property_type", "single_family")).lower()
        purpose = str(params.get("purpose", "purchase")).lower()
        program = str(params.get("product_type", "")).lower()
        rate_type = params.get("rate_type", "30yr_fixed")

        base_rates = self.matrix.get("baseRates", {})
        if rate_type not in base_rates:
            raise ValueError(f"Unknown rate_type: {rate_type}")
        base_rate = float(base_rates[rate_type])

        eligibility = self.matrix.get("eligibilityRules", {})
        max_ltv = eligibility.get("maxLtv", {}).get(occupancy)
        if max_ltv is not None and ltv > float(max_ltv):
            raise ValueError(
                f"LTV {ltv} exceeds the {occupancy} program maximum of {max_ltv}."
            )

        min_fico = eligibility.get("minFico", {}).get(program)
        if min_fico is not None and fico < int(min_fico):
            raise ValueError(
                f"FICO {fico} is below the {program} minimum of {min_fico}."
            )

        dti = params.get("dti")
        max_dti = eligibility.get("maxDti", {}).get(
            program, eligibility.get("maxDti", {}).get("standard")
        )
        if dti is not None and max_dti is not None and float(dti) > float(max_dti):
            raise ValueError(
                f"DTI {dti} exceeds the {program or 'standard'} maximum of {max_dti}."
            )

        grid_adjustment = self._grid_adjustment(fico, ltv) if use_llpa_grid else None
        if grid_adjustment is not None:
            fico_ltv_adjustment = grid_adjustment
            adjustment_source = "llpa.ficoLtvGrid"
        else:
            fico_adjustment = self._tier_adjustment("fico", fico)
            ltv_adjustment = self._tier_adjustment("ltv", ltv)
            fico_ltv_adjustment = fico_adjustment + ltv_adjustment
            adjustment_source = "pricingTiers"

        llpa = self.matrix.get("llpa", {})
        adjustments = {}

        def add_adjustment(name, value):
            if value is not None and float(value) != 0:
                adjustments[name] = float(value)

        add_adjustment(
            "occupancy",
            llpa.get("occupancy", {}).get(occupancy)
        )
        add_adjustment(
            "loanPurpose",
            llpa.get("loanPurpose", {}).get(purpose)
        )
        add_adjustment(
            "propertyType",
            llpa.get("propertyType", {}).get(property_type)
        )

        risk = self.matrix.get("riskFactors", {})
        if dti is not None:
            dti_rules = risk.get("dti", {})
            if float(dti) > 50:
                add_adjustment("dti", dti_rules.get("over_50"))
            elif float(dti) > 45:
                add_adjustment("dti", dti_rules.get("over_45"))

        # State LLPA is separate from occupancy, property, and loan-purpose LLPA.
        state = str(params.get("state", "")).strip().upper()
        add_adjustment("state", llpa.get("state", {}).get(state))

        # DSCR coverage-ratio pricing is separate from the DSCR loan-product adjustment.
        dscr = params.get("dscr")
        if dscr is not None:
            dscr_rules = risk.get("dscrRatio", [])
            matched_dscr = False
            for tier in dscr_rules:
                if self._matches_range(float(dscr), tier["range"]):
                    add_adjustment("dscrRatio", tier["adjustment"])
                    matched_dscr = True
                    break
            if not matched_dscr:
                raise ValueError(
                    f"No DSCR ratio pricing tier found for value {dscr}."
                )

        if params.get("first_time_homebuyer"):
            add_adjustment(
                "firstTimeHomebuyer",
                risk.get("firstTimeHomebuyer")
            )

        if params.get("bankruptcy_seasoning_under_2_years"):
            add_adjustment(
                "bankruptcySeasoningUnder2Years",
                risk.get("bankruptcySeasoningUnder2Years")
            )

        if params.get("foreclosure_seasoning_under_3_years"):
            add_adjustment(
                "foreclosureSeasoningUnder3Years",
                risk.get("foreclosureSeasoningUnder3Years")
            )

        product_adjustment = self.matrix.get(
            "productAdjustments", {}
        ).get(program)
        add_adjustment("product", product_adjustment)

        # Preserve the existing investor overlays from the original engine.
        investor_overlays = {
            "Bayview": 0.25,
            "AXA": 0.125,
            "Wealthfront": 0.375,
            "SubstantialFunding": -0.10,
        }
        investor_adjustment = float(investor_overlays.get(investor, 0.0))

        other_adjustments = sum(adjustments.values())
        adjusted_rate = base_rate + fico_ltv_adjustment + other_adjustments
        final_rate = adjusted_rate + investor_adjustment

        return {
            "base_rate": round(base_rate, 4),
            "fico_ltv_adjustment": round(fico_ltv_adjustment, 4),
            "adjustment_source": adjustment_source,
            "adjustments": adjustments,
            "investor_adjustment": round(investor_adjustment, 4),
            "adjusted_rate": round(adjusted_rate, 4),
            "final_rate": round(final_rate, 4),
            "investor": investor,
            "rate_type": rate_type,
            "inputs": params,
        }