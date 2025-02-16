from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.email import Email
from ..db import get_db
from ..models.user import User
from ..services.gmail import fetch_emails_from_gmail
from ..services.email_processor import process_and_store_emails
from ..dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/sync")
async def sync_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync emails from Gmail to local database
    """
    try:
        # Fetch emails from Gmail
        emails = fetch_emails_from_gmail(current_user.credentials)
        
        # Process and store emails
        processed_emails = process_and_store_emails(db, current_user, emails)
        
        return {
            "status": "success",
            "message": f"Processed {len(processed_emails)} emails",
            "sync_count": len(processed_emails)
        }
        
    except Exception as e:
        logger.error(f"Error syncing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync emails"
        )

@router.get("/")
async def get_emails(
    category: str = None,
    importance_threshold: int = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's emails with optional filtering
    """
    query = db.query(Email).filter(Email.user_id == current_user.id)
    
    if category:
        query = query.filter(Email.category == category)
    
    if importance_threshold is not None:
        query = query.filter(Email.importance_score >= importance_threshold)
    
    emails = query.order_by(Email.received_at.desc()).limit(limit).all()
    
    return {"emails": emails} 