# tests/test_auth_callback.py

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.routers.auth import process_auth_callback

# A simple dummy flow that simulates the behavior of the real Flow.
class DummyFlow:
    def __init__(self, dummy_credentials):
        self.redirect_uri = None
        self.credentials = dummy_credentials

    def fetch_token(self, code):
        # In the dummy flow, nothing is done.
        pass

# A dummy credentials class.
class DummyCredentials:
    def __init__(self):
        self.id_token = {"email": "test@example.com", "name": "Test User"}
        self.token = "dummy_token"
        self.refresh_token = "dummy_refresh_token"
        self.token_uri = "https://oauth2.googleapis.com/token"
        self.client_id = "dummy_client_id"
        self.client_secret = "dummy_client_secret"

# A dummy flow factory that returns a DummyFlow.
def dummy_flow_factory():
    return DummyFlow(DummyCredentials())

# A dummy Supabase client that fakes the upsert call.
class DummySupabaseClient:
    def table(self, name):
        # Simply return self regardless of the table name.
        return self

    def upsert(self, data):
        # Save the data for any future use if needed.
        self.data = data
        return self

    def execute(self):
        # Return a dummy response with no error.
        class DummyResponse:
            error = None
        return DummyResponse()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def supabase_client():
    return DummySupabaseClient()

def test_process_auth_callback_success(supabase_client):
    result = process_auth_callback("dummy_code", supabase_client, flow_factory=dummy_flow_factory)
    assert "access_token" in result
    assert result["token_type"] == "bearer"

def test_process_auth_callback_failure():
    # Create a dummy client that returns an error response.
    class DummyResponseWithError:
        error = "Some error"

    class DummySupabaseClientWithError:
        def table(self, name):
            return self

        def upsert(self, data):
            return self

        def execute(self):
            return DummyResponseWithError()

    dummy_client = DummySupabaseClientWithError()
    with pytest.raises(HTTPException) as exc_info:
        process_auth_callback("dummy_code", dummy_client, flow_factory=dummy_flow_factory)
    assert exc_info.value.status_code == 500

def test_callback_with_different_scope_order(client):
    # Mock the OAuth flow
    scope = "openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    response = client.get(f"/auth/callback?code=test_code&state=test_state&scope={scope}")
    assert response.status_code == 200  # Should succeed despite different scope order

def test_callback_with_missing_scope(client):
    # Mock the OAuth flow with missing scope
    scope = "openid email profile"  # Missing gmail.readonly scope
    response = client.get(f"/auth/callback?code=test_code&state=test_state&scope={scope}")
    assert response.status_code == 400
    assert "Missing required scopes" in response.json()["detail"]
