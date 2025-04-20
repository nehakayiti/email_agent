from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import or_, and_

from ..models.email import Email
from ..models.email_sync import EmailSync
from ..db import get_db
from ..models.user import User
# Use the module import pattern for gmail
from ..services import gmail
# Remove the individual function imports
from ..services.email_processor import process_and_store_emails
from ..services.email_sync_service import sync_emails_since_last_fetch
from ..dependencies import get_current_user
import logging
from ..models.email_operation import EmailOperation, OperationType, OperationStatus
from ..services import email_operations_service
from ..models.email_trash_event import EmailTrashEvent
from ..models.email_categorization_decision import EmailCategorizationDecision
from ..models.categorization_feedback import CategorizationFeedback
from ..models.email_category import EmailCategory
from ..models.sender_rule import SenderRule
from ..models.sync_details import SyncDetails, SyncDirection, SyncType, SyncStatus

logger = logging.getLogger(__name__)
router = APIRouter()

class CategoryUpdate(BaseModel):
    category: str

# Utility function for atomic category/label update
def set_email_category_and_labels(email, new_category):
    old_category = email.category
    email.category = new_category
    labels = set(email.labels or [])
    if new_category == 'trash':
        labels.add('TRASH')
        labels.discard('INBOX')
    elif new_category == 'archive':
        labels.discard('INBOX')
        labels.discard('TRASH')
    else:
        labels.add('INBOX')
        labels.discard('TRASH')
    email.labels = list(labels)
    return old_category != new_category

