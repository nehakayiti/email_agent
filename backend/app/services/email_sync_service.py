from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
    
    # Create new sync record with default values
    email_sync = EmailSync(
        user_id=user.id,
        last_fetched_at=datetime.now() - timedelta(days=1)  # Default to 1 day ago
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
    logger.info(f"Updating last_fetched_at to {new_timestamp}")
    email_sync.last_fetched_at = new_timestamp
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

def sync_emails_since_last_fetch(db: Session, user: User) -> Dict[str, Any]:
    """
    Sync emails from Gmail since the last fetch time
    
    Args:
        db: Database session
        user: User model instance
        
    Returns:
        Dictionary with sync results
    """
    try:
        # Get or create email sync record
        email_sync = get_or_create_email_sync(db, user)
        last_fetched_at = email_sync.last_fetched_at
        
        logger.info(f"Syncing emails for user {user.id} since {last_fetched_at}")
        
        # Fetch emails from Gmail with a filter for the date
        # Convert to RFC 3339 format for Gmail API
        after_date = last_fetched_at.strftime('%Y/%m/%d')
        query = f"after:{after_date}"
        
        emails = fetch_emails_from_gmail(user.credentials, query=query)
        
        if not emails:
            logger.info(f"No new emails found for user {user.id}")
            return {
                "status": "success",
                "message": "No new emails found",
                "sync_count": 0
            }
        
        # Process and store emails
        processed_emails = process_and_store_emails(db, user, emails)
        
        # Find the most recent email timestamp to update last_fetched_at
        latest_timestamp = None
        for email in processed_emails:
            if email.received_at and (latest_timestamp is None or email.received_at > latest_timestamp):
                latest_timestamp = email.received_at
        
        # Update the last_fetched_at timestamp if we found new emails
        if latest_timestamp:
            logger.info(f"Found latest timestamp: {latest_timestamp}")
            update_last_fetched_at(db, email_sync, latest_timestamp)
            logger.info(f"Updated last_fetched_at to {email_sync.last_fetched_at}")
        
        return {
            "status": "success",
            "message": f"Processed {len(processed_emails)} emails",
            "sync_count": len(processed_emails)
        }
        
    except Exception as e:
        logger.error(f"Error syncing emails: {str(e)}")
        raise 