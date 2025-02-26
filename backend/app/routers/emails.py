from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from ..models.email import Email
from ..db import get_db
from ..models.user import User
from ..services.gmail import fetch_emails_from_gmail
from ..services.email_processor import process_and_store_emails
from ..services.email_sync_service import sync_emails_since_last_fetch
from ..dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/sync")
async def sync_emails(
    use_current_date: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync emails from Gmail to local database since the last fetch time
    
    Parameters:
    - use_current_date: If true, use the current date for checkpoint instead of treating it as next day
    """
    logger.info(f"[API] Email sync requested for user {current_user.id} (email: {current_user.email})")
    logger.info(f"[API] Sync parameters: use_current_date={use_current_date}")
    
    try:
        # Use the new sync service
        start_time = datetime.now()
        logger.info(f"[API] Starting sync process at {start_time.isoformat()}")
        
        result = sync_emails_since_last_fetch(db, current_user, use_current_date=use_current_date)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"[API] Sync completed in {duration:.2f} seconds")
        logger.info(f"[API] Sync result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"[API] Error syncing emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync emails"
        )

@router.get("/")
async def get_emails(
    category: str = None,
    importance_threshold: int = None,
    limit: int = 20,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's emails with optional filtering for continuous scrolling
    
    Parameters:
    - category: Filter emails by category
    - importance_threshold: Filter emails with importance score >= threshold
    - limit: Number of emails per page (default: 20)
    - page: Page number (starting from 1)
    
    Returns paginated results for continuous scrolling with metadata
    """
    # Validate parameters
    if limit <= 0:
        limit = 20
    
    if page <= 0:
        page = 1
        
    # Calculate offset
    offset = (page - 1) * limit
        
    query = db.query(Email).filter(Email.user_id == current_user.id)
    
    if category:
        query = query.filter(Email.category == category)
    
    if importance_threshold is not None:
        query = query.filter(Email.importance_score >= importance_threshold)
    
    # Get total count for pagination metadata
    total_count = query.count()
    
    # Get emails for current page
    emails = query.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    
    # Calculate pagination metadata
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_previous = page > 1
    
    logger.info(f"Found {len(emails)} emails for page {page} (total: {total_count})")
    
    return {
        "emails": emails,
        "pagination": {
            "total": total_count,
            "limit": limit,
            "current_page": page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous,
            "next_page": page + 1 if has_next else None,
            "previous_page": page - 1 if has_previous else None
        }
    }

@router.get("/{email_id}")
async def get_email(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single email by ID
    """
    email = db.query(Email).filter(
        Email.id == email_id,
        Email.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email 