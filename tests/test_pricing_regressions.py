import copy
import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api_gateway.server import app
from shared.borrower_rules import (
    BorrowerValidationError,
    validate_borrower,
)
from shared.matrix_loader import load_matrix, validate_matrix
from shared.pricing_engine import PricingEngine
from shared.pricing_engine_v2 import PricingEngineV2


class BorrowerValidationTests(unittest.TestCase):
    def setUp(self):
        self.valid = {
            "fico": 740,
            "ltv": 75,
            "loan_amount": 250000,
        }

    def test_valid_borrower_is_normalized(self):
        result = validate_borrower(self.valid)
        self.assertEqual(result["fico"], 740)
        self.assertEqual(result["occupancy"], "primary")
        self.assertEqual(result["property_type"], "single_family")

    def test_missing_required_field_is_rejected(self):
        with self.assertRaises(BorrowerValidationError):
            validate_borrower({"fico": 740, "ltv": 75})

    def test_fractional_fico_is_rejected(self):
        data = {**self.valid, "fico": 740.5}
        with self.assertRaises(BorrowerValidationError):
            validate_borrower(data)

    def test_boolean_fico_is_rejected(self):
        data = {**self.valid, "fico": True}
        with self.assertRaises(BorrowerValidationError):
            validate_borrower(data)

    def test_non_finite_ltv_is_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                data = {**self.valid, "ltv": value}
                with self.assertRaises(BorrowerValidationError):
                    validate_borrower(data)

    def test_zero_dscr_is_rejected(self):
        data = {**self.valid, "dscr": 0}
        with self.assertRaises(BorrowerValidationError):
            validate_borrower(data)

    def test_valid_dscr_is_preserved(self):
        data = {**self.valid, "dscr": 1.2}
        result = validate_borrower(data)
        self.assertEqual(result["dscr"], 1.2)


