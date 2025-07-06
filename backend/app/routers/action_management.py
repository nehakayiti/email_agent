from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.user import User
from ..dependencies import get_current_user
from ..schemas.action_engine import (
    ActionRuleRequest,
    ActionRuleResponse,
    ActionPreviewResponse
)
from ..services.action_rule_service import (
    update_category_action_rule,
    get_action_rules_for_user,
    validate_action_rule,
    get_emails_affected_by_rule
)

router = APIRouter(prefix="/action-management", tags=["action-management"])

@router.post("/categories/{category_id}/action-rule", response_model=ActionRuleResponse)
async def create_or_update_action_rule(
    category_id: int,
    action_rule: ActionRuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update an action rule for a specific category.
    
    This endpoint allows users to configure automatic actions (ARCHIVE, TRASH)
    for emails in a specific category after a specified delay period.
    """
    try:
        # Validate the action rule
        if not validate_action_rule(action_rule.action, action_rule.delay_days):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action rule configuration"
            )
        
        # Update the action rule
        updated_category = update_category_action_rule(
            db=db,
            category_id=category_id,
            action=action_rule.action,
            delay_days=action_rule.delay_days,
            enabled=action_rule.enabled
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        return ActionRuleResponse(
            category_id=updated_category.id,
            category_name=updated_category.name,
            action=updated_category.action,
            delay_days=updated_category.action_delay_days,
            enabled=updated_category.action_enabled
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update action rule: {str(e)}"
        )

@router.get("/categories/{category_id}/action-rule", response_model=ActionRuleResponse)
async def get_action_rule(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current action rule configuration for a specific category.
    """
    try:
        # Get action rules for the user and find the specific category
        action_rules = get_action_rules_for_user(db, current_user.id)
        
        for rule in action_rules:
            if rule.id == category_id:
                return ActionRuleResponse(
                    category_id=rule.id,
                    category_name=rule.name,
                    action=rule.action,
                    delay_days=rule.action_delay_days,
                    enabled=rule.action_enabled
                )
        
        # If no action rule is configured, return a default response
        return ActionRuleResponse(
            category_id=category_id,
            category_name="Unknown",
            action=None,
            delay_days=None,
            enabled=False
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get action rule: {str(e)}"
        )

@router.delete("/categories/{category_id}/action-rule")
async def delete_action_rule(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete the action rule for a specific category.
    """
    try:
        # Clear the action rule by setting it to disabled with no action
        updated_category = update_category_action_rule(
            db=db,
            category_id=category_id,
            action=None,
            delay_days=None,
            enabled=False
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} not found"
            )
        
        return {"message": f"Action rule for category {category_id} has been deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete action rule: {str(e)}"
        )

@router.get("/categories/{category_id}/action-preview", response_model=ActionPreviewResponse)
async def get_action_preview(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a preview of emails that would be affected by the current action rule.
    """
    try:
        # Get emails that would be affected by the action rule
        affected_emails = get_emails_affected_by_rule(db, category_id)
        
        return ActionPreviewResponse(
            category_id=category_id,
            affected_email_count=len(affected_emails),
            affected_emails=affected_emails[:10]  # Limit to first 10 for preview
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get action preview: {str(e)}"
        )

@router.get("/action-rules", response_model=List[ActionRuleResponse])
async def get_all_action_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all action rules for the current user.
    """
    try:
        action_rules = get_action_rules_for_user(db, current_user.id)
        
        return [
            ActionRuleResponse(
                category_id=rule.id,
                category_name=rule.name,
                action=rule.action,
                delay_days=rule.action_delay_days,
                enabled=rule.action_enabled
            )
            for rule in action_rules
            if rule.has_action_rule()
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get action rules: {str(e)}"
        ) 