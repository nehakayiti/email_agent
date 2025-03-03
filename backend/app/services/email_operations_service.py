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

def execute_operation(
    db: Session,
    operation: EmailOperation
) -> Dict[str, Any]:
    """
    Execute a single email operation by sending it to Gmail
    
    Args:
        db: Database session
        operation: EmailOperation to execute
        
    Returns:
        Dictionary with execution result
    """
    try:
        # Mark as processing
        operation.status = OperationStatus.PROCESSING
        operation.retries += 1
        operation.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Get the email and user
        email = db.query(Email).filter(Email.id == operation.email_id).first()
        user = db.query(User).filter(User.id == operation.user_id).first()
        
        if not email or not user:
            error_msg = f"Email or user not found for operation {operation.id}"
            logger.error(f"[OPS] {error_msg}")
            return mark_operation_failed(db, operation, error_msg)
        
        # Format a descriptive email identifier for logs
        email_desc = f"'{email.subject[:40]}...' ({email.gmail_id})"
        
        logger.info(f"[EA→GMAIL] Processing {operation.operation_type} operation for email: {email_desc}")
        
        # Process based on operation type
        if operation.operation_type == OperationType.DELETE:
            # Move to trash
            logger.info(f"[EA→GMAIL] Trashing email: {email_desc}")
            result = gmail.update_email_labels(
                user.credentials,
                email.gmail_id,
                add_labels=['TRASH'],
                remove_labels=['INBOX']
            )
            logger.info(f"[EA→GMAIL] ✓ Email moved to trash: {email_desc}")
            
        elif operation.operation_type == OperationType.ARCHIVE:
            # Archive email (remove from inbox)
            logger.info(f"[EA→GMAIL] Archiving email: {email_desc}")
            result = gmail.update_email_labels(
                user.credentials,
                email.gmail_id,
                remove_labels=['INBOX']
            )
            logger.info(f"[EA→GMAIL] ✓ Email archived: {email_desc}")
            
        elif operation.operation_type == OperationType.UPDATE_LABELS:
            # Update labels
            data = operation.operation_data
            add_labels = data.get('add_labels', [])
            remove_labels = data.get('remove_labels', [])
            
            labels_desc = []
            if add_labels:
                labels_desc.append(f"adding {add_labels}")
            if remove_labels:
                labels_desc.append(f"removing {remove_labels}")
            
            labels_change = " & ".join(labels_desc)
            logger.info(f"[EA→GMAIL] Updating labels ({labels_change}): {email_desc}")
            
            result = gmail.update_email_labels(
                user.credentials,
                email.gmail_id,
                add_labels=add_labels,
                remove_labels=remove_labels
            )
            logger.info(f"[EA→GMAIL] ✓ Labels updated: {email_desc}")
            
        elif operation.operation_type == OperationType.MARK_READ:
            # Mark as read (remove UNREAD label)
            logger.info(f"[EA→GMAIL] Marking as read: {email_desc}")
            result = gmail.update_email_labels(
                user.credentials,
                email.gmail_id,
                remove_labels=['UNREAD']
            )
            logger.info(f"[EA→GMAIL] ✓ Marked as read: {email_desc}")
            
        elif operation.operation_type == OperationType.MARK_UNREAD:
            # Mark as unread (add UNREAD label)
            logger.info(f"[EA→GMAIL] Marking as unread: {email_desc}")
            result = gmail.update_email_labels(
                user.credentials,
                email.gmail_id,
                add_labels=['UNREAD']
            )
            logger.info(f"[EA→GMAIL] ✓ Marked as unread: {email_desc}")
            
        else:
            # Unknown operation type
            error_msg = f"Unknown operation type: {operation.operation_type}"
            logger.error(f"[OPS] {error_msg}")
            return mark_operation_failed(db, operation, error_msg)
            
        # If we got here, operation was successful
        return mark_operation_complete(db, operation)
            
    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"[EA→GMAIL] ✗ Error executing operation {operation.id}: "
            f"{error_msg[:100]}{'...' if len(error_msg) > 100 else ''}", 
            exc_info=True
        )
        
        # Check if we need to retry
        if "Rate Limit Exceeded" in error_msg or "ServiceUnavailable" in error_msg:
            operation.status = OperationStatus.RETRYING
            operation.error_message = error_msg
            operation.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"[EA→GMAIL] Operation {operation.id} marked for retry due to rate limit")
            return {"status": "retrying", "message": error_msg}
            
        # Mark as failed for other errors
        return mark_operation_failed(db, operation, error_msg)

def process_pending_operations(
    db: Session,
    user: User,
    max_operations: int = 20
) -> Dict[str, Any]:
    """
    Process pending operations for a user
    
    Args:
        db: Database session
        user: User model instance
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
        
    # Process each operation
    results = {
        "success": 0,
        "failure": 0,
        "retry": 0
    }
    
    for operation in operations:
        result = execute_operation(db, operation)
        
        if operation.status == OperationStatus.COMPLETED:
            results["success"] += 1
        elif operation.status == OperationStatus.FAILED:
            results["failure"] += 1
        elif operation.status == OperationStatus.RETRYING:
            results["retry"] += 1
    
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