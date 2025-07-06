"""
Action Engine Service - Core business logic for automated email actions

This service implements the Action Engine functionality, including:
- Finding emails eligible for actions based on category rules
- Creating proposed actions for user approval
- Executing approved actions
- Managing the approval/rejection workflow
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.email import Email
from ..models.user import User
from ..models.email_category import EmailCategory
from ..models.proposed_action import ProposedAction, ProposedActionStatus
from ..models.email_operation import EmailOperation, OperationType, OperationStatus
from .email_operations_service import create_operation
from .action_rule_service import get_action_rules_for_user

logger = logging.getLogger(__name__)

def process_category_actions(
    db: Session, 
    user: User, 
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Main orchestrator for processing category actions
    
    This function finds all categories with action rules enabled,
    identifies eligible emails, and either creates proposed actions
    (dry run mode) or executes actions directly (execute mode).
    
    Args:
        db: Database session
        user: User model instance
        dry_run: If True, create ProposedAction records only
        
    Returns:
        Dictionary with processing results
    """
    logger.info(f"[ACTION_ENGINE] Starting category action processing for user {user.id} (dry_run={dry_run})")
    
    # Get all categories with action rules enabled
    action_rules = get_action_rules_for_user(db, user.id)
    
    if not action_rules:
        logger.info(f"[ACTION_ENGINE] No action rules found for user {user.id}")
        return {
            "success": True,
            "dry_run": dry_run,
            "categories_processed": 0,
            "emails_found": 0,
            "actions_created": 0,
            "operations_created": 0
        }
    
    total_emails_found = 0
    total_actions_created = 0
    total_operations_created = 0
    
    for category in action_rules:
        logger.info(f"[ACTION_ENGINE] Processing category: {category.name} (action: {category.action}, delay: {category.action_delay_days} days)")
        
        # Find eligible emails for this category
        eligible_emails = find_emails_for_action(db, user, category)
        
        if not eligible_emails:
            logger.info(f"[ACTION_ENGINE] No eligible emails found for category {category.name}")
            continue
        
        logger.info(f"[ACTION_ENGINE] Found {len(eligible_emails)} eligible emails for category {category.name}")
        total_emails_found += len(eligible_emails)
        
        for email in eligible_emails:
            if dry_run:
                # Create proposed action
                proposed_action = create_proposed_action(db, email, category, category.action)
                if proposed_action:
                    total_actions_created += 1
            else:
                # Execute action directly
                operation = execute_action(db, email, category, category.action)
                if operation:
                    total_operations_created += 1
    
    result = {
        "success": True,
        "dry_run": dry_run,
        "categories_processed": len(action_rules),
        "emails_found": total_emails_found,
        "actions_created": total_actions_created,
        "operations_created": total_operations_created
    }
    
    logger.info(f"[ACTION_ENGINE] Completed processing: {result}")
    return result

def find_emails_for_action(
    db: Session, 
    user: User, 
    category: EmailCategory
) -> List[Email]:
    """
    Find emails eligible for action based on category rules
    
    Args:
        db: Database session
        user: User model instance
        category: EmailCategory with action rule configured
        
    Returns:
        List of eligible Email instances
    """
    if not category.has_action_rule():
        logger.warning(f"[ACTION_ENGINE] Category {category.name} has no action rule configured")
        return []
    
    # Calculate the cutoff date based on action delay
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=category.action_delay_days)
    
    # Build query for eligible emails
    query = db.query(Email).filter(
        Email.user_id == user.id,
        Email.category == category.name,
        Email.received_at <= cutoff_date,
        # Only consider emails that are still in INBOX (not already archived/trashed)
        Email.labels.contains(['INBOX'])
    )
    
    # Exclude emails that already have pending proposed actions for this category
    existing_proposals = db.query(ProposedAction.email_id).filter(
        ProposedAction.user_id == user.id,
        ProposedAction.category_id == category.id,
        ProposedAction.status == ProposedActionStatus.PENDING
    ).subquery()
    
    query = query.filter(~Email.id.in_(existing_proposals))
    
    # Exclude emails that already have pending operations
    existing_operations = db.query(EmailOperation.email_id).filter(
        EmailOperation.user_id == user.id,
        EmailOperation.status.in_([OperationStatus.PENDING, OperationStatus.PROCESSING])
    ).subquery()
    
    query = query.filter(~Email.id.in_(existing_operations))
    
    # Order by received date (oldest first)
    query = query.order_by(Email.received_at.asc())
    
    eligible_emails = query.all()
    
    logger.info(f"[ACTION_ENGINE] Found {len(eligible_emails)} eligible emails for category {category.name}")
    return eligible_emails

