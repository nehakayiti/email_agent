from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from ..config import get_settings
from ..dependencies import get_supabase_client
from ..utils.security import create_access_token
from starlette.concurrency import run_in_threadpool

router = APIRouter()
settings = get_settings()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def create_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )

@router.get("/login")
async def login():
    """Initiate Google OAuth login flow"""
    flow = create_flow()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
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
        flow = create_flow()
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Build a user data dict from the returned credentials
        user_data = {
            "email": credentials.id_token["email"],
            "name": credentials.id_token.get("name", ""),
            "credentials": {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
            }
        }
        
        # Run the blocking upsert call in a threadpool
        response = await run_in_threadpool(lambda: supabase.table("users").upsert(user_data).execute())
        if hasattr(response, 'error') and response.error is not None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(response.error)
            )
        
        access_token = create_access_token(data={"sub": user_data["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        print(f"Callback error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 