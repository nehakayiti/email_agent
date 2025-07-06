"""
Basic Test Setup Validation

This test validates that the test environment is working correctly:
1. Database connection and schema
2. Basic model operations
3. Test data seeding
"""

import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import User, Email, EmailCategory, CategoryKeyword, SenderRule

def test_database_connection(db):
    """Test that we can connect to the test database and perform basic operations."""
    # Test basic query
    result = db.execute(text("SELECT 1 as test_value")).fetchone()
    assert result[0] == 1
    
    # Test that we can access the session
    assert db is not None

def test_user_creation(db):
    """Test creating users in the test database."""
    # Create a test user with unique email
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"test-{unique_id}@example.com"
    
    test_user = User(
        id=uuid.uuid4(),
        email=test_email,
        name="Test User"
    )
    
    db.add(test_user)
    db.commit()
    
    # Verify the user was created
    retrieved_user = db.query(User).filter_by(email=test_email).first()
    assert retrieved_user is not None
    assert retrieved_user.name == "Test User"
    assert retrieved_user.email == test_email

def test_email_category_creation(db):
    """Test creating email categories in the test database."""
    # Create a test category with unique name
    unique_id = uuid.uuid4().hex[:8]
    category_name = f"test_category_{unique_id}"
    
    test_category = EmailCategory(
        name=category_name,
        display_name="Test Category",
        description="A test category for testing",
        priority=50,
        is_system=False
    )
    
    db.add(test_category)
    db.commit()
    
    # Verify the category was created
    retrieved_category = db.query(EmailCategory).filter_by(name=category_name).first()
    assert retrieved_category is not None
    assert retrieved_category.display_name == "Test Category"
    assert retrieved_category.priority == 50

def test_email_creation_with_category(db):
    """Test creating an email with a category in the test database."""
    # Create a test user with unique email
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"test_email_category_{unique_id}@example.com"
    
    test_user = User(
        id=uuid.uuid4(),
        email=test_email,
        name="Test User"
    )
    db.add(test_user)
    db.commit()
    
    # Create a test category with unique name
    category_name = f"test_category_email_{unique_id}"
    test_category = EmailCategory(
        name=category_name,
        display_name="Test Category Email",
        description="A test category for testing email creation",
        priority=50,
        is_system=False
    )
    db.add(test_category)
    db.commit()
    
    # Create a test email with unique gmail_id
    gmail_id = f"test_gmail_id_{unique_id}"
    test_email_obj = Email(
        id=uuid.uuid4(),
        user_id=test_user.id,
        gmail_id=gmail_id,
        thread_id="test_thread_id",
        subject="Test Email Subject",
        from_email="sender@example.com",
        received_at=datetime.now(timezone.utc),
        snippet="This is a test email snippet",
        category=category_name
    )
    
    db.add(test_email_obj)
    db.commit()
    
    # Verify the email was created
    retrieved_email = db.query(Email).filter_by(gmail_id=gmail_id).first()
    assert retrieved_email is not None
    assert retrieved_email.subject == "Test Email Subject"
    assert retrieved_email.category == category_name
    assert retrieved_email.user_id == test_user.id

def test_sender_rule_creation(db):
    """Test creating sender rules in the test database."""
    # Create a test user with unique email
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"test_sender_rule_{unique_id}@example.com"
    
    test_user = User(
        id=uuid.uuid4(),
        email=test_email,
        name="Test User"
    )
    db.add(test_user)
    db.commit()
    
    # Create a test category with unique name
    category_name = f"test_category_sender_rule_{unique_id}"
    test_category = EmailCategory(
        name=category_name,
        display_name="Test Category Sender Rule",
        description="A test category for testing sender rules",
        priority=50,
        is_system=False
    )
    db.add(test_category)
    db.commit()
    
    # Create a test sender rule with unique pattern
    pattern = f"example_{unique_id}.com"
    test_rule = SenderRule(
        category_id=test_category.id,
        pattern=pattern,
        is_domain=True,
        weight=1,
        user_id=test_user.id
    )
    
    db.add(test_rule)
    db.commit()
    
    # Verify the rule was created
    retrieved_rule = db.query(SenderRule).filter_by(pattern=pattern).first()
    assert retrieved_rule is not None
    assert retrieved_rule.is_domain is True
    assert retrieved_rule.weight == 1
    assert retrieved_rule.category_id == test_category.id

def test_database_isolation(db):
    """Test that the test database is isolated from the development database."""
    # This test ensures we're using the test database
    # by checking the database URL contains 'test'
    from tests.conftest import TEST_DATABASE_URL
    assert "test" in TEST_DATABASE_URL.lower()
    
    # Verify we can create and query data with unique email
    unique_id = uuid.uuid4().hex[:8]
    test_email = f"isolation_test_{unique_id}@example.com"
    
    test_user = User(
        id=uuid.uuid4(),
        email=test_email,
        name="Isolation Test User"
    )
    
    db.add(test_user)
    db.commit()
    
    # Verify the user was created in the test database
    retrieved_user = db.query(User).filter_by(email=test_email).first()
    assert retrieved_user is not None
    assert retrieved_user.name == "Isolation Test User" 