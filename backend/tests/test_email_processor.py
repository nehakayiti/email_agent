import pytest
from backend.app.services.email_processor import process_and_store_emails, reprocess_emails
from backend.app.db import SessionLocal
from backend.app.models.email import Email
from backend.app.models.user import User
from backend.app.models.email_category import EmailCategory, CategoryKeyword
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from backend.app.services.email_sync_service import sync_emails_since_last_fetch
from unittest.mock import patch
from datetime import timezone
import uuid
from backend.app.utils.email_utils import set_email_category_and_labels

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session: Session):
    unique_email = f"test_{uuid.uuid4()}@example.com"
    user = User(id=uuid4(), email=unique_email, credentials={"token": "fake-token"})
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture(autouse=True)
def ensure_trash_category(db_session: Session):
    # Ensure 'trash' category exists for the test
    if not db_session.query(EmailCategory).filter_by(name='trash').first():
        db_session.add(EmailCategory(name='trash', display_name='Trash', description='Trash', priority=5, is_system=True))
        db_session.commit()


def test_new_trash_email_removes_inbox_label(db_session, test_user):
    # Simulate a new email with INBOX label that should be categorized as trash
    email_data = {
        'gmail_id': 'test-gmail-id',
        'thread_id': 'test-thread-id',
        'subject': 'Spam offer',
        'from_email': 'spammer@spam.com',
        'received_at': datetime.utcnow().isoformat(),
        'snippet': 'Buy now!',
        'labels': ['INBOX', 'SOME_OTHER_LABEL'],
        'is_read': False,
        'raw_data': {},
    }
    # Patch categorize_email to always return 'trash'
    from backend.app.services import email_processor
    orig_categorize_email = email_processor.categorize_email
    email_processor.categorize_email = lambda *a, **kw: 'trash'
    try:
        emails = process_and_store_emails(db_session, test_user, [email_data])
        assert len(emails) == 1
        email = emails[0]
        assert email.category == 'trash'
        assert 'TRASH' in email.labels
        assert 'INBOX' not in email.labels
    finally:
        email_processor.categorize_email = orig_categorize_email 

def fake_gmail_fetch_history_changes(service, history_id, max_pages=5):
    # Simulate Gmail returning 2 new emails
    return {
        "new_history_id": "new-history-id",
        "new_emails": [
            {"gmail_id": "id1", "thread_id": "t1", "subject": "Test1", "from_email": "a@b.com", "received_at": datetime.now(timezone.utc).isoformat(), "snippet": "", "labels": ["INBOX"], "is_read": False, "raw_data": {}},
            {"gmail_id": "id2", "thread_id": "t2", "subject": "Test2", "from_email": "c@d.com", "received_at": datetime.now(timezone.utc).isoformat(), "snippet": "", "labels": ["INBOX"], "is_read": False, "raw_data": {}}
        ],
        "deleted_ids": [],
        "label_changes": {}
    }

@pytest.mark.asyncio
async def test_sync_emails_checked_count(db_session, test_user):
    from backend.app.services import gmail as gmail_mod
    with patch.object(gmail_mod, 'get_gmail_service', return_value=None), \
         patch.object(gmail_mod, 'fetch_history_changes', side_effect=fake_gmail_fetch_history_changes):
        # Patch process_pending_operations to do nothing
        from backend.app.services import email_operations_service
        async def fake_process_pending_operations(db, user, credentials):
            return {"processed_count": 0, "success_count": 0, "failure_count": 0, "retry_count": 0}
        email_operations_service.process_pending_operations = fake_process_pending_operations
        # Run the sync
        result = await sync_emails_since_last_fetch(db_session, test_user)
        # Check emails_checked is 2
        assert result["emails_checked"] == 2
        assert result["new_email_count"] == 2
        assert result["sync_count"] == 2 

@pytest.mark.asyncio
def test_trash_keyword_categorization(db_session, test_user):
    # Add trash category if not present
    trash_category = db_session.query(EmailCategory).filter_by(name='trash').first()
    if not trash_category:
        trash_category = EmailCategory(name='trash', display_name='Trash', description='Trash', priority=5, is_system=True)
        db_session.add(trash_category)
        db_session.commit()
    # Add trash keyword
    keyword = CategoryKeyword(category_id=trash_category.id, keyword='test 123', is_regex=False, weight=1)
    db_session.add(keyword)
    db_session.commit()
    # Add email with subject 'test 123'
    email = Email(
        user_id=test_user.id,
        gmail_id='test-trash-keyword',
        thread_id='t1',
        subject='test 123',
        from_email='sender@example.com',
        received_at=datetime.utcnow(),
        snippet='',
        labels=['INBOX'],
        is_read=False,
        raw_data={}
    )
    db_session.add(email)
    db_session.commit()
    # Run reprocess_emails
    reprocess_emails(db_session, test_user.id, include_reprocessed=True)
    db_session.refresh(email)
    assert email.category == 'trash', f"Expected 'trash', got '{email.category}'" 

def test_set_email_category_and_labels_consistency():
    from backend.app.utils.email_utils import set_email_category_and_labels
    class DummyEmail:
        def __init__(self, labels, category=None):
            self.labels = labels
            self.category = category
    # Trash: should add TRASH, remove INBOX
    email = DummyEmail(labels=["INBOX", "SOME_OTHER_LABEL"], category="primary")
    changed = set_email_category_and_labels(email, "trash")
    assert changed is True
    assert email.category == "trash"
    assert "TRASH" in email.labels
    assert "INBOX" not in email.labels
    # Archive: should remove INBOX and TRASH
    email = DummyEmail(labels=["INBOX", "TRASH", "OTHER"], category="trash")
    changed = set_email_category_and_labels(email, "archive")
    assert changed is True
    assert email.category == "archive"
    assert "INBOX" not in email.labels
    assert "TRASH" not in email.labels
    # Important: should add INBOX, remove TRASH
    email = DummyEmail(labels=["TRASH", "OTHER"], category="archive")
    changed = set_email_category_and_labels(email, "important")
    assert changed is True
    assert email.category == "important"
    assert "INBOX" in email.labels
    assert "TRASH" not in email.labels
    # Idempotency: no change if already correct
    email = DummyEmail(labels=["TRASH"], category="trash")
    changed = set_email_category_and_labels(email, "trash")
    assert changed is False
    assert email.category == "trash"
    assert email.labels.count("TRASH") == 1
    # No duplicate labels
    email = DummyEmail(labels=["INBOX", "INBOX", "TRASH", "TRASH"], category="primary")
    set_email_category_and_labels(email, "important")
    assert email.labels.count("INBOX") == 1
    assert email.labels.count("TRASH") == 0 