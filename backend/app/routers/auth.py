from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow

from ..config import get_settings
from ..db import get_db
from ..models.user import User
from ..utils.security import create_access_token
from ..utils.google import get_userinfo
from starlette.requests import Request
import logging
import requests
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)
logger.debug("Initializing auth router")

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
    """Initiate Google OAuth flow"""
    logger.debug("Login endpoint called")
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
    error: str | None = Query(None),
    db: Session = Depends(get_db)
):
    """Handle OAuth callback"""
    logger.debug(f"Callback received - code: {'present' if code else 'missing'}, state: {state}, error: {error}")
    
    if error:
        logger.error(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        logger.error("No code provided in callback")
        raise HTTPException(status_code=400, detail="No code provided")

    try:
        logger.info("Starting OAuth callback processing")
        logger.debug(f"Received code: {code[:10]}... and state: {state}")
        
        # Create flow and fetch credentials
        flow = create_flow()
        logger.debug("Created OAuth flow")
        
        try:
            flow.fetch_token(code=code)
            logger.debug("Successfully fetched OAuth token")
        except Exception as e:
            logger.error(f"Error fetching token: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail="Failed to fetch token")
        
        credentials = flow.credentials
        logger.debug("Got credentials object")
        
        # Get user info
        try:
            userinfo = get_userinfo(credentials)
            logger.debug(f"Got user info: {userinfo}")
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Store or update user
        try:
            user = db.query(User).filter(User.email == userinfo["email"]).first()
            logger.debug(f"Found existing user: {user is not None}")
            
            if user:
                logger.debug("Updating existing user")
                user.name = userinfo["name"]
                user.last_sign_in = func.now()
                user.credentials = {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                }
            else:
                logger.debug("Creating new user")
                user = User(
                    email=userinfo["email"],
                    name=userinfo["name"],
                    credentials={
                        "token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                    }
                )
                db.add(user)
            
            logger.debug("Committing to database")
            db.commit()
            logger.info(f"Successfully stored/updated user {user.email}")
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to update user information"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        logger.debug("Created access token")
        
        # Redirect to frontend with token
        redirect_url = f"http://localhost:8000/auth/callback?token={access_token}"
        logger.info(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"500: {str(e)}"
        )
