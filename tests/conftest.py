import os
import tempfile

# Use a temp file for the test database and ensure main recipe.db is never touched
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db", prefix="recipe_test_")
os.close(_test_db_fd)
TEST_DATABASE_URL = f"sqlite:///{_test_db_path}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


event.listen(engine, "connect", _set_sqlite_pragma)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """Provide a TestClient that uses the test database."""

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def make_recipe_payload(**overrides):
    """Build a valid recipe creation payload with optional overrides."""
    defaults = {
        "title": "Блины",
        "description": "Классические тонкие блины на молоке",
        "cooking_time_minutes": 30,
        "difficulty": 2,
        "category": "breakfast",
    }
    defaults.update(overrides)
    return {"recipe": defaults}


def make_ingredient_payload(recipe_id: int, **overrides):
    """Build a valid ingredient creation payload with optional overrides."""
    defaults = {
        "name": "Мука",
        "quantity": 200.0,
        "unit": "g",
        "recipe_id": recipe_id,
    }
    defaults.update(overrides)
    return {"ingredient": defaults}
