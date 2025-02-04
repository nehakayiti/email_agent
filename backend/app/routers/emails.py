from fastapi import APIRouter
from ..services.gmail import fetch_emails_from_gmail

router = APIRouter()

@router.get("/")
async def get_emails():
    """Return emails for morning review"""
    emails = fetch_emails_from_gmail()
    return {"emails": emails} 