"""Password hashing for user admin (Module 12.5)."""

from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"sha256:{salt}:{digest}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored or not stored.startswith("sha256:"):
        return False
    _, salt, expected = stored.split(":", 2)
    digest = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return digest == expected
