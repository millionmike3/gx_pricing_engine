# shared/borrower_rules.py

"""
Borrower validation rules for the GX Pricing Engine.

This module provides a clean validation layer that ensures borrower
inputs meet minimum underwriting and pricing requirements before
being passed into the PricingEngine.
"""

from typing import Dict, Any


class BorrowerValidationError(Exception):
    """Raised when borrower data fails validation."""
    pass


def validate_borrower(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate borrower input payload.

    Parameters
    ----------
    data : dict
        Borrower request payload from API.

    Returns
    -------
    dict
        Normalized borrower data.

    Raises
    ------
    BorrowerValidationError
        If any rule fails.
    """

    required_fields = [
        "fico",
        "ltv",
        "dti",
        "loan_amount",
        "property_type",
        "occupancy",
        "state"
    ]

    missing = [f for f in required_fields if f not in data]
    if missing:
        raise BorrowerValidationError(f"Missing required fields: {missing}")

    # --- FICO ---
    fico = int(data["fico"])
    if fico < 300 or fico > 850:
        raise BorrowerValidationError("FICO score must be between 300 and 850.")

    # --- LTV ---
    ltv = float(data["ltv"])
    if ltv <= 0 or ltv > 100:
        raise BorrowerValidationError("LTV must be between 0 and 100.")

    # --- DTI ---
    dti = float(data["dti"])
    if dti <= 0 or dti > 65:
        raise BorrowerValidationError("DTI must be between 0 and 65.")

    # --- Loan Amount ---
    loan_amount = float(data["loan_amount"])
    if loan_amount < 50000:
        raise BorrowerValidationError("Loan amount must be at least $50,000.")
    if loan_amount > 3000000:
        raise BorrowerValidationError("Loan amount exceeds program limits.")

    # --- Property Type ---
    allowed_property_types = {
        "SFR",
        "Condo",
        "Townhome",
        "2-4 Unit",
        "Manufactured"
    }

    if data["property_type"] not in allowed_property_types:
        raise BorrowerValidationError(
            f"Invalid property_type. Allowed: {allowed_property_types}"
        )

    # --- Occupancy ---
    allowed_occupancy = {"Primary", "Second", "Investment"}

    if data["occupancy"] not in allowed_occupancy:
        raise BorrowerValidationError(
            f"Invalid occupancy. Allowed: {allowed_occupancy}"
        )

    # --- State ---
    state = data["state"].upper()
    if len(state) != 2:
        raise BorrowerValidationError("State must be a 2‑letter abbreviation.")

    # Normalize output
    normalized = {
        "fico": fico,
        "ltv": ltv,
        "dti": dti,
        "loan_amount": loan_amount,
        "property_type": data["property_type"],
        "occupancy": data["occupancy"],
        "state": state,
    }

    return normalized
