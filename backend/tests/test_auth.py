from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('app.routers.auth.flow')
def test_login_redirect(mock_flow):
    # Mock the authorization URL
    mock_flow.authorization_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?mock=true", 
        None
    )
    
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"] 