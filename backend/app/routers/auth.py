from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from ..config import get_settings
from ..dependencies import get_supabase_client, get_supabase_admin_client
from ..utils.security import create_access_token
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
import logging
import google.oauth2.credentials
import google.auth.transport.requests
import requests

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def create_flow():
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
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    scope: str = Query(...),
    supabase = Depends(get_supabase_admin_client)
):
    """Handle OAuth callback and create user session"""
    try:
        flow = create_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info from credentials
        import google.oauth2.credentials
        import google.auth.transport.requests
        import requests

        # Create authorized session
        session = requests.Session()
        session.headers = {
            'Authorization': f'Bearer {credentials.token}',
        }

        # Get user info from Google
        userinfo_response = session.get('https://www.googleapis.com/oauth2/v3/userinfo')
        userinfo = userinfo_response.json()
        
        # Build user data dict from userinfo response
        user_data = {
            "email": userinfo["email"],
            "name": userinfo.get("name", ""),
            "credentials": {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
            }
        }
        
        # Run the blocking upsert call in a threadpool with admin client
        response = await run_in_threadpool(
            lambda: supabase.table("users").upsert(user_data).execute()
        )
        if hasattr(response, 'error') and response.error is not None:
            return JSONResponse(
                content={"error": str(response.error)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        access_token = create_access_token(data={"sub": user_data["email"]})
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Helper that contains most of the callback logic.
def process_auth_callback(code: str, supabase_client, flow_factory=create_flow):
    flow = flow_factory()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_data = {
        "email": credentials.id_token["email"],
        "name": credentials.id_token.get("name", ""),
        "credentials": {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
        },
    }
    response = supabase_client.table("users").upsert(user_data).execute()
    if hasattr(response, "error") and response.error is not None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(response.error),
        )
    access_token = create_access_token(data={"sub": user_data["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
