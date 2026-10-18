"""Admin protection: every write to the catalogue needs the secret key in the X-Admin-Key header."""

import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from backend import config

admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def require_admin(key: str | None = Security(admin_key_header)) -> None:
    """Reject the request unless the header matches ADMIN_API_KEY."""
    if not key or not secrets.compare_digest(
        key.encode(), config.ADMIN_API_KEY.encode()
    ):
        raise HTTPException(status_code=401, detail="Admin Key missing or wrong.")
