import math
from typing import Any, Dict


class BorrowerValidationError(Exception):
    """Raised when borrower data fails validation."""


def validate_borrower(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize borrower inputs without inventing missing DTI."""

    required = ("fico", "ltv", "loan_amount")
    missing = [field for field in required if field not in data or data[field] is None]
    if missing:
        raise BorrowerValidationError(
            f"Missing required fields: {', '.join(missing)}"
        )

    try:
        raw_fico = data["fico"]
        if isinstance(raw_fico, bool):
            raise ValueError("FICO cannot be boolean.")
        fico_number = float(raw_fico)
        if not math.isfinite(fico_number) or not fico_number.is_integer():
            raise ValueError("FICO must be a finite whole number.")
        fico = int(fico_number)

        ltv = float(data["ltv"])
        loan_amount = float(data["loan_amount"])
        dti = float(data["dti"]) if data.get("dti") is not None else None
        dscr = float(data["dscr"]) if data.get("dscr") is not None else None
    except (TypeError, ValueError, OverflowError):
        raise BorrowerValidationError(
            "FICO must be a whole number; LTV, loan amount, DTI, and DSCR must be numeric."
        )

    numeric_values = {
        "LTV": ltv,
        "loan amount": loan_amount,
    }
    if dti is not None:
        numeric_values["DTI"] = dti
    if dscr is not None:
        numeric_values["DSCR"] = dscr

    for label, value in numeric_values.items():
        if not math.isfinite(value):
            raise BorrowerValidationError(f"{label} must be finite.")

    if fico < 300 or fico > 850:
        raise BorrowerValidationError("FICO score must be between 300 and 850.")
    if ltv <= 0 or ltv > 100:
        raise BorrowerValidationError("LTV must be greater than 0 and no more than 100.")
    if dti is not None and (dti <= 0 or dti > 65):
        raise BorrowerValidationError("DTI must be greater than 0 and no more than 65.")
    if dscr is not None and dscr <= 0:
        raise BorrowerValidationError("DSCR must be greater than 0.")
    if loan_amount < 50000:
        raise BorrowerValidationError("Loan amount must be at least $50,000.")
    if loan_amount > 3000000:
        raise BorrowerValidationError("Loan amount exceeds the current $3,000,000 validation limit.")

    property_aliases = {
        "sfr": "single_family",
        "single family": "single_family",
        "townhome": "single_family",
        "2-4 unit": "2_4_unit",
        "2-4_unit": "2_4_unit",
        "manufactured": "single_family",
    }
    property_type = str(data.get("property_type") or "single_family").strip().lower()
    property_type = property_aliases.get(property_type, property_type)

    allowed_property_types = {
        "single_family",
        "condo",
        "non_warrantable_condo",
        "2_4_unit",
    }
    if property_type not in allowed_property_types:
        raise BorrowerValidationError(
            f"Invalid property_type. Allowed: {', '.join(sorted(allowed_property_types))}"
        )

    occupancy_aliases = {
        "primary": "primary",
        "second": "second_home",
        "second_home": "second_home",
        "investment": "investment",
    }
    occupancy_input = str(data.get("occupancy") or "primary").strip().lower()
    if occupancy_input not in occupancy_aliases:
        raise BorrowerValidationError(
            "Invalid occupancy. Allowed: primary, second_home, investment."
        )
    occupancy = occupancy_aliases[occupancy_input]

    state = data.get("state")
    if state is not None:
        state = str(state).strip().upper()
        if len(state) != 2 or not state.isalpha():
            raise BorrowerValidationError(
                "State must be a two-letter abbreviation."
            )

    normalized = {
        "fico": fico,
        "ltv": ltv,
        "loan_amount": loan_amount,
        "property_type": property_type,
        "occupancy": occupancy,
    }
    if dti is not None:
        normalized["dti"] = dti
    if dscr is not None:
        normalized["dscr"] = dscr
    if state:
        normalized["state"] = state

    return normalized