def create_proposed_action(
    db: Session, 
    email: Email, 
    category: EmailCategory, 
    action_type: str
) -> Optional[ProposedAction]:
    """
    Create a proposed action record for user approval
    
    Args:
        db: Database session
        email: Email model instance
        category: EmailCategory that triggered the action
        action_type: Type of action (ARCHIVE, TRASH, etc.)
        
    Returns:
        ProposedAction instance if created successfully, None otherwise
    """
    try:
        # Calculate email age in days
        email_age_days = (datetime.now(timezone.utc) - email.received_at).days
        
        # Generate reason for the action
        reason = f"Email is {email_age_days} days old and belongs to category '{category.display_name}' with {action_type.lower()} action rule"
        
        # Check if a proposal already exists
        existing_proposal = db.query(ProposedAction).filter(
            ProposedAction.email_id == email.id,
            ProposedAction.category_id == category.id,
            ProposedAction.status == ProposedActionStatus.PENDING
        ).first()
        
        if existing_proposal:
            logger.info(f"[ACTION_ENGINE] Proposal already exists for email {email.id} and category {category.id}")
            return existing_proposal
        
        # Create new proposed action
        proposed_action = ProposedAction(
            email_id=email.id,
            user_id=email.user_id,
            category_id=category.id,
            action_type=action_type,
            reason=reason,
            email_age_days=email_age_days,
            status=ProposedActionStatus.PENDING
        )
        
        db.add(proposed_action)
        db.commit()
        db.refresh(proposed_action)
        
        logger.info(f"[ACTION_ENGINE] Created proposed action {proposed_action.id} for email {email.id}")
        return proposed_action
        
    except Exception as e:
        logger.error(f"[ACTION_ENGINE] Error creating proposed action for email {email.id}: {str(e)}")
        db.rollback()
        return None

def execute_action(
    db: Session, 
    email: Email, 
    category: EmailCategory, 
    action_type: str
) -> Optional[EmailOperation]:
    """
    Execute an action by creating an EmailOperation
    
    Args:
        db: Database session
        email: Email model instance
        category: EmailCategory that triggered the action
        action_type: Type of action (ARCHIVE, TRASH, etc.)
        
    Returns:
        EmailOperation instance if created successfully, None otherwise
    """
    try:
        # Get user
        user = db.query(User).filter(User.id == email.user_id).first()
        if not user:
            logger.error(f"[ACTION_ENGINE] User not found for email {email.id}")
            return None
        
        # Prepare operation data
        operation_data = {
            "action_engine": True,
            "category_id": category.id,
            "category_name": category.name,
            "email_age_days": (datetime.now(timezone.utc) - email.received_at).days,
            "reason": f"Automated action from category '{category.display_name}'"
        }
        
        # Create operation using existing service
        operation = create_operation(
            db=db,
            user=user,
            email=email,
            operation_type=action_type,
            operation_data=operation_data
        )
        
        logger.info(f"[ACTION_ENGINE] Created operation {operation.id} for email {email.id}")
        return operation
        
    except Exception as e:
        logger.error(f"[ACTION_ENGINE] Error executing action for email {email.id}: {str(e)}")
        return None

