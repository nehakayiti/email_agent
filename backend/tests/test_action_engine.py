"""
Tests for Action Engine Services

This module tests the core Action Engine functionality including:
- Action detection and proposal generation
- Dry run vs execute modes
- Proposal approval/rejection workflow
- Action rule management and validation
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.email import Email
from app.models.user import User
from app.models.email_category import EmailCategory
from app.models.proposed_action import ProposedAction, ProposedActionStatus
from app.models.email_operation import EmailOperation, OperationStatus
from app.services.action_engine_service import (
    process_category_actions,
    find_emails_for_action,
    create_proposed_action,
    execute_action,
    approve_proposed_action,
    reject_proposed_action,
    cleanup_expired_proposals,
    get_proposed_actions_for_user
)
from app.services.action_rule_service import (
    update_category_action_rule,
    get_action_rules_for_user,
    validate_action_rule,
    get_emails_affected_by_rule,
    get_action_rule_stats,
    disable_action_rule,
    get_action_rule_history
)

import uuid

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        email=f"test_{unique_id}@example.com",
        name=f"Test User {unique_id}",
        credentials={}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_category(db: Session) -> EmailCategory:
    """Create a test category"""
    unique_id = str(uuid.uuid4())[:8]
    category = EmailCategory(
        name=f"test_category_action_engine_{unique_id}",
        display_name=f"Test Category Action Engine {unique_id}",
        description="Test category for action engine",
        priority=50,
        is_system=True
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture
def test_emails(db: Session, test_user: User, test_category: EmailCategory) -> list[Email]:
    """Create test emails with different ages"""
    emails = []
    
    # Create emails with different ages
    ages = [5, 15, 30, 60, 90]  # days old
    
    for i, age in enumerate(ages):
        email = Email(
            gmail_id=f"test_email_{i}",
            thread_id=f"test_thread_{i}",
            user_id=test_user.id,
            category=test_category.name,
            subject=f"Test Email {i}",
            from_email=f"sender{i}@example.com",
            received_at=datetime.now(timezone.utc) - timedelta(days=age),
            labels=["INBOX"]
        )
        emails.append(email)
    
    db.add_all(emails)
    db.commit()
    
    for email in emails:
        db.refresh(email)
    
    return emails

class TestActionRuleService:
    """Test Action Rule Service functionality"""
    
    def test_validate_action_rule_valid(self):
        """Test valid action rule validation"""
        assert validate_action_rule("ARCHIVE", 7) == True
        assert validate_action_rule("TRASH", 30) == True
        assert validate_action_rule(None, None) == True  # Disabling rule
    
    def test_validate_action_rule_invalid(self):
        """Test invalid action rule validation"""
        assert validate_action_rule("INVALID", 7) == False
        assert validate_action_rule("ARCHIVE", -1) == False
        assert validate_action_rule("ARCHIVE", 400) == False  # Too high
        assert validate_action_rule("ARCHIVE", None) == False
    
    def test_update_category_action_rule(self, db: Session, test_category: EmailCategory):
        """Test updating category action rule"""
        # Update with valid rule
        updated_category = update_category_action_rule(
            db, test_category.id, "ARCHIVE", 7, True
        )
        
        assert updated_category is not None
        assert updated_category.action == "ARCHIVE"
        assert updated_category.action_delay_days == 7
        assert updated_category.action_enabled == True
        assert updated_category.has_action_rule() == True
    
    def test_update_category_action_rule_invalid(self, db: Session, test_category: EmailCategory):
        """Test updating category with invalid action rule"""
        # Try with invalid action
        result = update_category_action_rule(
            db, test_category.id, "INVALID", 7, True
        )
        
        assert result is None
    
    def test_get_action_rules_for_user(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test getting action rules for user"""
        # Set up an action rule for the test category
        update_category_action_rule(db, test_category.id, "ARCHIVE", 7, True)
        
        # Should have at least one rule (our test category)
        rules = get_action_rules_for_user(db, test_user.id)
        assert len(rules) >= 1
        
        # Our test category should be in the list
        test_category_ids = [rule.id for rule in rules]
        assert test_category.id in test_category_ids
    
    def test_get_emails_affected_by_rule(self, db: Session, test_category: EmailCategory, test_emails: list[Email]):
        """Test getting emails affected by action rule"""
        # Set up action rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        
        # Get preview
        preview = get_emails_affected_by_rule(db, test_category.id)
        
        assert preview["has_action_rule"] == True
        assert preview["action"] == "ARCHIVE"
        assert preview["delay_days"] == 10
        assert preview["affected_emails"] > 0  # Should find emails older than 10 days
        assert "breakdown" in preview
    
    def test_disable_action_rule(self, db: Session, test_category: EmailCategory):
        """Test disabling action rule"""
        # Set up rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 7, True)
        assert test_category.has_action_rule() == True
        
        # Disable rule
        success = disable_action_rule(db, test_category.id)
        assert success == True
        
        # Verify rule is disabled
        db.refresh(test_category)
        assert test_category.has_action_rule() == False

