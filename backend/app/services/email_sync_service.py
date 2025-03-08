from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from ..models.user import User
from ..models.email_sync import EmailSync
from ..models.email import Email
from . import gmail
# Remove circular import
# from .email_processor import process_and_store_emails
import logging
import time
from uuid import UUID
from ..services import email_operations_service
from ..utils.email_categorizer import categorize_email
from ..services import email_classifier_service

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
        # Find the email in our database
        email = db.query(Email).filter(
            Email.user_id == user.id,
            Email.gmail_id == gmail_id
        ).first()
        
        if not email:
            logger.debug(f"[GMAIL→EA] Email {gmail_id} not found in database, skipping label update")
            continue
        
        # Format a descriptive email identifier for logs
        email_desc = f"'{email.subject[:40]}...' ({gmail_id})"
        
        # Prepare user-friendly label change description
        added_labels = changes.get('added', [])
        removed_labels = changes.get('removed', [])
        
        label_desc = []
        if added_labels:
            label_desc.append(f"added {added_labels}")
        if removed_labels:
            label_desc.append(f"removed {removed_labels}")
        
        change_desc = " & ".join(label_desc)
        logger.info(f"[GMAIL→EA] Processing label changes ({change_desc}): {email_desc}")
            
        # Check for Trash label to mark email as trash
        if 'TRASH' in changes.get('added', []):
            logger.info(f"[GMAIL→EA] Email moved to Trash: {email_desc}")
            
            # Update the email's labels to include TRASH
            current_labels = set(email.labels or [])
            current_labels.add('TRASH')
            email.labels = list(current_labels)
            
            # Also update category if needed to reflect trash status
            if email.category != 'trash':
                logger.info(f"[GMAIL→EA] Setting category to 'trash' for email (previously {email.category}): {email_desc}")
                email.category = 'trash'
            
            updated_count += 1
        
        # Check if email is being restored from trash
        if 'TRASH' in changes.get('removed', []):
            logger.info(f"[GMAIL→EA] Email removed from Trash: {email_desc}")
            
            # Remove TRASH from the email's labels
            current_labels = set(email.labels or [])
            if 'TRASH' in current_labels:
                current_labels.remove('TRASH')
                email.labels = list(current_labels)
            
            # Recategorize the email based on its current labels
            email.category = categorize_email_from_labels(email.labels, db, user.id)
            logger.info(f"[GMAIL→EA] Recategorized email as {email.category} after trash removal: {email_desc}")
    
    if updated_count > 0:
        db.commit()
        logger.info(f"[GMAIL→EA] Updated {updated_count} emails due to label changes")
        
    return updated_count

