import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_callback(client, mock_auth_dependencies):
    response = client.get("/auth/callback?code=test_code&state=test_state&scope=test_scope")
    assert response.status_code == 200