class TestActionEngineService:
    """Test Action Engine Service functionality"""
    
    def test_find_emails_for_action(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test finding emails eligible for action"""
        # Set up action rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        db.refresh(test_category)
        
        # Find eligible emails
        eligible_emails = find_emails_for_action(db, test_user, test_category)
        
        # Should find emails older than 10 days
        assert len(eligible_emails) > 0
        for email in eligible_emails:
            age_days = (datetime.now(timezone.utc) - email.received_at).days
            assert age_days >= 10
            assert "INBOX" in email.labels
    
    def test_find_emails_for_action_no_rule(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test finding emails when no action rule is configured"""
        eligible_emails = find_emails_for_action(db, test_user, test_category)
        assert len(eligible_emails) == 0
    
    def test_create_proposed_action(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test creating proposed action"""
        # Use the oldest email
        oldest_email = min(test_emails, key=lambda e: e.received_at)
        
        proposed_action = create_proposed_action(
            db, oldest_email, test_category, "ARCHIVE"
        )
        
        assert proposed_action is not None
        assert proposed_action.email_id == oldest_email.id
        assert proposed_action.category_id == test_category.id
        assert proposed_action.action_type == "ARCHIVE"
        assert proposed_action.status == ProposedActionStatus.PENDING
        assert proposed_action.reason is not None
    
    def test_create_proposed_action_duplicate(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test creating duplicate proposed action"""
        email = test_emails[0]
        
        # Create first proposal
        action1 = create_proposed_action(db, email, test_category, "ARCHIVE")
        assert action1 is not None
        
        # Try to create duplicate
        action2 = create_proposed_action(db, email, test_category, "ARCHIVE")
        assert action2 is not None
        assert action2.id == action1.id  # Should return existing proposal
    
    def test_execute_action(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test executing action"""
        email = test_emails[0]
        
        operation = execute_action(db, email, test_category, "ARCHIVE")
        
        assert operation is not None
        assert operation.email_id == email.id
        assert operation.operation_type == "ARCHIVE"
        assert operation.status == OperationStatus.PENDING
        assert operation.operation_data["action_engine"] == True
        assert operation.operation_data["category_id"] == test_category.id
    
    def test_approve_proposed_action(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test approving proposed action"""
        email = test_emails[0]
        
        # Create proposed action
        proposed_action = create_proposed_action(db, email, test_category, "ARCHIVE")
        assert proposed_action is not None
        
        # Approve it
        operation = approve_proposed_action(db, proposed_action.id)
        
        assert operation is not None
        assert operation.operation_type == "ARCHIVE"
        
        # Check that proposed action is marked as approved
        db.refresh(proposed_action)
        assert proposed_action.status == ProposedActionStatus.APPROVED
    
    def test_reject_proposed_action(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test rejecting proposed action"""
        email = test_emails[0]
        
        # Create proposed action
        proposed_action = create_proposed_action(db, email, test_category, "ARCHIVE")
        assert proposed_action is not None
        
        # Reject it
        success = reject_proposed_action(db, proposed_action.id)
        
        assert success == True
        
        # Check that proposed action is marked as rejected
        db.refresh(proposed_action)
        assert proposed_action.status == ProposedActionStatus.REJECTED
    
    def test_process_category_actions_dry_run(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test processing category actions in dry run mode"""
        # Set up action rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        
        # Process in dry run mode
        result = process_category_actions(db, test_user, dry_run=True)
        
        assert result["success"] == True
        assert result["dry_run"] == True
        assert result["categories_processed"] >= 1  # At least our test category
        assert result["emails_found"] > 0
        assert result["actions_created"] > 0
        assert result["operations_created"] == 0  # No operations in dry run
    
    def test_process_category_actions_execute(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test processing category actions in execute mode"""
        # Set up action rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        
        # Process in execute mode
        result = process_category_actions(db, test_user, dry_run=False)
        
        assert result["success"] == True
        assert result["dry_run"] == False
        assert result["categories_processed"] >= 1  # At least our test category
        assert result["emails_found"] > 0
        assert result["actions_created"] == 0  # No proposals in execute mode
        assert result["operations_created"] > 0  # Should create operations
    
    def test_cleanup_expired_proposals(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test cleaning up expired proposals"""
        email = test_emails[0]
        
        # Create a proposal
        proposed_action = create_proposed_action(db, email, test_category, "ARCHIVE")
        assert proposed_action is not None
        
        # Manually set created_at to old date
        proposed_action.created_at = datetime.now(timezone.utc) - timedelta(days=31)
        db.commit()
        
        # Clean up expired proposals (older than 30 days)
        cleaned_count = cleanup_expired_proposals(db, max_age_days=30)
        
        assert cleaned_count == 1
        
        # Check that proposal is marked as expired
        db.refresh(proposed_action)
        assert proposed_action.status == ProposedActionStatus.EXPIRED
    
    def test_get_proposed_actions_for_user(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test getting proposed actions for user"""
        # Create some proposals
        for email in test_emails[:3]:
            create_proposed_action(db, email, test_category, "ARCHIVE")
        
        # Get proposals
        proposals, total_count = get_proposed_actions_for_user(
            db, test_user.id, limit=10, offset=0
        )
        
        assert len(proposals) == 3
        assert total_count == 3
        
        # Test filtering by status
        proposals, total_count = get_proposed_actions_for_user(
            db, test_user.id, status=ProposedActionStatus.PENDING, limit=10, offset=0
        )
        
        assert len(proposals) == 3
        assert total_count == 3

class TestActionEngineIntegration:
    """Test Action Engine integration scenarios"""
    
    def test_full_workflow(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test complete action engine workflow"""
        # 1. Set up action rule
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        
        # 2. Process in dry run mode
        result = process_category_actions(db, test_user, dry_run=True)
        assert result["actions_created"] > 0
        
        # 3. Get proposed actions
        proposals, count = get_proposed_actions_for_user(db, test_user.id)
        assert len(proposals) > 0
        
        # 4. Approve one proposal
        operation = approve_proposed_action(db, proposals[0].id)
        assert operation is not None
        
        # 5. Reject another proposal
        if len(proposals) > 1:
            success = reject_proposed_action(db, proposals[1].id)
            assert success == True
    
    def test_action_rule_stats(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test getting action rule statistics"""
        # Set up action rule and create some activity
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        process_category_actions(db, test_user, dry_run=True)
        
        # Get stats
        stats = get_action_rule_stats(db, test_user.id)
        
        assert "categories_with_rules" in stats
        assert "proposed_actions" in stats
        assert "action_engine_operations" in stats
        assert stats["categories_with_rules"] >= 1  # At least our test category
    
    def test_action_rule_history(self, db: Session, test_user: User, test_category: EmailCategory, test_emails: list[Email]):
        """Test getting action rule history"""
        # Create some activity
        update_category_action_rule(db, test_category.id, "ARCHIVE", 10, True)
        process_category_actions(db, test_user, dry_run=True)
        
        # Get history
        history = get_action_rule_history(db, test_user.id)
        
        assert len(history) > 0
        assert all("type" in item for item in history)
        assert all("created_at" in item for item in history) 