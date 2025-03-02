from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.email_sync import EmailSync
from ..models.email import Email
from . import gmail
from .email_processor import process_and_store_emails
import logging

logger = logging.getLogger(__name__)

# Let's define a local reference to create_gmail_service to ensure it's available
gmail_service_creator = gmail.create_gmail_service

def get_or_create_email_sync(db: Session, user: User) -> EmailSync:
    """
    Get the user's email sync record or create a new one if it doesn't exist
    
    Args:
        db: Database session
        user: User model instance
        
    Returns:
        EmailSync model instance
    """
    # Check if user already has a sync record
    if user.email_sync:
        return user.email_sync
    
    # Create new sync record with default values - use UTC time
    email_sync = EmailSync(
        user_id=user.id,
        last_fetched_at=datetime.now(timezone.utc) - timedelta(days=1),  # Default to 1 day ago
        last_history_id=None  # Initialize with no history ID
    )
    
    db.add(email_sync)
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

def update_sync_checkpoint(
    db: Session, 
    email_sync: EmailSync, 
    new_timestamp: datetime,
    new_history_id: Optional[str] = None
) -> EmailSync:
    """
    Update the sync checkpoint (last_fetched_at and last_history_id) in the email_sync record
    
    Args:
        db: Database session
        email_sync: EmailSync model instance
        new_timestamp: New timestamp to set
        new_history_id: New history ID to set (optional)
        
    Returns:
        Updated EmailSync model instance
    """
    # Ensure the timestamp has timezone info
    if new_timestamp.tzinfo is None:
        new_timestamp = new_timestamp.replace(tzinfo=timezone.utc)
        
    logger.info(f"[SYNC] Updating last_fetched_at to {new_timestamp}")
    email_sync.last_fetched_at = new_timestamp
    
    # Update history ID if provided
    if new_history_id:
        logger.info(f"[SYNC] Updating last_history_id to {new_history_id}")
        email_sync.last_history_id = new_history_id
    
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

def process_label_changes(db: Session, user: User, label_changes: Dict[str, Dict[str, List[str]]]) -> int:
    """
    Process label changes from Gmail and update email records accordingly
    
    Args:
        db: Database session
        user: User model instance
        label_changes: Dictionary of message IDs to label changes {'added': [], 'removed': []}
        
    Returns:
        Number of emails updated
    """
    if not label_changes:
        return 0
        
    logger.info(f"[SYNC] Processing label changes for {len(label_changes)} emails")
    updated_count = 0
    
    for gmail_id, changes in label_changes.items():
        # Look up the email in our database
        email = db.query(Email).filter(
            Email.user_id == user.id,
            Email.gmail_id == gmail_id
        ).first()
        
        if not email:
            logger.debug(f"[SYNC] Email {gmail_id} not found in database, skipping label update")
            continue
            
        # Check for Trash label to mark as deleted
        if 'TRASH' in changes.get('added', []):
            logger.info(f"[SYNC] Email {gmail_id} moved to Trash, marking as deleted")
            email.is_deleted_in_gmail = True
            updated_count += 1
            
        # Update read status
        if 'UNREAD' in changes.get('added', []):
            logger.debug(f"[SYNC] Email {gmail_id} marked as unread")
            email.is_read = False
            updated_count += 1
        elif 'UNREAD' in changes.get('removed', []):
            logger.debug(f"[SYNC] Email {gmail_id} marked as read")
            email.is_read = True
            updated_count += 1
            
        # We could handle more label types here if needed
        # For example INBOX, SPAM, CATEGORY_SOCIAL, etc.
    
    if updated_count > 0:
        db.commit()
        logger.info(f"[SYNC] Updated {updated_count} emails due to label changes")
        
    return updated_count

