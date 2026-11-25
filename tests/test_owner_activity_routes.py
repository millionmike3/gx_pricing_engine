import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api_gateway.server import app
from api_gateway.middleware.auth_middleware import get_current_user
import api_gateway.routes.owner_activity_routes as owner_routes


OWNER_ENDPOINTS = [
    "/owners/revenue/summary",
    "/owners/fraud/summary",
    "/owners/behavior/summary",
    "/owners/execution/summary",
    "/pricing/audit-log/recent",
]


TEST_OVERVIEW = {
    "period_days": 30,
    "total_events": 10,
    "successful_events": 8,
    "failed_events": 2,
    "quote_requests": 5,
    "matrix_events": 2,
    "average_duration_ms": 12.5,
    "p95_duration_ms": 20.0,
    "by_module": [
        {"module": "PRICING", "event_count": 8},
        {"module": "MATRIX", "event_count": 2},
    ],
    "by_action": [
        {"action": "QUOTE_REQUEST", "event_count": 5},
        {"action": "MATRIX_VALIDATION_FAILED", "event_count": 1},
    ],
}


class OwnerActivityRouteAuthorizationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides.clear()

        self.overview_patch = patch.object(
            owner_routes,
            "fetch_activity_overview",
            return_value=TEST_OVERVIEW,
        )
        self.recent_patch = patch.object(
            owner_routes,
            "fetch_recent_activity",
            return_value=[
                {
                    "id": 1,
                    "actor_role": "ADMIN",
                    "actor_id": 123,
                    "action": "QUOTE_REQUEST",
                    "module": "PRICING",
                    "details": {},
                    "status": "SUCCESS",
                    "duration_ms": 12,
                    "created_at": "2026-11-24T12:00:00",
                }
            ],
        )

        self.overview_patch.start()
        self.recent_patch.start()

    def tearDown(self):
        self.overview_patch.stop()
        self.recent_patch.stop()

        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)

    def test_admin_and_owner_can_access_all_endpoints(self):
        for role in ("ADMIN", "OWNER"):
            app.dependency_overrides[get_current_user] = (
                lambda role=role: {
                    "user_id": 123,
                    "role": role,
                }
            )

            for endpoint in OWNER_ENDPOINTS:
                with self.subTest(role=role, endpoint=endpoint):
                    response = self.client.get(endpoint)
                    self.assertEqual(
                        response.status_code,
                        200,
                        response.text,
                    )

    def test_borrower_is_forbidden_from_all_endpoints(self):
        app.dependency_overrides[get_current_user] = (
            lambda: {
                "user_id": 456,
                "role": "BORROWER",
            }
        )

        for endpoint in OWNER_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(
                    response.status_code,
                    403,
                    response.text,
                )

    def test_missing_authentication_is_rejected_on_all_endpoints(self):
        for endpoint in OWNER_ENDPOINTS:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertEqual(
                    response.status_code,
                    401,
                    response.text,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
