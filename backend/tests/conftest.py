import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root and backend are on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import Dispute
from app.services.seeder import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure schema and baseline deterministic dataset exist prior to test suite execution."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Dispute).count() == 0:
            seed_database(db, force_reset=True)
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    """Reusable FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
