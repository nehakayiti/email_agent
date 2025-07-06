"""
Sync Coordinator Service - Orchestrates the email sync process

This service coordinates the entire sync process by orchestrating calls to:
- gmail_service: For Gmail API interactions
- processing_service: For database operations
- categorization_service: For email categorization
- email_operations_service: For processing pending operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.email_sync import EmailSync
from . import gmail_service
from . import processing_service
from . import categorization_service
from . import email_operations_service
import time

logger = logging.getLogger(__name__)

async def sync_emails_since_last_fetch(
    db: Session, 
    user: User, 
    use_current_date: bool = False, 
    force_full_sync: bool = False
) -> Dict[str, Any]:
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
    email_sync = processing_service.get_or_create_email_sync(db, user)
    
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
    existing_gmail_ids = processing_service.get_existing_gmail_ids(db, user_id)
    
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
        
        gmail_service_instance = await gmail_service.get_gmail_service(credentials, on_credentials_refresh)
        
        # Fetch history changes
        history_result = await gmail_service.fetch_history_changes(
            gmail_service_instance, 
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
            
            # Filter out emails that have already been processed
            new_emails = processing_service.filter_new_emails(new_emails_raw, existing_gmail_ids)
            
            deleted_email_ids = deleted_ids
            
            # Process label changes (mark as read/unread, deleted, etc.)
            label_changes_count = processing_service.process_label_changes(db, fresh_user, label_changes)
            
            # Process new emails
            new_email_count = 0
            if new_emails:
                logger.info(f"[SYNC] Processing {len(new_emails)} new emails")
                processed_emails = processing_service.process_and_store_emails(db, fresh_user, new_emails)
                new_email_count = len(processed_emails)
                logger.info(f"[SYNC] Processed {new_email_count} new emails")
                
                # Categorize the new emails
                categorized_count = categorization_service.categorize_emails_batch(db, processed_emails, user_id)
                logger.info(f"[SYNC] Categorized {categorized_count} new emails")
            
            # Process deleted emails
            deleted_email_count = 0
            if deleted_email_ids:
                logger.info(f"[SYNC] Processing {len(deleted_email_ids)} deleted emails")
                deleted_email_count = processing_service.mark_emails_deleted(db, fresh_user, deleted_email_ids)
                logger.info(f"[SYNC] Marked {deleted_email_count} emails as deleted")
            
            # Update the sync checkpoint
            processing_service.update_sync_checkpoint(db, email_sync, datetime.now(timezone.utc), new_history_id)
            
            # Calculate sync duration
            sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
            
            # Log sync summary
            logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
            logger.info(f"║                  SYNC COMPLETED SUCCESSFULLY                           ║")
            logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
            logger.info(f"Sync Duration: {sync_duration:.2f} seconds")
            logger.info(f"New Emails: {new_email_count}")
            logger.info(f"Deleted Emails: {deleted_email_count}")
            logger.info(f"Label Changes: {label_changes_count}")
            logger.info(f"Operations Processed: {operations_processed}")
            logger.info(f"New History ID: {new_history_id}")
            
            return {
                "status": "success",
                "message": "Email sync completed successfully",
                "sync_count": new_email_count,
                "sync_started_at": sync_start_timestamp,
                "sync_duration": sync_duration,
                "user_id": user_id,
                "sync_method": "incremental",
                "new_emails": new_email_count,
                "deleted_emails": deleted_email_count,
                "label_changes": label_changes_count,
                "operations_processed": operations_processed,
                "operations_succeeded": operations_succeeded,
                "operations_failed": operations_failed,
                "operations_retrying": operations_retrying,
                "new_history_id": new_history_id,
                "emails_checked": emails_checked
            }
        else:
            # No changes detected
            sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
            logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
            logger.info(f"║                  NO CHANGES DETECTED                                  ║")
            logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
            logger.info(f"Sync Duration: {sync_duration:.2f} seconds")
            logger.info(f"Operations Processed: {operations_processed}")
            
            return {
                "status": "success",
                "message": "No changes detected",
                "sync_count": 0,
                "sync_started_at": sync_start_timestamp,
                "sync_duration": sync_duration,
                "user_id": user_id,
                "sync_method": "no_changes",
                "new_emails": 0,
                "deleted_emails": 0,
                "label_changes": 0,
                "operations_processed": operations_processed,
                "operations_succeeded": operations_succeeded,
                "operations_failed": operations_failed,
                "operations_retrying": operations_retrying,
                "new_history_id": history_id,
                "emails_checked": emails_checked
            }
    
    except Exception as e:
        logger.error(f"[SYNC] Error during incremental sync: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Incremental sync failed: {str(e)}",
            "sync_count": 0,
            "sync_started_at": sync_start_timestamp,
            "user_id": user_id,
            "sync_method": "incremental_sync_error"
        }

async def perform_full_sync(db: Session, user: User) -> Dict[str, Any]:
    """
    Perform a full sync of all emails from Gmail
    
    Args:
        db: Database session
        user: User model instance
        
    Returns:
        Dictionary with sync results
    """
    sync_start_time = datetime.now(timezone.utc)
    sync_start_timestamp = sync_start_time.isoformat()
    user_id = user.id
    
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  STARTING FULL SYNC                                      ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    logger.info(f"User: {user.email}")
    logger.info(f"Time: {sync_start_timestamp}")
    
    try:
        # Get credentials
        credentials = user.credentials
        if not credentials:
            logger.error(f"[SYNC] No credentials found for user {user_id}")
            return {
                "status": "error",
                "message": "No credentials found",
                "sync_count": 0,
                "sync_started_at": sync_start_timestamp,
                "user_id": user_id,
                "sync_method": "full_sync_error"
            }
        
        # Create a callback to update credentials when refreshed
        def on_credentials_refresh(updated_credentials):
            update_user_credentials(db, user, updated_credentials)
        
        # Fetch emails from Gmail
        logger.info(f"[SYNC] Fetching emails from Gmail...")
        emails_data = await gmail_service.fetch_emails_from_gmail(
            credentials, 
            max_results=100,  # Limit for full sync
            on_credentials_refresh=on_credentials_refresh
        )
        
        if not emails_data:
            logger.info(f"[SYNC] No emails found in Gmail")
            return {
                "status": "success",
                "message": "No emails found in Gmail",
                "sync_count": 0,
                "sync_started_at": sync_start_timestamp,
                "user_id": user_id,
                "sync_method": "full_sync_no_emails"
            }
        
        # Process and store emails
        logger.info(f"[SYNC] Processing {len(emails_data)} emails...")
        processed_emails = processing_service.process_and_store_emails(db, user, emails_data)
        
        # Categorize emails
        categorized_count = categorization_service.categorize_emails_batch(db, processed_emails, user_id)
        
        # Get or create sync record and update checkpoint
        email_sync = processing_service.get_or_create_email_sync(db, user)
        
        # Get new history ID for future incremental syncs
        gmail_service_instance = await gmail_service.get_gmail_service(credentials, on_credentials_refresh)
        if processed_emails:
            # Use the first email's history ID as our checkpoint
            first_email_id = processed_emails[0].gmail_id
            try:
                # This would require implementing get_message_history_id in gmail_service
                # For now, we'll just update the timestamp
                processing_service.update_sync_checkpoint(db, email_sync, datetime.now(timezone.utc))
            except Exception as e:
                logger.warning(f"[SYNC] Could not get history ID for {first_email_id}: {str(e)}")
                processing_service.update_sync_checkpoint(db, email_sync, datetime.now(timezone.utc))
        else:
            processing_service.update_sync_checkpoint(db, email_sync, datetime.now(timezone.utc))
        
        # Calculate sync duration
        sync_duration = (datetime.now(timezone.utc) - sync_start_time).total_seconds()
        
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  FULL SYNC COMPLETED                                    ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        logger.info(f"Sync Duration: {sync_duration:.2f} seconds")
        logger.info(f"Emails Processed: {len(processed_emails)}")
        logger.info(f"Emails Categorized: {categorized_count}")
        
        return {
            "status": "success",
            "message": "Full sync completed successfully",
            "sync_count": len(processed_emails),
            "sync_started_at": sync_start_timestamp,
            "sync_duration": sync_duration,
            "user_id": user_id,
            "sync_method": "full_sync",
            "new_emails": len(processed_emails),
            "deleted_emails": 0,
            "label_changes": 0,
            "operations_processed": 0,
            "operations_succeeded": 0,
            "operations_failed": 0,
            "operations_retrying": 0,
            "emails_categorized": categorized_count
        }
    
    except Exception as e:
        logger.error(f"[SYNC] Error during full sync: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Full sync failed: {str(e)}",
            "sync_count": 0,
            "sync_method": "full_sync_error"
        }

def update_user_credentials(db: Session, user: User, updated_credentials: Dict[str, Any]) -> None:
    """
    Update user credentials in the database when they are refreshed
    
    Args:
        db: Database session
        user: User model instance
        updated_credentials: Updated credentials dictionary
    """
    try:
        user.credentials = updated_credentials
        db.commit()
        logger.info(f"[SYNC] Updated credentials for user {user.id}")
    except Exception as e:
        logger.error(f"[SYNC] Error updating credentials for user {user.id}: {str(e)}")
        db.rollback()
        raise 