from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_emails():
    response = client.get("/emails/")
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert isinstance(data["emails"], list)
    # Ensure our dummy data is returned
    assert len(data["emails"]) > 0 