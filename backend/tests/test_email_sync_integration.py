"""
Integration tests for email sync with attention scoring

These tests verify that attention scores are calculated and stored correctly
during the email sync process.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.email import Email
from app.services.processing_service import process_and_store_emails
from app.services.attention_scoring import calculate_attention_score


class TestEmailSyncWithAttentionScoring:
    """Test cases for email sync integration with attention scoring"""

    def test_new_emails_get_attention_scores(self, db_session: Session, test_user_with_credentials: User):
        """Test that new emails get attention scores calculated during sync"""
        # Create test email data
        test_emails = [
            {
                'gmail_id': 'test_email_1',
                'thread_id': 'thread_1',
                'subject': 'Important Meeting',
                'from_email': 'boss@company.com',
                'received_at': '2024-01-01T10:00:00Z',
                'snippet': 'Please attend the important meeting',
                'labels': ['IMPORTANT', 'INBOX'],
                'is_read': False,
                'raw_data': {}
            },
            {
                'gmail_id': 'test_email_2',
                'thread_id': 'thread_2',
                'subject': 'Newsletter',
                'from_email': 'newsletter@example.com',
                'received_at': '2024-01-01T11:00:00Z',
                'snippet': 'Weekly newsletter content',
                'labels': ['INBOX'],
                'is_read': True,
                'raw_data': {}
            }
        ]

        # Process emails through sync
        processed_emails = process_and_store_emails(db_session, test_user_with_credentials, test_emails)

        # Verify emails were processed
        assert len(processed_emails) == 2

        # Check that attention scores were calculated
        for email in processed_emails:
            assert email.attention_score is not None
            assert 0.0 <= email.attention_score <= 100.0

        # Verify specific attention scores
        important_email = next(e for e in processed_emails if e.gmail_id == 'test_email_1')
        newsletter_email = next(e for e in processed_emails if e.gmail_id == 'test_email_2')

        # Important unread email should have high attention score
        assert important_email.attention_score > 80.0  # 50 + 15 (unread) + 30 (important) = 95

        # Read newsletter should have lower attention score
        assert newsletter_email.attention_score < 60.0  # 50 (base) only

    def test_existing_emails_get_attention_scores_updated(self, db_session: Session, test_user_with_credentials: User):
        """Test that existing emails get attention scores updated during sync"""
        # Create an email first
        existing_email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id='existing_email',
            thread_id='thread_1',
            subject='Original Subject',
            from_email='test@example.com',
            labels=['INBOX'],
            is_read=True,
            attention_score=0.0  # Initial score
        )
        db_session.add(existing_email)
        db_session.commit()

        # Update email data with new labels
        updated_email_data = [
            {
                'gmail_id': 'existing_email',
                'thread_id': 'thread_1',
                'subject': 'Updated Subject',
                'from_email': 'test@example.com',
                'received_at': '2024-01-01T10:00:00Z',
                'snippet': 'Updated content',
                'labels': ['IMPORTANT', 'STARRED', 'INBOX'],  # Added important and starred
                'is_read': False,  # Changed to unread
                'raw_data': {}
            }
        ]

        # Process the update
        processed_emails = process_and_store_emails(db_session, test_user_with_credentials, updated_email_data)

        # Verify email was updated
        assert len(processed_emails) == 1
        updated_email = processed_emails[0]

        # Check that attention score was recalculated
        assert updated_email.attention_score > 0.0
        # Should be high due to IMPORTANT + STARRED + unread
        assert updated_email.attention_score > 90.0  # 50 + 15 (unread) + 30 (important) + 20 (starred) = 115, clamped to 100

    def test_label_changes_trigger_attention_score_recalculation(self, db_session: Session, test_user_with_credentials: User):
        """Test that label changes trigger attention score recalculation"""
        from app.services.processing_service import process_label_changes

        # Create an email with initial labels
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id='label_test_email',
            thread_id='thread_1',
            subject='Test Email',
            from_email='test@example.com',
            labels=['INBOX'],
            is_read=False,
            attention_score=65.0  # 50 + 15 (unread)
        )
        db_session.add(email)
        db_session.commit()

        # Simulate label changes (adding IMPORTANT label)
        label_changes = {
            'label_test_email': {
                'added': ['IMPORTANT'],
                'removed': []
            }
        }

        # Process label changes
        updated_count = process_label_changes(db_session, test_user_with_credentials, label_changes)

        # Verify email was updated
        assert updated_count == 1

        # Refresh email from database
        db_session.refresh(email)

        # Check that attention score was recalculated
        expected_score = 95.0  # 50 + 15 (unread) + 30 (important)
        assert email.attention_score == expected_score

    def test_attention_scores_are_persistent(self, db_session: Session, test_user_with_credentials: User):
        """Test that attention scores are properly persisted to database"""
        # Create test email data
        test_emails = [
            {
                'gmail_id': 'persistent_test_email',
                'thread_id': 'thread_1',
                'subject': 'Test Email',
                'from_email': 'test@example.com',
                'received_at': '2024-01-01T10:00:00Z',
                'snippet': 'Test content',
                'labels': ['STARRED', 'INBOX'],
                'is_read': False,
                'raw_data': {}
            }
        ]

        # Process emails
        processed_emails = process_and_store_emails(db_session, test_user_with_credentials, test_emails)

        # Verify email was processed
        assert len(processed_emails) == 1
        email = processed_emails[0]

        # Check attention score was calculated
        assert email.attention_score > 0.0

        # Query email from database to verify persistence
        db_session.commit()  # Ensure changes are committed
        persisted_email = db_session.query(Email).filter(
            Email.gmail_id == 'persistent_test_email'
        ).first()

        assert persisted_email is not None
        assert persisted_email.attention_score == email.attention_score

    def test_attention_score_calculation_consistency(self, db_session: Session, test_user_with_credentials: User):
        """Test that attention score calculation is consistent between sync and direct calculation"""
        # Create test email data
        test_emails = [
            {
                'gmail_id': 'consistency_test_email',
                'thread_id': 'thread_1',
                'subject': 'Consistency Test',
                'from_email': 'test@example.com',
                'received_at': '2024-01-01T10:00:00Z',
                'snippet': 'Test content',
                'labels': ['IMPORTANT', 'STARRED', 'INBOX'],
                'is_read': False,
                'raw_data': {}
            }
        ]

        # Process emails through sync
        processed_emails = process_and_store_emails(db_session, test_user_with_credentials, test_emails)

        # Get the processed email
        email = processed_emails[0]

        # Calculate attention score directly
        direct_score = calculate_attention_score(email)

        # Verify scores match
        assert email.attention_score == direct_score

    def test_multiple_emails_with_different_attention_factors(self, db_session: Session, test_user_with_credentials: User):
        """Test attention scoring with various combinations of factors"""
        test_emails = [
            # Unread + Important + Starred
            {
                'gmail_id': 'email_1',
                'thread_id': 'thread_1',
                'subject': 'Critical Email',
                'from_email': 'critical@example.com',
                'labels': ['IMPORTANT', 'STARRED', 'INBOX'],
                'is_read': False,
                'raw_data': {}
            },
            # Read + Important
            {
                'gmail_id': 'email_2',
                'thread_id': 'thread_2',
                'subject': 'Important but Read',
                'from_email': 'important@example.com',
                'labels': ['IMPORTANT', 'INBOX'],
                'is_read': True,
                'raw_data': {}
            },
            # Unread + Starred
            {
                'gmail_id': 'email_3',
                'thread_id': 'thread_3',
                'subject': 'Starred Unread',
                'from_email': 'starred@example.com',
                'labels': ['STARRED', 'INBOX'],
                'is_read': False,
                'raw_data': {}
            },
            # Read + no special labels
            {
                'gmail_id': 'email_4',
                'thread_id': 'thread_4',
                'subject': 'Regular Email',
                'from_email': 'regular@example.com',
                'labels': ['INBOX'],
                'is_read': True,
                'raw_data': {}
            }
        ]

        # Process emails
        processed_emails = process_and_store_emails(db_session, test_user_with_credentials, test_emails)

        # Verify all emails have attention scores
        assert len(processed_emails) == 4
        for email in processed_emails:
            assert email.attention_score is not None
            assert 0.0 <= email.attention_score <= 100.0

        # Verify attention score hierarchy (higher scores for more urgent emails)
        email_scores = {email.gmail_id: email.attention_score for email in processed_emails}
        
        # Critical email should have highest score
        assert email_scores['email_1'] > email_scores['email_2']  # Unread + Important + Starred > Read + Important
        assert email_scores['email_1'] > email_scores['email_3']  # Unread + Important + Starred > Unread + Starred
        assert email_scores['email_1'] > email_scores['email_4']  # Critical > Regular

        # Important read email should be higher than regular email
        assert email_scores['email_2'] > email_scores['email_4']  # Read + Important > Regular

        # Unread starred should be higher than regular
        assert email_scores['email_3'] > email_scores['email_4']  # Unread + Starred > Regular 