import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.user import User
from app.models.email import Email
from app.models.email_category import EmailCategory
from app.models.proposed_action import ProposedAction, ProposedActionStatus
from app.services.action_engine_service import process_category_actions
from app.services.action_rule_service import update_category_action_rule

# Override the get_current_user dependency for testing
from app.dependencies import get_current_user

def override_get_current_user():
    """Override the get_current_user dependency for testing"""
    # This will be replaced by individual test mocks
    pass

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for API tests"""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        name="Test User",
        credentials={
            "access_token": "test_token",
            "refresh_token": "test_refresh_token"
        }
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_category(db: Session) -> EmailCategory:
    """Create a test category for API tests"""
    category = EmailCategory(
        name=f"test_category_{uuid.uuid4().hex[:8]}",
        display_name="Test Category",
        description="A test category",
        priority=50,
        is_system=False
    )
    db.add(category)
    db.commit()
    db.refresh(category)  # Refresh to get the auto-generated ID
    return category

@pytest.fixture
def test_email(db: Session, test_user: User, test_category: EmailCategory) -> Email:
    """Create a test email for API tests"""
    email = Email(
        id=uuid.uuid4(),
        user_id=test_user.id,
        gmail_id="test_gmail_id",
        subject="Test Email Subject",
        from_email="sender@example.com",
        received_at=datetime.now() - timedelta(days=5),
        category=test_category.name,
        thread_id="test_thread_id"
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email

@pytest.fixture
def test_proposed_action(db: Session, test_user: User, test_email: Email, test_category: EmailCategory) -> ProposedAction:
    """Create a test proposed action for API tests"""
    proposed_action = ProposedAction(
        id=uuid.uuid4(),
        email_id=test_email.id,
        user_id=test_user.id,
        category_id=test_category.id,
        action_type="ARCHIVE",
        reason="Email is old and can be archived",
        email_age_days=5,
        status=ProposedActionStatus.PENDING
    )
    db.add(proposed_action)
    db.commit()
    db.refresh(proposed_action)
    return proposed_action

class TestActionManagementAPI:
    """Test cases for Action Management API endpoints"""
    
    def test_create_action_rule_success(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test successful creation of an action rule"""
        # Override the dependency to return our test user
        app.dependency_overrides[get_current_user] = lambda: test_user
        
        with patch('app.routers.action_management.update_category_action_rule') as mock_update:
            mock_update.return_value = test_category
            test_category.action = "ARCHIVE"
            test_category.action_delay_days = 7
            test_category.action_enabled = True
            
            response = client.post(
                f"/action-management/categories/{test_category.id}/action-rule",
                json={
                    "action": "ARCHIVE",
                    "delay_days": 7,
                    "enabled": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["category_id"] == test_category.id
            assert data["action"] == "ARCHIVE"
            assert data["delay_days"] == 7
            assert data["enabled"] is True
            
            mock_update.assert_called_once()
            # Verify the call arguments more flexibly
            call_args = mock_update.call_args
            assert isinstance(call_args.kwargs['db'], Session)
            assert call_args.kwargs['category_id'] == test_category.id
            assert call_args.kwargs['delay_days'] == 7
            assert call_args.kwargs['enabled'] is True
            # Action can be either string or enum, so check the value robustly
            action_value = call_args.kwargs['action']
            if hasattr(action_value, "value"):
                assert action_value.value == "ARCHIVE"
            else:
                assert action_value == "ARCHIVE"
        
        # Clean up the dependency override
        app.dependency_overrides.clear()
    
    def test_create_action_rule_invalid_delay(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test action rule creation with invalid delay days"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.post(
            f"/action-management/categories/{test_category.id}/action-rule",
            json={
                "action": "ARCHIVE",
                "delay_days": -1,
                "enabled": True
            }
        )
        assert response.status_code == 422 or response.status_code == 400  # Validation or bad request
        app.dependency_overrides.clear()
    
    def test_get_action_rule_success(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test successful retrieval of an action rule"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.get_action_rules_for_user') as mock_get:
            test_category.action = "TRASH"
            test_category.action_delay_days = 14
            test_category.action_enabled = True
            mock_get.return_value = [test_category]
            response = client.get(f"/action-management/categories/{test_category.id}/action-rule")
            assert response.status_code == 200
            data = response.json()
            assert data["category_id"] == test_category.id
            assert data["action"] == "TRASH"
            assert data["delay_days"] == 14
            assert data["enabled"] is True
            mock_get.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_get.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['user_id'] == test_user.id
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == test_user.id  # user_id
        app.dependency_overrides.clear()
    
    def test_delete_action_rule_success(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test successful deletion of an action rule"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.update_category_action_rule') as mock_update:
            mock_update.return_value = test_category
            response = client.delete(f"/action-management/categories/{test_category.id}/action-rule")
            assert response.status_code == 200
            data = response.json()
            assert "deleted" in data["message"]
            mock_update.assert_called_once()
            # Verify the call arguments
            call_args = mock_update.call_args
            assert isinstance(call_args.kwargs['db'], Session)
            assert call_args.kwargs['category_id'] == test_category.id
            assert call_args.kwargs['action'] is None
            assert call_args.kwargs['delay_days'] is None
            assert call_args.kwargs['enabled'] is False
        app.dependency_overrides.clear()
    
    def test_get_action_preview_success(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test successful retrieval of action preview"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.get_emails_affected_by_rule') as mock_get:
            mock_get.return_value = [
                {"id": "1", "subject": "Test Email 1"},
                {"id": "2", "subject": "Test Email 2"}
            ]
            response = client.get(f"/action-management/categories/{test_category.id}/action-preview")
            assert response.status_code == 200
            data = response.json()
            assert data["category_id"] == test_category.id
            assert data["affected_email_count"] == 2
            assert len(data["affected_emails"]) == 2
            mock_get.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_get.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['category_id'] == test_category.id
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == test_category.id  # category_id
        app.dependency_overrides.clear()
    
    def test_get_all_action_rules_success(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test successful retrieval of all action rules"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.get_action_rules_for_user') as mock_get:
            test_category.action = "ARCHIVE"
            test_category.action_delay_days = 7
            test_category.action_enabled = True
            mock_get.return_value = [test_category]
            response = client.get("/action-management/action-rules")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["category_id"] == test_category.id
            assert data[0]["action"] == "ARCHIVE"
            mock_get.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_get.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['user_id'] == test_user.id
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == test_user.id  # user_id
        app.dependency_overrides.clear()

class TestProposedActionsAPI:
    """Test cases for Proposed Actions API endpoints"""
    
    def test_get_proposed_actions_success(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test successful retrieval of proposed actions"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.get("/proposed-actions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        app.dependency_overrides.clear()
    
    def test_get_proposed_actions_with_filters(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test retrieval of proposed actions with filters"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.get("/proposed-actions?status_filter=pending&action_type=ARCHIVE")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        app.dependency_overrides.clear()
    
    def test_approve_action_success(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test successful approval of a proposed action"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.approve_proposed_action') as mock_approve:
            mock_approve.return_value = {"success": True}
            response = client.post(f"/proposed-actions/{test_proposed_action.id}/approve")
            assert response.status_code == 200
            data = response.json()
            assert "approved" in data["message"]
            assert data["action_id"] == str(test_proposed_action.id)
            mock_approve.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_approve.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['action_id'] == str(test_proposed_action.id)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == str(test_proposed_action.id)  # action_id
        app.dependency_overrides.clear()
    
    def test_reject_action_success(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test successful rejection of a proposed action"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.reject_proposed_action') as mock_reject:
            mock_reject.return_value = {"success": True}
            response = client.post(f"/proposed-actions/{test_proposed_action.id}/reject")
            assert response.status_code == 200
            data = response.json()
            assert "rejected" in data["message"]
            assert data["action_id"] == str(test_proposed_action.id)
            mock_reject.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_reject.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['action_id'] == str(test_proposed_action.id)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == str(test_proposed_action.id)  # action_id
        app.dependency_overrides.clear()
    
    def test_bulk_approve_actions_success(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test successful bulk approval of proposed actions"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.approve_proposed_action') as mock_approve:
            mock_approve.return_value = {"success": True}
            response = client.post(
                "/proposed-actions/bulk-approve",
                json={"action_ids": [str(test_proposed_action.id)]}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["approved_count"] == 1
            assert data["failed_count"] == 0
            mock_approve.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_approve.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['action_id'] == str(test_proposed_action.id)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == str(test_proposed_action.id)  # action_id
        app.dependency_overrides.clear()
    
    def test_bulk_reject_actions_success(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test successful bulk rejection of proposed actions"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.reject_proposed_action') as mock_reject:
            mock_reject.return_value = {"success": True}
            response = client.post(
                "/proposed-actions/bulk-reject",
                json={"action_ids": [str(test_proposed_action.id)]}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["rejected_count"] == 1
            assert data["failed_count"] == 0
            mock_reject.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_reject.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['action_id'] == str(test_proposed_action.id)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == str(test_proposed_action.id)  # action_id
        app.dependency_overrides.clear()
    
    def test_process_dry_run_success(self, db: Session, test_user: User):
        """Test successful dry run processing"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.process_category_actions') as mock_process:
            mock_process.return_value = {
                "proposals_created": 5,
                "emails_processed": 10
            }
            response = client.post(
                "/proposed-actions/process-dry-run",
                json={"category_ids": None, "force": False}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mode"] == "dry_run"
            assert data["proposals_created"] == 5
            assert data["emails_processed"] == 10
            mock_process.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_process.call_args
            if call_args.args:
                if len(call_args.args) >= 3:
                    assert isinstance(call_args.args[0], Session)  # db
                    assert call_args.args[1] == test_user  # user
                    assert call_args.args[2] is True  # dry_run
            elif call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['user'] == test_user
                assert call_args.kwargs['dry_run'] is True
        app.dependency_overrides.clear()
    
    def test_process_execute_success(self, db: Session, test_user: User):
        """Test successful execute processing"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.process_category_actions') as mock_process:
            mock_process.return_value = {
                "operations_created": 3,
                "emails_processed": 8
            }
            response = client.post(
                "/proposed-actions/process-execute",
                json={"category_ids": None, "force": False}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["mode"] == "execute"
            assert data["operations_created"] == 3
            assert data["emails_processed"] == 8
            mock_process.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_process.call_args
            if call_args.args:
                if len(call_args.args) >= 3:
                    assert isinstance(call_args.args[0], Session)  # db
                    assert call_args.args[1] == test_user  # user
                    assert call_args.args[2] is False  # dry_run
            elif call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['user'] == test_user
                assert call_args.kwargs['dry_run'] is False
        app.dependency_overrides.clear()
    
    def test_cleanup_expired_proposals_success(self, db: Session, test_user: User):
        """Test successful cleanup of expired proposals"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.cleanup_expired_proposals') as mock_cleanup:
            mock_cleanup.return_value = 3
            response = client.post("/proposed-actions/cleanup-expired")
            assert response.status_code == 200
            data = response.json()
            assert "completed" in data["message"]
            assert data["expired_proposals_removed"] == 3
            mock_cleanup.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_cleanup.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
        app.dependency_overrides.clear()
    
    def test_get_proposed_actions_stats_success(self, db: Session, test_user: User):
        """Test successful retrieval of proposed actions statistics"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.get("/proposed-actions/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_proposals" in data
        assert "by_status" in data
        assert "by_action_type" in data
        app.dependency_overrides.clear()

class TestAPIValidation:
    """Test cases for API validation and error handling"""
    
    def test_invalid_action_type(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test API validation for invalid action type"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.post(
            f"/action-management/categories/{test_category.id}/action-rule",
            json={
                "action": "INVALID_ACTION",
                "delay_days": 7,
                "enabled": True
            }
        )
        assert response.status_code == 422 or response.status_code == 400  # Validation or bad request
        app.dependency_overrides.clear()
    
    def test_invalid_status_filter(self, db: Session, test_user: User):
        """Test API validation for invalid status filter"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        response = client.get("/proposed-actions?status_filter=invalid_status")
        assert response.status_code == 400  # Bad request
        app.dependency_overrides.clear()
    
    def test_bulk_action_too_many_ids(self, db: Session, test_user: User):
        """Test API validation for too many action IDs in bulk operation"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        # Create a list with more than 100 IDs
        action_ids = [str(uuid.uuid4()) for _ in range(101)]
        response = client.post(
            "/proposed-actions/bulk-approve",
            json={"action_ids": action_ids}
        )
        assert response.status_code == 422  # Validation error
        app.dependency_overrides.clear()
    
    def test_process_request_too_many_categories(self, db: Session, test_user: User):
        """Test API validation for too many category IDs in process request"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        # Create a list with more than 50 category IDs
        category_ids = list(range(51))
        response = client.post(
            "/proposed-actions/process-dry-run",
            json={"category_ids": category_ids, "force": False}
        )
        assert response.status_code == 422  # Validation error
        app.dependency_overrides.clear()

class TestAPIErrorHandling:
    """Test cases for API error handling"""
    
    def test_action_rule_validation_error(self, db: Session, test_user: User, test_category: EmailCategory):
        """Test handling of action rule validation errors"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.validate_action_rule') as mock_validate:
            mock_validate.return_value = False  # Invalid rule
            response = client.post(
                f"/action-management/categories/{test_category.id}/action-rule",
                json={
                    "action": "ARCHIVE",
                    "delay_days": 7,
                    "enabled": True
                }
            )
            assert response.status_code == 400  # Bad request
            mock_validate.assert_called_once()
            # Verify the call arguments
            call_args = mock_validate.call_args
            assert call_args.args[0] == "ARCHIVE"  # action
            assert call_args.args[1] == 7  # delay_days
        app.dependency_overrides.clear()
    
    def test_category_not_found(self, db: Session, test_user: User):
        """Test handling of category not found error"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.action_management.update_category_action_rule') as mock_update:
            mock_update.return_value = None  # Category not found
            response = client.post(
                "/action-management/categories/99999/action-rule",
                json={
                    "action": "ARCHIVE",
                    "delay_days": 7,
                    "enabled": True
                }
            )
            assert response.status_code == 404  # Not found
            mock_update.assert_called_once()
            # Verify the call arguments
            call_args = mock_update.call_args
            assert isinstance(call_args.kwargs['db'], Session)
            assert call_args.kwargs['category_id'] == 99999
        app.dependency_overrides.clear()
    
    def test_approve_action_failure(self, db: Session, test_user: User, test_proposed_action: ProposedAction):
        """Test handling of action approval failure"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.approve_proposed_action') as mock_approve:
            mock_approve.return_value = {"success": False, "error": "Action not found"}
            response = client.post(f"/proposed-actions/{test_proposed_action.id}/approve")
            assert response.status_code == 400  # Bad request for failed approval
            mock_approve.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_approve.call_args
            if call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['action_id'] == str(test_proposed_action.id)
            else:
                # Handle positional arguments
                assert isinstance(call_args.args[0], Session)  # db
                assert call_args.args[1] == str(test_proposed_action.id)  # action_id
        app.dependency_overrides.clear()
    
    def test_process_dry_run_failure(self, db: Session, test_user: User):
        """Test handling of dry run processing failure"""
        app.dependency_overrides[get_current_user] = lambda: test_user
        with patch('app.routers.proposed_actions.process_category_actions') as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            response = client.post(
                "/proposed-actions/process-dry-run",
                json={"category_ids": None, "force": False}
            )
            assert response.status_code == 500  # Internal server error
            mock_process.assert_called_once()
            # Verify the call arguments - handle both positional and keyword args
            call_args = mock_process.call_args
            if call_args.args:
                if len(call_args.args) >= 3:
                    assert isinstance(call_args.args[0], Session)  # db
                    assert call_args.args[1] == test_user  # user
                    assert call_args.args[2] is True  # dry_run
            elif call_args.kwargs:
                assert isinstance(call_args.kwargs['db'], Session)
                assert call_args.kwargs['user'] == test_user
                assert call_args.kwargs['dry_run'] is True
        app.dependency_overrides.clear() 