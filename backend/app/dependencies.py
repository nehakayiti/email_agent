from functools import lru_cache
from fastapi import HTTPException, status, Depends
import logging
from .config import get_settings
from sqlalchemy.orm import Session
from .db import get_db
from .models.user import User
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timezone
import os

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current authenticated user from the JWT token
    """
    logger.debug(f"Authenticating user with token: {token[:10]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        logger.debug(f"Decoding JWT token with SECRET_KEY: {SECRET_KEY[:5]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        logger.debug(f"Decoded JWT token, user_email: {user_email}")
        
        if user_email is None:
            logger.warning("No user_email found in JWT token")
            raise credentials_exception
            
        # Get the user from the database by email (not ID)
        user = db.query(User).filter(User.email == user_email).first()
        
        if user is None:
            logger.warning(f"User with email {user_email} not found in database")
            raise credentials_exception
        
        logger.debug(f"Found user: {user.email} (ID: {user.id})")
        
        # Update last sign in time
        user.last_sign_in = datetime.now(timezone.utc)
        db.commit()
        
        # Check if credentials exist and are valid
        if not user.credentials:
            logger.warning(f"User {user.id} has no OAuth credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gmail credentials not found. Please authenticate with Gmail."
            )
        
        # Ensure the credentials have the required fields
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
        for field in required_fields:
            if field not in user.credentials:
                logger.warning(f"User {user.id} is missing required credential field: {field}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid Gmail credentials: missing {field}. Please re-authenticate with Gmail."
                )
        
        return user
        
    except JWTError:
        raise credentials_exception 