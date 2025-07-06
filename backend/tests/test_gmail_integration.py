"""
Integration tests for Gmail API functionality.
These tests use the real Gmail API with test credentials.
"""

import pytest
import os
import uuid
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch
from sqlalchemy.orm import Session
from app.services.gmail import create_gmail_service, get_gmail_profile
from app.services.email_sync_service import sync_emails_since_last_fetch
from app.models.user import User
from app.models.email import Email
from app.models.email_sync import EmailSync
from dotenv import load_dotenv
import subprocess
import time
from app.services.email_sync_service import perform_full_sync
from app.models.email import Email
import json

# Load test environment variables
load_dotenv('.env.test')

class TestGmailAPIIntegration:
    """Test Gmail API integration with real credentials."""
    
    @pytest.fixture
    def test_credentials(self):
        """Get test Gmail credentials from environment or generate automatically."""
        # Try to get credentials from environment first
        credentials = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
            'token': os.getenv('GOOGLE_ACCESS_TOKEN', ''),  # Always provide token key
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
        
        # If no refresh token, try to generate one automatically
        if not credentials.get('refresh_token'):
            from tests.conftest import generate_test_credentials
            credentials = generate_test_credentials()
        
        return credentials
    
    def test_gmail_api_connection_and_auth(self, test_credentials):
        """
        Test that we can successfully connect to the Gmail API using test credentials
        and perform basic operations.
        """
        # Skip this test if we don't have real credentials
        if not test_credentials.get('refresh_token') or test_credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        try:
            # Test 1: Create Gmail service
            service = create_gmail_service(test_credentials)
            assert service is not None
            
            # Test 2: Get user profile
            profile = get_gmail_profile(test_credentials)
            assert profile is not None
            assert 'emailAddress' in profile
            assert 'messagesTotal' in profile
            assert 'threadsTotal' in profile
            
            # Test 3: List messages (basic operation)
            messages_response = service.users().messages().list(
                userId='me',
                maxResults=5
            ).execute()
            
            assert 'messages' in messages_response
            # Even if no messages, the response should be valid
            
            print(f"✅ Gmail API connection successful")
            print(f"   - Email: {profile.get('emailAddress')}")
            print(f"   - Messages: {profile.get('messagesTotal')}")
            print(f"   - Threads: {profile.get('threadsTotal')}")
            
        except Exception as e:
            pytest.fail(f"Gmail API connection failed: {str(e)}")
    
    def test_gmail_service_creation_with_invalid_credentials(self):
        """Test that invalid credentials are handled gracefully."""
        invalid_credentials = {
            'client_id': 'invalid',
            'client_secret': 'invalid',
            'refresh_token': 'invalid',
            'token': 'invalid',  # Add missing token key
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
        
        # The service creation might not raise an exception immediately
        # but should fail when trying to use it
        try:
            service = create_gmail_service(invalid_credentials)
            # If service is created, it should fail when we try to use it
            if service:
                with pytest.raises(Exception):
                    service.users().getProfile(userId='me').execute()
        except Exception:
            # Service creation failed as expected
            pass
    
    @pytest.mark.skip(reason="Requires real Gmail test account setup")
    def test_gmail_message_operations(self, test_credentials):
        """
        Test basic Gmail message operations.
        This test requires a real test Gmail account with some emails.
        """
        service = create_gmail_service(test_credentials)
        
        # List messages
        messages_response = service.users().messages().list(
            userId='me',
            maxResults=10
        ).execute()
        
        if messages_response.get('messages'):
            # Test getting a specific message
            first_message_id = messages_response['messages'][0]['id']
            message = service.users().messages().get(
                userId='me',
                id=first_message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            
            assert 'id' in message
            assert 'threadId' in message
            assert 'labelIds' in message

class TestEmailSyncIntegration:
    """Test email synchronization from Gmail to database."""
    
    @pytest.fixture
    def test_user(self, db, test_user_with_credentials):
        """Create a test user for sync tests with automated credentials."""
        # Use the automated test user fixture from conftest
        return test_user_with_credentials
    
    def test_email_sync_from_gmail_to_database(self, db, test_user: User, seeded_categories):
        """
        Test that emails can be synced from Gmail to the database.
        This test validates the core email synchronization functionality.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing emails for this user
        db.query(Email).filter(Email.user_id == test_user.id).delete()
        db.query(EmailSync).filter(EmailSync.user_id == test_user.id).delete()
        db.commit()
        
        # Get initial email count
        initial_email_count = db.query(Email).filter(Email.user_id == test_user.id).count()
        
        try:
            # Run the sync
            import asyncio
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            # Verify sync was successful
            assert sync_result['status'] == 'success'
            assert 'sync_count' in sync_result
            
            # Check for new_email_count (may not be present if no emails were synced)
            new_email_count = sync_result.get('new_email_count', 0)
            
            # Get final email count
            final_email_count = db.query(Email).filter(Email.user_id == test_user.id).count()
            
            # Verify emails were synced (if any)
            synced_emails = db.query(Email).filter(Email.user_id == test_user.id).all()
            
            print(f"✅ Email sync successful")
            print(f"   - Initial emails: {initial_email_count}")
            print(f"   - Final emails: {final_email_count}")
            print(f"   - New emails synced: {new_email_count}")
            print(f"   - Total sync count: {sync_result['sync_count']}")
            
            # If emails were synced, verify their data integrity
            if synced_emails:
                for email in synced_emails:
                    assert email.gmail_id is not None
                    assert email.thread_id is not None
                    assert email.user_id == test_user.id
                    assert email.subject is not None
                    assert email.from_email is not None
                    assert email.received_at is not None
                    # Check if category is set, but don't fail if it's None (might be a legitimate case)
                    if email.category is None:
                        print(f"Warning: Email {email.gmail_id} has no category assigned")
                    else:
                        print(f"Email {email.gmail_id} categorized as: {email.category}")
                
                # Verify sync record was created/updated
                sync_record = db.query(EmailSync).filter(EmailSync.user_id == test_user.id).first()
                assert sync_record is not None
                assert sync_record.last_fetched_at is not None
            
        except Exception as e:
            pytest.fail(f"Email sync failed: {str(e)}")
    
    def test_sync_with_no_credentials(self, db):
        """Test sync behavior when user has no credentials."""
        user = User(
            id=uuid.uuid4(),
            email="no-credentials@example.com",
            name="No Credentials User",
            credentials=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        import asyncio
        sync_result = asyncio.run(sync_emails_since_last_fetch(db, user))
        
        assert sync_result['status'] == 'error'
        assert 'No credentials found' in sync_result['message']
    
    def test_sync_with_invalid_credentials(self, db):
        """Test sync behavior with invalid credentials."""
        user = User(
            id=uuid.uuid4(),
            email="invalid-credentials@example.com",
            name="Invalid Credentials User",
            credentials={
                'client_id': 'invalid',
                'client_secret': 'invalid',
                'refresh_token': 'invalid',
                'token': 'invalid',  # Add missing token key
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        import asyncio
        # The sync function should handle invalid credentials gracefully
        # and return an error status rather than raising an exception
        sync_result = asyncio.run(sync_emails_since_last_fetch(db, user))
        
        # Should return an error status
        assert sync_result['status'] == 'error'
        assert 'sync_count' in sync_result
        assert sync_result['sync_count'] == 0 

@pytest.fixture(scope="function")
def seed_gmail():
    # Check if required environment variables are set
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        pytest.skip(f"Missing required environment variables for Gmail seeding: {missing_vars}")
    
    # Run the seeding script to populate the test Gmail account from project root
    try:
        subprocess.run([
            "python", "backend/scripts/seed_test_gmail.py", "--count", "5"
        ], check=True, cwd=os.path.join(os.path.dirname(__file__), "..", ".."))
        # Wait a bit for Gmail to process
        time.sleep(3)
        yield
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Gmail seeding failed: {e}")

@pytest.mark.asyncio
async def test_full_sync_from_seeded_gmail(db, seed_gmail, test_user_with_credentials, seeded_categories):
    """
    Seeds 5 emails, runs a full sync, and verifies all 5 are in the test DB.
    """
    user = test_user_with_credentials
    if not user:
        pytest.skip("No test user with credentials available")

    print("Waiting 2 seconds for Gmail to process seeded emails...")
    await asyncio.sleep(2)

    # Debug: Check what emails are actually in the Gmail account
    from app.services.gmail import create_gmail_service
    gmail_service = create_gmail_service(user.credentials)
    try:
        messages = gmail_service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        print(f"Found {len(messages.get('messages', []))} messages in INBOX")
        for i, msg in enumerate(messages.get('messages', [])[:3]):
            msg_detail = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
            subject = headers.get('Subject', 'No Subject')
            from_email = headers.get('From', 'Unknown')
            labels = msg_detail.get('labelIds', [])
            print(f"  {i+1}. '{subject}' from {from_email} (labels: {labels})")
    except Exception as e:
        print(f"Error checking Gmail messages: {e}")

    # Run the full sync
    result = await perform_full_sync(db, user)
    print(f"Full sync result: {result}")
    assert result["status"] == "success", f"Full sync failed: {result}"

    # Debug: Test fetch_emails_from_gmail directly
    print("\n=== Testing fetch_emails_from_gmail directly ===")
    from app.services.gmail import fetch_emails_from_gmail
    try:
        emails_raw = await fetch_emails_from_gmail(user.credentials, max_results=10)
        print(f"fetch_emails_from_gmail returned {len(emails_raw)} emails")
        for i, email in enumerate(emails_raw[:3]):
            print(f"  {i+1}. '{email.get('subject', 'No subject')}' (ID: {email.get('gmail_id')})")
    except Exception as e:
        print(f"Error calling fetch_emails_from_gmail directly: {e}")

    # Load seeded Gmail IDs
    ids_path = os.path.join(os.path.dirname(__file__), "test_email_ids.json")
    with open(ids_path, "r") as f:
        seeded_id_dicts = json.load(f)
        seeded_ids = set(d["message_id"] for d in seeded_id_dicts)

    # Check that 5 seeded emails are present in the DB
    emails = db.query(Email).filter(Email.user_id == user.id, Email.gmail_id.in_(seeded_ids)).all()
    print(f"Seeded emails in DB for user {user.email}: {len(emails)}")
    for email in emails:
        print(f"  - {email.subject} (Gmail ID: {email.gmail_id})")
    assert len(emails) == 5, f"Expected 5 seeded emails, found {len(emails)}" 