def categorize_email_from_labels(labels: List[str], db: Session, user_id: Optional[UUID] = None) -> str:
    """
    Categorize an email based on Gmail labels and ML classification if needed
    
    Args:
        labels: List of Gmail labels
        db: Database session
        user_id: Optional user ID for user-specific classification
        
    Returns:
        Email category string
    """
    # Define standard label mappings
    category_map = {
        'INBOX': 'inbox',
        'IMPORTANT': 'important',
        'SENT': 'sent',
        'DRAFT': 'draft',
        'TRASH': 'trash',
        'SPAM': 'spam',
        'STARRED': 'starred',
        'CATEGORY_UPDATES': 'updates',
        'CATEGORY_PROMOTIONS': 'promotions',
        'CATEGORY_SOCIAL': 'social', 
        'CATEGORY_FORUMS': 'forums',
        'UNREAD': 'unread'
    }
    
    # Check for direct category matches from Gmail labels
    logger.debug(f"[CATEGORIZATION] Processing email with labels: {', '.join(labels)}")
    
    # Priority categories first
    if any(label in ['TRASH', 'SPAM'] for label in labels):
        category = next((category_map[label] for label in labels if label in ['TRASH', 'SPAM']), None)
        logger.debug(f"[CATEGORIZATION] Email categorized as '{category}' based on priority label")
        return category
        
    # Look for category labels
    for label in labels:
        if label in category_map:
            category = category_map[label]
            logger.debug(f"[CATEGORIZATION] Email categorized as '{category}' based on standard label")
            return category
    
    # If no category labels matched, use ML classification for inbox decision
    if 'INBOX' in labels:
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  EMAIL CLASSIFICATION                                    ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        
        # First try loading the user's classifier model
        classifier_loaded = email_classifier_service.load_trash_classifier(user_id)
        
        if classifier_loaded:
            # For now we just apply a simple rule for inbox emails
            # In a future update, this will use ML to predict inbox vs trash
            logger.info(f"[CLASSIFICATION] Classifier loaded successfully for user {user_id}")
            logger.info(f"[CLASSIFICATION] Using classifier to determine if email should be inbox or trash")
            
            # For now we always return inbox for emails in inbox that don't match other categories
            # ML functionality will be implemented in a future update
            logger.info(f"[CLASSIFICATION] Classification result: Email should be in 'inbox'")
            return 'inbox'
        else:
            logger.warning(f"[CLASSIFICATION] No classifier available for user {user_id}, defaulting to 'inbox'")
            return 'inbox'
    
    # Default to 'other' for emails that don't match any categories
    logger.debug(f"[CATEGORIZATION] Email does not match any categories, using default 'other'")
    return 'other'

def process_pending_category_updates(db: Session, user: User) -> int:
    """
    Process any pending category updates from our database to Gmail
    
    Args:
        db: Database session
        user: User model instance
        
    Returns:
        Number of emails updated
    """
    # Find all emails that have the EA_NEEDS_LABEL_UPDATE label
    pending_emails = db.query(Email).filter(
        Email.user_id == user.id,
        Email.labels.contains(["EA_NEEDS_LABEL_UPDATE"]),
    ).all()
    
    logger.info(f"[SYNC] Found {len(pending_emails)} emails with pending category updates")
    
    if not pending_emails:
        return 0
    
    # Get all categories from the database
    from ..models.email_category import EmailCategory
    categories = db.query(EmailCategory).all()
    
    # Dynamically build the mapping from categories to Gmail labels
    category_to_label = {}
    for category in categories:
        category_name = category.name.lower()
        # Special cases
        if category_name == 'primary':
            category_to_label[category_name] = None  # No specific label for primary
        elif category_name == 'trash':
            category_to_label[category_name] = 'TRASH'
        elif category_name == 'promotional':
            category_to_label[category_name] = 'CATEGORY_PROMOTIONS'
        else:
            # Standard format for Gmail category labels
            category_to_label[category_name] = f'CATEGORY_{category_name.upper()}'
    
    # All category labels for removal check
    all_category_labels = [label for label in category_to_label.values() if label]
    
    updated_count = 0
    for email in pending_emails:
        try:
            # Get current labels without our update marker
            current_labels = set(email.labels)
            current_labels.remove("EA_NEEDS_LABEL_UPDATE")
            
            # Determine which label to add based on the category
            add_labels = []
            if category_to_label.get(email.category):
                add_labels = [category_to_label[email.category]]
            
            # Remove all other category labels
            remove_labels = [label for label in all_category_labels if label not in add_labels]
            
            # Special handling for TRASH category - ensure INBOX is removed
            if email.category == 'trash':
                if 'INBOX' not in remove_labels:
                    remove_labels.append('INBOX')
            
            # If we have labels to add or remove, update in Gmail
            if add_labels or remove_labels:
                logger.info(f"[SYNC] Updating Gmail labels for email {email.id} (Gmail ID: {email.gmail_id}), "
                           f"category: {email.category}, add: {add_labels}, remove: {remove_labels}")
                
                try:
                    # Update labels in Gmail
                    result = gmail.update_email_labels(
                        credentials=user.credentials,
                        gmail_id=email.gmail_id,
                        add_labels=add_labels,
                        remove_labels=remove_labels
                    )
                    
                    # Update our database labels to match Gmail
                    for label in add_labels:
                        current_labels.add(label)
                    
                    for label in remove_labels:
                        if label in current_labels:
                            current_labels.remove(label)
                    
                    # Check for label inconsistencies and fix them
                    if 'TRASH' in current_labels and 'INBOX' in current_labels:
                        current_labels.remove('INBOX')
                        logger.info(f"[SYNC] Removed INBOX label from email {email.id} because it's in TRASH")
                    
                    # Update the email record
                    email.labels = list(current_labels)
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"[SYNC] Error updating Gmail labels for email {email.id}: {str(e)}")
                    # Keep the EA_NEEDS_LABEL_UPDATE label for retry in next sync
                    email.labels = list(current_labels) + ["EA_NEEDS_LABEL_UPDATE"]
            else:
                # No Gmail updates needed, just remove our marker
                email.labels = list(current_labels)
                updated_count += 1
        except Exception as e:
            logger.error(f"[SYNC] Error processing category update for email {email.id}: {str(e)}")
    
    if updated_count > 0:
        db.commit()
        logger.info(f"[SYNC] Successfully updated {updated_count} emails with pending category changes")
    
    return updated_count