def sync_emails_since_last_fetch(db: Session, user: User, use_current_date: bool = False, force_full_sync: bool = False) -> Dict[str, Any]:
    """
    Sync emails from Gmail using only the historyId approach for efficiency
    
    Args:
        db: Database session
        user: User model instance
        use_current_date: If true, use current date for checkpoint
        force_full_sync: If true, forces a full sync by setting a new history ID
        
    Returns:
        Dictionary with sync results
    """
    start_time = datetime.now(timezone.utc)
    try:
        # Get or create email sync record
        email_sync = get_or_create_email_sync(db, user)
        
        # Log sync parameters
        logger.info(f"[SYNC] Starting email sync for user {user.id} (email: {user.email})")
        logger.info(f'last_fetched_at: {email_sync.last_fetched_at}')
        logger.info(f'last_history_id: {email_sync.last_history_id}')
        logger.info(f'use_current_date: {use_current_date}')
        logger.info(f'force_full_sync: {force_full_sync}')
        logger.info(f"[SYNC] Current local time: {datetime.now().isoformat()}")
        
        # Initialize sync variables
        new_emails = []
        deleted_email_ids = []
        label_changes_count = 0
        new_history_id = None
        
        # For force_full_sync, we need to get a new history ID
        if force_full_sync or not email_sync.last_history_id:
            # Get a fresh history ID by fetching the latest message
            try:
                # Create Gmail service
                service = gmail_service_creator(user.credentials)
                
                # Get the latest message to get its history ID
                logger.info("[SYNC] Force full sync or no history ID - fetching latest message for new history ID")
                
                # Get the latest message
                result = service.users().messages().list(
                    userId='me', 
                    maxResults=1,
                    q="in:inbox"
                ).execute()
                
                if 'messages' in result and len(result['messages']) > 0:
                    latest_msg_id = result['messages'][0]['id']
                    
                    # Get the message to retrieve its history ID
                    msg = service.users().messages().get(
                        userId='me',
                        id=latest_msg_id,
                        format='minimal'
                    ).execute()
                    
                    # Set the new history ID 
                    new_history_id = msg.get('historyId')
                    logger.info(f"[SYNC] Obtained new history ID: {new_history_id}")
                    
                    # Update the sync checkpoint without processing any emails
                    update_sync_checkpoint(db, email_sync, start_time, new_history_id)
                    
                    return {
                        "status": "success",
                        "message": f"Initialized with new history ID: {new_history_id}",
                        "sync_count": 0,
                        "new_email_count": 0,
                        "deleted_email_count": 0,
                        "label_changes_count": 0,
                        "sync_started_at": start_time.isoformat(),
                        "user_id": str(user.id),
                        "sync_method": "init_history_id"
                    }
                else:
                    logger.warning("[SYNC] No messages found in inbox to obtain history ID")
                    return {
                        "status": "warning",
                        "message": "No messages found in inbox to obtain history ID",
                        "sync_count": 0,
                        "sync_started_at": start_time.isoformat(),
                        "user_id": str(user.id),
                        "sync_method": "history_init_failed"
                    }
            except Exception as e:
                logger.error(f"[SYNC] Error getting new history ID: {str(e)}", exc_info=True)
                return {
                    "status": "error",
                    "message": f"Failed to get new history ID: {str(e)}",
                    "sync_count": 0,
                    "sync_started_at": start_time.isoformat(),
                    "user_id": str(user.id),
                    "sync_method": "error"
                }
        
        # Get the list of already processed email IDs to filter them out
        existing_gmail_ids = db.query(Email.gmail_id).filter(
            Email.user_id == user.id
        ).all()
        existing_gmail_ids = set([id[0] for id in existing_gmail_ids])
        logger.info(f"[SYNC] Found {len(existing_gmail_ids)} already processed emails in database")
        
        # Use history-based approach with existing history ID
        logger.info(f"[SYNC] Using history-based approach with history ID: {email_sync.last_history_id}")
        try:
            # Use the sync_gmail_changes function to efficiently fetch changes since last history ID
            new_emails_raw, deleted_ids, label_changes, new_history_id = gmail.sync_gmail_changes(
                user.credentials,
                email_sync.last_history_id
            )
            
            # If we got a valid history ID back, process the results
            if new_history_id and new_history_id != email_sync.last_history_id:
                logger.info(f"[SYNC] History-based sync successful with new history ID: {new_history_id}")
                
                # Track total emails found vs filtered
                total_found = len(new_emails_raw)
                already_processed = 0
                
                # Filter out emails that have already been processed
                for email in new_emails_raw:
                    if email['gmail_id'] not in existing_gmail_ids:
                        new_emails.append(email)
                    else:
                        already_processed += 1
                        logger.debug(f"[SYNC] Skipping already processed email: {email['gmail_id']}")
                
                deleted_email_ids = deleted_ids
                
                # Process label changes (mark as read/unread, deleted, etc.)
                label_changes_count = process_label_changes(db, user, label_changes)
                
                logger.info(f"[SYNC] History-based sync found {total_found} emails, of which {already_processed} already processed and {len(new_emails)} are new")
                logger.info(f"[SYNC] Found {len(deleted_email_ids)} deleted, {label_changes_count} label changes")
            else:
                logger.warning(f"[SYNC] History-based sync did not produce a new history ID.")
                return {
                    "status": "warning",
                    "message": "No changes detected since last sync",
                    "sync_count": 0,
                    "sync_started_at": start_time.isoformat(),
                    "user_id": str(user.id),
                    "sync_method": "history_no_changes"
                }
        except Exception as e:
            error_msg = str(e)
            if "Invalid startHistoryId" in error_msg or "Start history ID is too old" in error_msg:
                logger.warning(f"[SYNC] History ID {email_sync.last_history_id} is invalid or too old: {error_msg}")
                # Clear the history ID
                email_sync.last_history_id = None
                db.commit()
                return {
                    "status": "error", 
                    "message": f"History ID is invalid or too old, please retry to initialize a new history ID",
                    "sync_count": 0,
                    "sync_started_at": start_time.isoformat(),
                    "user_id": str(user.id),
                    "sync_method": "history_reset"
                }
            else:
                logger.error(f"[SYNC] Error using history-based approach: {error_msg}", exc_info=True)
                return {
                    "status": "error", 
                    "message": f"History sync error: {error_msg}",
                    "sync_count": 0,
                    "sync_started_at": start_time.isoformat(),
                    "user_id": str(user.id),
                    "sync_method": "error"
                }
        
        # Process and store the new emails
        processed_emails = []
        if new_emails:
            logger.info(f"[SYNC] Processing {len(new_emails)} new emails for user {user.id}")
            processed_emails = process_and_store_emails(db, user, new_emails)
            logger.info(f"[SYNC] Successfully processed and stored {len(processed_emails)} emails")
            
            # Log details of the synced emails for debugging
            for i, email in enumerate(processed_emails, 1):
                logger.info(f"[SYNC] Email {i}/{len(processed_emails)}: ID={email.id}, Subject='{email.subject[:30]}...', From={email.from_email}, Received={email.received_at}, Category={email.category}")
        
        # Process deleted emails
        if deleted_email_ids:
            logger.info(f"[SYNC] Marking {len(deleted_email_ids)} emails as deleted")
            deleted_count = 0
            not_found_count = 0
            already_deleted_count = 0
            
            # Log the first few deleted Gmail IDs for debugging
            if len(deleted_email_ids) > 0:
                sample_ids = deleted_email_ids[:min(5, len(deleted_email_ids))]
                logger.info(f"[SYNC] Sample deleted Gmail IDs: {sample_ids}")
            
            # Diagnostic query to check Gmail ID format in database
            db_email_sample = db.query(Email.gmail_id).filter(
                Email.user_id == user.id
            ).limit(5).all()
            db_gmail_ids = [email[0] for email in db_email_sample]
            logger.info(f"[SYNC] Database Gmail ID format sample: {db_gmail_ids}")
            
            # Check if any of the deleted emails exist in the database
            found_emails = db.query(Email).filter(
                Email.user_id == user.id,
                Email.gmail_id.in_(deleted_email_ids[:min(10, len(deleted_email_ids))])
            ).all()
            logger.info(f"[SYNC] Found {len(found_emails)} of the first {min(10, len(deleted_email_ids))} deleted emails in DB")
            
            # Show examples of both not found and found emails for comparison
            if found_emails:
                logger.info(f"[SYNC] Format of found Gmail IDs: {[email.gmail_id for email in found_emails[:3]]}")
            
            for gmail_id in deleted_email_ids:
                # Find the email in our database
                email = db.query(Email).filter(
                    Email.user_id == user.id,
                    Email.gmail_id == gmail_id
                ).first()
                
                if not email:
                    not_found_count += 1
                    if not_found_count <= 5:  # Log first 5 not found emails to avoid log spam
                        logger.debug(f"[SYNC] Email with gmail_id {gmail_id} not found in database")
                elif email.is_deleted_in_gmail:
                    already_deleted_count += 1
                    if already_deleted_count <= 5:  # Log first 5 already deleted emails
                        logger.debug(f"[SYNC] Email {email.id} (gmail_id: {gmail_id}) already marked as deleted")
                else:
                    logger.info(f"[SYNC] Marking email {email.id} (gmail_id: {gmail_id}) as deleted")
                    email.is_deleted_in_gmail = True
                    deleted_count += 1
            
            logger.info(f"[SYNC] Deletion summary before commit: deleted_count={deleted_count}, not_found_count={not_found_count}, already_deleted_count={already_deleted_count}")
            
            if deleted_count > 0:
                db.commit()
                logger.info(f"[SYNC] Marked {deleted_count} emails as deleted")
            else:
                logger.warning(f"[SYNC] No emails were marked as deleted despite finding {len(deleted_email_ids)} deleted emails")
                # Check if all emails were either not found or already deleted
                if not_found_count + already_deleted_count == len(deleted_email_ids):
                    logger.info(f"[SYNC] All deleted emails were either not found ({not_found_count}) or already marked as deleted ({already_deleted_count})")
                else:
                    logger.warning(f"[SYNC] Unexpected state: deleted_count=0 but not all emails accounted for in not_found or already_deleted")
            
            # Log summary of deleted email processing
            logger.info(f"[SYNC] Deleted emails summary: {deleted_count} marked as deleted, {not_found_count} not found in database, {already_deleted_count} already marked as deleted")
        
        # Update the sync checkpoint with new timestamp and the new history_id
        update_sync_checkpoint(db, email_sync, start_time, new_history_id)
        logger.info(f"[SYNC] Updated checkpoint from {email_sync.last_fetched_at.isoformat()} to {start_time.isoformat()}")
        
        # Return summary of the sync
        result = {
            "status": "success",
            "message": f"Processed {len(processed_emails)} new emails, {len(deleted_email_ids)} deleted emails, and {label_changes_count} label changes",
            "sync_count": len(processed_emails) + len(deleted_email_ids) + label_changes_count,
            "new_email_count": len(processed_emails),
            "deleted_email_count": len(deleted_email_ids),
            "label_changes_count": label_changes_count,
            "sync_started_at": start_time.isoformat(),
            "user_id": str(user.id),
            "sync_method": "history"
        }
        
        logger.info(f"[SYNC] Sync completed successfully: {result}")
        return result
    
    except Exception as e:
        logger.error(f"[SYNC] Unhandled error during email sync: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Email sync failed: {str(e)}",
            "sync_count": 0,
            "sync_started_at": start_time.isoformat(),
            "user_id": str(user.id) if user else None,
            "sync_method": "error"
        } 