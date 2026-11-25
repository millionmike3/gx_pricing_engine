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



def _parse_absolute_band(label, *, discrete=False):
    """Convert a supported tier label into a half-open numeric interval."""
    import re

    if not isinstance(label, str) or not label.strip():
        raise ValueError("Absolute grid tier labels must be non-empty strings.")

    label = label.strip()
    number = r"(?:\d+(?:\.\d*)?|\.\d+)"

    if re.fullmatch(number + r"\+", label):
        lower = float(label[:-1])
        upper = math.inf
    elif re.fullmatch(r"<=" + number, label):
        value = float(label[2:])
        lower = -math.inf
        upper = value + 1.0 if discrete else math.nextafter(value, math.inf)
    elif re.fullmatch(r"<" + number, label):
        lower = -math.inf
        upper = float(label[1:])
    else:
        match = re.fullmatch(
            r"(" + number + r")-(?:<)?(" + number + r")", label
        )
        if match:
            lower = float(match.group(1))
            upper = float(match.group(2))
            if "-" in label and "-<" not in label and discrete:
                upper += 1.0
            elif "-" in label and "-<" not in label:
                upper = math.nextafter(upper, math.inf)
        elif re.fullmatch(number, label):
            lower = float(label)
            upper = lower + 1.0 if discrete else math.nextafter(
                lower, math.inf
            )
        else:
            raise ValueError(f"Invalid absolute grid tier label: {label}")

    if not lower < upper:
        raise ValueError(f"Invalid or empty absolute grid tier: {label}")

    return lower, upper


def _validate_contiguous_bands(section_name, labels, *, discrete=False,
                               expected_start=None):
    """Reject malformed, overlapping, or incomplete ordered tier bands."""
    if not labels:
        raise ValueError(f"{section_name} must contain at least one band.")

    if len(set(labels)) != len(labels):
        raise ValueError(
            f"{section_name} has overlapping or duplicate bands."
        )

    parsed = []
    for label in labels:
        lower, upper = _parse_absolute_band(label, discrete=discrete)
        parsed.append((lower, upper, label))

    parsed.sort(key=lambda item: item[0])

    if expected_start == "unbounded" and parsed[0][0] != -math.inf:
        raise ValueError(f"{section_name} must cover its lower range.")
    if expected_start == 0 and parsed[0][0] != 0:
        raise ValueError(f"{section_name} must start at 0.")

    for previous, current in zip(parsed, parsed[1:]):
        if previous[1] > current[0]:
            raise ValueError(
                f"{section_name} has overlapping or duplicate bands: "
                f"{previous[2]} and {current[2]}."
            )
        if previous[1] < current[0]:
            raise ValueError(
                f"{section_name} has a gap between bands: "
                f"{previous[2]} and {current[2]}."
            )

    if parsed[-1][1] != math.inf:
        raise ValueError(f"{section_name} must cover its upper range.")

    return [item[2] for item in parsed]

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

    # Absolute grids are optional for backward compatibility. When supplied,
    # FICO and LTV bands must be complete, contiguous, and non-overlapping.
    absolute_grids = matrix.get("absoluteRateGrids")
    if absolute_grids is not None:
        if not isinstance(absolute_grids, dict) or not absolute_grids:
            raise ValueError(
                "absoluteRateGrids must be a non-empty JSON object."
            )

        for rate_type, absolute_grid in absolute_grids.items():
            section = f"absoluteRateGrids.{rate_type}"
            if not isinstance(absolute_grid, dict):
                raise ValueError(f"{section} must be a JSON object.")

            rows = absolute_grid.get("ficoLtv")
            if not isinstance(rows, list) or not rows:
                raise ValueError(f"{section}.ficoLtv must be a non-empty array.")

            fico_labels = []
            expected_ltv_labels = None

            for index, row in enumerate(rows):
                row_name = f"{section}.ficoLtv[{index}]"
                if not isinstance(row, dict):
                    raise ValueError(f"{row_name} must be a JSON object.")

                fico_label = row.get("fico")
                if not isinstance(fico_label, str) or not fico_label.strip():
                    raise ValueError(
                        f"{row_name}.fico must be a non-empty string."
                    )
                fico_labels.append(fico_label.strip())

                ltv_rates = row.get("ltvRates")
                _validate_numeric_map(
                    f"{row_name}.ltvRates",
                    ltv_rates,
                    positive=True,
                )
                ltv_labels = list(ltv_rates.keys())

                if expected_ltv_labels is None:
                    expected_ltv_labels = ltv_labels
                elif ltv_labels != expected_ltv_labels:
                    raise ValueError(
                        f"{row_name}.ltvRates must use the same ordered "
                        "LTV bands as every other FICO row."
                    )

            _validate_contiguous_bands(
                f"{section}.ficoLtv FICO bands",
                fico_labels,
                discrete=True,
                expected_start="unbounded",
            )
            _validate_contiguous_bands(
                f"{section}.ficoLtv LTV bands",
                expected_ltv_labels,
                expected_start=0,
            )

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
