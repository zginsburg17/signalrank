# Set test environment variables before any app module is imported.
# pydantic-settings gives env vars priority over .env file, so these
# take effect when Settings() is first instantiated during import.
import os

os.environ["POSTGRES_URL"] = "sqlite:///:memory:"
os.environ["API_KEY"] = "test-key"
os.environ["ENRICHMENT_API_URL"] = "https://example.com/analyze"

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# Import app modules only after env vars are set.
import app.db_postgres as _pg  # noqa: E402
from app.db_postgres import Base  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.main import app  # noqa: E402

# Replace the module-level engine with an in-memory SQLite engine that
# uses StaticPool so every session shares the same underlying connection
# (required for SQLite :memory: to persist across sessions).
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_pg.engine = _test_engine
_pg.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Patch the engine reference inside app.main so the lifespan create_all
# uses SQLite instead of trying to connect to Postgres.
import app.main as _main  # noqa: E402

_main.engine = _test_engine

# Create all tables once for the test session.
Base.metadata.create_all(bind=_test_engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    """Truncate all tables before each test so tests are fully isolated."""
    from sqlalchemy import text

    session = _pg.SessionLocal()
    session.execute(text("DELETE FROM feedback"))
    session.commit()
    session.close()
    yield


@pytest.fixture()
def db_session():
    session = _pg.SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture()
def client(db_session):
    """HTTP test client with SQLite DB and mocked MongoDB collections."""

    def override_get_db():
        yield db_session

    with (
        patch("app.repos.mongo_repo.raw_feedback_collection") as m_raw,
        patch("app.repos.mongo_repo.enrichment_results_collection") as m_enrich,
        patch("app.repos.mongo_repo.issue_snapshots_collection") as m_snap,
    ):
        m_raw.insert_one = MagicMock(return_value=MagicMock())
        m_enrich.insert_one = MagicMock(return_value=MagicMock())
        m_snap.insert_one = MagicMock(return_value=MagicMock())

        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c
        app.dependency_overrides.clear()


# Convenience constant so test modules don't hardcode the key.
API_HEADERS = {"X-Api-Key": "test-key"}
