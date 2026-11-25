import os

import jwt
from fastapi import Depends, Header, HTTPException


GENXBABY_ROLES = {
    "ADMIN",
    "OWNER",
    "UNDERWRITER",
    "INVESTOR",
    "LOAN_OFFICER",
    "PROCESSOR",
    "SERVICING",
    "STAFF",
    "BORROWER",
}


def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    """Verify a GenXBaby NestJS access token."""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="A valid Bearer access token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured on this service.",
        )

    issuer = os.getenv("JWT_ISSUER") or "genxbaby-auth"
    audience = os.getenv("JWT_AUDIENCE") or "genxbaby-frontend"

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            issuer=issuer,
            audience=audience,
            options={
                "require": ["exp", "sub", "role", "typ"],
            },
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    role = payload.get("role")

    if (
        not isinstance(subject, str)
        or not subject.isdigit()
        or int(subject) <= 0
        or payload.get("typ") != "access"
        or not isinstance(role, str)
        or role not in GENXBABY_ROLES
    ):
        raise HTTPException(
            status_code=401,
            detail="Access token claims are invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": int(subject),
        "role": role,
    }


def require_admin_or_owner(
    user: dict = Depends(get_current_user),
) -> dict:
    """Allow only ADMIN and OWNER roles."""

    if user["role"] not in {"ADMIN", "OWNER"}:
        raise HTTPException(
            status_code=403,
            detail="ADMIN or OWNER permission is required.",
        )

    return user
