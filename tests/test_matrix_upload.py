import json
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
import api_gateway.routes.matrix_routes as matrix_routes
from shared.matrix_loader import load_matrix


TEST_SECRET = "matrix-upload-test-secret-long-enough-123456"


class MatrixUploadApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides.clear()

        app.dependency_overrides[require_admin_or_owner] = (
            lambda: {"user_id": 123, "role": "ADMIN"}
        )

        self.env_patch = patch.dict(
            os.environ,
            {"JWT_SECRET": TEST_SECRET},
        )
        self.env_patch.start()

        self.temp_dir = tempfile.TemporaryDirectory()
        self.matrix_path = Path(self.temp_dir.name) / "pricing_matrix.json"

        self.original_matrix = load_matrix()
        self.original_bytes = json.dumps(
            self.original_matrix,
            indent=2,
        ).encode("utf-8")
        self.matrix_path.write_bytes(self.original_bytes)

        self.path_patch = patch.object(
            matrix_routes,
            "MATRIX_PATH",
            self.matrix_path,
        )
        self.path_patch.start()

    def tearDown(self):
        self.path_patch.stop()
        self.env_patch.stop()
        self.temp_dir.cleanup()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)

    def upload(self, content, content_type="application/json"):
        return self.client.post(
            "/matrix/upload",
            files={
                "file": (
                    "pricing_matrix.json",
                    content,
                    content_type,
                )
            },
        )

    def assert_original_matrix_preserved(self):
        self.assertEqual(
            self.matrix_path.read_bytes(),
            self.original_bytes,
        )

    def test_admin_can_upload_valid_matrix(self):
        updated = json.loads(json.dumps(self.original_matrix))
        updated["metadata"]["description"] = "Upload regression test"

        response = self.upload(
            json.dumps(updated).encode("utf-8")
        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "ok")

        saved = json.loads(self.matrix_path.read_text(encoding="utf-8"))
        self.assertEqual(
            saved["metadata"]["description"],
            "Upload regression test",
        )

    def test_invalid_json_is_rejected_without_replacing_matrix(self):
        response = self.upload(b'{"broken":')

        self.assertEqual(response.status_code, 400)
        self.assert_original_matrix_preserved()

    def test_non_finite_matrix_value_is_rejected_without_replacing_matrix(self):
        updated = json.loads(json.dumps(self.original_matrix))
        first_key = next(iter(updated["baseRates"]))
        updated["baseRates"][first_key] = float("nan")

        response = self.upload(json.dumps(updated).encode("utf-8"))

        self.assertEqual(response.status_code, 400, response.text)
        self.assert_original_matrix_preserved()

    def test_missing_required_section_is_rejected_without_replacing_matrix(self):
        updated = json.loads(json.dumps(self.original_matrix))
        updated.pop("riskFactors")

        response = self.upload(json.dumps(updated).encode("utf-8"))

        self.assertEqual(response.status_code, 400)
        self.assert_original_matrix_preserved()

    def test_non_json_content_type_is_rejected(self):
        response = self.upload(
            self.original_bytes,
            content_type="text/plain",
        )

        self.assertEqual(response.status_code, 400)
        self.assert_original_matrix_preserved()

    def test_oversized_upload_is_rejected(self):
        oversized = b" " * (matrix_routes.MAX_UPLOAD_SIZE + 1)

        response = self.upload(oversized)

        self.assertEqual(response.status_code, 413)
        self.assert_original_matrix_preserved()

    def test_missing_authentication_is_rejected(self):
        app.dependency_overrides.pop(require_admin_or_owner, None)

        response = self.client.post(
            "/matrix/upload",
            files={
                "file": (
                    "pricing_matrix.json",
                    self.original_bytes,
                    "application/json",
                )
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assert_original_matrix_preserved()

    def test_borrower_cannot_upload_matrix(self):
        app.dependency_overrides.pop(require_admin_or_owner, None)
        app.dependency_overrides[get_current_user] = (
            lambda: {"user_id": 456, "role": "BORROWER"}
        )

        response = self.upload(self.original_bytes)

        self.assertEqual(response.status_code, 403)
        self.assert_original_matrix_preserved()


if __name__ == "__main__":
    unittest.main(verbosity=2)
