from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
from app.dependencies import get_supabase_client

# Pass the app instance as a positional argument.
client = TestClient(app)

@patch('app.routers.auth.create_flow')
def test_callback(mock_create_flow):
    # Clear the cached real client.
    get_supabase_client.cache_clear()

    # Set up the fake flow and credentials.
    mock_flow = Mock()
    dummy_credentials = Mock()
    dummy_credentials.id_token = {"email": "test@example.com", "name": "Test User"}
    dummy_credentials.token = "dummy_token"
    dummy_credentials.refresh_token = "dummy_refresh_token"
    dummy_credentials.token_uri = "https://oauth2.googleapis.com/token"
    dummy_credentials.client_id = "dummy_client_id"
    dummy_credentials.client_secret = "dummy_client_secret"

    mock_flow.authorization_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?mock=true", None
    )
    mock_flow.fetch_token.return_value = None
    mock_flow.credentials = dummy_credentials
    mock_create_flow.return_value = mock_flow

    # Create a dummy Supabase client with a dummy upsert response.
    dummy_client = Mock()
    class DummyResponse:
        error = None
    dummy_client.table.return_value.upsert.return_value.execute.return_value = DummyResponse()

    # Patch create_client in app.dependencies so that our dummy client is used.
    with patch('app.dependencies.create_client', return_value=dummy_client):
        # Override the dependency for FastAPI.
        app.dependency_overrides[get_supabase_client] = lambda: dummy_client

        response = client.get("/auth/callback?code=dummy_code")
        assert response.status_code == 200

        # Clean up the override.
        app.dependency_overrides.clear()
