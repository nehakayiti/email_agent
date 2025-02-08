# tests/test_auth.py
import pytest
import requests
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.db import get_db
from app.models.user import User
from app.routers.auth import router as auth_router

# Load settings from test.env (if your env is set correctly)
settings = get_settings()

# Create an engine using your test database
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the User table if it does not exist
User.__table__.create(bind=engine, checkfirst=True)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Fake classes to avoid real Google calls ---

class FakeCredentials:
    token = "test-token"
    refresh_token = "test-refresh-token"
    token_uri = "http://token-uri"
    client_id = "test-client-id"
    client_secret = "test-client-secret"

class FakeFlow:
    def __init__(self, *args, **kwargs):
        self.credentials = None

    def authorization_url(self, *args, **kwargs):
        return "http://test-authorization", "test-state"

    def fetch_token(self, code):
        self.credentials = FakeCredentials()

# Override functions in the auth module.
import app.routers.auth as auth_module
auth_module.create_flow = lambda: FakeFlow()
auth_module.create_access_token = lambda data: "test-access-token"

# --- Fake response for the Google user info endpoint ---

FAKE_USERINFO_STATUS = 200
FAKE_USERINFO_DATA = {"email": "test@example.com", "name": "Test User"}

class FakeResponse:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data

original_requests_get = requests.get

def fake_requests_get(url, headers=None):
    if url == "https://www.googleapis.com/oauth2/v3/userinfo":
        return FakeResponse(FAKE_USERINFO_STATUS, FAKE_USERINFO_DATA)
    return original_requests_get(url, headers=headers)

@pytest.fixture(autouse=True)
def override_requests_get_fixture():
    requests.get = fake_requests_get
    yield
    requests.get = original_requests_get

# --- Tests ---

def test_login_redirect(client):
    """Test that the login endpoint redirects to Google OAuth."""
    response = client.get("/auth/login", follow_redirects=False)  # Don't follow redirects
    print(f"Response status: {response.status_code}")
    print(f"Available routes: {[route.path for route in client.app.routes]}")
    print(f"Response headers: {response.headers}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "http://test-authorization"

def test_callback_new_user(client, db):
    global FAKE_USERINFO_STATUS, FAKE_USERINFO_DATA
    FAKE_USERINFO_STATUS = 200
    FAKE_USERINFO_DATA = {"email": "test@example.com", "name": "Test User"}

    params = {"code": "test-code", "state": "test-state", "scope": "openid"}
    response = client.get("/auth/callback", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "test-access-token"
    assert data["token_type"] == "bearer"
    assert data["status"] == "new_user_created"
    assert data["user"] == {"email": "test@example.com", "name": "Test User"}

    # Verify the user exists in the test database
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None

def test_callback_existing_user(client, db):
    params = {"code": "test-code", "state": "test-state", "scope": "openid"}
    # First call should create a new user
    response = client.get("/auth/callback", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "new_user_created"

    # A second call should update the existing user
    response = client.get("/auth/callback", params=params)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "existing_user_updated"

def test_callback_google_userinfo_failure(client):
    global FAKE_USERINFO_STATUS, FAKE_USERINFO_DATA
    FAKE_USERINFO_STATUS = 400
    FAKE_USERINFO_DATA = {}

    params = {"code": "test-code", "state": "test-state", "scope": "openid"}
    response = client.get("/auth/callback", params=params)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Failed to get user info from Google" in data["detail"]
