from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from ..models.email import Email
from ..db import get_db
from ..models.user import User
from ..services import gmail
from ..services.gmail import fetch_emails_from_gmail, update_email_labels
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
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Use the new sync service
        start_time = datetime.now()
        logger.info(f"[API] Starting sync process at {start_time.isoformat()}")
        
        try:
            result = sync_emails_since_last_fetch(db, current_user, use_current_date=use_current_date)
            
            # If credentials were refreshed, update them in the database
            current_token = current_user.credentials.get('token') if current_user.credentials else None
            if original_token and current_token and original_token != current_token:
                logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
                # Update the credentials in the database
                db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
                db.commit()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"[API] Sync completed in {duration:.2f} seconds")
            logger.info(f"[API] Sync result: {result}")
            
            return result
        except Exception as gmail_error:
            logger.error(f"[API] Gmail API error during sync: {str(gmail_error)}")
            # If there's an error with the Gmail API, we'll return a specific error
            return {
                "status": "error",
                "message": f"Error syncing emails with Gmail API: {str(gmail_error)}",
                "emails_synced": 0
            }
        
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

@router.post("/check-deleted")
async def check_deleted_emails_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check which emails have been deleted in Gmail and update their status in the database
    """
    try:
        logger.info(f"[API] Checking deleted emails for user {current_user.id}")
        
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Get all emails for the user that are not already marked as deleted
        emails = db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.is_deleted_in_gmail == False
        ).all()
        
        if not emails:
            logger.info(f"[API] No emails to check for user {current_user.id}")
            return {
                "status": "success",
                "message": "No emails to check",
                "deleted_count": 0
            }
        
        # Get the Gmail IDs to check
        gmail_ids = [email.gmail_id for email in emails]
        logger.info(f"[API] Checking {len(gmail_ids)} emails for deletion status")
        
        try:
            # Check which emails have been deleted in Gmail
            deleted_status = gmail.check_deleted_emails(current_user.credentials, gmail_ids)
            
            # Update the database with the deleted status
            deleted_count = 0
            for email in emails:
                if email.gmail_id in deleted_status and deleted_status[email.gmail_id]:
                    logger.info(f"[API] Marking email {email.id} as deleted in Gmail")
                    email.is_deleted_in_gmail = True
                    deleted_count += 1
            
            # If credentials were refreshed, update them in the database
            current_token = current_user.credentials.get('token') if current_user.credentials else None
            if original_token and current_token and original_token != current_token:
                logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
                # Update the credentials in the database
                db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
            
            # Commit the changes if needed
            if deleted_count > 0 or (original_token and current_token and original_token != current_token):
                db.commit()
                if deleted_count > 0:
                    logger.info(f"[API] Marked {deleted_count} emails as deleted in Gmail")
            
            return {
                "status": "success",
                "message": f"Checked {len(gmail_ids)} emails, found {deleted_count} deleted",
                "deleted_count": deleted_count
            }
        except Exception as gmail_error:
            logger.error(f"[API] Gmail API error: {str(gmail_error)}")
            # If there's an error with the Gmail API, we'll return a specific error
            return {
                "status": "error",
                "message": f"Error checking deleted emails with Gmail API: {str(gmail_error)}",
                "deleted_count": 0
            }
        
    except Exception as e:
        logger.error(f"[API] Error checking deleted emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check deleted emails: {str(e)}"
        )

@router.post("/{email_id}/update-labels")
async def update_email_labels(
    email_id: UUID,
    add_labels: List[str] = None,
    remove_labels: List[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the labels of an email in Gmail
    
    Parameters:
    - add_labels: List of labels to add
    - remove_labels: List of labels to remove
    """
    try:
        logger.info(f"[API] Updating labels for email {email_id}")
        
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Get the email from the database
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Check if the email has been deleted in Gmail
        if email.is_deleted_in_gmail:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update labels for an email that has been deleted in Gmail"
            )
        
        try:
            # Update the labels in Gmail
            result = update_email_labels(
                current_user.credentials,
                email.gmail_id,
                add_labels=add_labels,
                remove_labels=remove_labels
            )
            
            # Update the labels in the database
            current_labels = set(email.labels or [])
            
            if add_labels:
                for label in add_labels:
                    current_labels.add(label)
            
            if remove_labels:
                for label in remove_labels:
                    if label in current_labels:
                        current_labels.remove(label)
            
            email.labels = list(current_labels)
            
            # Update read status if UNREAD label is added or removed
            if add_labels and 'UNREAD' in add_labels:
                email.is_read = False
            elif remove_labels and 'UNREAD' in remove_labels:
                email.is_read = True
            
            # If credentials were refreshed, update them in the database
            current_token = current_user.credentials.get('token') if current_user.credentials else None
            if original_token and current_token and original_token != current_token:
                logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
                # Update the credentials in the database
                db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
            
            # Commit the changes
            db.commit()
            
            logger.info(f"[API] Labels updated successfully for email {email_id}")
            
            return {
                "status": "success",
                "message": "Labels updated successfully",
                "email_id": str(email_id),
                "labels": email.labels,
                "is_read": email.is_read
            }
        except Exception as gmail_error:
            logger.error(f"[API] Gmail API error updating labels: {str(gmail_error)}")
            # If there's an error with the Gmail API, we'll return a specific error
            return {
                "status": "error",
                "message": f"Error updating labels with Gmail API: {str(gmail_error)}",
                "email_id": str(email_id)
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"[API] Error updating labels for email {email_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email labels"
        ) 