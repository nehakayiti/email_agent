from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from ..config import get_settings
from ..dependencies import get_supabase_client
from ..utils.security import create_access_token

router = APIRouter()
settings = get_settings()

# Create OAuth2 flow
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
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

@router.get("/login")
async def login():
    """Initiate Google OAuth login flow"""
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(
    code: str,
    supabase = Depends(get_supabase_client)
):
    """Handle OAuth callback and create user session"""
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from Google
        user_info = {
            "email": credentials.id_token["email"],
            "name": credentials.id_token.get("name", ""),
            "google_credentials": {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
            }
        }
        
        # Store user in Supabase
        response = supabase.table("users").upsert(user_info).execute()
        
        # Create access token
        access_token = create_access_token(data={"sub": user_info["email"]})
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 