def approve_proposed_action(
    db: Session, 
    action_id: UUID
) -> Optional[EmailOperation]:
    """
    Approve a proposed action and convert it to an EmailOperation
    
    Args:
        db: Database session
        action_id: ProposedAction ID to approve
        
    Returns:
        EmailOperation instance if created successfully, None otherwise
    """
    try:
        # Get the proposed action
        proposed_action = db.query(ProposedAction).filter(
            ProposedAction.id == action_id,
            ProposedAction.status == ProposedActionStatus.PENDING
        ).first()
        
        if not proposed_action:
            logger.error(f"[ACTION_ENGINE] Proposed action {action_id} not found or not pending")
            return None
        
        # Get the email and category
        email = db.query(Email).filter(Email.id == proposed_action.email_id).first()
        category = db.query(EmailCategory).filter(EmailCategory.id == proposed_action.category_id).first()
        
        if not email or not category:
            logger.error(f"[ACTION_ENGINE] Email or category not found for proposed action {action_id}")
            return None
        
        # Mark proposed action as approved
        proposed_action.status = ProposedActionStatus.APPROVED
        db.commit()
        
        # Execute the action
        operation = execute_action(db, email, category, proposed_action.action_type)
        
        if operation:
            logger.info(f"[ACTION_ENGINE] Approved and executed action {action_id} -> operation {operation.id}")
        else:
            logger.error(f"[ACTION_ENGINE] Failed to execute approved action {action_id}")
        
        return operation
        
    except Exception as e:
        logger.error(f"[ACTION_ENGINE] Error approving proposed action {action_id}: {str(e)}")
        db.rollback()
        return None

def reject_proposed_action(
    db: Session, 
    action_id: UUID
) -> bool:
    """
    Reject a proposed action
    
    Args:
        db: Database session
        action_id: ProposedAction ID to reject
        
    Returns:
        True if rejected successfully, False otherwise
    """
    try:
        # Get the proposed action
        proposed_action = db.query(ProposedAction).filter(
            ProposedAction.id == action_id,
            ProposedAction.status == ProposedActionStatus.PENDING
        ).first()
        
        if not proposed_action:
            logger.error(f"[ACTION_ENGINE] Proposed action {action_id} not found or not pending")
            return False
        
        # Mark as rejected
        proposed_action.status = ProposedActionStatus.REJECTED
        db.commit()
        
        logger.info(f"[ACTION_ENGINE] Rejected proposed action {action_id}")
        return True
        
    except Exception as e:
        logger.error(f"[ACTION_ENGINE] Error rejecting proposed action {action_id}: {str(e)}")
        db.rollback()
        return False

def cleanup_expired_proposals(
    db: Session, 
    max_age_days: int = 30
) -> int:
    """
    Remove old proposed actions that are no longer relevant
    
    Args:
        db: Database session
        max_age_days: Maximum age in days before proposals are considered expired
        
    Returns:
        Number of proposals cleaned up
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        
        # Find expired proposals
        expired_proposals = db.query(ProposedAction).filter(
            ProposedAction.created_at <= cutoff_date,
            ProposedAction.status.in_([ProposedActionStatus.PENDING, ProposedActionStatus.REJECTED])
        ).all()
        
        count = len(expired_proposals)
        
        if count > 0:
            # Mark as expired
            for proposal in expired_proposals:
                proposal.status = ProposedActionStatus.EXPIRED
            
            db.commit()
            logger.info(f"[ACTION_ENGINE] Cleaned up {count} expired proposals")
        
        return count
        
    except Exception as e:
        logger.error(f"[ACTION_ENGINE] Error cleaning up expired proposals: {str(e)}")
        db.rollback()
        return 0

def get_proposed_actions_for_user(
    db: Session,
    user_id: UUID,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[ProposedAction], int]:
    """
    Get proposed actions for a user with optional filtering
    
    Args:
        db: Database session
        user_id: User ID
        status: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        Tuple of (proposed_actions_list, total_count)
    """
    query = db.query(ProposedAction).filter(ProposedAction.user_id == user_id)
    
    if status:
        query = query.filter(ProposedAction.status == status)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    proposed_actions = query.order_by(
        ProposedAction.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return proposed_actions, total_count 