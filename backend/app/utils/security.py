from datetime import datetime, timedelta
from jose import jwt
from ..config import get_settings

settings = get_settings()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=1)):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256") 