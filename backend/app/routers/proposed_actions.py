from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import get_db
from ..models.user import User
from ..dependencies import get_current_user
from ..schemas.action_engine import (
    ProposedActionItem,
    ProposedActionList,
    BulkActionRequest,
    ActionProcessRequest,
    ActionProcessResponse
)
from ..services.action_engine_service import (
    approve_proposed_action,
    reject_proposed_action,
    cleanup_expired_proposals,
    process_category_actions
)
from ..models.proposed_action import ProposedAction, ProposedActionStatus
from sqlalchemy import and_, or_

router = APIRouter(prefix="/proposed-actions", tags=["proposed-actions"])

@router.get("", response_model=ProposedActionList)
async def get_proposed_actions(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected, expired"),
    action_type: Optional[str] = Query(None, description="Filter by action type: ARCHIVE, TRASH"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get proposed actions with pagination and filtering.
    """
    try:
        # Build query filters
        filters = [ProposedAction.user_id == current_user.id]
        
        if status_filter:
            if status_filter not in [s.value for s in ProposedActionStatus]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter: {status_filter}"
                )
            filters.append(ProposedAction.status == status_filter)
        
        if action_type:
            filters.append(ProposedAction.action_type == action_type)
        
        if category_id:
            filters.append(ProposedAction.category_id == category_id)
        
        # Calculate pagination
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = db.query(ProposedAction).filter(*filters).count()
        
        # Get paginated results
        proposed_actions = (
            db.query(ProposedAction)
            .filter(*filters)
            .order_by(ProposedAction.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Convert to response models
        items = []
        for action in proposed_actions:
            items.append(ProposedActionItem(
                id=str(action.id),
                email_id=str(action.email_id),
                email_subject=action.email.subject if action.email else "Unknown",
                email_sender=action.email.from_email if action.email else "Unknown",
                email_date=action.email.received_date if action.email else None,
                category_id=action.category_id,
                category_name=action.category.name if action.category else "Unknown",
                action_type=action.action_type,
                reason=action.reason,
                email_age_days=action.email_age_days,
                created_at=action.created_at,
                status=action.status
            ))
        
        return ProposedActionList(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get proposed actions: {str(e)}"
        )

@router.post("/{action_id}/approve")
async def approve_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a specific proposed action.
    """
    try:
        result = approve_proposed_action(db, action_id)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"message": "Action approved successfully", "action_id": action_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve action: {str(e)}"
        )

@router.post("/{action_id}/reject")
async def reject_action(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a specific proposed action.
    """
    try:
        result = reject_proposed_action(db, action_id)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"message": "Action rejected successfully", "action_id": action_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject action: {str(e)}"
        )

@router.post("/bulk-approve")
async def bulk_approve_actions(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve multiple proposed actions in bulk.
    """
    try:
        approved_count = 0
        failed_actions = []
        
        for action_id in request.action_ids:
            result = approve_proposed_action(db, action_id)
            if result["success"]:
                approved_count += 1
            else:
                failed_actions.append({"action_id": action_id, "error": result["error"]})
        
        return {
            "message": f"Bulk approval completed",
            "approved_count": approved_count,
            "failed_count": len(failed_actions),
            "failed_actions": failed_actions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk approve actions: {str(e)}"
        )

@router.post("/bulk-reject")
async def bulk_reject_actions(
    request: BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject multiple proposed actions in bulk.
    """
    try:
        rejected_count = 0
        failed_actions = []
        
        for action_id in request.action_ids:
            result = reject_proposed_action(db, action_id)
            if result["success"]:
                rejected_count += 1
            else:
                failed_actions.append({"action_id": action_id, "error": result["error"]})
        
        return {
            "message": f"Bulk rejection completed",
            "rejected_count": rejected_count,
            "failed_count": len(failed_actions),
            "failed_actions": failed_actions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk reject actions: {str(e)}"
        )

@router.post("/process-dry-run", response_model=ActionProcessResponse)
async def process_dry_run(
    request: ActionProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run the action engine in dry-run mode to generate proposed actions.
    """
    try:
        result = process_category_actions(db, current_user, dry_run=True)
        
        return ActionProcessResponse(
            success=True,
            mode="dry_run",
            proposals_created=result.get("proposals_created", 0),
            emails_processed=result.get("emails_processed", 0),
            message="Dry run completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process dry run: {str(e)}"
        )

@router.post("/process-execute", response_model=ActionProcessResponse)
async def process_execute(
    request: ActionProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run the action engine in execute mode to process approved actions.
    """
    try:
        result = process_category_actions(db, current_user, dry_run=False)
        
        return ActionProcessResponse(
            success=True,
            mode="execute",
            operations_created=result.get("operations_created", 0),
            emails_processed=result.get("emails_processed", 0),
            message="Execute mode completed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process execute: {str(e)}"
        )

@router.post("/cleanup-expired")
async def cleanup_expired_proposals_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up expired proposed actions.
    """
    try:
        cleaned_count = cleanup_expired_proposals(db)
        
        return {
            "message": f"Cleanup completed",
            "expired_proposals_removed": cleaned_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup expired proposals: {str(e)}"
        )

@router.get("/stats")
async def get_proposed_actions_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about proposed actions for the current user.
    """
    try:
        # Get counts by status
        pending_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.status == ProposedActionStatus.PENDING
            )
        ).count()
        
        approved_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.status == ProposedActionStatus.APPROVED
            )
        ).count()
        
        rejected_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.status == ProposedActionStatus.REJECTED
            )
        ).count()
        
        expired_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.status == ProposedActionStatus.EXPIRED
            )
        ).count()
        
        # Get counts by action type
        archive_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.action_type == "ARCHIVE"
            )
        ).count()
        
        trash_count = db.query(ProposedAction).filter(
            and_(
                ProposedAction.user_id == current_user.id,
                ProposedAction.action_type == "TRASH"
            )
        ).count()
        
        return {
            "total_proposals": pending_count + approved_count + rejected_count + expired_count,
            "by_status": {
                "pending": pending_count,
                "approved": approved_count,
                "rejected": rejected_count,
                "expired": expired_count
            },
            "by_action_type": {
                "archive": archive_count,
                "trash": trash_count
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get proposed actions stats: {str(e)}"
        ) 