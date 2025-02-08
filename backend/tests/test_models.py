import pytest
from app.models.user import User
from sqlalchemy.exc import IntegrityError

def test_create_user(db):
    """Test creating a user"""
    user = User(
        email="test@example.com",
        name="Test User",
        credentials={
            "token": "test_token",
            "refresh_token": "test_refresh_token"
        }
    )
    db.add(user)
    db.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.created_at is not None

def test_unique_email_constraint(db, test_user):
    """Test that emails must be unique"""
    duplicate_user = User(
        email="test@example.com",  # Same email as test_user
        name="Another User"
    )
    db.add(duplicate_user)
    
    with pytest.raises(IntegrityError):
        db.commit()

def test_user_credentials_json(db):
    """Test JSON credentials field"""
    credentials = {
        "token": "test_token",
        "refresh_token": "test_refresh_token",
        "extra_field": {
            "nested": "value"
        }
    }
    
    user = User(
        email="test@example.com",
        name="Test User",
        credentials=credentials
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.credentials == credentials
    assert user.credentials["extra_field"]["nested"] == "value" 