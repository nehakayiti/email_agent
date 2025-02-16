from datetime import datetime
from app.models.email import Email
from app.dependencies import get_current_user

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
