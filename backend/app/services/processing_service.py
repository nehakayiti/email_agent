"""
Processing Service - Database operations for email processing

This service contains only the logic for taking raw email data from the API
and creating/updating Email model instances in the database.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.email import Email
from ..models.user import User
from ..models.email_sync import EmailSync
from uuid import UUID
import uuid

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
    # Check if user already has a sync record - query directly to avoid detached session issues
    email_sync = db.query(EmailSync).filter(EmailSync.user_id == user.id).first()
    
    if email_sync:
        return email_sync
    
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
        
    logger.info(f"[PROCESSOR] Updating last_fetched_at to {new_timestamp}")
    email_sync.last_fetched_at = new_timestamp
    
    # Update history ID if provided
    if new_history_id:
        logger.info(f"[PROCESSOR] Updating last_history_id to {new_history_id}")
        email_sync.last_history_id = new_history_id
    
    db.commit()
    db.refresh(email_sync)
    
    return email_sync

def process_and_store_emails(
    db: Session,
    user: User,
    emails: List[Dict[str, Any]]
) -> List[Email]:
    """
    Process fetched emails and store them in database
    
    Args:
        db: Database session
        user: User model instance
        emails: List of email data dictionaries from Gmail API
        
    Returns:
        List of processed Email model instances
    """
    processed_emails = []
    new_emails_count = 0
    updated_emails_count = 0
    logger.info(f"[PROCESSOR] Processing {len(emails)} emails for user {user.id} (email: {user.email})")
    
    for i, email_data in enumerate(emails):
        try:
            gmail_id = email_data.get('gmail_id', 'unknown')
            subject = email_data.get('subject', 'No Subject')[:30]
            from_email = email_data.get('from_email', 'unknown')
            received_at = email_data.get('received_at', 'unknown')
            
            logger.debug(f"[PROCESSOR] Processing email {i+1}/{len(emails)}: '{subject}' from {from_email}")
            
            # Check if email already exists
            existing_email = db.query(Email).filter(
                and_(
                    Email.gmail_id == gmail_id,
                    Email.user_id == user.id
                )
            ).first()
            
            if existing_email:
                # Update existing email
                existing_email.subject = email_data.get('subject')
                existing_email.from_email = email_data.get('from_email')
                existing_email.received_at = email_data.get('received_at')
                existing_email.snippet = email_data.get('snippet')
                existing_email.labels = email_data.get('labels')
                existing_email.raw_data = email_data.get('raw_data')
                existing_email.is_processed = True
                
                processed_emails.append(existing_email)
                updated_emails_count += 1
                logger.debug(f"[PROCESSOR] Updated existing email: {gmail_id}")
            else:
                # Create new email (categorization will be handled separately)
                new_email = Email(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    gmail_id=gmail_id,
                    thread_id=email_data.get('thread_id'),
                    subject=email_data.get('subject'),
                    from_email=email_data.get('from_email'),
                    received_at=email_data.get('received_at'),
                    snippet=email_data.get('snippet'),
                    labels=email_data.get('labels'),
                    is_read=email_data.get('is_read', False),
                    is_processed=True,
                    importance_score=email_data.get('importance_score'),
                    category=email_data.get('category'),  # Will be set by categorization service
                    raw_data=email_data.get('raw_data')
                )
                
                db.add(new_email)
                processed_emails.append(new_email)
                new_emails_count += 1
                logger.debug(f"[PROCESSOR] Created new email: {gmail_id}")
                
        except Exception as e:
            logger.error(f"[PROCESSOR] Error processing email {i+1}: {str(e)}")
            continue
    
    # Commit all changes
    try:
        db.commit()
        logger.info(f"[PROCESSOR] Successfully processed {len(processed_emails)} emails (new: {new_emails_count}, updated: {updated_emails_count})")
    except Exception as e:
        db.rollback()
        logger.error(f"[PROCESSOR] Error committing emails: {str(e)}")
        raise
    
    return processed_emails

def mark_emails_deleted(db: Session, user: User, deleted_gmail_ids: List[str]) -> int:
    """
    Mark emails as deleted in our database based on Gmail IDs
    
    Args:
        db: Database session
        user: User model instance
        deleted_gmail_ids: List of Gmail IDs that were deleted
        
    Returns:
        Number of emails marked as deleted
    """
    if not deleted_gmail_ids:
        return 0
    
    deleted_count = 0
    not_found_count = 0
    already_deleted_count = 0
    
    # Log the first few deleted Gmail IDs for debugging
    debug_ids = deleted_gmail_ids[:5]
    logger.info(f"[PROCESSOR] Processing {len(deleted_gmail_ids)} deleted emails (sample: {debug_ids})")
    
    for gmail_id in deleted_gmail_ids:
        try:
            # Find the email in our database
            email = db.query(Email).filter(
                and_(
                    Email.gmail_id == gmail_id,
                    Email.user_id == user.id
                )
            ).first()
            
            if not email:
                not_found_count += 1
                logger.debug(f"[PROCESSOR] Email {gmail_id} not found in database")
                continue
            
            # Check if already marked as deleted
            if email.category == 'trash':
                already_deleted_count += 1
                logger.debug(f"[PROCESSOR] Email {gmail_id} already marked as deleted")
                continue
            
            # Mark as deleted by setting category to trash
            email.category = 'trash'
            deleted_count += 1
            
            logger.debug(f"[PROCESSOR] Marked email {gmail_id} as deleted")
            
        except Exception as e:
            logger.error(f"[PROCESSOR] Error marking email {gmail_id} as deleted: {str(e)}")
            continue
    
    # Commit changes
    try:
        db.commit()
        logger.info(f"[PROCESSOR] Deletion summary: {deleted_count} marked, {not_found_count} not found, {already_deleted_count} already deleted")
    except Exception as e:
        db.rollback()
        logger.error(f"[PROCESSOR] Error committing deletions: {str(e)}")
        raise
    
    return deleted_count

def process_label_changes(db: Session, user: User, label_changes: Dict[str, Dict[str, List[str]]]) -> int:
    """
    Process label changes from Gmail's history API
    
    Args:
        db: Database session
        user: User model instance
        label_changes: Dictionary of Gmail ID to label changes
        
    Returns:
        Number of emails updated
    """
    if not label_changes:
        return 0

    updated_count = 0
    for gmail_id, changes in label_changes.items():
        email = db.query(Email).filter(
            Email.user_id == user.id,
            Email.gmail_id == gmail_id
        ).first()
        
        if not email:
            logger.debug(f"[PROCESSOR] Email {gmail_id} not found in database, skipping label update")
            continue
            
        email_desc = f"'{email.subject[:40]}...' ({gmail_id})"
        added_labels = changes.get('added', [])
        removed_labels = changes.get('removed', [])
        
        label_desc = []
        if added_labels:
            label_desc.append(f"added {added_labels}")
        if removed_labels:
            label_desc.append(f"removed {removed_labels}")
        change_desc = " & ".join(label_desc)
        
        logger.info(f"[PROCESSOR] Processing label changes ({change_desc}): {email_desc}")
        
        changed = False
        current_labels = set(email.labels or [])
        
        for label in added_labels:
            if label not in current_labels:
                current_labels.add(label)
                changed = True
                
        for label in removed_labels:
            if label in current_labels:
                current_labels.remove(label)
                changed = True
                
        if changed:
            email.labels = list(current_labels)
            updated_count += 1
            
    if updated_count > 0:
        db.commit()
        logger.info(f"[PROCESSOR] Updated {updated_count} emails due to label changes")
        
    return updated_count

def get_existing_gmail_ids(db: Session, user_id: UUID) -> List[str]:
    """
    Get list of Gmail IDs that already exist in the database for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of existing Gmail IDs
    """
    existing_gmail_ids = db.query(Email.gmail_id).filter(
        Email.user_id == user_id
    ).all()
    return [id[0] for id in existing_gmail_ids]

def filter_new_emails(emails: List[Dict[str, Any]], existing_gmail_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Filter out emails that already exist in the database
    
    Args:
        emails: List of email data dictionaries
        existing_gmail_ids: List of Gmail IDs that already exist
        
    Returns:
        List of new email data dictionaries
    """
    new_emails = []
    already_processed = 0
    
    for email in emails:
        if email['gmail_id'] not in existing_gmail_ids:
            new_emails.append(email)
        else:
            already_processed += 1
            logger.debug(f"[PROCESSOR] Skipping already processed email: {email['gmail_id']}")
    
    if already_processed > 0:
        logger.info(f"[PROCESSOR] Filtered out {already_processed} already processed emails")
        
    return new_emails 