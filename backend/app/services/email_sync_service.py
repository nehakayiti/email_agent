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
            email.is_deleted = True
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

def sync_emails_since_last_fetch(db: Session, user: User, use_current_date: bool = False) -> Dict[str, Any]:
    """
    Sync emails from Gmail since the last fetch time
    
    Args:
        db: Database session
        user: User model instance
        use_current_date: If true, use the current date for checkpoint instead of treating it as next day
        
    Returns:
        Dictionary with sync results
    """
    try:
        # Get or create email sync record
        email_sync = get_or_create_email_sync(db, user)
        last_fetched_at = email_sync.last_fetched_at
        last_history_id = email_sync.last_history_id
        
        # Check if the last_fetched_at is in the future (timezone issue)
        now = datetime.now(timezone.utc)
        if last_fetched_at > now:
            logger.warning(f"[SYNC] Last checkpoint date {last_fetched_at.isoformat()} is in the future! Resetting to current time.")
            last_fetched_at = now - timedelta(hours=1)  # Set to 1 hour ago to be safe
            update_sync_checkpoint(db, email_sync, last_fetched_at)
        
        # Get local time for logging
        local_time = datetime.now()
        logger.info(f"[SYNC] Starting email sync for user {user.id} (email: {user.email})")
        logger.info(f"[SYNC] Current local time: {local_time.isoformat()}")
        logger.info(f"[SYNC] Last checkpoint (UTC): {last_fetched_at.isoformat()} (use_current_date: {use_current_date})")
        
        # Get the list of already processed email IDs to filter them out
        existing_gmail_ids = db.query(Email.gmail_id).filter(
            Email.user_id == user.id
        ).all()
        existing_gmail_ids = set([id[0] for id in existing_gmail_ids])
        logger.info(f"[SYNC] Found {len(existing_gmail_ids)} already processed emails in database")
        
        # Determine sync strategy based on available data
        new_emails = []
        deleted_email_ids = []
        label_changes_count = 0
        new_history_id = None
        
        # If we have a history ID, use the history-based approach
        if last_history_id:
            logger.info(f"[SYNC] Using history-based approach with history ID: {last_history_id}")
            try:
                # Use the sync_gmail_changes function to efficiently fetch changes
                new_emails_raw, deleted_ids, label_changes, new_history_id = sync_gmail_changes(user.credentials, last_history_id)
                
                # Filter out emails that have already been processed
                for email in new_emails_raw:
                    if email['gmail_id'] not in existing_gmail_ids:
                        new_emails.append(email)
                        logger.debug(f"[SYNC] New email found: {email['gmail_id']} - {email['subject'][:30]}")
                    else:
                        logger.debug(f"[SYNC] Skipping already processed email: {email['gmail_id']}")
                
                deleted_email_ids = deleted_ids
                
                # Process label changes (mark as read/unread, deleted, etc.)
                label_changes_count = process_label_changes(db, user, label_changes)
                
                logger.info(f"[SYNC] History-based sync found {len(new_emails)} new, {len(deleted_email_ids)} deleted, {label_changes_count} label changes")
            except Exception as e:
                logger.error(f"[SYNC] Error using history-based approach: {str(e)}")
                # Fall back to traditional approach
                new_emails = []
                deleted_email_ids = []
                new_history_id = None
        
        # If history-based approach failed or we don't have a history ID, fall back to traditional approach
        if not new_history_id:
            logger.info(f"[SYNC] Using traditional approach with date-based query")
            
            # Get the most recent email ID from the database to use as a reference point
            most_recent_email = db.query(Email).filter(
                Email.user_id == user.id
            ).order_by(Email.received_at.desc()).first()
            
            # Format the date for the query - we still need a date filter as a baseline
            after_date = last_fetched_at.strftime('%Y/%m/%d')
            
            # Create a query that will find emails since our date
            query = f"after:{after_date}"
            
            # Fetch emails from Gmail with optimization
            if most_recent_email and most_recent_email.gmail_id:
                logger.info(f"[SYNC] Using reference email ID: {most_recent_email.gmail_id} from {most_recent_email.received_at.isoformat()}")
                # Use the historyId/pageToken approach to get only newer emails
                emails = fetch_emails_from_gmail(
                    user.credentials, 
                    query=query,
                    reference_email_id=most_recent_email.gmail_id
                )
            else:
                logger.info(f"[SYNC] No reference email found, fetching with date query: '{query}'")
                # No reference point, use the date query
                emails = fetch_emails_from_gmail(user.credentials, query=query)
            
            if emails:
                logger.info(f"[SYNC] Retrieved {len(emails)} emails from Gmail API")
                
                # Filter out emails that have already been processed
                for email in emails:
                    if email['gmail_id'] not in existing_gmail_ids:
                        new_emails.append(email)
                        logger.debug(f"[SYNC] New email found: {email['gmail_id']} - {email['subject'][:30]}")
                    else:
                        logger.debug(f"[SYNC] Skipping already processed email: {email['gmail_id']}")
                
                logger.info(f"[SYNC] After filtering, {len(new_emails)} new emails remain for processing")
                
                # Check for deleted emails (only if we have existing emails)
                if existing_gmail_ids:
                    # Check just a small sample to determine if a full scan is needed
                    logger.info(f"[SYNC] Checking sample of existing emails for deletions")
                    deleted_status = check_deleted_emails(user.credentials, list(existing_gmail_ids), force_full_check=False)
                    
                    # Extract the IDs of deleted emails
                    deleted_email_ids = [gmail_id for gmail_id, is_deleted in deleted_status.items() if is_deleted]
                    logger.info(f"[SYNC] Found {len(deleted_email_ids)} deleted emails")
        
        # Process results
        if not new_emails and not deleted_email_ids and label_changes_count == 0:
            logger.info(f"[SYNC] No new or deleted emails found for user {user.id}")
            return {
                "status": "success",
                "message": "No changes detected",
                "sync_count": 0,
                "new_email_count": 0,
                "deleted_email_count": 0,
                "label_changes_count": 0
            }
        
        # Process and store new emails
        processed_emails = []
        if new_emails:
            processed_emails = process_and_store_emails(db, user, new_emails)
            logger.info(f"[SYNC] Successfully processed and stored {len(processed_emails)} emails")
            
            # Log details about each processed email
            for i, email in enumerate(processed_emails):
                logger.info(f"[SYNC] Email {i+1}/{len(processed_emails)}: ID={email.id}, Subject='{email.subject[:30]}...', "
                           f"From={email.from_email}, Received={email.received_at.isoformat()}, "
                           f"Category={email.category}")
        
        # Process deleted emails
        deleted_count = 0
        if deleted_email_ids:
            logger.info(f"[SYNC] Processing {len(deleted_email_ids)} deleted emails")
            
            # Mark emails as deleted in our database
            for gmail_id in deleted_email_ids:
                email = db.query(Email).filter(
                    Email.user_id == user.id,
                    Email.gmail_id == gmail_id
                ).first()
                
                if email:
                    logger.info(f"[SYNC] Marking email {gmail_id} as deleted")
                    email.is_deleted = True
                    deleted_count += 1
                else:
                    logger.debug(f"[SYNC] Email {gmail_id} not found in database, skipping deletion")
            
            db.commit()
            logger.info(f"[SYNC] Marked {deleted_count} emails as deleted")
        
        # Find the most recent email timestamp to update last_fetched_at
        latest_timestamp = None
        for email in processed_emails:
            if email.received_at and (latest_timestamp is None or email.received_at > latest_timestamp):
                latest_timestamp = email.received_at
        
        # Update the sync checkpoint
        if latest_timestamp or new_history_id:
            # Use current timestamp if no emails were processed
            if not latest_timestamp:
                latest_timestamp = now
            
            # Ensure the timestamp has timezone info
            if latest_timestamp.tzinfo is None:
                latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
                
            logger.info(f"[SYNC] Found latest timestamp: {latest_timestamp.isoformat()}")
            old_checkpoint = email_sync.last_fetched_at
            
            # Don't set the checkpoint in the future
            if latest_timestamp > now:
                logger.warning(f"[SYNC] Latest email timestamp {latest_timestamp.isoformat()} is in the future! Using current time instead.")
                latest_timestamp = now
                
            update_sync_checkpoint(db, email_sync, latest_timestamp, new_history_id)
            logger.info(f"[SYNC] Updated checkpoint from {old_checkpoint.isoformat()} to {email_sync.last_fetched_at.isoformat()}")
            if new_history_id:
                logger.info(f"[SYNC] Updated history ID to {new_history_id}")
        
        sync_result = {
            "status": "success",
            "message": f"Processed {len(processed_emails)} new emails, {deleted_count} deleted emails, and {label_changes_count} label changes",
            "sync_count": len(processed_emails) + deleted_count + label_changes_count,
            "new_email_count": len(processed_emails),
            "deleted_email_count": deleted_count,
            "label_changes_count": label_changes_count,
            "sync_started_at": datetime.now().isoformat(),
            "user_id": str(user.id)
        }
        
        logger.info(f"[SYNC] Sync completed successfully: {sync_result}")
        return sync_result
        
    except Exception as e:
        logger.error(f"[SYNC] Error syncing emails: {str(e)}", exc_info=True)
        raise 