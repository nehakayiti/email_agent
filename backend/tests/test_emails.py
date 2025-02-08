from fastapi.testclient import TestClient
from app.utils.security import create_access_token

def test_get_emails(client, test_user):
    """Test email fetching with authentication"""
    token = create_access_token(data={"sub": test_user.email})
    response = client.get(
        "/emails/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "emails" in data
    assert isinstance(data["emails"], list)
    # Ensure our dummy data is returned
    assert len(data["emails"]) > 0 
