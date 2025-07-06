from googleapiclient.errors import HttpError
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from ..models.user import User
from ..models.email_sync import EmailSync
from ..models.email import Email
from . import gmail
# Import process_and_store_emails from email_processor
from .email_processor import process_and_store_emails
import logging
import time
from uuid import UUID
from ..services import email_operations_service
from ..utils.email_categorizer import RuleBasedCategorizer, categorize_email
from ..services import email_classifier_service
from ..core.logging_config import configure_logging
from ..config import settings
from ..models.sync_details import SyncDetails, SyncDirection, SyncType, SyncStatus
from .sync_recording import record_sync_details

# Configure logging if this module is run directly
if __name__ == "__main__":
    configure_logging(log_file_name="email_sync.log")

# Get logger
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

    categorizer = RuleBasedCategorizer(db, user.id)
    # Collect all labels used in rules for relevance check
    rule_labels = set()
    for rule in categorizer.rules:
        if rule["type"] == "label":
            rule_labels.add(rule["value"].upper())
    # Always consider INBOX and TRASH as relevant
    rule_labels.update(["INBOX", "TRASH"])

    def is_relevant_label_change(added, removed):
        # Only recategorize if any added/removed label is relevant
        for label in (added or []) + (removed or []):
            if label.upper() in rule_labels:
                return True
        return False

    updated_count = 0
    for gmail_id, changes in label_changes.items():
        email = db.query(Email).filter(
            Email.user_id == user.id,
            Email.gmail_id == gmail_id
        ).first()
        if not email:
            logger.debug(f"[GMAIL→EA] Email {gmail_id} not found in database, skipping label update")
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
        logger.info(f"[GMAIL→EA] Processing label changes ({change_desc}): {email_desc}")
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
            # Only recategorize if relevant label changed
            if is_relevant_label_change(added_labels, removed_labels):
                email_data = {
                    'id': email.id,
                    'gmail_id': email.gmail_id,
                    'labels': list(current_labels),
                    'subject': email.subject,
                    'from_email': email.from_email,
                    'snippet': email.snippet,
                    'is_read': email.is_read
                }
                new_category = categorize_email(email_data, db, user.id, categorizer=categorizer)
                if email.category != new_category:
                    logger.info(f"[GMAIL→EA] Recategorized email from '{email.category}' to '{new_category}' after label changes: {email_desc}")
                    email.category = new_category
            updated_count += 1
    if updated_count > 0:
        db.commit()
        logger.info(f"[GMAIL→EA] Updated {updated_count} emails due to label changes")
    return updated_count

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
    if len(deleted_gmail_ids) > 0:
        sample_ids = deleted_gmail_ids[:min(5, len(deleted_gmail_ids))]
        logger.info(f"[SYNC] Sample deleted Gmail IDs: {sample_ids}")
    
    for gmail_id in deleted_gmail_ids:
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
    
    logger.info(f"[SYNC] Deletion summary: deleted_count={deleted_count}, not_found_count={not_found_count}, already_deleted_count={already_deleted_count}")
    
    if deleted_count > 0:
        db.commit()
        logger.info(f"[SYNC] Added TRASH label to {deleted_count} emails")
    
    return deleted_count

# Removed old implementation as we're now using the modular categorizer
# The function is now directly imported from email_categorizer.py

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
    
    # Simplified mapping from categories to Gmail standard labels
    # We'll only use Gmail's standard labels that don't require creating custom labels
    category_to_label = {
        'trash': 'TRASH',  # Only standard label for trash
        # We don't map other categories to Gmail labels to avoid intrusive changes
    }
    
    # We'll only remove the INBOX label for archived emails and add TRASH for trash
    # This is much less intrusive than creating custom CATEGORY_* labels
    
    updated_count = 0
    for email in pending_emails:
        try:
            # Get current labels without our update marker
            current_labels = set(email.labels)
            current_labels.remove("EA_NEEDS_LABEL_UPDATE")
            
            # Initialize empty lists for labels to add and remove
            add_labels = []
            remove_labels = []
            
            # Only handle special cases: trash, archive
            # For all other categories, we won't modify Gmail labels directly
            
            # Handle trash category
            if email.category == 'trash':
                add_labels.append('TRASH')
                # Remove from inbox when trashing
                if 'INBOX' in current_labels:
                    remove_labels.append('INBOX')
            
            # Handle archive - just remove from inbox
            elif email.category == 'archive':
                if 'INBOX' in current_labels:
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

