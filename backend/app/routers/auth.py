from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from ..config import get_settings
from ..db import get_db
from ..models.user import User
from ..utils.security import create_access_token
from starlette.requests import Request
import logging
import requests
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Add debug print
print("\nCreating auth router")
router = APIRouter()
settings = get_settings()

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def create_flow():
    """Create and configure Google OAuth flow"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GOOGLE_SCOPES
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow

@router.get("/login")
async def login():
    """Initiate Google OAuth login flow"""
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return RedirectResponse(
        url=authorization_url, 
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

@router.get("/callback")
async def callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    scope: str = Query(...),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback and create/update user"""
    try:
        # Get Google credentials
        flow = create_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from Google
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user info from Google"
            )
            
        userinfo = userinfo_response.json()
        email = userinfo["email"]
        
        try:
            # Try to get existing user
            user = db.query(User).filter(User.email == email).first()
            
            user_data = {
                "email": email,
                "name": userinfo.get("name", ""),
                "credentials": {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                }
            }
            
            if user:
                # Update existing user
                for key, value in user_data.items():
                    setattr(user, key, value)
                status_message = "existing_user_updated"
            else:
                # Create new user
                user = User(**user_data)
                db.add(user)
                status_message = "new_user_created"
                
            db.commit()
            db.refresh(user)
            
            # Create JWT access token
            access_token = create_access_token(data={"sub": email})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "status": status_message,
                "user": {
                    "email": email,
                    "name": user_data["name"]
                }
            }
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user information"
            )
            
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
