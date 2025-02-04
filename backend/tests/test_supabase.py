from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, Mock, MagicMock
import pytest
from app.main import app
from app.dependencies import get_supabase_client

client = TestClient(app)

def test_supabase_connection():
    """Test that Supabase client can be created"""
    with patch('app.dependencies.create_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = {"data": []}
        mock_create_client.return_value = mock_client

        test_client = get_supabase_client()
        assert test_client is not None

def test_supabase_connection_failure():
    from app.dependencies import get_supabase_client
    get_supabase_client.cache_clear()  # clear the cache first

    mock_client = MagicMock()
    # Simulate an exception during the connection test
    mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection failed")

    with patch('app.dependencies.create_client', return_value=mock_client):
        with pytest.raises(HTTPException) as exc_info:
            get_supabase_client()

        assert exc_info.value.status_code == 503
        assert "Database connection error" in exc_info.value.detail

        
        
def test_supabase_user_insertion():
    from app.dependencies import get_supabase_client
    get_supabase_client.cache_clear()  # clear the cache so the patch takes effect

    expected_result = {
        "data": [{
            "id": 1,
            "email": "test@example.com",
            "name": "Test User"
        }],
        "error": None
    }

    # Create separate mocks for the connection test and the upsert chain
    connection_chain = MagicMock()
    connection_chain.select.return_value.limit.return_value.execute.return_value = {"data": []}

    upsert_chain = MagicMock()
    upsert_chain.upsert.return_value.execute.return_value = expected_result

    call_count = 0
    def table_side_effect(table_name: str):
        nonlocal call_count
        call_count += 1
        # The first call is the connection test
        if call_count == 1:
            return connection_chain
        # Later calls are for operations
        return upsert_chain

    mock_client = MagicMock()
    mock_client.table.side_effect = table_side_effect

    with patch('app.dependencies.create_client', return_value=mock_client):
        supabase = get_supabase_client()  # This call will use the patched create_client
        result = supabase.table("users").upsert({
            "email": "test@example.com",
            "name": "Test User"
        }).execute()

        assert result == expected_result
