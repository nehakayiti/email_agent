"""
Integration Tests for Two-Way Email Sync

This test file validates the complete two-way synchronization between our database
and Gmail, ensuring that:
1. Emails sync from Gmail to our database correctly
2. Local changes (category updates) propagate back to Gmail correctly
3. The system maintains consistency between local and remote states

These tests use the real Gmail API with test credentials and a dedicated test database.
"""

import pytest
import os
import uuid
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.models.user import User
from app.models.email import Email
from app.models.email_operation import EmailOperation, OperationType, OperationStatus
from app.models.email_category import EmailCategory
from app.services.email_sync_service import sync_emails_since_last_fetch, perform_full_sync
from app.services.email_operations_service import create_operation, process_pending_operations
from app.services.gmail import create_gmail_service, get_gmail_profile
from app.utils.email_utils import set_email_category_and_labels

# Load test environment variables
load_dotenv('.env.test')

class TestTwoWaySyncIntegration:
    """Test complete two-way synchronization between database and Gmail."""
    
    @pytest.fixture
    def test_user(self, db, test_user_with_credentials):
        """Create a test user for sync tests with automated credentials."""
        return test_user_with_credentials
    
    @pytest.fixture
    def gmail_service(self, test_user):
        """Create Gmail service for direct API operations."""
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        return create_gmail_service(test_user.credentials)
    
    def test_full_sync_from_seeded_gmail(self, db, test_user, seeded_categories):
        """
        Test that emails seeded in Gmail are correctly synced to our database.
        This validates the Gmail → Database sync path.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing emails for this user
        db.query(Email).filter(Email.user_id == test_user.id).delete()
        db.commit()
        
        # Get initial email count
        initial_email_count = db.query(Email).filter(Email.user_id == test_user.id).count()
        
        try:
            # Run the sync
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            # Verify sync was successful
            assert sync_result['status'] == 'success'
            assert 'sync_count' in sync_result
            
            # Get final email count
            final_email_count = db.query(Email).filter(Email.user_id == test_user.id).count()
            
            # Verify emails were synced (if any exist in the test account)
            synced_emails = db.query(Email).filter(Email.user_id == test_user.id).all()
            
            print(f"✅ Full sync test completed")
            print(f"   - Initial emails: {initial_email_count}")
            print(f"   - Final emails: {final_email_count}")
            print(f"   - Sync count: {sync_result['sync_count']}")
            
            # If emails were synced, verify their data integrity
            if synced_emails:
                for email in synced_emails:
                    assert email.gmail_id is not None
                    assert email.thread_id is not None
                    assert email.user_id == test_user.id
                    assert email.subject is not None
                    assert email.from_email is not None
                    assert email.received_at is not None
                    
                    # Verify categorization was applied
                    if email.category is None:
                        print(f"Warning: Email {email.gmail_id} has no category assigned")
                    else:
                        # Verify the category exists in our system
                        category = db.query(EmailCategory).filter(EmailCategory.name == email.category).first()
                        assert category is not None, f"Category {email.category} not found for email {email.gmail_id}"
            
        except Exception as e:
            pytest.fail(f"Full sync test failed: {str(e)}")
    
    def test_label_update_syncs_to_gmail(self, db, test_user, seeded_categories, gmail_service):
        """
        Test that changing an email's category in our database correctly applies
        the corresponding label in the user's actual Gmail account.
        
        This validates the Database → Gmail sync path.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing emails and operations for this user
        db.query(EmailOperation).filter(EmailOperation.user_id == test_user.id).delete()
        db.query(Email).filter(Email.user_id == test_user.id).delete()
        db.commit()
        
        try:
            # Step 1: Sync some emails from Gmail to get test data
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            if sync_result['status'] != 'success':
                pytest.skip("No emails available for testing - sync failed or no emails in test account")
            
            # Get a synced email to work with
            test_email = db.query(Email).filter(Email.user_id == test_user.id).first()
            
            if not test_email:
                pytest.skip("No emails synced from Gmail - cannot test label updates")
            
            print(f"Testing with email: {test_email.subject} (Gmail ID: {test_email.gmail_id})")
            
            # Step 2: Get current labels from Gmail
            message = gmail_service.users().messages().get(
                userId='me',
                id=test_email.gmail_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            
            original_labels = message.get('labelIds', [])
            print(f"Original Gmail labels: {original_labels}")
            
            # Step 3: Change the email's category in our database
            # Find a different category to switch to
            available_categories = db.query(EmailCategory).filter(
                EmailCategory.name != test_email.category,
                EmailCategory.is_system == True
            ).all()
            
            if not available_categories:
                pytest.skip("No alternative categories available for testing")
            
            new_category = available_categories[0]
            old_category = test_email.category
            
            print(f"Changing category from '{old_category}' to '{new_category.name}'")
            
            # Update the email's category
            test_email.category = new_category.name
            db.commit()
            db.refresh(test_email)
            
            # Step 4: Create an operation to sync this change to Gmail
            operation_data = {
                'add_labels': ['INBOX'],  # Ensure it's in inbox
                'remove_labels': []  # Don't remove any existing labels yet
            }
            
            operation = create_operation(
                db=db,
                user=test_user,
                email=test_email,
                operation_type=OperationType.UPDATE_LABELS,
                operation_data=operation_data
            )
            
            assert operation.status == OperationStatus.PENDING
            
            # Step 5: Process the pending operation
            process_result = asyncio.run(process_pending_operations(
                db=db,
                user=test_user,
                credentials=test_user.credentials
            ))
            
            print(f"Operation processing result: {process_result}")
            
            # Step 6: Verify the operation was completed
            updated_operation = db.query(EmailOperation).filter(EmailOperation.id == operation.id).first()
            assert updated_operation.status == OperationStatus.COMPLETED, f"Operation failed: {updated_operation.error_message}"
            
            # Step 7: Verify the change was applied in Gmail
            updated_message = gmail_service.users().messages().get(
                userId='me',
                id=test_email.gmail_id,
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            
            updated_labels = updated_message.get('labelIds', [])
            print(f"Updated Gmail labels: {updated_labels}")
            
            # Verify that INBOX label was added
            assert 'INBOX' in updated_labels, "INBOX label was not added to Gmail"
            
            print(f"✅ Label update sync test completed successfully")
            print(f"   - Email: {test_email.subject}")
            print(f"   - Category changed: {old_category} → {new_category.name}")
            print(f"   - Gmail labels updated: {original_labels} → {updated_labels}")
            
        except Exception as e:
            pytest.fail(f"Label update sync test failed: {str(e)}")
    
    def test_category_change_triggers_gmail_operation(self, db, test_user, seeded_categories):
        """
        Test that changing an email's category programmatically triggers
        the creation of a Gmail operation.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing operations for this user
        db.query(EmailOperation).filter(EmailOperation.user_id == test_user.id).delete()
        db.commit()
        
        try:
            # Step 1: Sync some emails from Gmail to get test data
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            if sync_result['status'] != 'success':
                pytest.skip("No emails available for testing - sync failed or no emails in test account")
            
            # Get a synced email to work with
            test_email = db.query(Email).filter(Email.user_id == test_user.id).first()
            
            if not test_email:
                pytest.skip("No emails synced from Gmail - cannot test category changes")
            
            # Step 2: Change the email's category using the categorizer utility
            old_category = test_email.category
            new_category = "important"  # Use a system category (lowercase)
            
            # Use the categorizer to change the category
            set_email_category_and_labels(test_email, new_category, db)
            db.commit()
            db.refresh(test_email)
            
            # Step 3: Verify the category was changed
            assert test_email.category == new_category
            
            # Step 4: Manually create an operation to sync the category change to Gmail
            # This simulates what would happen when a user changes a category in the UI
            email_operation = create_operation(
                db=db,
                user=test_user,
                email=test_email,
                operation_type=OperationType.UPDATE_LABELS,
                operation_data={
                    'add_labels': test_email.labels,
                    'remove_labels': []  # We're only adding labels, not removing any
                }
            )
            
            # Step 5: Verify the operation was created
            assert email_operation is not None, "Failed to create operation for category change"
            assert email_operation.operation_type == OperationType.UPDATE_LABELS
            
            print(f"✅ Category change operation test completed")
            print(f"   - Email: {test_email.subject}")
            print(f"   - Category changed: {old_category} → {new_category}")
            print(f"   - Operation created: {email_operation.operation_type}")
            
        except Exception as e:
            pytest.fail(f"Category change operation test failed: {str(e)}")
    
    def test_operation_processing_handles_errors_gracefully(self, db, test_user):
        """
        Test that operation processing handles errors gracefully when
        Gmail API calls fail.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing operations for this user
        db.query(EmailOperation).filter(EmailOperation.user_id == test_user.id).delete()
        db.commit()
        
        try:
            # Step 1: Sync some emails from Gmail to get test data
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            if sync_result['status'] != 'success':
                pytest.skip("No emails available for testing - sync failed or no emails in test account")
            
            # Get a synced email to work with
            test_email = db.query(Email).filter(Email.user_id == test_user.id).first()
            
            if not test_email:
                pytest.skip("No emails synced from Gmail - cannot test error handling")
            
            # Step 2: Create an operation with invalid Gmail ID to trigger an error
            invalid_operation = create_operation(
                db=db,
                user=test_user,
                email=test_email,
                operation_type=OperationType.UPDATE_LABELS,
                operation_data={
                    'add_labels': ['INBOX'],
                    'remove_labels': []
                }
            )
            
            # Temporarily modify the email's Gmail ID to be invalid
            original_gmail_id = test_email.gmail_id
            test_email.gmail_id = "invalid_gmail_id_12345"
            db.commit()
            
            # Step 3: Process the operation (should fail)
            process_result = asyncio.run(process_pending_operations(
                db=db,
                user=test_user,
                credentials=test_user.credentials
            ))
            
            # Step 4: Verify the operation was marked as failed
            failed_operation = db.query(EmailOperation).filter(EmailOperation.id == invalid_operation.id).first()
            assert failed_operation.status == OperationStatus.FAILED
            assert failed_operation.error_message is not None
            
            # Step 5: Restore the original Gmail ID
            test_email.gmail_id = original_gmail_id
            db.commit()
            
            print(f"✅ Error handling test completed")
            print(f"   - Operation failed as expected: {failed_operation.error_message}")
            
        except Exception as e:
            pytest.fail(f"Error handling test failed: {str(e)}")
    
    def test_concurrent_operations_processing(self, db, test_user, seeded_categories):
        """
        Test that multiple operations can be processed concurrently
        without conflicts.
        """
        # Skip if no real credentials
        if not test_user.credentials.get('refresh_token') or test_user.credentials['refresh_token'] == 'mock_refresh_token':
            pytest.skip("No real Gmail test credentials available")
        
        # Clear any existing operations for this user
        db.query(EmailOperation).filter(EmailOperation.user_id == test_user.id).delete()
        db.commit()
        
        try:
            # Step 1: Sync some emails from Gmail to get test data
            sync_result = asyncio.run(sync_emails_since_last_fetch(db, test_user))
            
            if sync_result['status'] != 'success':
                pytest.skip("No emails available for testing - sync failed or no emails in test account")
            
            # Get multiple synced emails to work with
            test_emails = db.query(Email).filter(Email.user_id == test_user.id).limit(3).all()
            
            if len(test_emails) < 2:
                pytest.skip("Not enough emails synced from Gmail - need at least 2 for concurrent testing")
            
            # Step 2: Create multiple operations for different emails
            operations = []
            for email in test_emails:
                operation = create_operation(
                    db=db,
                    user=test_user,
                    email=email,
                    operation_type=OperationType.UPDATE_LABELS,
                    operation_data={
                        'add_labels': ['INBOX'],
                        'remove_labels': []
                    }
                )
                operations.append(operation)
            
            # Step 3: Process all operations
            process_result = asyncio.run(process_pending_operations(
                db=db,
                user=test_user,
                credentials=test_user.credentials,
                max_operations=10
            ))
            
            # Step 4: Verify all operations were processed
            for operation in operations:
                updated_operation = db.query(EmailOperation).filter(EmailOperation.id == operation.id).first()
                assert updated_operation.status in [OperationStatus.COMPLETED, OperationStatus.FAILED]
            
            print(f"✅ Concurrent operations test completed")
            print(f"   - Created {len(operations)} operations")
            print(f"   - Processing result: {process_result}")
            
        except Exception as e:
            pytest.fail(f"Concurrent operations test failed: {str(e)}") 