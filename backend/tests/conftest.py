import pytest
import os
import asyncio
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database, drop_database
import subprocess
from unittest.mock import patch

# Import all models to ensure they're registered
from app.models import (
    User, Email, EmailCategory, CategoryKeyword, SenderRule,
    CategorizationFeedback, EmailCategorizationDecision,
    EmailOperation, EmailTrashEvent, EmailSync, SyncDetails
)

# Load test environment variables
load_dotenv(dotenv_path='.env.test')

# Get the test database URL from environment variables
TEST_DATABASE_URL = os.environ.get("DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env.test. Make sure it points to email_agent_test_db.")

print(f"Using test database: {TEST_DATABASE_URL}")

# Create a test engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create a test session local
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def generate_test_credentials(email=None, password=None):
    """
    Generate test credentials using intelligent strategy selection.
    
    Priority order:
    1. Environment tokens (real API access)
    2. Service account (enterprise)
    3. Mock credentials (fallback)
    """
    # Strategy 1: Environment tokens (real API access)
    if os.getenv('GOOGLE_REFRESH_TOKEN'):
        return {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
            'token': os.getenv('GOOGLE_ACCESS_TOKEN', ''),  # Always provide token key
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
    
    # Strategy 2: Service account (enterprise)
    if os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'):
        return generate_service_account_credentials()
    
    # Strategy 3: Mock credentials (fallback)
    return generate_mock_credentials()

def generate_service_account_credentials():
    """Generate credentials using Google Service Account."""
    service_account_key_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    test_email = os.getenv('TEST_GMAIL_EMAIL', 'test@example.com')
    
    if not service_account_key_path or not os.path.exists(service_account_key_path):
        return generate_mock_credentials()
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_key_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly',
                   'https://www.googleapis.com/auth/gmail.modify']
        )
        
        # Create delegated credentials for the test user
        delegated_credentials = credentials.with_subject(test_email)
        
        return {
            'client_id': delegated_credentials.client_id,
            'client_secret': delegated_credentials.client_secret,
            'refresh_token': delegated_credentials.refresh_token,
            'token': delegated_credentials.token,
            'token_uri': delegated_credentials.token_uri,
        }
    except Exception as e:
        print(f"Service account credential generation failed: {e}")
        return generate_mock_credentials()

def generate_mock_credentials():
    """Generate mock credentials for unit tests."""
    return {
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'refresh_token': 'mock_refresh_token',
        'token': 'mock_access_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
    }

def run_alembic_migrations():
    """Run Alembic migrations on the test database"""
    try:
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Override the database URL for testing
        alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
        
        print(f"Running migrations with URL: {alembic_cfg.get_main_option('sqlalchemy.url')}")
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise

@pytest.fixture(scope="session")
def setup_test_db():
    """
    Session-scoped fixture to set up the test database once.
    Uses Alembic migrations to ensure schema consistency.
    """
    print(f"\n--- Setting up test database: {TEST_DATABASE_URL} ---")
    
    # Drop and recreate the test database
    url = make_url(TEST_DATABASE_URL)
    if database_exists(url):
        drop_database(url)
    create_database(url)
    
    # Run Alembic migrations to create schema
    try:
        run_alembic_migrations()
        print("--- Alembic migrations applied successfully ---")
    except Exception as e:
        print(f"--- Error running migrations: {e} ---")
        raise
    
    # Verify tables were created
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        print(f"--- Created tables: {tables} ---")
    
    yield  # This is where the tests run
    
    # Drop the test database after the session
    drop_database(url)

@pytest.fixture(scope="session")
def test_db(setup_test_db):
    # Create a new session
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def db(test_db):
    # Provide a clean session for each test function
    yield test_db
    test_db.rollback()

@pytest.fixture(scope="function")
def seeded_categories(db):
    """
    Seed the database with required system categories for testing.
    This ensures all tests have access to the expected categories.
    """
    from app.services.category_service import initialize_system_categories, populate_system_keywords, populate_system_sender_rules
    
    # Initialize system categories
    categories = initialize_system_categories(db)
    
    # Populate with default keywords and sender rules
    populate_system_keywords(db)
    populate_system_sender_rules(db)
    
    print(f"Seeded {len(categories)} system categories")
    return categories

@pytest.fixture(scope="function")
def clean_test_users(db):
    """
    Clean up test users before each test to ensure isolation.
    This fixture runs before each test function.
    """
    # Delete all users with test emails (either TEST_GMAIL_EMAIL or random test emails)
    test_email = os.getenv('TEST_GMAIL_EMAIL')
    
    if test_email:
        # Delete emails first to avoid foreign key constraint violation
        from app.models.email import Email
        from app.models.email_sync import EmailSync
        from app.models.email_operation import EmailOperation
        from app.models.email_trash_event import EmailTrashEvent
        from app.models.email_categorization_decision import EmailCategorizationDecision
        from app.models.categorization_feedback import CategorizationFeedback
        
        # Find the user first
        user = db.query(User).filter(User.email == test_email).first()
        if user:
            # Delete related data first
            db.query(Email).filter(Email.user_id == user.id).delete()
            db.query(EmailSync).filter(EmailSync.user_id == user.id).delete()
            db.query(EmailOperation).filter(EmailOperation.user_id == user.id).delete()
            db.query(EmailTrashEvent).filter(EmailTrashEvent.user_id == user.id).delete()
            db.query(CategorizationFeedback).filter(CategorizationFeedback.user_id == user.id).delete()
            
            # Now delete the user
            db.query(User).filter(User.email == test_email).delete()
            print(f"Cleaned up test user: {test_email}")
    
    # Also clean up any users with random test emails (pattern: test-*@example.com)
    random_users = db.query(User).filter(User.email.like('test-%@example.com')).all()
    for user in random_users:
        # Delete related data first
        db.query(Email).filter(Email.user_id == user.id).delete()
        db.query(EmailSync).filter(EmailSync.user_id == user.id).delete()
        db.query(EmailOperation).filter(EmailOperation.user_id == user.id).delete()
        db.query(EmailTrashEvent).filter(EmailTrashEvent.user_id == user.id).delete()
        db.query(CategorizationFeedback).filter(CategorizationFeedback.user_id == user.id).delete()
        
        # Now delete the user
        db.query(User).filter(User.id == user.id).delete()
    
    db.commit()
    yield
    # No cleanup needed after test since we're using function scope

@pytest.fixture
def test_user_with_credentials(db, clean_test_users):
    """
    Create a test user with automatically generated credentials.
    Uses the best available credential strategy.
    
    If TEST_GMAIL_EMAIL is set, will try to reuse existing user with that email.
    Otherwise, creates a unique user with a random email.
    """
    credentials = generate_test_credentials()
    
    # Use TEST_GMAIL_EMAIL from .env.test if available
    test_email = os.getenv('TEST_GMAIL_EMAIL')
    
    if test_email:
        # Try to find existing user with this email
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            # Update credentials for existing user
            existing_user.credentials = credentials
            db.commit()
            db.refresh(existing_user)
            print(f"Reusing existing test user: {existing_user.email}")
            return existing_user
        else:
            # Create new user with TEST_GMAIL_EMAIL
            user = User(
                id=uuid.uuid4(),
                email=test_email,
                credentials=credentials
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created new test user with TEST_GMAIL_EMAIL: {user.email}")
            return user
    else:
        # Create unique user with random email
        unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
        user = User(
            id=uuid.uuid4(),
            email=unique_email,
            credentials=credentials
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created new test user with unique email: {user.email}")
        return user

# Removed deprecated event_loop fixture - pytest-asyncio will handle this automatically
