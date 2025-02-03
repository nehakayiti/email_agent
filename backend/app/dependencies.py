from functools import lru_cache
from supabase import create_client, Client
from .config import get_settings

settings = get_settings()

@lru_cache()
def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY) 