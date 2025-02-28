from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timedelta

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
    force_full_sync: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync emails from Gmail to local database since the last fetch time
    
    Parameters:
    - use_current_date: If true, use the current date for checkpoint instead of treating it as next day
    - force_full_sync: If true, forces a full sync ignoring the last checkpoint date
    """
    logger.info(f"[API] Email sync requested for user {current_user.id} (email: {current_user.email})")
    logger.info(f"[API] Sync parameters: use_current_date={use_current_date}, force_full_sync={force_full_sync}")
    
    try:
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Use the new sync service
        start_time = datetime.now()
        logger.info(f"[API] Starting sync process at {start_time.isoformat()}")
        
        try:
            # When force_full_sync is true, we'll pass it to sync_emails_since_last_fetch
            # which will adjust the query to get more emails
            result = sync_emails_since_last_fetch(
                db, 
                current_user, 
                use_current_date=use_current_date,
                force_full_sync=force_full_sync
            )
            
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

@router.post("/sync/fresh")
async def sync_fresh_emails(
    days_back: int = 3,
    max_emails: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Force a fresh sync grabbing recent emails without using history ID
    
    This endpoint is useful when you want to grab recent emails with a cleaner approach
    than the standard sync (avoiding date-time parsing issues).
    
    Parameters:
    - days_back: Number of days to look back for emails (default: 3)
    - max_emails: Maximum number of emails to retrieve (default: 200)
    """
    logger.info(f"[API] Fresh email sync requested for user {current_user.id} (email: {current_user.email})")
    logger.info(f"[API] Fresh sync parameters: days_back={days_back}, max_emails={max_emails}")
    
    try:
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Start timer for performance tracking
        start_time = datetime.now()
        logger.info(f"[API] Starting fresh sync at {start_time.isoformat()}")
        
        try:
            # Get existing Gmail IDs to filter out already processed emails
            existing_gmail_ids = db.query(Email.gmail_id).filter(
                Email.user_id == current_user.id
            ).all()
            existing_gmail_ids = set([id[0] for id in existing_gmail_ids]) 
            logger.info(f"[API] Found {len(existing_gmail_ids)} existing emails in database")
            
            # Create a date-based query that looks back a specific number of days
            # This is more reliable than trying to use timestamp-based queries
            past_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f"after:{past_date} in:inbox"
            logger.info(f"[API] Using query: '{query}'")
            
            # Fetch emails from Gmail with the specified query
            emails = gmail.fetch_emails_from_gmail(
                current_user.credentials, 
                max_results=max_emails,
                query=query
            )
            
            if not emails:
                logger.info(f"[API] No emails found with query: '{query}'")
                return {
                    "status": "success",
                    "message": "No emails found",
                    "emails_synced": 0
                }
            
            logger.info(f"[API] Retrieved {len(emails)} emails from Gmail API")
            
            # Filter out already processed emails
            new_emails = []
            for email in emails:
                if email['gmail_id'] not in existing_gmail_ids:
                    new_emails.append(email)
            
            logger.info(f"[API] After filtering, {len(new_emails)} new emails remain for processing")
            
            if not new_emails:
                logger.info(f"[API] All retrieved emails were already processed")
                return {
                    "status": "success",
                    "message": "All emails already synced",
                    "emails_synced": 0
                }
            
            # Process and store the new emails
            processed_emails = process_and_store_emails(db, current_user, new_emails)
            logger.info(f"[API] Successfully processed and stored {len(processed_emails)} emails")
            
            # If credentials were refreshed, update them
            current_token = current_user.credentials.get('token') if current_user.credentials else None
            if original_token and current_token and original_token != current_token:
                logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
                db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
                db.commit()
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"[API] Fresh sync completed in {duration:.2f} seconds")
            
            return {
                "status": "success",
                "message": f"Synced {len(processed_emails)} new emails",
                "emails_synced": len(processed_emails)
            }
            
        except Exception as gmail_error:
            logger.error(f"[API] Gmail API error during fresh sync: {str(gmail_error)}")
            return {
                "status": "error",
                "message": f"Error during fresh sync: {str(gmail_error)}",
                "emails_synced": 0
            }
        
    except Exception as e:
        logger.error(f"[API] Error in fresh sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync fresh emails"
        )