class PricingEngineRegressionTests(unittest.TestCase):
    def setUp(self):
        self.engine = PricingEngine()
        self.params = {
            "fico": 740,
            "ltv": 75,
            "loan_amount": 250000,
            "investor": "SubstantialFunding",
            "occupancy": "primary",
            "property_type": "single_family",
            "purpose": "purchase",
            "rate_type": "30yr_fixed",
        }

    def test_pricing_engine_rejects_invalid_matrix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid_matrix.json"
            invalid_path.write_text(
                '{"baseRates": {"30yr_fixed": 6.25}}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing required sections"):
                PricingEngine(matrix_path=str(invalid_path))

    def test_baseline_pricing_uses_absolute_30yr_grid(self):
        result = self.engine.calculate_price(self.params)
        self.assertEqual(result["base_rate"], 7.415)
        self.assertEqual(result["fico_ltv_adjustment"], 0.0)
        self.assertEqual(result["adjustment_source"], "absoluteRateGrids")
        self.assertEqual(result["investor_adjustment"], -0.1)
        self.assertEqual(result["final_rate"], 7.315)

    def test_absolute_30yr_grid_covers_all_42_cells(self):
        matrix = load_matrix()
        fico_values = [760, 740, 720, 700, 680, 679]
        ltv_values = [30, 65, 72, 77, 82, 87, 95]
        grid = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]

        checked = 0
        for row, fico in zip(grid, fico_values):
            for (ltv_label, expected_rate), ltv in zip(
                row["ltvRates"].items(), ltv_values
            ):
                with self.subTest(fico=fico, ltv=ltv, tier=ltv_label):
                    self.assertEqual(
                        self.engine._absolute_rate("30yr_fixed", fico, ltv),
                        expected_rate,
                    )
                    checked += 1

        self.assertEqual(checked, 42)

    def test_approved_occupancy_property_and_purpose_adjustments(self):
        cases = [
            ({"occupancy": "second_home"}, "occupancy", 0.25),
            ({"occupancy": "investment"}, "occupancy", 0.50),
            ({"property_type": "condo"}, "propertyType", 0.25),
            ({"property_type": "2_4_unit"}, "propertyType", 0.50),
            ({"property_type": "mixed_use"}, "propertyType", 0.75),
            ({"purpose": "cash_out"}, "loanPurpose", 0.375),
            ({"purpose": "delayed_financing"}, "loanPurpose", 0.25),
        ]

        for overrides, adjustment_key, expected in cases:
            with self.subTest(overrides=overrides):
                result = self.engine.calculate_price(
                    {**self.params, **overrides}
                )
                self.assertEqual(
                    result["adjustments"].get(adjustment_key), expected
                )

    def test_state_adjustment_is_applied(self):
        data = {**self.params, "state": "NY"}
        result = self.engine.calculate_price(data)
        self.assertEqual(result["adjustments"].get("state"), 0.125)

    def test_dscr_boundaries(self):
        expected = [
            (0.99, 1.00),
            (1.0, 0.50),
            (1.1999, 0.50),
            (1.2, 0.25),
            (1.3999, 0.25),
            (1.4, None),
            (1.6, None),
        ]

        for dscr, expected_adjustment in expected:
            with self.subTest(dscr=dscr):
                data = {**self.params, "dscr": dscr}
                result = self.engine.calculate_price(data)
                actual = result["adjustments"].get("dscrRatio")
                self.assertEqual(actual, expected_adjustment)

    def test_state_and_dscr_adjustments_are_combined(self):
        data = {**self.params, "state": "NJ", "dscr": 0.99}
        result = self.engine.calculate_price(data)
        self.assertEqual(result["adjustments"].get("state"), 0.125)
        self.assertEqual(result["adjustments"].get("dscrRatio"), 1.0)

    def test_v2_uses_state_and_dscr_rules(self):
        data = {**self.params, "state": "NY", "dscr": 1.2}
        result = PricingEngineV2().calculate_price(data)
        self.assertEqual(result["version"], 2)
        self.assertEqual(result["adjustments"].get("state"), 0.125)
        self.assertEqual(result["adjustments"].get("dscrRatio"), 0.25)
        self.assertEqual(result["rate"], result["final_rate"])


    def test_v2_falls_back_to_legacy_tiers_when_grids_are_absent(self):
        matrix = copy.deepcopy(load_matrix())
        matrix["llpa"].pop("ficoLtvGrid", None)
        matrix.pop("absoluteRateGrids", None)

        with tempfile.TemporaryDirectory() as temp_dir:
            matrix_path = Path(temp_dir) / "matrix_without_grid.json"
            matrix_path.write_text(
                json.dumps(matrix),
                encoding="utf-8",
            )

            engine_v2 = PricingEngineV2()
            engine_v2.engine = PricingEngine(matrix_path=str(matrix_path))

            result = engine_v2.calculate_price(self.params)

        self.assertEqual(result["version"], 2)
        self.assertEqual(result["adjustment_source"], "pricingTiers")
        self.assertEqual(result["fico_ltv_adjustment"], 0.5)
        self.assertEqual(result["final_rate"], 6.65)
        self.assertEqual(result["rate"], 6.65)


    def test_absolute_grid_fico_boundaries_select_correct_rows(self):
        expected = [
            (679, 7.79),
            (680, 7.54),
            (699, 7.54),
            (700, 7.29),
            (719, 7.29),
            (720, 7.04),
            (739, 7.04),
            (740, 6.915),
            (759, 6.915),
            (760, 6.79),
        ]
        for fico, expected_rate in expected:
            with self.subTest(fico=fico):
                self.assertEqual(
                    self.engine._absolute_rate("30yr_fixed", fico, 30),
                    expected_rate,
                )

    def test_absolute_grid_ltv_boundaries_select_correct_columns(self):
        expected = [
            (60, 6.915),
            (70, 7.04),
            (75, 7.29),
            (80, 7.415),
            (85, 7.665),
            (90, 7.915),
        ]
        for ltv, expected_rate in expected:
            with self.subTest(ltv=ltv):
                self.assertEqual(
                    self.engine._absolute_rate("30yr_fixed", 760, ltv),
                    expected_rate,
                )