async def perform_full_sync(db: Session, user: User) -> Dict[str, Any]:
    """
    Perform a full sync of all emails from Gmail.
    This is used when the historyId is invalid or a full sync is forced.
    """
    sync_start_time = datetime.now(timezone.utc)
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  PERFORMING FULL SYNC                                    ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    logger.info(f"User: {user.email}")

    # Fetch all emails from Gmail
    try:
        # Create a callback to update credentials when refreshed
        def on_credentials_refresh(updated_credentials):
            update_user_credentials(db, user, updated_credentials)
        
        # We need to get the latest historyId after fetching all emails.
        # The Gmail API doesn't directly provide a way to get the current historyId
        # without a history.list call. So, we'll fetch emails and then get the
        # historyId from the most recent email.
        all_emails_raw = await gmail.fetch_emails_from_gmail(user.credentials, max_results=10000, on_credentials_refresh=on_credentials_refresh) # A large number to get all emails

        if not all_emails_raw:
            logger.warning("[SYNC] No emails found during full sync.")
            return {"status": "success", "message": "No emails found to sync.", "sync_count": 0}

        # Get the latest historyId from the most recent email
        latest_history_id = all_emails_raw[0].get('raw_data', {}).get('historyId')

        # Process and store the emails
        processed_emails = process_and_store_emails(db, user, all_emails_raw)
        new_email_count = len(processed_emails)

        # Update the sync checkpoint
        email_sync = get_or_create_email_sync(db, user)
        email_sync.last_history_id = latest_history_id
        email_sync.last_fetched_at = sync_start_time
        db.commit()

        sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
        logger.info(f"[SYNC] Full sync completed in {sync_duration:.2f} seconds. Processed {new_email_count} emails.")

        return {
            "status": "success",
            "message": f"Successfully performed a full sync, processing {new_email_count} emails.",
            "sync_count": new_email_count,
            "sync_method": "full_sync"
        }

    except Exception as e:
        logger.error(f"[SYNC] Error during full sync: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Full sync failed: {str(e)}",
            "sync_count": 0,
            "sync_method": "full_sync_error"
        }


