import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_supabase_admin_client
from starlette.concurrency import run_in_threadpool
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)  # Return TestClient instance directly, not the fixture function

@pytest.fixture
def mock_auth_dependencies(mocker):
    """Fixture to set up all auth-related mocks"""
    mock_flow = mocker.patch('app.routers.auth.create_flow')
    mock_session = mocker.patch('requests.Session')
    mock_supabase = mocker.patch('app.dependencies.get_supabase_admin_client')
    
    # Mock userinfo response
    mock_session.return_value.get.return_value.json.return_value = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    # Mock flow credentials and fetch_token
    mock_credentials = mocker.Mock(
        token="test_token",
        refresh_token="test_refresh_token",
        token_uri="test_uri",
        client_id="test_client_id",
        client_secret="test_secret",
        id_token={
            "email": "test@example.com",
            "name": "Test User1"
        }
    )
    mock_flow.return_value.credentials = mock_credentials
    mock_flow.return_value.fetch_token.return_value = None  # Mock successful token fetch
    
    # Mock Supabase response
    mock_response = mocker.Mock()
    mock_response.error = None
    mock_supabase.return_value.table.return_value.upsert.return_value.execute.return_value = mock_response
    
    return mock_flow, mock_session, mock_supabase

@pytest.fixture(autouse=True)
def cleanup_test_user():
    """Automatically clean up test user after each test"""
    yield  # Run the test
    
    # Clean up after test
    try:
        supabase = get_supabase_admin_client()
        supabase.table("users") \
            .delete() \
            .eq("email", "test@example.com") \
            .execute()
    except Exception as e:
        logger.warning(f"Failed to cleanup test user: {e}")