import pytest
import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database, drop_database
import subprocess

# Import all models to ensure they're registered
from app.models import (
    User, Email, EmailCategory, CategoryKeyword, SenderRule,
    CategorizationFeedback, EmailCategorizationDecision,
    EmailOperation, EmailTrashEvent, EmailSync, SyncDetails
)

# Load test environment variables
load_dotenv(dotenv_path='backend/.env.test')

# Get the test database URL from environment variables
TEST_DATABASE_URL = os.environ.get("DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env.test. Make sure it points to email_agent_test_db.")

print(f"Using test database: {TEST_DATABASE_URL}")

# Create a test engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create a test session local
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

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

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
