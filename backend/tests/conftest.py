from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cqox.db import Base

TEST_DB_PATH = Path("/tmp/emotion_cqox_test.db")


@pytest.fixture(scope="session")
def engine():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def clean_database(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
