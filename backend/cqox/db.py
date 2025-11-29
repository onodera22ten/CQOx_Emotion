"""
Database helpers (SQLAlchemy engine/session factory) used across the backend.

FastAPI dependencies as well as the analytics/batch jobs import from here,
so keeping it in a single file avoids circular imports.
"""
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from .config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


# SQLite needs the check_same_thread flag, Postgres does not.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """
    Context manager for jobs/CLI scripts that need a transactional session.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

