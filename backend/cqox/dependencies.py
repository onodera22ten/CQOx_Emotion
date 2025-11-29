"""
FastAPI dependency helpers.

Authentication is out-of-scope for the PDF spec, so we expose a simple
`get_current_user` placeholder that mimics a logged-in account.
"""
from typing import Any, Dict

from sqlalchemy.orm import Session

from .db import get_db as _get_db


def get_db() -> Session:
    """
    FastAPI dependency that yields a SQLAlchemy session.

    FastAPI expects callables that return generators; we simply re-yield the
    generator from cqox.db without exposing it directly.
    """
    yield from _get_db()


def get_current_user() -> Dict[str, Any]:
    """
    Placeholder auth dependency.

    In production this would decode a JWT/OAuth2 token. For now,
    we ensure tests and demo flows always have a deterministic user.
    """
    return {"id": 1, "username": "demo_user"}
