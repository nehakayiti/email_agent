# tests/test_supabase_integration.py
import pytest
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Generator
from postgrest.exceptions import APIError

# Load environment variables from .env file
load_dotenv()

def ensure_table_exists(supabase) -> None:
    """Ensure the users table exists with correct structure"""
    try:
        # Try to create the table if it doesn't exist
        supabase.table("users").select("*").limit(1).execute()
    except APIError as e:
        if "relation" in str(e) and "does not exist" in str(e):
            # Create table using SQL
            supabase.rest.rpc(
                "create_users_table",
                {
                    "sql": """
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        name TEXT,
                        credentials JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
                    );
                    """
                }
            ).execute()

@pytest.fixture(scope="module")
def supabase():
    """Create a Supabase client fixture with service role key for full access"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")  # anon key
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # service role key
    
    assert url, "SUPABASE_URL environment variable is not set"
    assert key, "SUPABASE_KEY environment variable is not set"
    assert service_key, "SUPABASE_SERVICE_ROLE_KEY environment variable is not set"
    
    client = create_client(url, service_key)
    ensure_table_exists(client)
    return client

@pytest.fixture
def test_user(supabase) -> Generator[dict, None, None]:
    """Fixture to create and clean up a test user"""
    response = None
    user_data = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "name": "Test User",
        "credentials": {
            "access_token": "test_token",
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
        if response and response.data:
            try:
                supabase.table("users").delete().eq('id', response.data[0]['id']).execute()
            except APIError:
                pass

def test_connection(supabase):
    """Test basic Supabase connection"""
    response = supabase.table("users").select("*").limit(1).execute()
    assert response is not None
    assert hasattr(response, 'data'), "Response missing data attribute"

def test_user_creation(supabase):
    """Test user creation with validation"""
    response = None
    email = f"test_{datetime.now().timestamp()}@example.com"
    test_user = {
        "email": email,
        "name": "Test User",
        "credentials": {
            "access_token": "test_token",
            "refresh_token": "test_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    
    try:
        response = supabase.table("users").insert(test_user).execute()
        assert response.data, "Insert failed"
        
        user = response.data[0]
        assert user['email'] == email, "Email mismatch"
        assert user['name'] == "Test User", "Name mismatch"
        assert user['credentials']['access_token'] == "test_token", "Credentials not stored correctly"
        assert 'id' in user, "No ID generated"
        assert 'created_at' in user, "Created timestamp not set"
        
    finally:
        if response and response.data:
            try:
                supabase.table("users").delete().eq('id', response.data[0]['id']).execute()
            except APIError:
                pass

def test_user_retrieval(test_user, supabase):
    """Test user retrieval by ID and email"""
    # Test retrieval by ID
    response = supabase.table("users").select("*").eq('id', test_user['id']).execute()
    assert response.data, "No user found by ID"
    assert response.data[0]['id'] == test_user['id'], "ID mismatch"
    
    # Test retrieval by email
    response = supabase.table("users").select("*").eq('email', test_user['email']).execute()
    assert response.data, "No user found by email"
    assert response.data[0]['email'] == test_user['email'], "Email mismatch"

def test_user_update(test_user, supabase):
    """Test user update operations"""
    new_name = "Updated User Name"
    new_credentials = {
        "access_token": "updated_token",
        "refresh_token": "updated_refresh_token",
        "token_type": "Bearer",
        "expires_in": 7200
    }
    
    # Update multiple fields
    response = supabase.table("users")\
        .update({
            "name": new_name,
            "credentials": new_credentials
        })\
        .eq('id', test_user['id'])\
        .execute()
    
    assert response.data, "Update failed"
    updated_user = response.data[0]
    assert updated_user['name'] == new_name, "Name update failed"
    assert updated_user['credentials']['access_token'] == "updated_token", "Credentials update failed"
    assert updated_user['credentials']['expires_in'] == 7200, "Expiry update failed"

    # Verify update persisted
    verify_response = supabase.table("users")\
        .select("*")\
        .eq('id', test_user['id'])\
        .execute()
    
    assert verify_response.data[0]['name'] == new_name, "Update not persisted"
    assert verify_response.data[0]['credentials'] == new_credentials, "Credentials update not persisted"

def test_user_deletion(supabase):
    """Test user deletion with verification"""
    response = None
    test_user = {
        "email": f"delete_test_{datetime.now().timestamp()}@example.com",
        "name": "Delete Test User"
    }
    
    try:
        # Insert user
        response = supabase.table("users").insert(test_user).execute()
        user_id = response.data[0]['id']
        
        # Delete user
        delete_response = supabase.table("users").delete().eq('id', user_id).execute()
        assert delete_response.data, "Delete failed"
        
        # Verify deletion
        verify_response = supabase.table("users").select("*").eq('id', user_id).execute()
        assert not verify_response.data, "User still exists after deletion"
    finally:
        if response and response.data:
            try:
                supabase.table("users").delete().eq('id', response.data[0]['id']).execute()
            except APIError:
                pass

def test_credentials_update(test_user, supabase):
    """Test updating user credentials"""
    new_credentials = {
        "access_token": "new_token",
        "refresh_token": "new_refresh_token",
        "token_type": "Bearer",
        "expires_in": 7200
    }
    
    # Update credentials
    response = supabase.table("users")\
        .update({"credentials": new_credentials})\
        .eq('id', test_user['id'])\
        .execute()
    
    assert response.data, "Update failed"
    updated_user = response.data[0]
    assert updated_user['credentials']['access_token'] == "new_token", "Access token update failed"
    assert updated_user['credentials']['refresh_token'] == "new_refresh_token", "Refresh token update failed"
    assert updated_user['credentials']['expires_in'] == 7200, "Expiry update failed"

def test_user_filtering(supabase):
    """Test filtering and querying capabilities"""
    response = None
    test_users = [
        {
            "email": f"user1_{datetime.now().timestamp()}@example.com",
            "name": "User One",
            "credentials": {"access_token": "token1"}
        },
        {
            "email": f"user2_{datetime.now().timestamp()}@example.com",
            "name": "User Two",
            "credentials": {"access_token": "token2"}
        }
    ]
    
    try:
        response = supabase.table("users").insert(test_users).execute()
        user_ids = [user['id'] for user in response.data]
        
        # Test filtering by email pattern
        users = supabase.table("users")\
            .select("*")\
            .ilike('email', '%user1%')\
            .in_('id', user_ids)\
            .execute()
            
        assert len(users.data) == 1, "Wrong number of filtered users"
        assert users.data[0]['credentials']['access_token'] == "token1", "Wrong user credentials"
        
    finally:
        if response and response.data:
            for user_id in [user['id'] for user in response.data]:
                try:
                    supabase.table("users").delete().eq('id', user_id).execute()
                except APIError:
                    pass

