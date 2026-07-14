import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    # Ensures startup & shutdown events are handled correctly
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_documents_unauthenticated(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"Hello World", "text/plain")},
    )
    assert response.status_code in (401, 403)
