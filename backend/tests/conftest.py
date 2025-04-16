import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
from app.models.user import User
import os
import logging
from app.services.category_service import (
    initialize_system_categories,
    populate_system_keywords,
    populate_system_sender_rules,
)

logger = logging.getLogger(__name__)

# Use test database URL from environment
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/email_agent_test_db"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database tables once for test session"""
    try:
        Base.metadata.create_all(bind=engine)
        yield
    finally:
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def db():
    """Provide test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db):
    """Create test client with real test database"""
    from app.main import app  # Import here to ensure app is fully configured
    
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def test_user(db):
    """Create a real test user in the database"""
    user = User(
        email="test@example.com",
        name="Test User",
        credentials={
            "token": "valid_test_token",
            "refresh_token": "valid_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET")
        }
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="session", autouse=True)
def seed_system_rules(db):
    """Seed system categories, keywords, and sender rules for all tests."""
    logger.info("Seeding system categories, keywords, and sender rules for tests...")
    initialize_system_categories(db)
    populate_system_keywords(db)
    populate_system_sender_rules(db)
    logger.info("System rules seeded.")
