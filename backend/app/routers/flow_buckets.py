"""
Flow Buckets API Router

This module provides REST API endpoints for flow bucket functionality.
It uses the flow_buckets service to organize emails into NOW/LATER/REFERENCE
buckets based on attention scores.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..dependencies import get_current_user
from app.models.user import User
from app.models.email import Email
from app.services.flow_buckets import (
    query_bucket_emails,
    get_bucket_counts,
    get_bucket_summary,
    BucketType
)
from pydantic import BaseModel, field_serializer
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/flow", tags=["flow-buckets"])


class EmailResponse(BaseModel):
    """Response model for email data in flow buckets."""
    id: UUID
    gmail_id: str
    subject: Optional[str]
    from_email: Optional[str]
    received_at: Optional[datetime]
    snippet: Optional[str]
    labels: Optional[List[str]]
    is_read: bool
    attention_score: float
    category: Optional[str]
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    @field_serializer('received_at')
    def serialize_received_at(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None
    
    class Config:
        from_attributes = True


class BucketCountsResponse(BaseModel):
    """Response model for bucket counts."""
    now: int
    later: int
    reference: int


class BucketSummaryResponse(BaseModel):
    """Response model for comprehensive bucket summary."""
    buckets: BucketCountsResponse
    percentages: Dict[str, float]
    total_emails: int
    classification_rules: Dict[str, str]


@router.get("/buckets/now", response_model=List[EmailResponse])
async def get_now_bucket_emails(
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    order_by: str = Query("attention_score", description="Field to order by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get high-priority emails (attention_score >= 60) that need immediate attention.
    
    These are emails that should be handled NOW - they have high attention scores
    indicating urgency, importance, or time sensitivity.
    """
    try:
        emails = query_bucket_emails(
            db, 
            user_id=current_user.id,
            bucket="now",
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        
        # Convert to response format
        return [EmailResponse.from_orm(email) for email in emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving NOW bucket emails: {str(e)}")


@router.get("/buckets/later", response_model=List[EmailResponse])
async def get_later_bucket_emails(
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    order_by: str = Query("attention_score", description="Field to order by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medium-priority emails (30 <= attention_score < 60) that can be handled later.
    
    These emails are important but not urgent - they can be scheduled for later
    attention when high-priority items are handled.
    """
    try:
        emails = query_bucket_emails(
            db,
            user_id=current_user.id,
            bucket="later",
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        
        return [EmailResponse.from_orm(email) for email in emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving LATER bucket emails: {str(e)}")


@router.get("/buckets/reference", response_model=List[EmailResponse])
async def get_reference_bucket_emails(
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    order_by: str = Query("attention_score", description="Field to order by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get low-priority emails (attention_score < 30) for reference.
    
    These emails are typically newsletters, notifications, or other content
    that might be useful for reference but doesn't require immediate action.
    """
    try:
        emails = query_bucket_emails(
            db,
            user_id=current_user.id,
            bucket="reference",
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        
        return [EmailResponse.from_orm(email) for email in emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving REFERENCE bucket emails: {str(e)}")


@router.get("/bucket-counts", response_model=BucketCountsResponse)
async def get_bucket_counts_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the count of emails in each flow bucket.
    
    Returns the number of emails in NOW, LATER, and REFERENCE buckets
    for quick overview of email distribution.
    """
    try:
        counts = get_bucket_counts(db, user_id=current_user.id)
        return BucketCountsResponse(**counts)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bucket counts: {str(e)}")


@router.get("/bucket-summary", response_model=BucketSummaryResponse)
async def get_bucket_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive summary of all flow buckets.
    
    Returns bucket counts, percentages, total emails, and classification rules
    for complete overview of user's email organization.
    """
    try:
        summary = get_bucket_summary(db, user_id=current_user.id)
        return BucketSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bucket summary: {str(e)}")


@router.get("/buckets/{bucket_type}", response_model=List[EmailResponse])
async def get_bucket_emails_generic(
    bucket_type: BucketType,
    limit: int = Query(50, ge=1, le=100, description="Number of emails to return"),
    offset: int = Query(0, ge=0, description="Number of emails to skip"),
    order_by: str = Query("attention_score", description="Field to order by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generic endpoint to get emails from any bucket type.
    
    This provides a unified interface for accessing any bucket type
    while maintaining the same functionality as the specific endpoints.
    """
    try:
        emails = query_bucket_emails(
            db,
            user_id=current_user.id,
            bucket=bucket_type,
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        
        return [EmailResponse.from_orm(email) for email in emails]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {bucket_type} bucket emails: {str(e)}")