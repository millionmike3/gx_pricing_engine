import json
import math
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api_gateway.server import app
from api_gateway.middleware.auth_middleware import (
    get_current_user,
    require_admin_or_owner,
)
import api_gateway.routes.pricing_routes as pricing_routes
from shared.matrix_loader import load_matrix
from shared.engine_registry import get_engines


class BaseRatesApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides.clear()

        app.dependency_overrides[require_admin_or_owner] = (
            lambda: {"user_id": 123, "role": "ADMIN"}
        )

        self.temp_dir = tempfile.TemporaryDirectory()
        self.matrix_path = Path(self.temp_dir.name) / "pricing_matrix.json"

        self.original_matrix = load_matrix()
        self.original_bytes = json.dumps(
            self.original_matrix,
            indent=2,
        ).encode("utf-8")
        self.matrix_path.write_bytes(self.original_bytes)

        self.path_patch = patch.object(
            pricing_routes,
            "resolve_matrix_path",
            return_value=self.matrix_path,
        )
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.temp_dir.cleanup()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)

    def assert_original_matrix_preserved(self):
        self.assertEqual(
            self.matrix_path.read_bytes(),
            self.original_bytes,
        )

    def test_admin_can_read_all_base_rates(self):
        response = self.client.get("/pricing/base-rates")

        self.assertEqual(response.status_code, 200, response.text)

        returned = response.json()
        expected = self.original_matrix["baseRates"]

        self.assertEqual(len(returned), len(expected))
        self.assertEqual(
            {item["product_type"]: item["base_rate"] for item in returned},
            expected,
        )

    def test_admin_can_update_one_base_rate(self):
        product_type = next(iter(self.original_matrix["baseRates"]))
        new_rate = 6.875

        response = self.client.put(
            "/pricing/base-rates",
            json={
                "product_type": product_type,
                "base_rate": new_rate,
            },
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["product_type"], product_type)
        self.assertEqual(response.json()["base_rate"], new_rate)

        saved = json.loads(
            self.matrix_path.read_text(encoding="utf-8")
        )

        self.assertEqual(saved["baseRates"][product_type], new_rate)

        for key, value in self.original_matrix.items():
            if key == "baseRates":
                continue
            self.assertEqual(saved[key], value)

        for key, value in self.original_matrix["baseRates"].items():
            if key != product_type:
                self.assertEqual(saved["baseRates"][key], value)


    def test_base_rate_update_refreshes_both_pricing_engines(self):
        product_type = next(iter(self.original_matrix["baseRates"]))
        new_rate = 6.875

        engine_v1_before, engine_v2_before = get_engines(self.matrix_path)

        response = self.client.put(
            "/pricing/base-rates",
            json={
                "product_type": product_type,
                "base_rate": new_rate,
            },
        )

        self.assertEqual(response.status_code, 200, response.text)

        engine_v1_after, engine_v2_after = get_engines(self.matrix_path)

        self.assertIsNot(engine_v1_before, engine_v1_after)
        self.assertIsNot(engine_v2_before, engine_v2_after)

        self.assertEqual(
            engine_v1_after.matrix["baseRates"][product_type],
            new_rate,
        )
        self.assertEqual(
            engine_v2_after.engine.matrix["baseRates"][product_type],
            new_rate,
        )

    def test_unknown_product_type_is_rejected_without_changing_matrix(self):
        response = self.client.put(
            "/pricing/base-rates",
            json={
                "product_type": "unknown_product",
                "base_rate": 6.5,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assert_original_matrix_preserved()

    def test_invalid_rates_are_rejected_without_changing_matrix(self):
        product_type = next(iter(self.original_matrix["baseRates"]))

        invalid_rates = [
            0,
            -1,
            float("nan"),
            float("inf"),
            True,
            "6.5",
        ]

        for invalid_rate in invalid_rates:
            with self.subTest(base_rate=repr(invalid_rate)):
                payload = {
                    "product_type": product_type,
                    "base_rate": invalid_rate,
                }
                response = self.client.put(
                    "/pricing/base-rates",
                    content=json.dumps(payload, allow_nan=True),
                    headers={"Content-Type": "application/json"},
                )

                self.assertEqual(
                    response.status_code,
                    422,
                    response.text,
                )
                self.assert_original_matrix_preserved()

    def test_missing_authentication_is_rejected(self):
        app.dependency_overrides.pop(require_admin_or_owner, None)

        response = self.client.get("/pricing/base-rates")

        self.assertEqual(response.status_code, 401)

    def test_borrower_cannot_read_base_rates(self):
        app.dependency_overrides.pop(require_admin_or_owner, None)
        app.dependency_overrides[get_current_user] = (
            lambda: {"user_id": 456, "role": "BORROWER"}
        )

        response = self.client.get("/pricing/base-rates")

        self.assertEqual(response.status_code, 403)

    def test_owner_can_read_base_rates(self):
        app.dependency_overrides[require_admin_or_owner] = (
            lambda: {"user_id": 789, "role": "OWNER"}
        )

        response = self.client.get("/pricing/base-rates")

        self.assertEqual(response.status_code, 200, response.text)

    def test_failed_atomic_save_preserves_original_matrix(self):
        product_type = next(iter(self.original_matrix["baseRates"]))

        with patch.object(
            pricing_routes.os,
            "replace",
            side_effect=OSError("Simulated file replacement failure"),
        ):
            response = self.client.put(
                "/pricing/base-rates",
                json={
                    "product_type": product_type,
                    "base_rate": 6.875,
                },
            )

        self.assertEqual(response.status_code, 500)
        self.assert_original_matrix_preserved()


if __name__ == "__main__":
    unittest.main(verbosity=2)
