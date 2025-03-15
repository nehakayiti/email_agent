from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
import logging
import json
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.email import Email
from ..models.user import User
from ..models.email_operation import EmailOperation, OperationType, OperationStatus
from . import gmail
from ..utils.naive_bayes_classifier import record_trash_event

logger = logging.getLogger(__name__)

def create_operation(
    db: Session,
    user: User,
    email: Email,
    operation_type: str,
    operation_data: Dict[str, Any]
) -> EmailOperation:
    """
    Create a new email operation record to track pending sync to Gmail
    
    Args:
        db: Database session
        user: User model instance
        email: Email model instance
        operation_type: Type of operation (from OperationType enum)
        operation_data: JSON data with operation details
        
    Returns:
        New EmailOperation instance
    """
    logger.info(f"[OPS] Creating new {operation_type} operation for email {email.id} (Gmail ID: {email.gmail_id})")
    
    # Create new operation
    operation = EmailOperation(
        email_id=email.id,
        user_id=user.id,
        operation_type=operation_type,
        operation_data=operation_data,
        status=OperationStatus.PENDING
    )
    
    # Add to DB and commit
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    logger.info(f"[OPS] Created operation id={operation.id}, type={operation_type}")
    return operation

def get_pending_operations(
    db: Session, 
    user_id: UUID, 
    limit: int = 100
) -> List[EmailOperation]:
    """
    Get pending operations for a user
    
    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of operations to return
        
    Returns:
        List of pending EmailOperation instances
    """
    operations = db.query(EmailOperation).filter(
        EmailOperation.user_id == user_id,
        EmailOperation.status == OperationStatus.PENDING
    ).order_by(
        EmailOperation.created_at.asc()
    ).limit(limit).all()
    
    logger.info(f"[OPS] Found {len(operations)} pending operations for user {user_id}")
    return operations

def mark_operation_complete(
    db: Session,
    operation: EmailOperation
) -> EmailOperation:
    """
    Mark an operation as completed
    
    Args:
        db: Database session
        operation: EmailOperation instance
        
    Returns:
        Updated EmailOperation instance
    """
    operation.status = OperationStatus.COMPLETED
    operation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(operation)
    logger.info(f"[OPS] Marked operation {operation.id} as completed")
    return operation

def mark_operation_failed(
    db: Session,
    operation: EmailOperation,
    error_message: str
) -> EmailOperation:
    """
    Mark an operation as failed
    
    Args:
        db: Database session
        operation: EmailOperation instance
        error_message: Error message
        
    Returns:
        Updated EmailOperation instance
    """
    operation.status = OperationStatus.FAILED
    operation.error_message = error_message
    operation.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(operation)
    logger.info(f"[OPS] Marked operation {operation.id} as failed: {error_message}")
    return operation

def update_operation_status(
    db: Session,
    operation: EmailOperation,
    status: str,
    error_message: Optional[str] = None
) -> EmailOperation:
    """
    Update the status of an operation
    
    Args:
        db: Database session
        operation: EmailOperation instance
        status: New status (from OperationStatus enum)
        error_message: Error message (only for failed operations)
        
    Returns:
        Updated EmailOperation instance
    """
    operation.status = status
    operation.updated_at = datetime.now(timezone.utc)
    
    if status == OperationStatus.COMPLETED:
        operation.completed_at = datetime.now(timezone.utc)
    
    if error_message and status == OperationStatus.FAILED:
        operation.error_message = error_message
    
    db.commit()
    db.refresh(operation)
    logger.info(f"[OPS] Updated operation {operation.id} status to {status}")
    return operation

