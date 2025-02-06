from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from app.main import app
from app.config import Settings
from google_auth_oauthlib.flow import Flow

@pytest.fixture
def mock_settings(mocker: MockerFixture) -> Settings:
    """Mock settings to avoid loading real environment variables"""
    settings = Settings(
        GOOGLE_CLIENT_ID="mock_client_id",
        GOOGLE_CLIENT_SECRET="mock_secret",
        GOOGLE_REDIRECT_URI="http://mock-redirect",
        SUPABASE_URL="http://mock-supabase",
        SUPABASE_KEY="mock-key",
        SUPABASE_SERVICE_ROLE_KEY="mock-service-role-key",
        SECRET_KEY="mock-secret"
    )
    mocker.patch("app.dependencies.get_settings", return_value=settings)
    mocker.patch("app.routers.auth.settings", settings)
    mocker.patch("app.routers.auth.get_settings", return_value=settings)
    return settings

@pytest.fixture
def mock_flow(mocker: MockerFixture):
    """Mock Google OAuth flow"""
    mock_flow = MagicMock(spec=Flow)
    mock_flow.authorization_url.return_value = (
        "https://accounts.google.com/o/oauth2/auth?mock_params",
        "mock_state"
    )
    mocker.patch("app.routers.auth.create_flow", return_value=mock_flow)
    return mock_flow

@pytest.fixture
def client(mock_settings, mock_flow, override_supabase_dependency):
    """Create test client with dependency override applied"""
    with TestClient(app) as client:
        yield client

def test_google_login_redirect(client: TestClient, mock_settings: Settings, mock_flow):
    """Test that login endpoint redirects to Google OAuth URL"""
    response = client.get("/auth/login", follow_redirects=False)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"]
    
    mock_flow.authorization_url.assert_called_once_with(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

@pytest.fixture
def mock_credentials(mocker: MockerFixture):
    """Mock Google credentials"""
    mock_creds = MagicMock()
    mock_creds.token = "mock_token"
    mock_creds.refresh_token = "mock_refresh_token"
    mock_creds.token_uri = "https://oauth2.googleapis.com/token"
    mock_creds.client_id = "mock_client_id"
    mock_creds.client_secret = "mock_client_secret"
    # Use a dictionary instead of MagicMock for id_token
    mock_creds.id_token = {
        "email": "test@example.com",
        "name": "Test User"
    }
    return mock_creds

@pytest.fixture
def mock_supabase(mocker: MockerFixture):
    """Mock Supabase client"""
    mock_client = MagicMock()
    # Return a dictionary for the execute response
    response = MagicMock()
    response.error = None
    response.data = [{
        "id": "mock-user-id",
        "email": "test@example.com",
        "name": "Test User"
    }]
    mock_client.table.return_value.upsert.return_value.execute.return_value = response
    
    # Patch creating and retrieving the Supabase client
    mocker.patch("app.dependencies.create_client", return_value=mock_client)
    mocker.patch("app.dependencies.get_supabase_client", return_value=mock_client)
    mocker.patch("app.dependencies.get_supabase_admin_client", return_value=mock_client)
    mocker.patch("app.routers.auth.get_supabase_admin_client", return_value=mock_client)
    return mock_client

@pytest.fixture
def mock_userinfo_session(mocker: MockerFixture):
    """Mock requests Session for userinfo"""
    mock_session = MagicMock()
    mock_session.get.return_value.json.return_value = {
        "email": "test@example.com",
        "name": "Test User"
    }
    mocker.patch("requests.Session", return_value=mock_session)
    return mock_session

@pytest.fixture
def mock_threadpool(mocker: MockerFixture):
    """Mock run_in_threadpool to run synchronously"""
    async def mock_run(func, *args, **kwargs):
        return func(*args, **kwargs)
    mocker.patch("app.routers.auth.run_in_threadpool", side_effect=mock_run)
    return mock_run

@pytest.fixture(autouse=True)
def override_supabase_dependency(mock_supabase):
    """
    Override the get_supabase_admin_client dependency so that the
    /callback endpoint receives the mock_supabase instance.
    """
    from app.dependencies import get_supabase_admin_client
    app.dependency_overrides[get_supabase_admin_client] = lambda: mock_supabase
    yield
    app.dependency_overrides.pop(get_supabase_admin_client, None)

def test_google_callback_success(
    client: TestClient,
    mock_flow,
    mock_credentials,
    mock_supabase,
    mock_userinfo_session,
    mock_threadpool
):
    """Test successful Google OAuth callback"""
    # Set up the mock flow to return our mock credentials
    mock_flow.fetch_token = MagicMock()  # Mock the fetch_token method
    mock_flow.credentials = mock_credentials
    
    # Set up the Supabase mock to track calls
    mock_table = MagicMock(name="mock_table")
    # Mock the select query for checking existing user
    mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    # Mock the insert for new user
    mock_table.insert.return_value.execute.return_value = MagicMock(error=None)
    mock_supabase.table = MagicMock(return_value=mock_table)
    
    response = client.get(
        "/auth/callback",
        params={
            "code": "mock_auth_code",
            "state": "mock_state",
            "scope": "mock_scope"
        }
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"
    assert response_data["status"] == "new_user_created"
    assert response_data["user"]["email"] == "test@example.com"
    
    # Verify our mocks were called correctly
    mock_flow.fetch_token.assert_called_once_with(code="mock_auth_code")
    mock_table.select.assert_called_once()
    mock_table.insert.assert_called_once()

def test_google_callback_missing_code(client: TestClient):
    """Test callback fails when code is missing"""
    # FastAPI returns 422 for missing required parameters
    response = client.get("/auth/callback")
    assert response.status_code == 422
    assert "detail" in response.json()

def test_google_callback_upsert_error(
    client: TestClient,
    mock_flow,
    mock_credentials,
    mock_supabase,
    mock_userinfo_session,
    mock_threadpool
):
    """Test callback when Supabase insert returns an error"""
    # Set up the mock flow to return our mock credentials
    mock_flow.fetch_token = MagicMock()
    mock_flow.credentials = mock_credentials

    # Set up the Supabase mock to simulate an error response
    mock_table = MagicMock(name="mock_table")
    # Mock the select query
    mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    # Mock the insert with error
    error_response = MagicMock(name="mock_execute_response")
    error_response.error = "Test error"
    mock_table.insert.return_value.execute.return_value = error_response
    mock_supabase.table = MagicMock(return_value=mock_table)

    response = client.get(
        "/auth/callback",
        params={
            "code": "mock_auth_code",
            "state": "mock_state",
            "scope": "mock_scope"
        }
    )

    assert response.status_code == 500
    response_data = response.json()
    assert "error" in response_data
    assert response_data["error"] == "Test error"

def test_google_callback_fetch_token_exception(
    client: TestClient,
    mock_flow,
    mock_credentials,
    mock_supabase,
    mock_userinfo_session,
    mock_threadpool
):
    """Test callback when flow.fetch_token raises an exception"""
    # Simulate an exception when fetch_token is called.
    mock_flow.fetch_token = MagicMock(side_effect=Exception("Token fetch error"))
    
    # Note: Since fetch_token fails, credentials are not used.
    response = client.get(
        "/auth/callback",
        params={
            "code": "mock_auth_code",
            "state": "mock_state",
            "scope": "mock_scope"
        }
    )
    
    # The endpoint now returns a JSONResponse with error and message
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data
    assert "message" in response_data
    assert response_data["error"] == "Token fetch error"
    assert response_data["message"] == "Authentication failed"
