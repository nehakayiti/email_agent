from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('app.routers.auth.create_flow')
def test_login_redirect(mock_create_flow):
    # Create a mock flow
    mock_flow = Mock()
    mock_flow.authorization_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?mock=true", 
        None
    )
    mock_create_flow.return_value = mock_flow
    
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"] 