@router.post("/notifications/setup")
async def setup_push_notifications(
    webhook_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Set up Gmail push notifications for real-time updates
    
    Parameters:
    - webhook_url: HTTPS URL that will receive push notifications
    """
    logger.info(f"[API] Setting up push notifications for user {current_user.id} with webhook: {webhook_url}")
    
    try:
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Set up push notifications
        result = gmail.setup_push_notifications(
            current_user.credentials,
            webhook_url
        )
        
        # If credentials were refreshed, update them
        current_token = current_user.credentials.get('token') if current_user.credentials else None
        if original_token and current_token and original_token != current_token:
            logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
            db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
            db.commit()
        
        # Store the push notification details in the user record for future reference
        update_data = {
            "push_notification_data": {
                "webhook_url": webhook_url,
                "history_id": result.get("historyId"),
                "expiration": result.get("expiration"),
                "topic_name": result.get("topic_name"),
                "setup_time": datetime.now().isoformat()
            }
        }
        
        db.query(User).filter(User.id == current_user.id).update(update_data)
        db.commit()
        
        logger.info(f"[API] Push notifications set up successfully: {result}")
        
        return {
            "status": "success",
            "message": "Push notifications set up successfully",
            "historyId": result.get("historyId"),
            "expiration": result.get("expiration")
        }
        
    except Exception as e:
        logger.error(f"[API] Error setting up push notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set up push notifications: {str(e)}"
        )

@router.post("/notifications/stop")
async def stop_push_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stop Gmail push notifications that were previously set up
    """
    logger.info(f"[API] Stopping push notifications for user {current_user.id}")
    
    try:
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Stop push notifications
        result = gmail.stop_push_notifications(current_user.credentials)
        
        # If credentials were refreshed, update them
        current_token = current_user.credentials.get('token') if current_user.credentials else None
        if original_token and current_token and original_token != current_token:
            logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
            db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
            db.commit()
        
        # Clear the push notification data from the user record
        db.query(User).filter(User.id == current_user.id).update({"push_notification_data": None})
        db.commit()
        
        logger.info(f"[API] Push notifications stopped successfully")
        
        return {
            "status": "success",
            "message": "Push notifications stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"[API] Error stopping push notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop push notifications: {str(e)}"
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
    Check which emails have been deleted in Gmail and update their status in the database.
    This endpoint uses an optimized approach to minimize API calls by:
    1. Sampling a small subset of emails first
    2. Only performing a full check if needed
    3. Using exponential backoff for rate limiting
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
            # Check which emails have been deleted in Gmail - using optimized approach
            # The force_full_check parameter is False by default, which means it will
            # first sample a few emails and only check all if deletions are detected
            deleted_status = gmail.check_deleted_emails(
                credentials=current_user.credentials, 
                gmail_ids=gmail_ids
            )
            
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
async def update_labels_endpoint(
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
            # Update the labels in Gmail - be careful with parameter names to avoid errors
            result = gmail.update_email_labels(
                credentials=current_user.credentials,
                gmail_id=email.gmail_id,
                add_labels=add_labels,
                remove_labels=remove_labels
            )
            
            # Update the email model with new labels
            email_updated = False
            current_labels = set(email.labels or [])
            
            if add_labels:
                for label in add_labels:
                    if label not in current_labels:
                        current_labels.add(label)
                        email_updated = True
                
                # Special handling for read status based on UNREAD label
                if 'UNREAD' in add_labels and email.is_read:
                    email.is_read = False
                    email_updated = True
            
            if remove_labels:
                for label in remove_labels:
                    if label in current_labels:
                        current_labels.remove(label)
                        email_updated = True
                
                # Special handling for read status based on UNREAD label
                if 'UNREAD' in remove_labels and not email.is_read:
                    email.is_read = True
                    email_updated = True
            
            # Update labels if changed
            if email_updated:
                email.labels = list(current_labels)
                logger.info(f"[API] Updated email {email_id} labels in database to {list(current_labels)}")
            
            # If credentials were refreshed, update them in the database
            current_token = current_user.credentials.get('token') if current_user.credentials else None
            if original_token and current_token and original_token != current_token:
                logger.info(f"[API] Updating refreshed credentials for user {current_user.id}")
                db.query(User).filter(User.id == current_user.id).update({"credentials": current_user.credentials})
                email_updated = True
            
            # Commit if needed
            if email_updated:
                db.commit()
            
            return {
                "status": "success",
                "message": "Labels updated successfully",
                "email_id": str(email_id),
                "current_labels": list(current_labels)
            }
            
        except Exception as gmail_error:
            logger.error(f"[API] Gmail API error updating labels: {str(gmail_error)}")
            # If there's an error with the Gmail API, we'll return a specific error
            return {
                "status": "error",
                "message": f"Error updating labels with Gmail API: {str(gmail_error)}",
                "email_id": str(email_id)
            }
    
    except Exception as e:
        logger.error(f"[API] Error updating labels: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update labels: {str(e)}"
        ) 