from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)

@patch('app.routers.auth.create_flow')
def test_callback(mock_create_flow):
    # Setup a mock flow and fake credentials
    mock_flow = Mock()
    dummy_credentials = Mock()
    dummy_credentials.id_token = {"email": "test@example.com", "name": "Test User"}
    dummy_credentials.token = "dummy_token"
    dummy_credentials.refresh_token = "dummy_refresh_token"
    dummy_credentials.token_uri = "https://oauth2.googleapis.com/token"
    dummy_credentials.client_id = "dummy_client_id"
    dummy_credentials.client_secret = "dummy_client_secret"
    
    mock_flow.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?mock=true", None)
    mock_flow.fetch_token.return_value = None
    mock_flow.credentials = dummy_credentials
    mock_create_flow.return_value = mock_flow
    
    # Patch the Supabase dependency for callback route
    class DummyResponse:
        error = None
    with patch('app.routers.auth.get_supabase_client') as mock_supabase_dep:
        mock_client = Mock()
        # When upsert().execute() is called, return a dummy response with no error.
        mock_client.table.return_value.upsert.return_value.execute.return_value = DummyResponse()
        mock_supabase_dep.return_value = mock_client
        
        response = client.get("/auth/callback?code=dummy_code")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer" 