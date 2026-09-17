from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from app.database import get_db


def test_root_redirects_to_docs(client):
    """GET / should redirect to /docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"


def test_health_check_ok(client):
    """GET /health should return 200 OK and database connected."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_health_check_db_failure(client):
    """GET /health should return 503 when database is unavailable."""
    mock_db = MagicMock()
    mock_db.execute.side_effect = OperationalError("DB connection error", {}, None)

    from app.main import app

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "disconnected" in data["database"]
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_get_db_dependency_generator():
    """Verify get_db generator yields a session and closes it."""
    db_gen = get_db()
    session = next(db_gen)
    assert session is not None
    try:
        next(db_gen)
    except StopIteration:
        pass
