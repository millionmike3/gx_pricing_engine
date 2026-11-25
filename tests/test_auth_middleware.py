import os
import time
import unittest
from unittest.mock import patch

import jwt
from fastapi import HTTPException

from api_gateway.middleware.auth_middleware import (
    GENXBABY_ROLES,
    get_current_user,
    require_admin_or_owner,
)


TEST_SECRET = "local-test-secret-that-is-long-enough-123456"


class AuthMiddlewareTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(
            os.environ,
            {
                "JWT_SECRET": TEST_SECRET,
                "JWT_ISSUER": "genxbaby-auth",
                "JWT_AUDIENCE": "genxbaby-frontend",
            },
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def make_token(self, **overrides):
        now = int(time.time())
        payload = {
            "sub": "123",
            "role": "BORROWER",
            "typ": "access",
            "iss": "genxbaby-auth",
            "aud": "genxbaby-frontend",
            "iat": now,
            "exp": now + 300,
        }
        payload.update(overrides)
        return jwt.encode(payload, TEST_SECRET, algorithm="HS256")

    def test_all_nine_supported_roles_are_accepted(self):
        self.assertEqual(len(GENXBABY_ROLES), 9)
        for role in sorted(GENXBABY_ROLES):
            with self.subTest(role=role):
                token = self.make_token(role=role)
                result = get_current_user("Bearer " + token)
                self.assertEqual(result, {"user_id": 123, "role": role})

    def test_non_string_role_claims_return_401(self):
        for role in (None, [], {}, 123, True):
            with self.subTest(role=role):
                token = self.make_token(role=role)
                with self.assertRaises(HTTPException) as context:
                    get_current_user("Bearer " + token)
                self.assertEqual(context.exception.status_code, 401)

    def test_unknown_role_returns_401(self):
        token = self.make_token(role="PROPERTY_OWNER")
        with self.assertRaises(HTTPException) as context:
            get_current_user("Bearer " + token)
        self.assertEqual(context.exception.status_code, 401)

    def test_invalid_subject_returns_401(self):
        for subject in ("abc", "0", "-1", 123):
            with self.subTest(subject=subject):
                token = self.make_token(sub=subject)
                with self.assertRaises(HTTPException) as context:
                    get_current_user("Bearer " + token)
                self.assertEqual(context.exception.status_code, 401)

    def test_non_access_token_returns_401(self):
        token = self.make_token(typ="refresh")
        with self.assertRaises(HTTPException) as context:
            get_current_user("Bearer " + token)
        self.assertEqual(context.exception.status_code, 401)

    def test_expired_token_returns_401(self):
        token = self.make_token(exp=int(time.time()) - 60)
        with self.assertRaises(HTTPException) as context:
            get_current_user("Bearer " + token)
        self.assertEqual(context.exception.status_code, 401)

    def test_wrong_audience_returns_401(self):
        token = self.make_token(aud="another-client")
        with self.assertRaises(HTTPException) as context:
            get_current_user("Bearer " + token)
        self.assertEqual(context.exception.status_code, 401)

    def test_missing_bearer_token_returns_401(self):
        for authorization in (None, "", "Basic abc", "Bearer "):
            with self.subTest(authorization=authorization):
                with self.assertRaises(HTTPException) as context:
                    get_current_user(authorization)
                self.assertEqual(context.exception.status_code, 401)

    def test_admin_and_owner_pass_admin_guard(self):
        for role in ("ADMIN", "OWNER"):
            with self.subTest(role=role):
                self.assertEqual(
                    require_admin_or_owner({"user_id": 123, "role": role})["role"],
                    role,
                )

    def test_non_admin_owner_is_forbidden(self):
        with self.assertRaises(HTTPException) as context:
            require_admin_or_owner({"user_id": 123, "role": "BORROWER"})
        self.assertEqual(context.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
