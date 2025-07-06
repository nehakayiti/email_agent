"""
Simple test to validate the test environment works.
"""

import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(dotenv_path='backend/.env.test')

# Get the test database URL
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/email_agent_test_db"

def test_simple_database_connection():
    """Test that we can connect to the test database and create tables manually."""
    # Create engine
    engine = create_engine(TEST_DATABASE_URL)
    
    # Test basic connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test_value"))
        assert result.fetchone()[0] == 1
    
    # Create a simple test table
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_users (
                id UUID PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        conn.commit()
    
    # Test inserting and querying data
    with engine.connect() as conn:
        test_id = uuid.uuid4()
        conn.execute(text("""
            INSERT INTO test_users (id, email, name) 
            VALUES (:id, :email, :name)
        """), {"id": test_id, "email": "test@example.com", "name": "Test User"})
        conn.commit()
        
        result = conn.execute(text("SELECT * FROM test_users WHERE email = :email"), 
                            {"email": "test@example.com"})
        user = result.fetchone()
        assert user is not None
        assert user[1] == "test@example.com"
        assert user[2] == "Test User"
    
    # Clean up
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS test_users"))
        conn.commit() 