async def sync_emails_since_last_fetch(db: Session, user: User, use_current_date: bool = False, force_full_sync: bool = False) -> Dict[str, Any]:
    """
    Sync emails since the last fetch using Gmail's historyId for incremental sync
    
    Args:
        db: Database session
        user: User model instance
        use_current_date: If True, use current date as checkpoint instead of next day
        force_full_sync: If True, force a full sync ignoring the last checkpoint date
        
    Returns:
        Dictionary with sync results
    """
    # Start timer for performance tracking
    sync_start_time = datetime.now(timezone.utc)
    sync_start_timestamp = sync_start_time.isoformat()
    
    # Get user ID for logging
    user_id = user.id
    
    # Log sync start
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  STARTING EMAIL SYNC                                     ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    logger.info(f"User: {user.email}")
    logger.info(f"Time: {sync_start_timestamp}")
    
    # Get or create email sync record
    email_sync = get_or_create_email_sync(db, user)
    
    # Log last sync time and history ID
    logger.info(f"Last sync: {email_sync.last_fetched_at}")
    logger.info(f"History ID: {email_sync.last_history_id}")
    
    # Store the original token for comparison later
    original_token = user.credentials.get('token') if user.credentials else None
    
    # Make a copy of the user object to avoid modifying the original
    # This allows us to refresh the token without affecting the original user object
    # until we explicitly update it
    fresh_user = User(
        id=user.id,
        email=user.email,
        name=user.name,
        credentials=user.credentials.copy() if user.credentials else None
    )
    
    # Get credentials for API calls
    credentials = fresh_user.credentials
    
    if not credentials:
        logger.error(f"[SYNC] No credentials found for user {user_id}")
        return {
            "status": "error",
            "message": "No credentials found",
            "sync_count": 0,
            "sync_started_at": sync_start_timestamp,
            "user_id": user_id,
            "sync_method": "error"
        }
    
    # Get the list of already processed email IDs to filter them out
    existing_gmail_ids = db.query(Email.gmail_id).filter(
        Email.user_id == user_id
    ).all()
    existing_gmail_ids = [id[0] for id in existing_gmail_ids]
    
    # Process pending operations - push changes from EA to Gmail
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  PROCESSING EA → GMAIL OPERATIONS                        ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    
    ops_start_time = datetime.now(timezone.utc)
    try:
        logger.info(f"[SYNC] Processing pending operations with user credentials")
        operations_result = await email_operations_service.process_pending_operations(db, fresh_user, credentials)
        logger.info(f"[SYNC] Operations processing completed successfully")
    except Exception as e:
        logger.error(f"[SYNC] Error during operations processing: {str(e)}")
        return {
            "status": "error",
            "message": f"Email sync failed: {str(e)}",
            "sync_count": 0,
            "sync_started_at": sync_start_timestamp,
            "user_id": user_id,
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
    
    # Fetch changes from Gmail
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  FETCHING GMAIL → EA CHANGES                             ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    
    # Use the history ID from the last sync if available
    history_id = email_sync.last_history_id
    logger.info(f"Using history ID: {history_id}")
    
    # If no history ID is available, perform a full sync
    if not history_id:
        logger.info(f"No history ID available, performing full sync")
        return await perform_full_sync(db, user)
    
    # Fetch changes from Gmail
    try:
        # Create a callback to update credentials when refreshed
        def on_credentials_refresh(updated_credentials):
            update_user_credentials(db, fresh_user, updated_credentials)
        
        gmail_service = await gmail.get_gmail_service(credentials, on_credentials_refresh)
        
        # Fetch history changes
        history_result = await gmail.fetch_history_changes(
            gmail_service, 
            history_id,
            max_pages=5
        )
        
        new_history_id = history_result.get("new_history_id")
        new_emails_raw = history_result.get("new_emails", [])
        deleted_ids = history_result.get("deleted_ids", [])
        label_changes = history_result.get("label_changes", {})
        
        emails_checked = len(new_emails_raw)  # Track all emails fetched from Gmail
        
        # If we got a valid history ID back, process the results
        if new_history_id and new_history_id != email_sync.last_history_id:
            logger.info(f"History ID changed: {email_sync.last_history_id} → {new_history_id}")
            
            # Track total emails found vs filtered
            total_found = len(new_emails_raw)
            already_processed = 0
            
            # Initialize new_emails list
            new_emails = []
            
            # Filter out emails that have already been processed
            for email in new_emails_raw:
                if email['gmail_id'] not in existing_gmail_ids:
                    new_emails.append(email)
                else:
                    already_processed += 1
                    logger.debug(f"[SYNC] Skipping already processed email: {email['gmail_id']}")
            
            deleted_email_ids = deleted_ids
            
            # Process label changes (mark as read/unread, deleted, etc.)
            label_changes_count = process_label_changes(db, fresh_user, label_changes)
            
            # Process new emails
            new_email_count = 0
            if new_emails:
                logger.info(f"[SYNC] Processing {len(new_emails)} new emails")
                processed_emails = process_and_store_emails(db, fresh_user, new_emails)
                new_email_count = len(processed_emails)
                logger.info(f"[SYNC] Processed {new_email_count} new emails")
            
            # Process deleted emails
            deleted_email_count = 0
            if deleted_email_ids:
                logger.info(f"[SYNC] Processing {len(deleted_email_ids)} deleted emails")
                deleted_email_count = mark_emails_deleted(db, fresh_user, deleted_email_ids)
                logger.info(f"[SYNC] Marked {deleted_email_count} emails as deleted")
            
            # Update the sync checkpoint
            email_sync.last_history_id = new_history_id
            email_sync.last_fetched_at = datetime.now(timezone.utc)
            db.commit()
            
            # Calculate sync duration
            sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
            
            # Return success with counts
            return {
                "status": "success",
                "message": f"Synced {new_email_count} new emails, {deleted_email_count} deleted, and {label_changes_count} label changes",
                "sync_count": new_email_count + deleted_email_count + label_changes_count,
                "new_email_count": new_email_count,
                "deleted_email_count": deleted_email_count,
                "label_changes_count": label_changes_count,
                "emails_checked": emails_checked,
                "sync_started_at": sync_start_timestamp,
                "user_id": user_id,
                "sync_method": "history",
                "debug_info": {
                    "last_history_id": str(email_sync.last_history_id),
                    "new_history_id": str(new_history_id),
                    "sync_duration_seconds": sync_duration
                }
            }
        else:
            # No changes detected from Gmail
            logger.info(f"No changes detected from Gmail")
            
            # Update the sync checkpoint timestamp even if no changes
            email_sync.last_fetched_at = datetime.now(timezone.utc)
            db.commit()
            
            # Calculate sync duration
            sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
            
            # Check if we processed any operations
            if operations_processed > 0 and operations_succeeded > 0:
                # We processed operations but didn't detect Gmail changes
                logger.warning(f"╔══════════════════════════════════════════════════════════════════════════╗")
                logger.warning(f"║                  OPERATIONS PROCESSED BUT NO GMAIL CHANGES               ║")
                logger.warning(f"╚══════════════════════════════════════════════════════════════════════════╝")
                logger.warning(f"Processed {operations_succeeded} operations successfully, but no changes detected from Gmail")
                
                return {
                    "status": "success",
                    "message": f"Processed {operations_succeeded} operations successfully",
                    "sync_count": operations_succeeded,
                    "operations_processed": operations_processed,
                    "operations_succeeded": operations_succeeded,
                    "operations_failed": operations_failed,
                    "emails_checked": 0,
                    "sync_started_at": sync_start_timestamp,
                    "user_id": user_id,
                    "sync_method": "operations_only",
                    "debug_info": {
                        "last_history_id": str(email_sync.last_history_id),
                        "new_history_id": str(new_history_id) if new_history_id else "None",
                        "sync_duration_seconds": sync_duration
                    }
                }
            else:
                # No changes detected from Gmail and no operations processed
                logger.warning(f"╔══════════════════════════════════════════════════════════════════════════╗")
                logger.warning(f"║                  NO CHANGES DETECTED                                     ║")
                logger.warning(f"╚══════════════════════════════════════════════════════════════════════════╝")
                logger.warning(f"History ID unchanged: {email_sync.last_history_id}")
                
                return {
                    "status": "warning",
                    "message": "No changes detected since last sync",
                    "sync_count": 0,
                    "emails_checked": 0,
                    "sync_started_at": sync_start_timestamp,
                    "user_id": user_id,
                    "sync_method": "history_no_changes",
                    "debug_info": {
                        "last_history_id": str(email_sync.last_history_id),
                        "new_history_id": str(new_history_id) if new_history_id else str(email_sync.last_history_id),
                        "sync_duration_seconds": sync_duration
                    }
                }
    except HttpError as e:
        if e.resp.status == 404:
            logger.warning(f"[SYNC] History ID {email_sync.last_history_id} not found. Triggering a full sync.")
            email_sync.last_history_id = None
            db.commit()
            return await perform_full_sync(db, user)
        else:
            logger.error(f"[SYNC] HTTP error during history sync: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"HTTP error during sync: {str(e)}", "sync_count": 0}
    except Exception as e:
        logger.error(f"[SYNC] Error using history-based approach: {str(e)}", exc_info=True)
        return {
            "status": "error", 
            "message": f"History sync error: {str(e)}",
            "sync_count": 0,
            "sync_started_at": sync_start_timestamp,
            "user_id": str(user_id),
            "sync_method": "error"
        } 

def update_user_credentials(db: Session, user: User, updated_credentials: Dict[str, Any]) -> None:
    """
    Update user's credentials in the database with refreshed tokens.
    """
    try:
        user.credentials = updated_credentials
        db.commit()
        logger.info(f"[SYNC] Updated credentials for user {user.email}")
    except Exception as e:
        logger.error(f"[SYNC] Failed to update credentials for user {user.email}: {str(e)}")
        db.rollback()
        raise 