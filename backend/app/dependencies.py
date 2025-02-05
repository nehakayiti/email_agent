from functools import lru_cache
from supabase import create_client, Client
from fastapi import HTTPException, status
import logging
from .config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache()
def get_supabase_client() -> Client:
    """Initialize and test Supabase client connection"""
    try:
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Test the connection by making a simple query
        client.table('users').select("*").limit(1).execute()
        logger.info("Supabase connection established successfully")
        return client
        
    except Exception as e:
        logger.error(f"Supabase client error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection error"
        )

def get_supabase_admin_client():
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY  # Use service key instead of anon key
    )
    return client 