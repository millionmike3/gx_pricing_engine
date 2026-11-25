import json
import math
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = (
    "metadata",
    "baseRates",
    "pricingTiers",
    "llpa",
    "riskFactors",
    "productAdjustments",
    "eligibilityRules",
)


def resolve_matrix_path(matrix_path=None):
    configured = matrix_path or os.getenv(
        "MATRIX_FILE", "data/pricing_matrix.json"
    )
    path = Path(configured)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _validate_numeric_map(section_name, values, *, positive=False):
    if not isinstance(values, dict) or not values:
        raise ValueError(f"{section_name} must be a non-empty JSON object.")

    for key, value in values.items():
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError(
                f"{section_name}.{key} must be finite and numeric."
            )
        if positive and float(value) <= 0:
            raise ValueError(f"{section_name}.{key} must be positive.")


def _require_keys(section_name, values, required_keys):
    missing = [key for key in required_keys if key not in values]
    if missing:
        raise ValueError(
            f"{section_name} is missing required keys: "
            + ", ".join(missing)
        )


def _validate_tier_list(section_name, entries):
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{section_name} must be a non-empty array.")

    for index, entry in enumerate(entries):
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("range"), str)
            or not entry["range"].strip()
        ):
            raise ValueError(
                f"{section_name}[{index}] needs a non-empty string range."
            )

        adjustment = entry.get("adjustment")
        if (
            not isinstance(adjustment, (int, float))
            or isinstance(adjustment, bool)
            or not math.isfinite(float(adjustment))
        ):
            raise ValueError(
                f"{section_name}[{index}].adjustment "
                "must be finite and numeric."
            )


def validate_matrix(matrix: Any) -> dict:
    if not isinstance(matrix, dict):
        raise ValueError("Pricing matrix must be a JSON object.")

    missing = [key for key in REQUIRED_SECTIONS if key not in matrix]
    if missing:
        raise ValueError(
            "Pricing matrix is missing required sections: "
            + ", ".join(missing)
        )

    if not isinstance(matrix["metadata"], dict):
        raise ValueError("metadata must be a JSON object.")

    _validate_numeric_map(
        "baseRates", matrix["baseRates"], positive=True
    )

    tiers = matrix["pricingTiers"]
    if not isinstance(tiers, dict):
        raise ValueError("pricingTiers must be a JSON object.")

    for category in ("fico", "ltv"):
        _validate_tier_list(
            f"pricingTiers.{category}", tiers.get(category)
        )

    llpa = matrix["llpa"]
    if not isinstance(llpa, dict):
        raise ValueError("llpa must be a JSON object.")

    # The grid is optional: PricingEngineV2 falls back to pricingTiers.
    grid = llpa.get("ficoLtvGrid", [])
    if not isinstance(grid, list):
        raise ValueError("llpa.ficoLtvGrid must be an array.")

    for index, row in enumerate(grid):
        if not isinstance(row, dict):
            raise ValueError(
                f"llpa.ficoLtvGrid[{index}] must be an object."
            )
        if (
            not isinstance(row.get("fico"), str)
            or not row["fico"].strip()
        ):
            raise ValueError(
                f"llpa.ficoLtvGrid[{index}].fico must be a non-empty string."
            )
        _validate_numeric_map(
            f"llpa.ficoLtvGrid[{index}].ltvAdjustments",
            row.get("ltvAdjustments"),
        )

    for subsection in ("occupancy", "loanPurpose", "propertyType"):
        values = llpa.get(subsection)
        _validate_numeric_map(f"llpa.{subsection}", values)

    # State overlays are intentionally optional.
    if "state" in llpa:
        _validate_numeric_map("llpa.state", llpa["state"])

    risk = matrix["riskFactors"]
    if not isinstance(risk, dict):
        raise ValueError("riskFactors must be a JSON object.")

    dti_rules = risk.get("dti")
    _validate_numeric_map("riskFactors.dti", dti_rules)
    _require_keys(
        "riskFactors.dti", dti_rules, ("over_45", "over_50")
    )

    for key in (
        "firstTimeHomebuyer",
        "bankruptcySeasoningUnder2Years",
        "foreclosureSeasoningUnder3Years",
    ):
        _validate_numeric_map("riskFactors", {key: risk.get(key)})

    _validate_tier_list(
        "riskFactors.dscrRatio", risk.get("dscrRatio")
    )

    _validate_numeric_map(
        "productAdjustments", matrix["productAdjustments"]
    )

    eligibility = matrix["eligibilityRules"]
    if not isinstance(eligibility, dict):
        raise ValueError("eligibilityRules must be a JSON object.")

    for subsection in ("maxLtv", "minFico", "maxDti"):
        _validate_numeric_map(
            f"eligibilityRules.{subsection}",
            eligibility.get(subsection),
            positive=True,
        )

    max_dti = eligibility["maxDti"]
    if "standard" not in max_dti:
        raise ValueError(
            "eligibilityRules.maxDti is missing required key: standard"
        )

    return matrix


def load_matrix(matrix_path=None) -> dict:
    path = resolve_matrix_path(matrix_path)
    if not path.is_file():
        raise FileNotFoundError(f"Pricing matrix not found at {path}")

    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            matrix = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Pricing matrix contains invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}."
        ) from exc

    return validate_matrix(matrix)