async def execute_operation(
    db: Session,
    operation: EmailOperation,
    credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a single email operation by sending it to Gmail
    
    Args:
        db: Database session
        operation: EmailOperation to execute
        credentials: User's Gmail API credentials
        
    Returns:
        Dictionary with execution result
    """
    try:
        # Mark as processing
        operation.status = OperationStatus.PROCESSING
        operation.retries += 1
        operation.updated_at = datetime.now()
        db.commit()
        
        # Get the email and user
        email = db.query(Email).filter(Email.id == operation.email_id).first()
        user = db.query(User).filter(User.id == operation.user_id).first()
        
        if not email or not user:
            error_msg = f"Email or user not found for operation {operation.id}"
            logger.error(f"[OPS] {error_msg}")
            operation = mark_operation_failed(db, operation, error_msg)
            return {"success": False, "error": error_msg}
        
        # Format a descriptive email identifier for logs
        email_desc = f"'{email.subject[:40] if email.subject else 'No subject'}...' ({email.gmail_id})"
        
        logger.info(f"[EA→GMAIL] Processing {operation.operation_type} operation for email: {email_desc}")
        
        # Process based on operation type
        if operation.operation_type == OperationType.DELETE:
            # Move to trash
            logger.info(f"[EA→GMAIL] Trashing email: {email_desc}")
            result = await gmail.update_email_labels(
                credentials,
                email.gmail_id,
                add_labels=['TRASH'],
                remove_labels=['INBOX']
            )
            logger.info(f"[EA→GMAIL] ✓ Email moved to trash: {email_desc}")
            # Mark operation as completed
            operation.status = OperationStatus.COMPLETED
            operation.completed_at = datetime.now()
            db.commit()
            return {"success": True}
            
        elif operation.operation_type == OperationType.ARCHIVE:
            # Archive email (remove from inbox)
            logger.info(f"[EA→GMAIL] Archiving email: {email_desc}")
            result = await gmail.update_email_labels(
                credentials,
                email.gmail_id,
                remove_labels=['INBOX']
            )
            logger.info(f"[EA→GMAIL] ✓ Email archived: {email_desc}")
            # Mark operation as completed
            operation.status = OperationStatus.COMPLETED
            operation.completed_at = datetime.now()
            db.commit()
            return {"success": True}
            
        elif operation.operation_type == OperationType.UPDATE_LABELS:
            # Update labels
            data = operation.operation_data
            add_labels = data.get('add_labels', [])
            remove_labels = data.get('remove_labels', [])
            
            # Special handling for UNREAD label
            has_unread_change = 'UNREAD' in add_labels or 'UNREAD' in remove_labels
            
            labels_desc = []
            if add_labels:
                labels_desc.append(f"adding {add_labels}")
            if remove_labels:
                labels_desc.append(f"removing {remove_labels}")
                
            action_desc = " & ".join(labels_desc)
            logger.info(f"[EA→GMAIL] Updating email labels ({action_desc}): {email_desc}")
            
            try:
                # Log detailed information about the operation
                logger.info(f"[EA→GMAIL] Gmail ID: {email.gmail_id}, Add labels: {add_labels}, Remove labels: {remove_labels}")
                
                result = await gmail.update_email_labels(
                    credentials,
                    email.gmail_id,
                    add_labels=add_labels,
                    remove_labels=remove_labels
                )
                
                # Log the result from Gmail API
                logger.info(f"[EA→GMAIL] Gmail API response: {result}")
                
                # Mark operation as completed
                operation.status = OperationStatus.COMPLETED
                operation.completed_at = datetime.now()
                db.commit()
                
                # Log success with special note for read/unread status
                if has_unread_change:
                    read_status = "unread" if 'UNREAD' in add_labels else "read"
                    logger.info(f"[EA→GMAIL] ✓ Email marked as {read_status} in Gmail: {email_desc}")
                else:
                    logger.info(f"[EA→GMAIL] ✓ Email labels updated: {email_desc}")
                
                return {"success": True}
            except Exception as e:
                error_msg = f"Error updating labels in Gmail: {str(e)}"
                logger.error(f"[EA→GMAIL] ✗ {error_msg}")
                operation = mark_operation_failed(db, operation, error_msg)
                return {"success": False, "error": error_msg}
            
        else:
            error_msg = f"Unsupported operation type: {operation.operation_type}"
            logger.error(f"[OPS] {error_msg}")
            operation = mark_operation_failed(db, operation, error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"Error executing operation: {str(e)}"
        logger.error(f"[OPS] {error_msg}", exc_info=True)
        operation = mark_operation_failed(db, operation, error_msg)
        return {"success": False, "error": error_msg}

async def process_pending_operations(
    db: Session,
    user: User,
    credentials: Dict[str, Any] = None,
    max_operations: int = 20
) -> Dict[str, Any]:
    """
    Process pending operations for a user
    
    Args:
        db: Database session
        user: User model instance
        credentials: User's Gmail API credentials
        max_operations: Maximum number of operations to process in one batch
        
    Returns:
        Dictionary with processing results
    """
    # Get pending operations
    operations = get_pending_operations(db, user.id, limit=max_operations)
    
    if not operations:
        logger.info(f"[OPS] No pending operations for user {user.id}")
        return {
            "status": "success",
            "message": "No pending operations",
            "processed_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "retry_count": 0
        }
    
    logger.info(f"[OPS] Found {len(operations)} pending operations for user {user.id}")
    logger.info(f"[OPS] Processing {len(operations)} pending operations for user {user.id}")
    
    # Process each operation
    results = {
        "success": 0,
        "failure": 0,
        "retry": 0
    }
    
    for operation in operations:
        operation_id = operation.id
        operation_type = operation.operation_type
        logger.info(f"[OPS] Processing operation {operation_id}: {operation_type}")
        
        try:
            # Execute the operation
            result = await execute_operation(db, operation, credentials)
            
            # Check the operation status after execution
            refreshed_operation = db.query(EmailOperation).filter(EmailOperation.id == operation_id).first()
            
            if refreshed_operation.status == OperationStatus.COMPLETED:
                results["success"] += 1
                logger.info(f"[OPS] Operation {operation_id} completed successfully")
            elif refreshed_operation.status == OperationStatus.FAILED:
                results["failure"] += 1
                logger.info(f"[OPS] Operation {operation_id} failed: {refreshed_operation.error_message}")
            elif refreshed_operation.status == OperationStatus.RETRYING:
                results["retry"] += 1
                logger.info(f"[OPS] Operation {operation_id} scheduled for retry")
            else:
                logger.warning(f"[OPS] Operation {operation_id} has unexpected status: {refreshed_operation.status}")
        except Exception as e:
            logger.error(f"[OPS] Error processing operation {operation_id}: {str(e)}", exc_info=True)
            mark_operation_failed(db, operation, str(e))
            results["failure"] += 1
    
    # Return summary
    logger.info(
        f"[OPS] Processed {len(operations)} operations for user {user.id}: "
        f"{results['success']} succeeded, {results['failure']} failed, {results['retry']} retrying"
    )
    
    return {
        "status": "success",
        "message": f"Processed {len(operations)} operations",
        "processed_count": len(operations),
        "success_count": results["success"],
        "failure_count": results["failure"],
        "retry_count": results["retry"]
    }

async def process_operations(
    db: Session,
    user: User,
    credentials: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process pending email operations and sync them with Gmail
    
    Args:
        db: Database session
        user: User model instance
        credentials: User's Gmail API credentials
        
    Returns:
        Dictionary with results
    """
    logger.info(f"[OPERATIONS] Processing pending operations for user {user.id}")
    
    pending_operations = get_pending_operations(db, user.id)
    if not pending_operations:
        logger.info(f"[OPERATIONS] No pending operations for user {user.id}")
        return {"processed": 0, "succeeded": 0, "failed": 0}
    
    logger.info(f"[OPERATIONS] Found {len(pending_operations)} pending operations")
    
    success_count = 0
    failed_count = 0
    processed_operations = []
    
    for operation in pending_operations:
        try:
            # Mark as processing
            operation = update_operation_status(db, operation, OperationStatus.PROCESSING)
            
            # Execute the operation
            result = await execute_operation(db, operation, credentials)
            
            if result.get("success", False):
                # Mark as completed
                operation = update_operation_status(db, operation, OperationStatus.COMPLETED)
                success_count += 1
                processed_operations.append(operation)
            else:
                # Mark as failed
                error_message = result.get("error", "Unknown error")
                operation = update_operation_status(
                    db, operation, OperationStatus.FAILED, error_message
                )
                failed_count += 1
        except Exception as e:
            logger.error(f"[OPERATIONS] Error processing operation {operation.id}: {str(e)}", exc_info=True)
            # Mark as failed
            update_operation_status(
                db, operation, OperationStatus.FAILED, str(e)
            )
            failed_count += 1
    
    # Record trash events for training data
    try:
        # Only record operations that were successful
        trash_operations = [op for op in processed_operations if op.operation_type == OperationType.DELETE]
        if trash_operations:
            from .email_classifier_service import record_trash_operations
            record_trash_operations(db, trash_operations)
            logger.info(f"[OPERATIONS] Recorded {len(trash_operations)} trash events for training data")
    except Exception as e:
        logger.error(f"[OPERATIONS] Error recording trash events: {str(e)}", exc_info=True)
    
    logger.info(f"[OPERATIONS] Processed {len(pending_operations)} operations: {success_count} succeeded, {failed_count} failed")
    
    return {
        "processed": len(pending_operations),
        "succeeded": success_count,
        "failed": failed_count
    } 