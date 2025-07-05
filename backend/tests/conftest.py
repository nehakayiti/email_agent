import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Import Base from your models
from backend.app.models.user import Base  # Assuming User model defines Base

# Explicitly load environment variables from .env.test
load_dotenv(dotenv_path='backend/.env.test')

# Get the test database URL from environment variables
TEST_DATABASE_URL = os.environ.get("DATABASE_URL")

if not TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL not found in environment variables. Make sure .env.test is configured correctly.")

# Create a test engine
test_engine = create_engine(TEST_DATABASE_URL)

# Create a test session local
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session")
def setup_test_db():
    """
    Fixture to set up and tear down the test database.
    Ensures a clean database state for each test session by dropping and recreating tables.
    """
    print(f"\n--- Setting up test database: {TEST_DATABASE_URL} ---")
    
    # Drop all tables to ensure a clean slate
    # This is a destructive operation, ensure TEST_DATABASE_URL is correct
    try:
        Base.metadata.drop_all(test_engine)
        print("--- All existing tables dropped ---")
    except Exception as e:
        print(f"--- Error dropping tables (might be first run or tables don't exist): {e} ---")

    # Create all tables
    print("--- Creating all tables in test database ---")
    Base.metadata.create_all(test_engine)
    print("--- All tables created ---")

    yield  # This is where the tests run

    # Teardown: Drop all tables after the session tests are complete
    print("--- Tearing down test database ---")
    Base.metadata.drop_all(test_engine)
    print("--- Test database teardown complete ---")

@pytest.fixture(scope="function")
def db_session(setup_test_db):
    """
    Fixture to provide a database session for each test function.
    Rolls back transactions after each test to ensure isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
