# tests/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime
from typing import Generator
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture(scope="module")
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture(scope="module")
def supabase():
    """Create a Supabase client with service role for test data management"""
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    assert url and service_key, "Supabase credentials not found in environment"
    return create_client(url, service_key)

@pytest.fixture
def test_user(supabase) -> Generator[dict, None, None]:
    """Create a test user and clean up afterwards"""
    timestamp = datetime.now().timestamp()
    user_data = {
        "email": f"test_auth_{timestamp}@example.com",
        "name": "Test Auth User",
        "credentials": {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    
    try:
        response = supabase.table("users").insert(user_data).execute()
        user = response.data[0]
        yield user
    finally:
        if user.get('id'):
            supabase.table("users").delete().eq('id', user['id']).execute()


def test_callback_endpoint_invalid(client):
    """Test callback endpoint with invalid code"""
    response = client.get("/auth/callback")
    assert response.status_code == 422  # FastAPI validation error

def test_callback_endpoint_missing_code(client):
    """Test callback endpoint without code parameter"""
    response = client.get("/auth/callback?state=test&scope=test")
    assert response.status_code == 422  # FastAPI validation error
