"""
Action Rule Service - Management of action rules for email categories

This service handles the configuration and validation of action rules
for email categories, including CRUD operations and preview functionality.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.email_category import EmailCategory
from ..models.email import Email
from ..models.proposed_action import ProposedAction, ProposedActionStatus
from ..models.email_operation import EmailOperation, OperationStatus

logger = logging.getLogger(__name__)

# Valid action types
VALID_ACTION_TYPES = ["ARCHIVE", "TRASH"]

def update_category_action_rule(
    db: Session, 
    category_id: int, 
    action: Optional[str], 
    delay_days: Optional[int], 
    enabled: bool = False
) -> Optional[EmailCategory]:
    """
    Update the action rule for a category
    
    Args:
        db: Database session
        category_id: Category ID to update
        action: Action type (ARCHIVE, TRASH, or None to disable)
        delay_days: Number of days to wait before applying action
        enabled: Whether the action rule is enabled
        
    Returns:
        Updated EmailCategory instance if successful, None otherwise
    """
    try:
        # Validate the action rule
        if not validate_action_rule(action, delay_days):
            logger.error(f"[ACTION_RULE] Invalid action rule: action={action}, delay_days={delay_days}")
            return None
        
        # Get the category
        category = db.query(EmailCategory).filter(EmailCategory.id == category_id).first()
        if not category:
            logger.error(f"[ACTION_RULE] Category {category_id} not found")
            return None
        
        # Update the action rule
        category.set_action_rule(action, delay_days, enabled)
        
        db.commit()
        db.refresh(category)
        
        logger.info(f"[ACTION_RULE] Updated action rule for category {category_id}: action={action}, delay={delay_days}, enabled={enabled}")
        return category
        
    except Exception as e:
        logger.error(f"[ACTION_RULE] Error updating action rule for category {category_id}: {str(e)}")
        db.rollback()
        return None

def get_action_rules_for_user(
    db: Session, 
    user_id: UUID
) -> List[EmailCategory]:
    """
    Get all categories with action rules enabled for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of EmailCategory instances with action rules enabled
    """
    # For now, we only support system categories with action rules
    # In the future, this could be extended to support user-specific categories
    categories = db.query(EmailCategory).filter(
        EmailCategory.is_system == True,
        EmailCategory.action_enabled == True,
        EmailCategory.action.isnot(None),
        EmailCategory.action_delay_days.isnot(None)
    ).all()
    
    logger.info(f"[ACTION_RULE] Found {len(categories)} categories with action rules for user {user_id}")
    return categories

def validate_action_rule(
    action: Optional[str], 
    delay_days: Optional[int]
) -> bool:
    """
    Validate an action rule configuration
    
    Args:
        action: Action type (ARCHIVE, TRASH, or None)
        delay_days: Number of days to wait before applying action
        
    Returns:
        True if valid, False otherwise
    """
    # If action is None, the rule is being disabled (valid)
    if action is None:
        return True
    
    # Validate action type
    if action not in VALID_ACTION_TYPES:
        logger.error(f"[ACTION_RULE] Invalid action type: {action}")
        return False
    
    # Validate delay days
    if delay_days is None or delay_days < 0:
        logger.error(f"[ACTION_RULE] Invalid delay days: {delay_days}")
        return False
    
    # Reasonable upper limit (1 year)
    if delay_days > 365:
        logger.error(f"[ACTION_RULE] Delay days too high: {delay_days}")
        return False
    
    return True

def get_emails_affected_by_rule(
    db: Session, 
    category_id: int
) -> Dict[str, Any]:
    """
    Preview function to show how many emails would be affected by an action rule
    
    Args:
        db: Database session
        category_id: Category ID to check
        
    Returns:
        Dictionary with preview information
    """
    try:
        # Get the category
        category = db.query(EmailCategory).filter(EmailCategory.id == category_id).first()
        if not category:
            return {"error": "Category not found"}
        
        if not category.has_action_rule():
            return {
                "category_id": category_id,
                "category_name": category.name,
                "has_action_rule": False,
                "affected_emails": 0,
                "breakdown": {}
            }
        
        # Calculate the cutoff date based on action delay
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=category.action_delay_days)
        
        # Count emails that would be affected
        affected_emails_query = db.query(Email).filter(
            Email.category == category.name,
            Email.received_at <= cutoff_date,
            Email.labels.contains(['INBOX'])
        )
        
        # Exclude emails that already have pending proposed actions
        existing_proposals = db.query(ProposedAction.email_id).filter(
            ProposedAction.category_id == category_id,
            ProposedAction.status == ProposedActionStatus.PENDING
        ).subquery()
        
        affected_emails_query = affected_emails_query.filter(~Email.id.in_(existing_proposals))
        
        # Exclude emails that already have pending operations
        existing_operations = db.query(EmailOperation.email_id).filter(
            EmailOperation.status.in_([OperationStatus.PENDING, OperationStatus.PROCESSING])
        ).subquery()
        
        affected_emails_query = affected_emails_query.filter(~Email.id.in_(existing_operations))
        
        total_affected = affected_emails_query.count()
        
        # Get breakdown by age ranges
        breakdown = {}
        age_ranges = [
            (0, 7, "0-7 days"),
            (8, 30, "8-30 days"),
            (31, 90, "31-90 days"),
            (91, 365, "91-365 days"),
            (366, None, "Over 1 year")
        ]
        
        for min_days, max_days, label in age_ranges:
            if max_days is None:
                # Over 1 year
                range_cutoff = datetime.now(timezone.utc) - timedelta(days=min_days)
                count = affected_emails_query.filter(Email.received_at <= range_cutoff).count()
            else:
                # Specific range
                min_cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
                max_cutoff = datetime.now(timezone.utc) - timedelta(days=min_days)
                count = affected_emails_query.filter(
                    Email.received_at > min_cutoff,
                    Email.received_at <= max_cutoff
                ).count()
            
            breakdown[label] = count
        
        result = {
            "category_id": category_id,
            "category_name": category.name,
            "has_action_rule": True,
            "action": category.action,
            "delay_days": category.action_delay_days,
            "enabled": category.action_enabled,
            "affected_emails": total_affected,
            "breakdown": breakdown,
            "cutoff_date": cutoff_date.isoformat()
        }
        
        logger.info(f"[ACTION_RULE] Preview for category {category_id}: {total_affected} emails would be affected")
        return result
        
    except Exception as e:
        logger.error(f"[ACTION_RULE] Error getting preview for category {category_id}: {str(e)}")
        return {"error": str(e)}

def get_action_rule_stats(
    db: Session, 
    user_id: UUID
) -> Dict[str, Any]:
    """
    Get statistics about action rules for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with action rule statistics
    """
    try:
        # Get categories with action rules
        action_categories = get_action_rules_for_user(db, user_id)
        
        # Count proposed actions by status
        proposed_actions_stats = db.query(
            ProposedAction.status,
            func.count(ProposedAction.id).label('count')
        ).filter(
            ProposedAction.user_id == user_id
        ).group_by(ProposedAction.status).all()
        
        # Convert to dictionary
        proposed_actions_by_status = {stat.status: stat.count for stat in proposed_actions_stats}
        
        # Count operations created by action engine
        action_engine_operations = db.query(EmailOperation).filter(
            EmailOperation.user_id == user_id,
            EmailOperation.operation_data.contains({"action_engine": True})
        ).count()
        
        result = {
            "categories_with_rules": len(action_categories),
            "proposed_actions": {
                "total": sum(proposed_actions_by_status.values()),
                "by_status": proposed_actions_by_status
            },
            "action_engine_operations": action_engine_operations,
            "categories": [
                {
                    "id": cat.id,
                    "name": cat.name,
                    "action": cat.action,
                    "delay_days": cat.action_delay_days,
                    "enabled": cat.action_enabled
                }
                for cat in action_categories
            ]
        }
        
        return result
        
    except Exception as e:
        logger.error(f"[ACTION_RULE] Error getting stats for user {user_id}: {str(e)}")
        return {"error": str(e)}

def disable_action_rule(
    db: Session, 
    category_id: int
) -> bool:
    """
    Disable the action rule for a category
    
    Args:
        db: Database session
        category_id: Category ID to disable
        
    Returns:
        True if disabled successfully, False otherwise
    """
    try:
        category = db.query(EmailCategory).filter(EmailCategory.id == category_id).first()
        if not category:
            logger.error(f"[ACTION_RULE] Category {category_id} not found")
            return False
        
        category.clear_action_rule()
        db.commit()
        
        logger.info(f"[ACTION_RULE] Disabled action rule for category {category_id}")
        return True
        
    except Exception as e:
        logger.error(f"[ACTION_RULE] Error disabling action rule for category {category_id}: {str(e)}")
        db.rollback()
        return False

def get_action_rule_history(
    db: Session,
    user_id: UUID,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get recent action rule activity for a user
    
    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of records to return
        
    Returns:
        List of action rule activity records
    """
    try:
        # Get recent proposed actions
        recent_proposals = db.query(ProposedAction).filter(
            ProposedAction.user_id == user_id
        ).order_by(
            ProposedAction.created_at.desc()
        ).limit(limit).all()
        
        # Get recent action engine operations
        recent_operations = db.query(EmailOperation).filter(
            EmailOperation.user_id == user_id,
            EmailOperation.operation_data.contains({"action_engine": True})
        ).order_by(
            EmailOperation.created_at.desc()
        ).limit(limit).all()
        
        # Combine and sort by date
        history = []
        
        for proposal in recent_proposals:
            history.append({
                "type": "proposed_action",
                "id": str(proposal.id),
                "action_type": proposal.action_type,
                "status": proposal.status,
                "created_at": proposal.created_at.isoformat(),
                "email_id": str(proposal.email_id),
                "category_id": proposal.category_id,
                "reason": proposal.reason
            })
        
        for operation in recent_operations:
            history.append({
                "type": "operation",
                "id": str(operation.id),
                "action_type": operation.operation_type,
                "status": operation.status,
                "created_at": operation.created_at.isoformat(),
                "email_id": str(operation.email_id),
                "operation_data": operation.operation_data
            })
        
        # Sort by created_at descending
        history.sort(key=lambda x: x["created_at"], reverse=True)
        
        return history[:limit]
        
    except Exception as e:
        logger.error(f"[ACTION_RULE] Error getting history for user {user_id}: {str(e)}")
        return [] 