class MatrixLoaderTests(unittest.TestCase):
    def test_active_matrix_loads_and_validates(self):
        matrix = load_matrix()
        self.assertIsInstance(matrix, dict)
        self.assertIn("riskFactors", matrix)
        self.assertIs(validate_matrix(matrix), matrix)

    def test_missing_required_section_is_rejected(self):
        matrix = copy.deepcopy(load_matrix())
        matrix.pop("riskFactors")
        with self.assertRaisesRegex(ValueError, "riskFactors"):
            validate_matrix(matrix)

    def test_missing_dti_adjustment_key_is_rejected(self):
        matrix = copy.deepcopy(load_matrix())
        del matrix["riskFactors"]["dti"]["over_50"]
        with self.assertRaisesRegex(ValueError, "over_50"):
            validate_matrix(matrix)

    def test_missing_required_eligibility_map_is_rejected(self):
        matrix = copy.deepcopy(load_matrix())
        del matrix["eligibilityRules"]["maxLtv"]
        with self.assertRaisesRegex(ValueError, "maxLtv"):
            validate_matrix(matrix)

    def test_missing_required_llpa_map_is_rejected(self):
        matrix = copy.deepcopy(load_matrix())
        del matrix["llpa"]["occupancy"]
        with self.assertRaisesRegex(ValueError, "llpa.occupancy"):
            validate_matrix(matrix)

    def test_optional_llpa_grid_can_be_absent(self):
        matrix = copy.deepcopy(load_matrix())
        matrix["llpa"].pop("ficoLtvGrid", None)
        self.assertIs(validate_matrix(matrix), matrix)

    def test_absolute_rate_grid_rejects_non_finite_rate(self):
        matrix = copy.deepcopy(load_matrix())
        matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"][0][
            "ltvRates"
        ]["0-<60"] = float("inf")

        with self.assertRaisesRegex(ValueError, "absoluteRateGrids"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_missing_ltv_rates(self):
        matrix = copy.deepcopy(load_matrix())
        del matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"][0][
            "ltvRates"
        ]

        with self.assertRaisesRegex(ValueError, "ltvRates"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_missing_fico_band(self):
        matrix = copy.deepcopy(load_matrix())
        rows = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]
        rows.pop(2)

        with self.assertRaisesRegex(ValueError, "gap"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_duplicate_fico_band(self):
        matrix = copy.deepcopy(load_matrix())
        rows = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]
        rows[1]["fico"] = rows[0]["fico"]

        with self.assertRaisesRegex(ValueError, "overlapping or duplicate"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_missing_ltv_band(self):
        matrix = copy.deepcopy(load_matrix())
        rows = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]
        del rows[0]["ltvRates"]["60-<70"]

        with self.assertRaisesRegex(ValueError, "same ordered LTV bands"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_duplicate_ltv_band(self):
        matrix = copy.deepcopy(load_matrix())
        rows = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]
        for row in rows:
            rates = row["ltvRates"]
            rates["65-<75"] = rates.pop("70-<75")

        with self.assertRaisesRegex(ValueError, "overlapping or duplicate"):
            validate_matrix(matrix)

    def test_absolute_rate_grid_rejects_ltv_gap(self):
        matrix = copy.deepcopy(load_matrix())
        rows = matrix["absoluteRateGrids"]["30yr_fixed"]["ficoLtv"]
        for row in rows:
            rates = row["ltvRates"]
            rates["60-<69"] = rates.pop("60-<70")

        with self.assertRaisesRegex(ValueError, "gap"):
            validate_matrix(matrix)

    def test_absolute_rate_grids_remain_optional(self):
        matrix = copy.deepcopy(load_matrix())
        matrix.pop("absoluteRateGrids", None)
        self.assertIs(validate_matrix(matrix), matrix)

    def test_non_finite_base_rate_is_rejected(self):
        matrix = copy.deepcopy(load_matrix())
        first_key = next(iter(matrix["baseRates"]))
        matrix["baseRates"][first_key] = float("inf")
        with self.assertRaises(ValueError):
            validate_matrix(matrix)

    def test_missing_matrix_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"
            with self.assertRaises(FileNotFoundError):
                load_matrix(missing_path)


class PricingApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.payload = {
            "fico": 740,
            "ltv": 75,
            "loan_amount": 250000,
            "investor": "SubstantialFunding",
            "property_type": "single_family",
            "occupancy": "primary",
            "purpose": "purchase",
            "rate_type": "30yr_fixed",
            "version": 1,
        }

    def test_baseline_quote_endpoint(self):
        response = self.client.post("/pricing/quote", json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["final_rate"], 7.315)

    def test_zero_dscr_returns_validation_error(self):
        payload = {**self.payload, "dscr": 0}
        response = self.client.post("/pricing/quote", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_compare_endpoint_returns_both_versions(self):
        response = self.client.post(
            "/pricing/quote/compare",
            json=self.payload,
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("v1", body)
        self.assertIn("v2", body)
        self.assertIn("final_rate_diff", body["delta"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