@router.post("/sync")
async def sync_emails(
    use_current_date: bool = False,
    force_full_sync: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sync emails from Gmail to local database using the efficient historyId approach
    
    This endpoint syncs emails using Gmail's historyId for incremental synchronization when available,
    falling back to the label approach only when necessary.
    
    Parameters:
    - use_current_date: If true, use the current date for checkpoint instead of treating it as next day
    - force_full_sync: If true, forces a full sync ignoring the last checkpoint date
    """
    logger.info(f"[API] Email sync requested for user {current_user.id} (email: {current_user.email})")
    logger.info(f"[API] Sync parameters: use_current_date={use_current_date}, force_full_sync={force_full_sync}")
    
    try:
        # Store the original token for comparison later
        original_token = current_user.credentials.get('token') if current_user.credentials else None
        
        # Use the optimized sync service
        start_time = datetime.now()
        logger.info(f"[API] Starting sync process at {start_time.isoformat()}")
        
        result = await sync_emails_since_last_fetch(
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
        
        # Insert SyncDetails record
        sync_details = SyncDetails(
            user_id=current_user.id,
            account_email=current_user.email,
            direction=SyncDirection.GMAIL_TO_EA,  # or infer from context
            sync_type=SyncType.MANUAL,  # or infer if automatic
            sync_started_at=start_time,
            sync_completed_at=end_time,
            duration_sec=duration,
            status=SyncStatus.SUCCESS if result.get("status") == "success" else SyncStatus.ERROR,
            error_message=result.get("message") if result.get("status") == "error" else None,
            emails_synced=result.get("sync_count", 0),
            changes_detected=result.get("changes_detected", 0),
            changes_applied=result.get("changes_applied", 0),
            pending_ea_changes=result.get("pending_ea_changes", []),
            backend_version="v1.2.3",  # or use a version constant
            data_freshness_sec=60  # or calculate if available
        )
        db.add(sync_details)
        db.commit()
        
        # Find new emails for display (if any were synced)
        if result.get("new_email_count", 0) > 0:
            page_size = 20  # Number of emails to show on the first page
            emails = db.query(Email).filter(
                Email.user_id == current_user.id,
                ~Email.labels.contains(['TRASH'])
            ).order_by(Email.received_at.desc()).limit(page_size).all()
            
            if emails:
                logger.info(f"[API] Found {len(emails)} emails for page 1 (total: {result.get('new_email_count', 0) + result.get('deleted_email_count', 0)})")
            
        return result
    except Exception as e:
        logger.error(f"[API] Error syncing emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync emails: {str(e)}"
        )

@router.post("/sync/fresh")
async def sync_fresh_emails(
    days_back: int = 3,
    max_emails: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Force a fresh sync grabbing recent emails efficiently 
    
    This endpoint first attempts to use the historyId approach for optimal efficiency
    and falls back to date-based queries only when necessary.
    
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
        
        # Get existing Gmail IDs to filter out already processed emails
        existing_gmail_ids = db.query(Email.gmail_id).filter(
            Email.user_id == current_user.id
        ).all()
        existing_gmail_ids = set([id[0] for id in existing_gmail_ids]) 
        logger.info(f"[API] Found {len(existing_gmail_ids)} existing emails in database")
        
        # Try to get the user's last history ID (if available)
        email_sync = db.query(EmailSync).filter(EmailSync.user_id == current_user.id).first()
        history_id = email_sync.last_history_id if email_sync else None
        
        # Try different sync strategies based on available data
        emails = []
        sync_method = "query"
        
        # First try using history ID if available
        if history_id:
            logger.info(f"[API] Attempting sync using history ID: {history_id}")
            try:
                # Use the history approach first if we have a history ID
                new_emails_raw, _, _, new_history_id = gmail.sync_gmail_changes(
                    current_user.credentials, 
                    history_id
                )
                
                if new_emails_raw:
                    logger.info(f"[API] Successfully retrieved {len(new_emails_raw)} emails using history ID")
                    emails = new_emails_raw
                    sync_method = "history"
                    
                    # Update the history ID in the database
                    if new_history_id and new_history_id != history_id:
                        email_sync.last_history_id = new_history_id
                        db.commit()
                        logger.info(f"[API] Updated history ID from {history_id} to {new_history_id}")
                else:
                    logger.info(f"[API] No new emails found using history ID")
            except Exception as e:
                logger.warning(f"[API] Error using history ID: {str(e)}")
                # Fall back to query approach
        
        # If history approach didn't work or found no emails, try query approach
        if not emails:
            # Create a date-based query that looks back a specific number of days
            past_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
            query = f"after:{past_date} in:inbox"
            logger.info(f"[API] Using query approach with: '{query}'")
            
            # Fetch emails from Gmail with the specified query
            emails = gmail.fetch_emails_from_gmail(
                current_user.credentials, 
                max_results=max_emails,
                query=query
            )
            sync_method = "query"
        
        if not emails:
            logger.info(f"[API] No emails found with {sync_method} approach")
            return {
                "status": "success",
                "message": "No emails found",
                "emails_synced": 0,
                "sync_method": sync_method
            }
        
        logger.info(f"[API] Retrieved {len(emails)} emails from Gmail API using {sync_method} approach")
        
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
                "emails_synced": 0,
                "sync_method": sync_method
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
            "emails_synced": len(processed_emails),
            "sync_method": sync_method
        }
            
    except Exception as e:
        logger.error(f"[API] Error in fresh sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync fresh emails: {str(e)}"
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
    page: int = 1,
    limit: int = 20,
    folder: Optional[str] = None,
    important: Optional[bool] = None,
    read_status: Optional[bool] = None,
    sort_by: str = "received_at",
    sort_order: str = "desc",
    query: Optional[str] = None,
    label: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    update_read_status: bool = False,
    show_all: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's emails with flexible filtering and sorting
    
    Parameters:
    - page: Page number (starting from 1)
    - limit: Number of emails per page
    - folder: Filter by folder (inbox, sent, etc.)
    - important: Filter by importance flag
    - read_status: Filter by read status (true/false)
    - sort_by: Field to sort by (received_at, importance_score, etc.)
    - sort_order: Sort direction (asc/desc)
    - query: Search query for subject and snippet
    - label: Filter by specific label
    - category: Filter emails by category
    - date_from: Filter emails received after this date (ISO format: YYYY-MM-DD)
    - date_to: Filter emails received before this date (ISO format: YYYY-MM-DD)
    - update_read_status: Whether to mark returned emails as read
    - show_all: Whether to include all emails (including Trash and Archive)
    
    Returns paginated results with metadata
    """
    # Validate parameters
    if limit <= 0:
        limit = 20
    
    if page <= 0:
        page = 1
        
    # Parse date parameters if provided
    parsed_date_from = None
    parsed_date_to = None
    
    if date_from:
        try:
            parsed_date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            logger.warning(f"Invalid date_from format: {date_from}")
    
    if date_to:
        try:
            parsed_date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            logger.warning(f"Invalid date_to format: {date_to}")
    
    # Build the query
    query_obj = db.query(Email).filter(Email.user_id == current_user.id)
    
    # Apply date filters if parsed successfully
    if parsed_date_from:
        query_obj = query_obj.filter(Email.received_at >= parsed_date_from)
    
    if parsed_date_to:
        query_obj = query_obj.filter(Email.received_at <= parsed_date_to)

    # Determine folder logic
    folder = (folder or '').lower() if folder else None
    is_trash_view = category and category.lower() == 'trash'
    is_archive_view = category and category.lower() == 'archive'
    is_all_mails_view = folder == 'all' or (category and category.lower() == 'all')
    is_inbox_view = folder == 'inbox' or (category and category.lower() == 'inbox')

    if show_all:
        # Include all emails when show_all is true
        pass
    elif is_trash_view:
        # Trash: category = 'trash' OR 'TRASH' in labels
        query_obj = query_obj.filter(
            or_(
                Email.category == 'trash',
                Email.labels.contains(['TRASH'])
            )
        )
    elif is_archive_view:
        # Archive: category = 'archive'
        query_obj = query_obj.filter(Email.category == 'archive')
    elif is_all_mails_view:
        # All Mails: everything except Trash
        query_obj = query_obj.filter(
            and_(
                Email.category != 'trash',
                ~Email.labels.contains(['TRASH'])
            )
        )
    elif is_inbox_view:
        # Inbox: everything except Trash and Archive
        query_obj = query_obj.filter(
            and_(
                Email.category != 'trash',
                Email.category != 'archive',
                ~Email.labels.contains(['TRASH'])
            )
        )
    elif category:
        # For other categories, show emails where category matches and not in trash
        query_obj = query_obj.filter(
            and_(
                Email.category == category,
                Email.category != 'trash',
                ~Email.labels.contains(['TRASH'])
            )
        )
    else:
        # Default: exclude emails in trash
        query_obj = query_obj.filter(~Email.labels.contains(['TRASH']))
    
    if important is not None:
        query_obj = query_obj.filter(Email.importance_score >= 70 if important else Email.importance_score < 70)
    
    if read_status is not None:
        query_obj = query_obj.filter(Email.is_read == read_status)
    
    if query:
        search_term = f"%{query}%"
        query_obj = query_obj.filter(
            or_(
                Email.subject.ilike(search_term),
                Email.snippet.ilike(search_term),
                Email.from_email.ilike(search_term)
            )
        )
    
    # Apply label filter except for the special trash case handled above
    if label and not (is_trash_view and label == 'TRASH'):
        query_obj = query_obj.filter(Email.labels.contains([label]))
    
    # Get total count for pagination metadata
    total_count = query_obj.count()
    
    # Calculate offset
    offset = (page - 1) * limit
    
    # Get emails for current page
    emails = query_obj.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    
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

@router.get("/deleted")
async def get_deleted_emails(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get emails that are in the Trash (have the TRASH label)
    
    Args:
        page: Page number (1-indexed)
        limit: Number of emails per page
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of emails with pagination metadata
    """
    # Validate parameters
    if limit <= 0:
        limit = 20
    
    if page <= 0:
        page = 1
        
    # Calculate offset
    offset = (page - 1) * limit
        
    # Specifically query for emails that have the TRASH label
    query = db.query(Email).filter(
        Email.user_id == current_user.id,
        Email.labels.contains(['TRASH'])
    )
    
    # Get total count for pagination metadata
    total_count = query.count()
    
    # Get emails for current page
    emails = query.order_by(Email.received_at.desc()).offset(offset).limit(limit).all()
    
    # Calculate pagination metadata
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_previous = page > 1
    
    logger.info(f"Found {len(emails)} trashed emails for page {page} (total: {total_count})")
    
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
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update email labels and add a flag for the next Gmail sync to apply the changes
    
    Args:
        email_id: UUID of the email to update
        request: Request with add_labels and remove_labels arrays
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Status message and updated labels
    """
    try:
        # Get request body
        body = await request.json()
        add_labels = body.get('add_labels', [])
        remove_labels = body.get('remove_labels', [])
        
        logger.info(f"[API] Updating labels for email {email_id}: adding {add_labels}, removing {remove_labels}")
        
        # Find the email
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get current labels and convert to set for easy manipulation
        current_labels = set(email.labels or [])
        
        # Add new labels
        for label in add_labels:
            current_labels.add(label)
            logger.info(f"[API] Added label {label} to email {email_id}")
        
        # Remove labels
        for label in remove_labels:
            if label in current_labels:
                current_labels.remove(label)
                logger.info(f"[API] Removed label {label} from email {email_id}")
        
        # Update email with new labels
        email.labels = list(current_labels)
        
        # Add a needs_label_update flag - this will be used during sync to apply changes to Gmail
        current_labels.add("EA_NEEDS_LABEL_UPDATE")
        email.labels = list(current_labels)
        
        # Special handling for TRASH label
        if 'TRASH' in add_labels and email.category != 'trash':
            # If adding TRASH label, set category to trash
            email.category = 'trash'
            logger.info(f"[API] Updated category to 'trash' for email {email_id} because TRASH label was added")
            
            # Also remove INBOX label if present
            if 'INBOX' in current_labels:
                current_labels.remove('INBOX')
                email.labels = list(current_labels)
                logger.info(f"[API] Removed INBOX label from email {email_id} because it's being moved to trash")
        
        # If removing TRASH label and category is trash, update the category to primary
        if 'TRASH' in remove_labels and email.category == 'trash':
            email.category = 'primary'
            logger.info(f"[API] Updated category from 'trash' to 'primary' for email {email_id} because TRASH label was removed")
        
        # Special handling for UNREAD label (read status)
        # Update the is_read flag based on UNREAD label presence
        if 'UNREAD' in add_labels:
            email.is_read = False
            logger.info(f"[API] Marked email {email_id} as unread")
        elif 'UNREAD' in remove_labels:
            email.is_read = True
            logger.info(f"[API] Marked email {email_id} as read")
        
        # Create an operation to sync the label changes to Gmail
        operation_data = {
            "add_labels": add_labels,
            "remove_labels": remove_labels
        }
        
        email_operations_service.create_operation(
            db=db,
            user=current_user,
            email=email,
            operation_type=OperationType.UPDATE_LABELS,
            operation_data=operation_data
        )
        
        logger.info(f"[API] Created label update operation for email {email_id}")
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Labels updated successfully. Changes will sync to Gmail during next email sync.",
            "email_id": str(email.id),
            "labels": email.labels
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[API] Error updating labels: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update labels: {str(e)}"
        )

@router.post("/{email_id}/update-category")
async def update_category_endpoint(
    email_id: UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the category of an email in the database and store feedback for learning
    
    Args:
        email_id: UUID of the email to update
        category_data: New category information
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated email information
        
    Notes:
        - category: New category for the email (primary, social, promotions, updates, forums, personal, trash)
    """
    try:
        category = category_data.category
        logger.info(f"[API] Updating category for email {email_id} to {category}")
        
        # Find the email
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get valid categories from database
        valid_categories = [
            cat.name for cat in db.query(EmailCategory).filter(
                or_(
                    EmailCategory.is_system == True,
                    and_(
                        EmailCategory.is_system == False,
                        # TODO: Add user ownership check once implemented
                    )
                )
            ).all()
        ]
        
        normalized_category = category.lower()
        
        if normalized_category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        # Update the category and labels using the unified utility
        category_changed = set_email_category_and_labels(email, normalized_category)

        # Add a needs_label_update flag if we changed category - this will be used during sync
        if category_changed:
            current_labels = set(email.labels or [])
            current_labels.add("EA_NEEDS_LABEL_UPDATE")
            email.labels = list(current_labels)

            # Always create a sync operation for Gmail
            operation_data = {}
            if normalized_category == 'trash':
                operation_data["add_labels"] = ["TRASH"]
                if 'INBOX' in current_labels:
                    operation_data["remove_labels"] = ["INBOX"]
                email_operations_service.create_operation(
                    db=db,
                    user=current_user,
                    email=email,
                    operation_type=OperationType.TRASH,
                    operation_data=operation_data
                )
            elif normalized_category == 'archive':
                operation_data["remove_labels"] = ["INBOX", "TRASH"]
                email_operations_service.create_operation(
                    db=db,
                    user=current_user,
                    email=email,
                    operation_type=OperationType.UPDATE_CATEGORY,
                    operation_data=operation_data
                )
            else:
                operation_data["add_labels"] = ["INBOX"]
                operation_data["remove_labels"] = ["TRASH"]
                email_operations_service.create_operation(
                    db=db,
                    user=current_user,
                    email=email,
                    operation_type=OperationType.UPDATE_CATEGORY,
                    operation_data=operation_data
                )

        db.commit()
        
        return {
            "status": "success",
            "message": "Category updated successfully. Changes will sync to Gmail during next email sync.",
            "email_id": str(email.id),
            "category": normalized_category,
            "labels": email.labels
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[API] Error updating category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update category: {str(e)}"
        )

@router.delete("/{email_id}")
async def delete_email(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Move an email to trash by adding the TRASH label and setting category to 'trash'
    
    Args:
        email_id: UUID of the email to move to trash
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Status message and updated email information
    """
    try:
        logger.info(f"[API] Moving email {email_id} to trash")
        
        # Find the email
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get current labels and convert to set for easy manipulation
        current_labels = set(email.labels or [])
        
        # Add TRASH label if not already present
        if 'TRASH' not in current_labels:
            current_labels.add('TRASH')
        
        # Remove INBOX label if present
        if 'INBOX' in current_labels:
            current_labels.remove('INBOX')
        
        # Update email with new labels
        email.labels = list(current_labels)
        
        # Set category to trash
        email.category = 'trash'
        
        # Add a needs_label_update flag - this will be used during sync to apply changes to Gmail
        current_labels.add("EA_NEEDS_LABEL_UPDATE")
        email.labels = list(current_labels)
        
        # Create operation record for Gmail sync
        operation_data = {
            "add_labels": ["TRASH"],
            "remove_labels": ["INBOX"] if 'INBOX' in email.labels else []
        }
        
        email_operations_service.create_operation(
            db=db,
            user=current_user,
            email=email,
            operation_type=OperationType.TRASH,
            operation_data=operation_data
        )
        
        logger.info(f"[API] Created trash operation for email {email_id}")
        
        # Record the trash event for potential classifier training
        trash_event = EmailTrashEvent(
            user_id=current_user.id,
            email_id=email.id,
            sender_email=email.from_email,
            sender_domain=email.from_email.split('@')[-1] if '@' in email.from_email else '',
            subject=email.subject,
            snippet=email.snippet,
            event_type='moved_to_trash',
            email_metadata={
                "category": email.category,
                "labels": email.labels
            },
            created_at=datetime.utcnow()
        )
        db.add(trash_event)
        logger.info(f"[API] Created trash event record for email {email_id}")
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Email moved to trash. Changes will sync to Gmail during next email sync.",
            "email_id": str(email.id),
            "labels": email.labels,
            "category": email.category
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[API] Error moving email to trash: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to move email to trash: {str(e)}"
        )

@router.post("/{email_id}/archive")
async def archive_email_endpoint(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archive or unarchive an email
    
    If the email has the INBOX label, it will be archived (INBOX label removed)
    If the email doesn't have the INBOX label, it will be unarchived (INBOX label added)
    """
    try:
        logger.info(f"[API] Archive/unarchive request for email {email_id}")
        
        # Find the email
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Check if email has INBOX label
        current_labels = set(email.labels or [])
        is_in_inbox = 'INBOX' in current_labels
        
        operation_data = {}
        
        if is_in_inbox:
            # Archive: Remove INBOX label
            current_labels.remove('INBOX')
            email.labels = list(current_labels)
            
            # Get archive category from database
            archive_category = db.query(EmailCategory).filter(
                EmailCategory.name == 'archive',
                EmailCategory.is_system == True
            ).first()
            
            if archive_category:
                email.category = archive_category.name
            
            operation_data = {
                "remove_labels": ["INBOX"]
            }
            operation_type = OperationType.ARCHIVE
            message = "Email archived successfully"
            logger.info(f"[API] Removed INBOX label from email {email_id} and set category to 'archive'")
        else:
            # Unarchive: Add INBOX label
            current_labels.add('INBOX')
            email.labels = list(current_labels)
            
            # Get highest priority system category from database
            default_category = db.query(EmailCategory).filter(
                EmailCategory.is_system == True
            ).order_by(EmailCategory.priority).first()
            
            if default_category:
                email.category = default_category.name
            
            operation_data = {
                "add_labels": ["INBOX"]
            }
            operation_type = OperationType.UPDATE_LABELS
            message = "Email unarchived successfully"
            logger.info(f"[API] Added INBOX label to email {email_id} and set category to highest priority category")
        
        # Create operation record for Gmail sync
        email_operations_service.create_operation(
            db=db,
            user=current_user,
            email=email,
            operation_type=operation_type,
            operation_data=operation_data
        )
        
        logger.info(f"[API] Created {'archive' if is_in_inbox else 'unarchive'} operation for email {email_id}")
        
        db.commit()
        
        return {
            "status": "success",
            "message": message,
            "labels": email.labels,
            "category": email.category
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[API] Error archiving/unarchiving email: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to archive/unarchive email: {str(e)}")

@router.post("/empty-trash")
async def empty_trash(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permanently delete all emails in the trash for the current user
    """
    try:
        # Find all emails with TRASH label for the current user
        trash_emails = db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.labels.contains(['TRASH'])
        ).all()
        
        # Count how many emails will be deleted
        delete_count = len(trash_emails)
        
        if delete_count == 0:
            return {
                "success": True,
                "message": "Trash is already empty",
                "deleted_count": 0
            }
        
        # Delete all trash emails
        db.query(Email).filter(
            Email.user_id == current_user.id,
            Email.labels.contains(['TRASH'])
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"[API] Permanently deleted {delete_count} emails from trash for user {current_user.id}")
        
        return {
            "success": True,
            "message": f"Permanently deleted {delete_count} emails from trash",
            "deleted_count": delete_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"[API] Error emptying trash: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to empty trash: {str(e)}"
        ) 