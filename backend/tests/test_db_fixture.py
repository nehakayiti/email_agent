from sqlalchemy.orm import Session
from backend.app.models.user import User

def test_db_fixture_works(db_session: Session):
    # Try to add a user to verify the database is accessible and migrated
    new_user = User(email="test@example.com", name="Test User", credentials={})
    db_session.add(new_user)
    db_session.commit()
    
    # Verify the user was added
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.name == "Test User"

    print("\n--- Test database fixture is working correctly! ---")

