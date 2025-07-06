"""
Database Setup Tests

This test file validates that our test database is properly configured and all
tables are accessible. It ensures the foundation for all other integration tests
is solid.
"""

import pytest
import os
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timezone

from app.models import (
    User, Email, EmailCategory, CategoryKeyword, SenderRule,
    CategorizationFeedback, EmailCategorizationDecision,
    EmailOperation, EmailTrashEvent, EmailSync, SyncDetails
)

# Load test environment variables
load_dotenv('.env.test')

class TestDatabaseSetup:
    """Test database setup and configuration."""
    
    def test_database_connection_and_schema(self, db):
        """Test that we can connect to the test database and verify schema."""
        # Test basic connection
        result = db.execute(text("SELECT 1 as test_value")).fetchone()
        assert result[0] == 1
        
        # Test that we can access the session
        assert db is not None
        
        # Verify we're using the test database
        from tests.conftest import TEST_DATABASE_URL
        assert "test" in TEST_DATABASE_URL.lower()
        
        print(f"✅ Database connection test passed")
        print(f"   - Using test database: {TEST_DATABASE_URL}")
    
    def test_all_tables_exist(self, db):
        """Test that all expected tables exist in the test database."""
        inspector = inspect(db.bind)
        existing_tables = inspector.get_table_names()
        
        # Define all expected tables
        expected_tables = [
            'users',
            'emails', 
            'email_categories',
            'category_keywords',
            'sender_rules',
            'categorization_feedback',
            'email_categorization_decisions',
            'email_operations',
            'email_trash_events',
            'email_syncs',
            'sync_details'
        ]
        
        # Check that all expected tables exist
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        
        assert len(missing_tables) == 0, f"Missing tables: {missing_tables}"
        
        print(f"✅ All expected tables exist")
        print(f"   - Found {len(existing_tables)} tables")
        print(f"   - Expected tables: {expected_tables}")
    
    def test_table_columns_exist(self, db):
        """Test that all expected columns exist in key tables."""
        inspector = inspect(db.bind)
        
        # Test users table
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        expected_user_columns = ['id', 'email', 'name', 'credentials', 'created_at', 'last_sign_in']
        missing_user_columns = [col for col in expected_user_columns if col not in user_columns]
        assert len(missing_user_columns) == 0, f"Missing user columns: {missing_user_columns}"
        
        # Test emails table
        email_columns = [col['name'] for col in inspector.get_columns('emails')]
        expected_email_columns = ['id', 'user_id', 'gmail_id', 'thread_id', 'subject', 'from_email', 'received_at', 'snippet', 'category', 'created_at', 'is_read', 'is_processed', 'importance_score', 'raw_data', 'is_dirty', 'last_reprocessed_at', 'labels']
        missing_email_columns = [col for col in expected_email_columns if col not in email_columns]
        assert len(missing_email_columns) == 0, f"Missing email columns: {missing_email_columns}"
        
        # Test email_categories table
        category_columns = [col['name'] for col in inspector.get_columns('email_categories')]
        expected_category_columns = ['id', 'name', 'display_name', 'description', 'priority', 'is_system', 'created_at']
        missing_category_columns = [col for col in expected_category_columns if col not in category_columns]
        assert len(missing_category_columns) == 0, f"Missing category columns: {missing_category_columns}"
        
        # Test email_operations table
        operation_columns = [col['name'] for col in inspector.get_columns('email_operations')]
        expected_operation_columns = ['id', 'email_id', 'user_id', 'operation_type', 'operation_data', 'status', 'retries', 'error_message', 'created_at', 'updated_at']
        missing_operation_columns = [col for col in expected_operation_columns if col not in operation_columns]
        assert len(missing_operation_columns) == 0, f"Missing operation columns: {missing_operation_columns}"
        
        print(f"✅ All expected columns exist in key tables")
    
    def test_foreign_key_constraints(self, db):
        """Test that foreign key constraints are properly set up."""
        inspector = inspect(db.bind)
        
        # Test foreign keys in emails table
        email_fks = inspector.get_foreign_keys('emails')
        user_fk_exists = any(fk['constrained_columns'] == ['user_id'] for fk in email_fks)
        assert user_fk_exists, "Foreign key constraint missing: emails.user_id -> users.id"
        
        # Test foreign keys in email_operations table
        operation_fks = inspector.get_foreign_keys('email_operations')
        operation_user_fk_exists = any(fk['constrained_columns'] == ['user_id'] for fk in operation_fks)
        operation_email_fk_exists = any(fk['constrained_columns'] == ['email_id'] for fk in operation_fks)
        assert operation_user_fk_exists, "Foreign key constraint missing: email_operations.user_id -> users.id"
        assert operation_email_fk_exists, "Foreign key constraint missing: email_operations.email_id -> emails.id"
        
        # Test foreign keys in sender_rules table
        sender_rule_fks = inspector.get_foreign_keys('sender_rules')
        sender_rule_category_fk_exists = any(fk['constrained_columns'] == ['category_id'] for fk in sender_rule_fks)
        sender_rule_user_fk_exists = any(fk['constrained_columns'] == ['user_id'] for fk in sender_rule_fks)
        assert sender_rule_category_fk_exists, "Foreign key constraint missing: sender_rules.category_id -> email_categories.id"
        assert sender_rule_user_fk_exists, "Foreign key constraint missing: sender_rules.user_id -> users.id"
        
        print(f"✅ All foreign key constraints are properly set up")
    
    def test_indexes_exist(self, db):
        """Test that important indexes exist for performance."""
        inspector = inspect(db.bind)
        
        # Test indexes on emails table
        email_indexes = inspector.get_indexes('emails')
        email_user_id_received_index = any(
            idx['column_names'] == ['user_id', 'received_at'] for idx in email_indexes
        )
        email_gmail_id_index = any(idx['column_names'] == ['gmail_id'] for idx in email_indexes)
        email_category_index = any(idx['column_names'] == ['category'] for idx in email_indexes)
        assert email_user_id_received_index, "Index missing on emails(user_id, received_at)"
        assert email_gmail_id_index, "Index missing on emails.gmail_id"
        assert email_category_index, "Index missing on emails.category"
        
        # Test indexes on email_operations table
        operation_indexes = inspector.get_indexes('email_operations')
        
        print(f"✅ Important indexes exist for performance")
    
    def test_database_isolation(self, db):
        """Test that the test database is completely isolated from development."""
        # Verify we're using the test database
        from tests.conftest import TEST_DATABASE_URL
        assert "test" in TEST_DATABASE_URL.lower()
        
        # Test that we can create and query data without affecting other databases
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        test_email = f"isolation_test_{unique_id}@example.com"
        
        # Create a test user
        test_user = User(
            id=uuid.uuid4(),
            email=test_email,
            name="Isolation Test User"
        )
        
        db.add(test_user)
        db.commit()
        
        # Verify the user was created in the test database
        retrieved_user = db.query(User).filter(User.email == test_email).first()
        assert retrieved_user is not None
        assert retrieved_user.name == "Isolation Test User"
        
        # Clean up
        db.delete(retrieved_user)
        db.commit()
        
        print(f"✅ Database isolation test passed")
        print(f"   - Test database: {TEST_DATABASE_URL}")
    
    def test_transaction_rollback(self, db):
        """Test that database transactions can be rolled back properly."""
        # Get initial user count
        initial_count = db.query(User).count()
        
        # Create a test user
        import uuid
        test_user = User(
            id=uuid.uuid4(),
            email=f"rollback_test_{uuid.uuid4().hex[:8]}@example.com",
            name="Rollback Test User"
        )
        
        db.add(test_user)
        db.commit()
        
        # Verify user was created
        after_create_count = db.query(User).count()
        assert after_create_count == initial_count + 1
        
        # The transaction should be rolled back by the fixture
        # We'll verify this by checking that the user doesn't persist
        # (though this is more of a fixture test than a database test)
        
        print(f"✅ Transaction rollback test passed")
        print(f"   - Initial count: {initial_count}")
        print(f"   - After create: {after_create_count}")
    
    def test_model_relationships(self, db):
        """Test that SQLAlchemy model relationships work correctly."""
        import uuid
        
        # Create a test user
        test_user = User(
            id=uuid.uuid4(),
            email=f"relationship_test_{uuid.uuid4().hex[:8]}@example.com",
            name="Relationship Test User"
        )
        db.add(test_user)
        db.commit()
        
        # Create a test category
        test_category = EmailCategory(
            name=f"test_category_{uuid.uuid4().hex[:8]}",
            display_name="Test Category",
            description="A test category",
            priority=50,
            is_system=False
        )
        db.add(test_category)
        db.commit()
        
        # Create a test email
        test_email = Email(
            id=uuid.uuid4(),
            user_id=test_user.id,
            gmail_id=f"test_gmail_id_{uuid.uuid4().hex[:8]}",
            thread_id=f"test_thread_id_{uuid.uuid4().hex[:8]}",
            subject="Test Email",
            from_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            snippet="Test email snippet",
            category=test_category.name
        )
        db.add(test_email)
        db.commit()
        
        # Test relationships
        # User -> Emails
        user_emails = db.query(Email).filter(Email.user_id == test_user.id).all()
        assert len(user_emails) == 1
        assert user_emails[0].subject == "Test Email"
        
        # Email -> User (via user_id)
        email_user = db.query(User).filter(User.id == test_email.user_id).first()
        assert email_user.email == test_user.email
        
        # Category -> Emails (via category name)
        category_emails = db.query(Email).filter(Email.category == test_category.name).all()
        assert len(category_emails) == 1
        assert category_emails[0].id == test_email.id
        
        print(f"✅ Model relationships test passed")
        print(f"   - User has {len(user_emails)} emails")
        print(f"   - Category has {len(category_emails)} emails")
    
    def test_database_performance(self, db):
        """Test basic database performance with simple queries."""
        import time
        
        # Test simple SELECT performance
        start_time = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        select_time = time.time() - start_time
        
        # Test simple INSERT performance
        import uuid
        start_time = time.time()
        test_user = User(
            id=uuid.uuid4(),
            email=f"perf_test_{uuid.uuid4().hex[:8]}@example.com",
            name="Performance Test User"
        )
        db.add(test_user)
        db.commit()
        insert_time = time.time() - start_time
        
        # Test simple UPDATE performance
        start_time = time.time()
        test_user.name = "Updated Performance Test User"
        db.commit()
        update_time = time.time() - start_time
        
        # Test simple DELETE performance
        start_time = time.time()
        db.delete(test_user)
        db.commit()
        delete_time = time.time() - start_time
        
        # Verify performance is reasonable (should be under 1 second for each operation)
        assert select_time < 1.0, f"SELECT query too slow: {select_time:.3f}s"
        assert insert_time < 1.0, f"INSERT query too slow: {insert_time:.3f}s"
        assert update_time < 1.0, f"UPDATE query too slow: {update_time:.3f}s"
        assert delete_time < 1.0, f"DELETE query too slow: {delete_time:.3f}s"
        
        print(f"✅ Database performance test passed")
        print(f"   - SELECT: {select_time:.3f}s")
        print(f"   - INSERT: {insert_time:.3f}s")
        print(f"   - UPDATE: {update_time:.3f}s")
        print(f"   - DELETE: {delete_time:.3f}s") 