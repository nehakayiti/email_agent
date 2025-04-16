from datetime import datetime
from app.models.email import Email
from app.dependencies import get_current_user
from app.services.email_processor import categorize_email
from app.models.email_category import EmailCategory
from app.models.sender_rule import SenderRule
from app.core.logging_config import configure_logging
import pytest
import json
import os

configure_logging(log_dir="backend/logs", log_file_name="email_agent.log", log_level=10, console_output=True)

def test_get_emails(client, test_user, db):
    # Override get_current_user using client.app.dependency_overrides
    client.app.dependency_overrides[get_current_user] = lambda: test_user

    # Create a dummy email for the test user.
    dummy_email = Email(
        user_id=test_user.id,
        gmail_id="dummy_gmail_id",
        thread_id="dummy_thread_id",
        subject="Test Subject",
        from_email="sender@example.com",
        received_at=datetime.utcnow(),
        snippet="This is a test snippet",
        labels=["INBOX"],
        is_read=False,
        is_processed=False,
        importance_score=50,
        category="primary",
        raw_data={"example": "data"}
    )
    db.add(dummy_email)
    db.commit()
    db.refresh(dummy_email)

    response = client.get("/emails/")
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert isinstance(data["emails"], list)
    # Now that we've added a dummy email, the list should have at least one item.
    assert len(data["emails"]) > 0

    # Optionally, remove the override after the test.
    client.app.dependency_overrides.pop(get_current_user, None)

def seed_category_with_rules(db, category_name, display_name, description, priority, sender_rules, keyword_rules):
    from app.models.email_category import CategoryKeyword
    from app.models.sender_rule import SenderRule
    # Create or get the category
    category = db.query(EmailCategory).filter_by(name=category_name).first()
    if not category:
        category = EmailCategory(
            name=category_name,
            display_name=display_name,
            description=description,
            priority=priority,
            is_system=True
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    # Add sender rules
    for rule in sender_rules:
        exists = db.query(SenderRule).filter_by(
            category_id=category.id, pattern=rule["pattern"], is_domain=rule.get("is_domain", True), user_id=None
        ).first()
        if not exists:
            db.add(SenderRule(
                category_id=category.id,
                pattern=rule["pattern"],
                is_domain=rule.get("is_domain", True),
                weight=rule.get("weight", 1),
                user_id=None
            ))
    # Add keyword rules
    for kw in keyword_rules:
        exists = db.query(CategoryKeyword).filter_by(
            category_id=category.id, keyword=kw["keyword"], is_regex=kw.get("is_regex", False), user_id=None
        ).first()
        if not exists:
            db.add(CategoryKeyword(
                category_id=category.id,
                keyword=kw["keyword"],
                is_regex=kw.get("is_regex", False),
                weight=kw.get("weight", 1),
                user_id=None
            ))
    db.commit()
    return category

# Utility to load test cases from an external JSON file
TEST_CASES_FILE = os.path.join(os.path.dirname(__file__), "categorization_test_cases.json")

def load_test_cases():
    with open(TEST_CASES_FILE, "r") as f:
        return json.load(f)

@pytest.mark.parametrize("email_data, expected_category", load_test_cases())
def test_categorization_logic_with_samples(db, test_user, email_data, expected_category):
    """
    This test checks the categorization logic using sample emails and expected categories.
    Test cases are loaded from categorization_test_cases.json in this directory.
    To add new cases, edit that file and add more (email_data, expected_category) pairs.
    """
    result = categorize_email(email_data, db, test_user.id)
    assert result.lower() == expected_category.lower(), f"Expected '{expected_category}', got '{result}' for email: {email_data}"
