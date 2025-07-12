import pytest
from sqlalchemy.orm import Session
from app.models.email import Email
from app.models.user import User
import uuid


class TestEmailModel:
    """Test cases for Email model with attention_score field"""

    def test_email_creation_with_attention_score(self, db_session: Session, test_user_with_credentials: User):
        """Test that emails can be created with attention_score field"""
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id="test_gmail_id_123",
            thread_id="test_thread_id_123",
            subject="Test Email",
            from_email="test@example.com",
            attention_score=75.5
        )
        
        db_session.add(email)
        db_session.commit()
        db_session.refresh(email)
        
        assert email.attention_score == 75.5
        assert email.id is not None

    def test_email_creation_with_default_attention_score(self, db_session: Session, test_user_with_credentials: User):
        """Test that emails get default attention_score of 0.0 when not specified"""
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id="test_gmail_id_456",
            thread_id="test_thread_id_456",
            subject="Test Email Default",
            from_email="test@example.com"
        )
        
        db_session.add(email)
        db_session.commit()
        db_session.refresh(email)
        
        assert email.attention_score == 0.0

    def test_attention_score_can_be_updated(self, db_session: Session, test_user_with_credentials: User):
        """Test that attention_score can be updated after creation"""
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id="test_gmail_id_789",
            thread_id="test_thread_id_789",
            subject="Test Email Update",
            from_email="test@example.com",
            attention_score=25.0
        )
        
        db_session.add(email)
        db_session.commit()
        db_session.refresh(email)
        
        # Update attention score
        email.attention_score = 85.5
        db_session.commit()
        db_session.refresh(email)
        
        assert email.attention_score == 85.5

    def test_attention_score_float_values(self, db_session: Session, test_user_with_credentials: User):
        """Test that attention_score accepts various float values"""
        test_values = [0.0, 25.5, 50.0, 75.25, 100.0]
        
        for i, score in enumerate(test_values):
            email = Email(
                user_id=test_user_with_credentials.id,
                gmail_id=f"test_gmail_id_{i}",
                thread_id=f"test_thread_id_{i}",
                subject=f"Test Email {i}",
                from_email="test@example.com",
                attention_score=score
            )
            
            db_session.add(email)
            db_session.commit()
            db_session.refresh(email)
            
            assert email.attention_score == score

    def test_attention_score_query(self, db_session: Session, test_user_with_credentials: User):
        """Test that emails can be queried by attention_score"""
        # Create emails with different attention scores
        emails_data = [
            ("email1", 10.0),
            ("email2", 50.0),
            ("email3", 90.0),
            ("email4", 30.0),
            ("email5", 70.0)
        ]
        
        for gmail_id, score in emails_data:
            email = Email(
                user_id=test_user_with_credentials.id,
                gmail_id=gmail_id,
                thread_id=f"thread_{gmail_id}",
                subject=f"Test {gmail_id}",
                from_email="test@example.com",
                attention_score=score
            )
            db_session.add(email)
        
        db_session.commit()
        
        # Query emails with attention_score > 50
        high_attention_emails = db_session.query(Email).filter(
            Email.attention_score > 50.0
        ).all()
        
        assert len(high_attention_emails) == 2
        assert all(email.attention_score > 50.0 for email in high_attention_emails)

    def test_existing_email_fields_still_work(self, db_session: Session, test_user_with_credentials: User):
        """Test that existing email fields continue to work with attention_score"""
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id="test_gmail_id_existing",
            thread_id="test_thread_id_existing",
            subject="Test Existing Fields",
            from_email="test@example.com",
            is_read=False,
            importance_score=75,
            category="primary",
            attention_score=65.5
        )
        
        db_session.add(email)
        db_session.commit()
        db_session.refresh(email)
        
        # Verify all fields work correctly
        assert email.user_id == test_user_with_credentials.id
        assert email.gmail_id == "test_gmail_id_existing"
        assert email.subject == "Test Existing Fields"
        assert email.is_read == False
        assert email.importance_score == 75
        assert email.category == "primary"
        assert email.attention_score == 65.5 