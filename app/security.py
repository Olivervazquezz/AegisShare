"""
AegisShare — Security Utilities

Handles password hashing/verification and JWT token creation.
Secrets are loaded from environment variables to avoid hard-coding credentials.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

# Load variables from the .env file (if it exists) into os.environ.
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration – loaded from environment variables
# ---------------------------------------------------------------------------
SECRET_KEY: str = os.getenv("AEGIS_SECRET_KEY", "change-me-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("AEGIS_TOKEN_EXPIRE_MINUTES", "30")
)

# ---------------------------------------------------------------------------
# Password context (bcrypt)
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Return the bcrypt hash for the given plain-text password."""
    return pwd_context.hash(password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT with an expiration claim.

    Args:
        data:          Payload claims (e.g. ``{"sub": user_email}``).
        expires_delta: Custom lifetime. Defaults to
                       ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)