def sync_emails_since_last_fetch(db: Session, user: User, use_current_date: bool = False, force_full_sync: bool = False) -> Dict[str, Any]:
    """
    Sync emails from Gmail using only the historyId approach for efficiency
    """
    start_time = datetime.now(timezone.utc)
    sync_start_timestamp = start_time.isoformat()
    
    try:
        # Get or create email sync record
        email_sync = get_or_create_email_sync(db, user)
        
        # Enhanced logging for sync start
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  STARTING EMAIL SYNC                                     ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        logger.info(f"User: {user.email}")
        logger.info(f"Time: {sync_start_timestamp}")
        logger.info(f"Last sync: {email_sync.last_fetched_at}")
        logger.info(f"History ID: {email_sync.last_history_id}")
        
        # Initialize sync variables
        new_emails = []
        deleted_email_ids = []
        label_changes_count = 0
        new_history_id = None
        
        # For force_full_sync, we need to get a new history ID
        if force_full_sync or not email_sync.last_history_id:
            # Log the full sync start
            logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
            logger.info(f"║                  PERFORMING FULL SYNC                                    ║")
            logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
            
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
        existing_gmail_ids = [id[0] for id in existing_gmail_ids]
        
        # Process pending operations - push changes from EA to Gmail
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  PROCESSING EA → GMAIL OPERATIONS                        ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        
        ops_start_time = datetime.now(timezone.utc)
        try:
            logger.info(f"[SYNC] Processing pending operations with user credentials")
            operations_result = email_operations_service.process_pending_operations(db, user, user.credentials)
            logger.info(f"[SYNC] Operations processing completed successfully")
        except Exception as e:
            logger.error(f"[SYNC] Error during operations processing: {str(e)}")
            return {
                "status": "error",
                "message": f"Email sync failed: {str(e)}",
                "sync_count": 0,
                "sync_started_at": sync_start_timestamp,
                "user_id": user.id,
                "sync_method": "error"
            }
            
        ops_duration = (datetime.now(timezone.utc) - ops_start_time).total_seconds()
        
        operations_processed = operations_result.get("processed_count", 0)
        operations_succeeded = operations_result.get("success_count", 0)
        operations_failed = operations_result.get("failure_count", 0)
        operations_retrying = operations_result.get("retry_count", 0)
        
        if operations_processed > 0:
            logger.info(f"EA → GMAIL Summary:")
            logger.info(f"  - Processed: {operations_processed} operations in {ops_duration:.2f} seconds")
            logger.info(f"  - Succeeded: {operations_succeeded} operations")
            logger.info(f"  - Failed: {operations_failed} operations")
            logger.info(f"  - Retry pending: {operations_retrying} operations")
            
            # If operations were processed, wait a moment for Gmail to update its state
            if operations_processed > 0:
                logger.info(f"Waiting 1 second for Gmail to process our changes...")
                time.sleep(1)
        else:
            logger.info(f"No pending EA → GMAIL operations to process")
        
        # Use history-based approach with existing history ID
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  FETCHING GMAIL → EA CHANGES                             ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        logger.info(f"Using history ID: {email_sync.last_history_id}")
        
        try:
            sync_start = datetime.now(timezone.utc)
            # Use the sync_gmail_changes function to efficiently fetch changes since last history ID
            new_emails_raw, deleted_ids, label_changes, new_history_id = gmail.sync_gmail_changes(
                user.credentials,
                email_sync.last_history_id
            )
            sync_duration = (datetime.now(timezone.utc) - sync_start).total_seconds()
            
            # Log summary of changes from Gmail
            if new_emails_raw or deleted_ids or label_changes:
                logger.info(f"GMAIL → EA Changes detected:")
                
                if new_emails_raw:
                    logger.info(f"  - {len(new_emails_raw)} new emails")
                    # Log a sample of new emails
                    for i, email in enumerate(new_emails_raw[:5]):
                        subject = email.get('subject', 'No subject')
                        sender = email.get('from_address', 'Unknown sender')
                        logger.info(f"    {i+1}. New: '{subject[:40]}...' from {sender[:30]}")
                    if len(new_emails_raw) > 5:
                        logger.info(f"    ... and {len(new_emails_raw) - 5} more")
                
                if deleted_ids:
                    logger.info(f"  - {len(deleted_ids)} deleted emails")
                    # Log a few deleted IDs
                    for i, gmail_id in enumerate(deleted_ids[:5]):
                        logger.info(f"    {i+1}. Deleted: {gmail_id}")
                    if len(deleted_ids) > 5:
                        logger.info(f"    ... and {len(deleted_ids) - 5} more")
                
                if label_changes:
                    logger.info(f"  - {len(label_changes)} emails with label changes")
                    # Log a few label changes
                    for i, (gmail_id, changes) in enumerate(list(label_changes.items())[:5]):
                        added = changes.get('added', [])
                        removed = changes.get('removed', [])
                        change_desc = []
                        if added:
                            change_desc.append(f"added {added}")
                        if removed:
                            change_desc.append(f"removed {removed}")
                        logger.info(f"    {i+1}. Labels changed ({' & '.join(change_desc)}): {gmail_id}")
                    if len(label_changes) > 5:
                        logger.info(f"    ... and {len(label_changes) - 5} more")
            else:
                logger.info(f"No changes detected from Gmail")
            
            # If we've processed operations but no Gmail changes, we should still report success
            if operations_processed > 0 and (new_history_id is None or new_history_id == email_sync.last_history_id):
                logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
                logger.info(f"║                  SYNC COMPLETED SUCCESSFULLY                             ║")
                logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
                logger.info(f"EA → GMAIL operations processed, no Gmail changes detected")
                
                # Update the sync checkpoint - use the same history ID but new timestamp
                update_sync_checkpoint(db, email_sync, start_time, email_sync.last_history_id)
                
                return {
                    "status": "success",
                    "message": f"Processed {operations_processed} operations ({operations_succeeded} successful)",
                    "sync_count": operations_processed,
                    "operations_processed": operations_processed,
                    "operations_succeeded": operations_succeeded,
                    "new_email_count": 0,
                    "deleted_email_count": 0,
                    "label_changes_count": 0,
                    "sync_started_at": start_time.isoformat(),
                    "user_id": str(user.id),
                    "sync_method": "operations_only",
                    "sync_duration_seconds": ops_duration
                }
            
            # If we got a valid history ID back, process the results
            if new_history_id and new_history_id != email_sync.last_history_id:
                logger.info(f"History ID changed: {email_sync.last_history_id} → {new_history_id}")
                
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
                
                # Process any pending category updates from our database to Gmail
                category_updates_count = process_pending_category_updates(db, user)
                
                logger.info(f"[SYNC] Processing summary:")
                logger.info(f"  - Total emails found: {total_found}")
                logger.info(f"  - Already processed: {already_processed}")
                logger.info(f"  - New emails to process: {len(new_emails)}")
                logger.info(f"  - Deleted emails to process: {len(deleted_email_ids)}")
                logger.info(f"  - Label changes processed: {label_changes_count}")
                logger.info(f"  - Category updates processed: {category_updates_count}")
                logger.info(f"  - Operations processed: {operations_processed}")
                
                # Final summary
                logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
                logger.info(f"║                  SYNC COMPLETED SUCCESSFULLY                             ║")
                logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
                logger.info(f"Bidirectional sync summary:")
                logger.info(f"  EA → GMAIL:")
                logger.info(f"    - Operations processed: {operations_processed}")
                logger.info(f"    - Operations succeeded: {operations_succeeded}")
                logger.info(f"  GMAIL → EA:")
                logger.info(f"    - New emails: {len(new_emails)}")
                logger.info(f"    - Deleted emails: {len(deleted_email_ids)}")
                logger.info(f"    - Label changes: {label_changes_count}")
            else:
                # Only show the warning if we didn't process any operations
                if operations_processed == 0:
                    logger.warning(f"╔══════════════════════════════════════════════════════════════════════════╗")
                    logger.warning(f"║                  NO CHANGES DETECTED                                     ║")
                    logger.warning(f"╚══════════════════════════════════════════════════════════════════════════╝")
                    logger.warning(f"History ID unchanged: {email_sync.last_history_id}")
                    return {
                        "status": "warning",
                        "message": "No changes detected since last sync",
                        "sync_count": 0,
                        "sync_started_at": start_time.isoformat(),
                        "user_id": str(user.id),
                        "sync_method": "history_no_changes",
                        "debug_info": {
                            "last_history_id": email_sync.last_history_id,
                            "new_history_id": new_history_id,
                            "sync_duration_seconds": sync_duration
                        }
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
            # Use local import to avoid circular dependency
            from .email_processor import process_and_store_emails
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
                elif 'TRASH' in (email.labels or []):
                    already_deleted_count += 1
                    if already_deleted_count <= 5:  # Log first 5 already deleted emails
                        logger.debug(f"[SYNC] Email {email.id} (gmail_id: {gmail_id}) already has TRASH label")
                else:
                    logger.info(f"[SYNC] Adding TRASH label to email {email.id} (gmail_id: {gmail_id})")
                    # Add TRASH label
                    current_labels = set(email.labels or [])
                    current_labels.add('TRASH')
                    email.labels = list(current_labels)
                    
                    # Update category to 'trash'
                    email.category = 'trash'
                    
                    deleted_count += 1
            
            logger.info(f"[SYNC] Deletion summary before commit: deleted_count={deleted_count}, not_found_count={not_found_count}, already_deleted_count={already_deleted_count}")
            
            if deleted_count > 0:
                db.commit()
                logger.info(f"[SYNC] Added TRASH label to {deleted_count} emails")
            else:
                logger.warning(f"[SYNC] No emails were updated with TRASH label despite finding {len(deleted_email_ids)} deleted emails")
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
            "message": f"Processed {len(processed_emails)} new emails, {len(deleted_email_ids)} deleted emails, and {label_changes_count} label changes, {category_updates_count} category updates",
            "sync_count": len(processed_emails) + len(deleted_email_ids) + label_changes_count + category_updates_count,
            "new_email_count": len(processed_emails),
            "deleted_email_count": len(deleted_email_ids),
            "label_changes_count": label_changes_count,
            "category_updates_processed": category_updates_count,
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