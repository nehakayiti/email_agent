import sys
import os
from datetime import datetime, timedelta
from jose import jwt
import logging

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_token(email: str, expires_delta: timedelta = timedelta(days=1)):
    """Create a test JWT token for the given email"""
    settings = get_settings()
    
    to_encode = {"sub": email}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return token

if __name__ == "__main__":
    # Check if email is provided as command line argument
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        # Default test email
        email = "test@example.com"
    
    token = create_test_token(email)
    
    print("\n=== TEST TOKEN ===")
    print(f"Email: {email}")
    print(f"Token: {token}")
    print("=================\n")
    print(f"curl -X POST \"http://localhost:8000/emails/sync\" -H \"Authorization: Bearer {token}\"")
    print("=================\n") 