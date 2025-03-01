from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.email_sync import EmailSync
from ..models.email import Email
from .gmail import fetch_emails_from_gmail, sync_gmail_changes, check_deleted_emails, update_email_labels
from .email_processor import process_and_store_emails
import logging

logger = logging.getLogger(__name__)

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
    Sync emails from Gmail since the last fetch time using Gmail's historyId for efficiency
    
    Args:
        db: Database session
        user: User model instance
        use_current_date: If true, use the current date for checkpoint instead of treating it as next day
        force_full_sync: If true, uses a much broader date range (7 days) to force a more complete sync
        
    Returns:
        Dictionary with sync results
    """
    start_time = datetime.now(timezone.utc)
    try:
        # Get or create email sync record
        email_sync = get_or_create_email_sync(db, user)
        last_fetched_at = email_sync.last_fetched_at
        last_history_id = email_sync.last_history_id
        
        # Current time with UTC timezone
        now = datetime.now(timezone.utc)
        
        # If force_full_sync is true, set the last_fetched_at to 7 days ago and clear history_id
        if force_full_sync:
            logger.info(f"[SYNC] Force full sync requested, setting checkpoint to 7 days ago")
            last_fetched_at = now - timedelta(days=7)
            last_history_id = None  # Don't use history ID for forced syncs
        
        # Get local time for logging
        local_time = datetime.now()
        logger.info(f"[SYNC] Starting email sync for user {user.id} (email: {user.email})")
        logger.info(f"[SYNC] Current local time: {local_time.isoformat()}")
        logger.info(f"[SYNC] Last checkpoint (UTC): {last_fetched_at.isoformat()} (use_current_date: {use_current_date}, force_full_sync: {force_full_sync})")
        
        # Get the list of already processed email IDs to filter them out
        existing_gmail_ids = db.query(Email.gmail_id).filter(
            Email.user_id == user.id
        ).all()
        existing_gmail_ids = set([id[0] for id in existing_gmail_ids])
        logger.info(f"[SYNC] Found {len(existing_gmail_ids)} already processed emails in database")
        
        # Initialize sync variables
        new_emails = []
        deleted_email_ids = []
        new_history_id = None
        label_changes_count = 0
        sync_method = "history"
        
        # Primary Strategy: Use history-based approach if we have a history ID and not forcing full sync
        if last_history_id and not force_full_sync:
            logger.info(f"[SYNC] Using history-based approach with history ID: {last_history_id}")
            try:
                # Use the sync_gmail_changes function to efficiently fetch changes since last history ID
                new_emails_raw, deleted_ids, label_changes, new_history_id = sync_gmail_changes(user.credentials, last_history_id)
                
                # If we got a valid history ID back, process the results
                if new_history_id and new_history_id != last_history_id:
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
                    logger.warning(f"[SYNC] History-based sync did not produce a new history ID. Will fallback to label-based sync.")
                    sync_method = "fallback"
            except Exception as e:
                error_msg = str(e)
                if "Invalid startHistoryId" in error_msg or "Start history ID is too old" in error_msg:
                    logger.warning(f"[SYNC] History ID {last_history_id} is invalid or too old: {error_msg}")
                    # Clear the history ID for next time
                    last_history_id = None
                    # Update the sync record with null history ID
                    email_sync.last_history_id = None
                    db.commit()
                else:
                    logger.error(f"[SYNC] Error using history-based approach: {error_msg}", exc_info=True)
                
                # Use fallback approach
                sync_method = "fallback"
        else:
            sync_method = "fallback" if not last_history_id else "full_sync"
        
        # Fallback Strategy / Full Sync Strategy: Use label approach as fallback
        if sync_method in ["fallback", "full_sync"]:
            logger.info(f"[SYNC] Using {sync_method} approach")
            
            # Determine how many emails to fetch
            max_results = 500 if force_full_sync else 100
            logger.info(f"[SYNC] Fetching up to {max_results} emails with INBOX label")
            
            try:
                # Get the latest emails from INBOX or other relevant labels
                inbox_emails = fetch_emails_from_gmail(
                    user.credentials,
                    max_results=max_results,
                    query=None  # We'll use the default INBOX label
                )
                
                # Filter by date if we're not doing a force_full_sync
                date_filtered_emails = []
                if not force_full_sync:
                    # Filter out emails older than the last_fetched_at timestamp
                    for email in inbox_emails:
                        # Convert to datetime for comparison (required because received_at can be a string in some cases)
                        received_at = email['received_at'] if isinstance(email['received_at'], datetime) else datetime.fromisoformat(email['received_at'])
                        
                        # Convert to UTC timezone if not already set
                        if received_at.tzinfo is None:
                            received_at = received_at.replace(tzinfo=timezone.utc)
                            
                        # Include the email if it's newer than the last fetch timestamp
                        if received_at >= last_fetched_at:
                            date_filtered_emails.append(email)
                else:
                    # For forced full sync, include all emails
                    date_filtered_emails = inbox_emails
                
                logger.info(f"[SYNC] Retrieved {len(inbox_emails)} emails, filtered to {len(date_filtered_emails)} by date criteria")
                
                # Filter out emails that already exist in our database
                for email in date_filtered_emails:
                    if email['gmail_id'] not in existing_gmail_ids:
                        new_emails.append(email)
                
                logger.info(f"[SYNC] After filtering, {len(new_emails)} new emails remain for processing (filtered out {len(date_filtered_emails) - len(new_emails)} already processed)")
                
                # Check for deleted emails if we have a significant number of emails in database
                if len(existing_gmail_ids) > 0:
                    logger.info(f"[SYNC] Checking sample of existing emails for deletions")
                    
                    # Check if emails have been deleted from Gmail
                    # Start with a small sample to avoid unnecessary API calls if no deletions
                    deleted_email_gmail_ids = {}
                    
                    try:
                        # If we have many emails, check a sample first
                        if len(existing_gmail_ids) > 50:
                            # Take a small sample of the oldest emails first (most likely to be deleted)
                            sample_size = 5
                            sample_emails = db.query(Email).filter(
                                Email.user_id == user.id,
                                Email.gmail_id.in_(existing_gmail_ids)
                            ).order_by(Email.received_at).limit(sample_size).all()
                            
                            sample_gmail_ids = [email.gmail_id for email in sample_emails]
                            logger.info(f"[GMAIL] Large number of emails ({len(existing_gmail_ids)}), checking sample of {sample_size} first")
                            
                            sample_deleted = check_deleted_emails(user.credentials, sample_gmail_ids)
                            sample_deleted_count = sum(1 for is_deleted in sample_deleted.values() if is_deleted)
                            
                            # If we found deleted emails in the sample, check all emails
                            if sample_deleted_count > 0:
                                logger.info(f"[GMAIL] Found {sample_deleted_count} deleted emails in sample, checking all {len(existing_gmail_ids)} emails")
                                deleted_email_gmail_ids = check_deleted_emails(user.credentials, list(existing_gmail_ids), force_full_check=True)
                            else:
                                logger.info(f"[GMAIL] No deletions found in sample, skipping full check of {len(existing_gmail_ids)} emails")
                                deleted_email_gmail_ids = sample_deleted
                        else:
                            # For a small number of emails, check them all directly
                            deleted_email_gmail_ids = check_deleted_emails(user.credentials, list(existing_gmail_ids))
                        
                        # Process deletions
                        for gmail_id, is_deleted in deleted_email_gmail_ids.items():
                            if is_deleted:
                                deleted_email_ids.append(gmail_id)
                        
                        logger.info(f"[SYNC] Found {len(deleted_email_ids)} deleted emails")
                        
                    except Exception as e:
                        logger.error(f"[SYNC] Error checking for deleted emails: {str(e)}", exc_info=True)
                        # Continue with the sync, just without deletions
            except Exception as e:
                logger.error(f"[SYNC] Error in fallback sync approach: {str(e)}", exc_info=True)
                # Return error since both primary and fallback methods failed
                return {
                    "status": "error", 
                    "message": f"Email sync failed: {str(e)}",
                    "sync_count": 0
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
            for gmail_id in deleted_email_ids:
                # Find the email in our database
                email = db.query(Email).filter(
                    Email.user_id == user.id,
                    Email.gmail_id == gmail_id
                ).first()
                
                if email and not email.is_deleted_in_gmail:
                    email.is_deleted_in_gmail = True
                    deleted_count += 1
            
            if deleted_count > 0:
                db.commit()
                logger.info(f"[SYNC] Marked {deleted_count} emails as deleted")
        
        # Find the latest timestamp from the processed emails to use as the new checkpoint
        latest_timestamp = start_time  # Default to the start time
        if processed_emails:
            # Find the maximum received_at time
            latest_received = max(email.received_at for email in processed_emails)
            if latest_received > latest_timestamp:
                latest_timestamp = latest_received
                logger.info(f"[SYNC] Found latest timestamp: {latest_timestamp.isoformat()}")
        
        # Update the sync checkpoint with new timestamp and possibly new history_id
        update_sync_checkpoint(db, email_sync, latest_timestamp, new_history_id)
        
        logger.info(f"[SYNC] Updated checkpoint from {last_fetched_at.isoformat()} to {latest_timestamp.isoformat()}")
        
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
            "sync_method": sync_method
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