from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.email_sync import EmailSync
from ..models.email import Email
from .gmail import fetch_emails_from_gmail
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
        last_fetched_at=datetime.now(timezone.utc) - timedelta(days=1)  # Default to 1 day ago
    )
    
    db.add(email_sync)
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

def update_last_fetched_at(db: Session, email_sync: EmailSync, new_timestamp: datetime) -> EmailSync:
    """
    Update the last_fetched_at timestamp in the email_sync record
    
    Args:
        db: Database session
        email_sync: EmailSync model instance
        new_timestamp: New timestamp to set
        
    Returns:
        Updated EmailSync model instance
    """
    # Ensure the timestamp has timezone info
    if new_timestamp.tzinfo is None:
        new_timestamp = new_timestamp.replace(tzinfo=timezone.utc)
        
    logger.info(f"Updating last_fetched_at to {new_timestamp}")
    email_sync.last_fetched_at = new_timestamp
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

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
        
        # Check if the last_fetched_at is in the future (timezone issue)
        now = datetime.now(timezone.utc)
        if last_fetched_at > now:
            logger.warning(f"[SYNC] Last checkpoint date {last_fetched_at.isoformat()} is in the future! Resetting to current time.")
            last_fetched_at = now - timedelta(hours=1)  # Set to 1 hour ago to be safe
            update_last_fetched_at(db, email_sync, last_fetched_at)
        
        # Get local time for logging
        local_time = datetime.now()
        logger.info(f"[SYNC] Starting email sync for user {user.id} (email: {user.email})")
        logger.info(f"[SYNC] Current local time: {local_time.isoformat()}")
        logger.info(f"[SYNC] Last checkpoint (UTC): {last_fetched_at.isoformat()} (use_current_date: {use_current_date})")
        
        # Get the most recent email ID from the database to use as a reference point
        # This allows us to use Gmail's pagination to only get emails newer than what we have
        most_recent_email = db.query(Email).filter(
            Email.user_id == user.id
        ).order_by(Email.received_at.desc()).first()
        
        # Format the date for the query - we still need a date filter as a baseline
        # But we'll combine it with historyId/pagination for more efficiency
        after_date = last_fetched_at.strftime('%Y/%m/%d')
        
        # Create a query that will find emails since our date
        # We'll use the historyId/pagination to further filter
        query = f"after:{after_date}"
        
        # Get the list of already processed email IDs to filter them out
        existing_gmail_ids = db.query(Email.gmail_id).filter(
            Email.user_id == user.id
        ).all()
        existing_gmail_ids = set([id[0] for id in existing_gmail_ids])
        logger.info(f"[SYNC] Found {len(existing_gmail_ids)} already processed emails in database")
        
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
        
        if not emails:
            logger.info(f"[SYNC] No emails found matching query for user {user.id}")
            return {
                "status": "success",
                "message": "No new emails found",
                "sync_count": 0,
                "new_email_count": 0
            }
        
        logger.info(f"[SYNC] Retrieved {len(emails)} emails from Gmail API")
        
        # Filter out emails that have already been processed
        new_emails = []
        for email in emails:
            if email['gmail_id'] not in existing_gmail_ids:
                # This is a new email we haven't seen before
                new_emails.append(email)
                logger.debug(f"[SYNC] New email found: {email['gmail_id']} - {email['subject'][:30]}")
            else:
                logger.debug(f"[SYNC] Skipping already processed email: {email['gmail_id']}")
                
        logger.info(f"[SYNC] After filtering, {len(new_emails)} new emails remain for processing")
        
        if not new_emails:
            logger.info(f"[SYNC] All retrieved emails have already been processed")
            return {
                "status": "success",
                "message": "No new emails found after filtering",
                "sync_count": 0,
                "new_email_count": 0
            }
        
        # Process and store emails
        processed_emails = process_and_store_emails(db, user, new_emails)
        logger.info(f"[SYNC] Successfully processed and stored {len(processed_emails)} emails")
        
        # Log details about each processed email
        for i, email in enumerate(processed_emails):
            logger.info(f"[SYNC] Email {i+1}/{len(processed_emails)}: ID={email.id}, Subject='{email.subject[:30]}...', "
                       f"From={email.from_email}, Received={email.received_at.isoformat()}, "
                       f"Category={email.category}")
        
        # Count only the actual new emails
        new_email_count = len(processed_emails)
        
        logger.info(f"[SYNC] Email counts - Total: {len(processed_emails)}, New: {new_email_count}")
        
        # Find the most recent email timestamp to update last_fetched_at
        latest_timestamp = None
        for email in processed_emails:
            if email.received_at and (latest_timestamp is None or email.received_at > latest_timestamp):
                latest_timestamp = email.received_at
        
        # Update the last_fetched_at timestamp if we found new emails
        if latest_timestamp:
            # Ensure the timestamp has timezone info
            if latest_timestamp.tzinfo is None:
                latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
                
            logger.info(f"[SYNC] Found latest timestamp: {latest_timestamp.isoformat()}")
            old_checkpoint = email_sync.last_fetched_at
            
            # Don't set the checkpoint in the future
            if latest_timestamp > now:
                logger.warning(f"[SYNC] Latest email timestamp {latest_timestamp.isoformat()} is in the future! Using current time instead.")
                latest_timestamp = now
                
            update_last_fetched_at(db, email_sync, latest_timestamp)
            logger.info(f"[SYNC] Updated checkpoint from {old_checkpoint.isoformat()} to {email_sync.last_fetched_at.isoformat()}")
        
        sync_result = {
            "status": "success",
            "message": f"Processed {new_email_count} new emails",
            "sync_count": len(processed_emails),
            "new_email_count": new_email_count,
            "sync_started_at": datetime.now().isoformat(),
            "user_id": str(user.id)
        }
        
        logger.info(f"[SYNC] Sync completed successfully: {sync_result}")
        return sync_result
        
    except Exception as e:
        logger.error(f"[SYNC] Error syncing emails: {str(e)}", exc_info=True)
        raise 