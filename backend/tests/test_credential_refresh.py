import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.gmail import create_gmail_service, _service_cache
from app.services.email_sync_service import update_user_credentials


class TestCredentialRefresh:
    """Test credential refresh functionality"""
    
    def setup_method(self):
        """Clear the service cache before each test"""
        _service_cache.clear()
    
    def test_credential_refresh_callback_called(self):
        """Test that the callback is called when credentials are refreshed"""
        # Mock credentials that are expired
        mock_credentials = {
            'token': 'expired_token',
            'refresh_token': 'valid_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }
        
        # Create a mock callback
        callback_called = False
        updated_credentials = None
        
        def mock_callback(creds):
            nonlocal callback_called, updated_credentials
            callback_called = True
            updated_credentials = creds
        
        # Mock all the dependencies
        with patch('app.services.gmail.datetime') as mock_datetime, \
             patch('app.services.gmail.Credentials') as mock_creds_class, \
             patch('app.services.gmail.build') as mock_build, \
             patch('app.services.gmail.Request') as mock_request:
            
            # Mock datetime.now() to return a real datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            # Create a mock credentials object
            mock_creds = Mock()
            mock_creds.expired = True  # Simulate expired credentials
            mock_creds.token = 'new_token'
            mock_creds.refresh_token = 'valid_refresh_token'
            mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
            mock_creds.client_id = 'test_client_id'
            mock_creds.client_secret = 'test_client_secret'
            
            # Mock the refresh method
            def mock_refresh(request):
                # Update the token to simulate refresh
                mock_creds.token = 'new_refreshed_token'
            
            mock_creds.refresh = mock_refresh
            mock_creds_class.return_value = mock_creds
            
            # Mock the build function
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Call the function
            service = create_gmail_service(mock_credentials, mock_callback)
            
            # Verify the callback was called
            assert callback_called, "Callback should have been called"
            assert updated_credentials is not None, "Updated credentials should be passed to callback"
            assert updated_credentials['token'] == 'new_refreshed_token', "Token should be updated"
            
            # Verify the service was created
            assert service is not None
            mock_build.assert_called_once()
    
    def test_credential_refresh_no_callback(self):
        """Test that no error occurs when no callback is provided"""
        # Mock credentials that are expired
        mock_credentials = {
            'token': 'expired_token',
            'refresh_token': 'valid_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }
        
        # Mock all the dependencies
        with patch('app.services.gmail.datetime') as mock_datetime, \
             patch('app.services.gmail.Credentials') as mock_creds_class, \
             patch('app.services.gmail.build') as mock_build, \
             patch('app.services.gmail.Request') as mock_request:
            
            # Mock datetime.now() to return a real datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            # Create a mock credentials object
            mock_creds = Mock()
            mock_creds.expired = True  # Simulate expired credentials
            mock_creds.token = 'new_token'
            mock_creds.refresh_token = 'valid_refresh_token'
            mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
            mock_creds.client_id = 'test_client_id'
            mock_creds.client_secret = 'test_client_secret'
            
            # Mock the refresh method
            def mock_refresh(request):
                # Update the token to simulate refresh
                mock_creds.token = 'new_refreshed_token'
            
            mock_creds.refresh = mock_refresh
            mock_creds_class.return_value = mock_creds
            
            # Mock the build function
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Call the function without callback
            service = create_gmail_service(mock_credentials)
            
            # Verify the service was created without error
            assert service is not None
            mock_build.assert_called_once()
    
    def test_credential_refresh_callback_exception_handled(self):
        """Test that callback exceptions are handled gracefully"""
        # Mock credentials that are expired
        mock_credentials = {
            'token': 'expired_token',
            'refresh_token': 'valid_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }
        
        # Create a mock callback that raises an exception
        def mock_callback(creds):
            raise Exception("Callback error")
        
        # Mock all the dependencies
        with patch('app.services.gmail.datetime') as mock_datetime, \
             patch('app.services.gmail.Credentials') as mock_creds_class, \
             patch('app.services.gmail.build') as mock_build, \
             patch('app.services.gmail.Request') as mock_request:
            
            # Mock datetime.now() to return a real datetime
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            # Create a mock credentials object
            mock_creds = Mock()
            mock_creds.expired = True  # Simulate expired credentials
            mock_creds.token = 'new_token'
            mock_creds.refresh_token = 'valid_refresh_token'
            mock_creds.token_uri = 'https://oauth2.googleapis.com/token'
            mock_creds.client_id = 'test_client_id'
            mock_creds.client_secret = 'test_client_secret'
            
            # Mock the refresh method
            def mock_refresh(request):
                # Update the token to simulate refresh
                mock_creds.token = 'new_refreshed_token'
            
            mock_creds.refresh = mock_refresh
            mock_creds_class.return_value = mock_creds
            
            # Mock the build function
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Call the function - should not raise an exception
            service = create_gmail_service(mock_credentials, mock_callback)
            
            # Verify the service was created despite callback error
            assert service is not None
            mock_build.assert_called_once() 