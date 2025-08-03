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
        credentials = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
            'token': os.getenv('GOOGLE_ACCESS_TOKEN', ''),  # Always provide token key
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
        
        # Test credentials validity
        if not _test_credentials_validity(credentials):
            print_credential_refresh_instructions()
            return generate_mock_credentials()
        
        return credentials
    
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

def _test_credentials_validity(credentials):
    """Test if credentials are valid by attempting to refresh the token."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        
        # Create credentials object
        creds = Credentials(
            token=credentials.get('token'),
            refresh_token=credentials.get('refresh_token'),
            token_uri=credentials.get('token_uri'),
            client_id=credentials.get('client_id'),
            client_secret=credentials.get('client_secret')
        )
        
        # Try to refresh the token
        creds.refresh(Request())
        return True
        
    except Exception as e:
        error_str = str(e).lower()
        if 'invalid_grant' in error_str:
            print(f"\n❌ CREDENTIAL ERROR: Refresh token has expired or been revoked")
            return False
        elif 'client_id' in error_str or 'client_secret' in error_str:
            print(f"\n❌ CREDENTIAL ERROR: Invalid client credentials")
            return False
        else:
            print(f"\n❌ CREDENTIAL ERROR: {e}")
            return False

def print_credential_refresh_instructions():
    """Print clear instructions for refreshing Gmail test credentials."""
    client_id = os.getenv('GOOGLE_CLIENT_ID', 'YOUR_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET', 'YOUR_CLIENT_SECRET')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/auth/callback')
    
    print("\n" + "="*80)
    print("🔑 GMAIL TEST CREDENTIALS NEED REFRESH")
    print("="*80)
    print()
    print("Your Gmail API refresh token has expired. To fix this:")
    print()
    print("1️⃣  Get authorization URL - visit in browser:")
    print(f"   https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/gmail.modify&access_type=offline&prompt=consent")
    print()
    print("2️⃣  Sign in with:")
    print(f"   📧 Email: {os.getenv('TEST_GMAIL_EMAIL', 'emailagenttester@gmail.com')}")
    print()
    print("3️⃣  Copy authorization code from redirect URL (ignore connection error)")
    print()
    print("4️⃣  Exchange code for token:")
    print('   curl -X POST https://oauth2.googleapis.com/token \\')
    print('     -H "Content-Type: application/x-www-form-urlencoded" \\')
    print(f'     -d "client_id={client_id}" \\')
    print(f'     -d "client_secret={client_secret}" \\')
    print('     -d "code=YOUR_AUTHORIZATION_CODE" \\')
    print('     -d "grant_type=authorization_code" \\')
    print(f'     -d "redirect_uri={redirect_uri}"')
    print()
    print("5️⃣  Update GOOGLE_REFRESH_TOKEN in .env.test with refresh_token from response")
    print()
    print("6️⃣  Re-run your tests:")
    print("   pytest tests/test_gmail_integration.py -v")
    print("   make refresh-gmail-credentials  # (if available)")
    print()
    print("💡 Refresh tokens expire after 7 days of inactivity or if revoked")
    print("="*80)
    print()

def _should_validate_gmail_credentials():
    """Check if we should validate Gmail credentials based on test selection."""
    import sys
    
    # Check command line arguments for Gmail-related tests
    args = ' '.join(sys.argv)
    gmail_indicators = [
        'gmail',
        'test_gmail_integration.py',
        'test_integration_two_way_sync.py',
        'TestGmailAPIIntegration',
        'TestEmailSyncIntegration',
        'TestTwoWaySyncIntegration'
    ]
    
    return any(indicator in args for indicator in gmail_indicators)

@pytest.fixture(scope="session", autouse=True)
def validate_gmail_credentials_early():
    """
    Session-scoped fixture that validates Gmail credentials before any tests run.
    If credentials are invalid, it will cause pytest to exit immediately with clear instructions.
    """
    # Only validate if we're running Gmail integration tests
    if not _should_validate_gmail_credentials():
        return  # Skip validation for non-Gmail tests
    
    print("\n🔍 Validating Gmail credentials before running tests...")
    
    # Check if we have environment credentials
    if not os.getenv('GOOGLE_REFRESH_TOKEN'):
        print("⚠️  No Gmail credentials found - tests will use mock credentials")
        return
    
    # Test credential validity
    credentials = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'refresh_token': os.getenv('GOOGLE_REFRESH_TOKEN'),
        'token': os.getenv('GOOGLE_ACCESS_TOKEN', ''),
        'token_uri': 'https://oauth2.googleapis.com/token',
    }
    
    if not _test_credentials_validity(credentials):
        print_credential_refresh_instructions()
        print("❌ TESTS ABORTED: Fix credentials first, then re-run tests")
        print("="*80)
        pytest.exit("Gmail credentials are invalid. Please refresh them and try again.", returncode=1)

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
    
    # Create the database if it doesn't exist
    url = make_url(TEST_DATABASE_URL)
    if not database_exists(url):
        create_database(url)
        print("--- Test database created ---")
    
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
    
    # Optional: Drop the test database after the session
    # drop_database(url)

@pytest.fixture(scope="function")
def db_session(setup_test_db):
    """
    Provides a fresh database session for each test function.
    This ensures complete isolation between tests.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def db(db_session):
    """
    Provides a transactional scope for each test function.
    This is now an alias for db_session since we're using function-scoped sessions.
    """
    yield db_session

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
    Clean up test data before each test to ensure isolation.
    Delete related records in the correct order to avoid foreign key violations.
    """
    # Import all models that might have foreign key relationships
    from app.models.email import Email
    from app.models.email_operation import EmailOperation
    from app.models.proposed_action import ProposedAction
    from app.models.categorization_feedback import CategorizationFeedback
    from app.models.email_categorization_decision import EmailCategorizationDecision
    from app.models.email_trash_event import EmailTrashEvent
    from app.models.email_sync import EmailSync
    from app.models.sync_details import SyncDetails
    
    # Get test user IDs first
    test_user_ids = [user.id for user in db.query(User).filter(User.email.like("test_%")).all()]
    test_user_ids.extend([user.id for user in db.query(User).filter(User.email.like("test-%")).all()])
    
    if not test_user_ids:
        # No test users to clean up
        yield
        return
    
    # Delete child records first (in dependency order)
    # 1. Delete operations and proposed actions
    db.query(EmailOperation).filter(EmailOperation.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(ProposedAction).filter(ProposedAction.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 2. Delete categorization feedback (has user_id)
    db.query(CategorizationFeedback).filter(CategorizationFeedback.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 3. Delete trash events (has user_id)
    db.query(EmailTrashEvent).filter(EmailTrashEvent.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 4. Delete sync details (has user_id)
    db.query(SyncDetails).filter(SyncDetails.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 5. Delete email syncs (has user_id)
    db.query(EmailSync).filter(EmailSync.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 6. Delete categorization decisions (no user_id, but has email_id - will be handled by cascade or email deletion)
    # Get test user email IDs first
    test_email_ids = [email.id for email in db.query(Email).filter(Email.user_id.in_(test_user_ids)).all()]
    if test_email_ids:
        db.query(EmailCategorizationDecision).filter(EmailCategorizationDecision.email_id.in_(test_email_ids)).delete(synchronize_session=False)
    
    # 7. Delete emails (main child table)
    db.query(Email).filter(Email.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 8. Now delete users (parent table)
    db.query(User).filter(User.id.in_(test_user_ids)).delete(synchronize_session=False)
    
    # 9. Delete test categories
    db.query(EmailCategory).filter(EmailCategory.name.like("test_%")).delete(synchronize_session=False)
    
    db.commit()
    yield

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
