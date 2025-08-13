"""
Flow Buckets API Router

This module provides REST API endpoints for flow bucket functionality.
It uses the flow_buckets service to organize emails into NOW/LATER/REFERENCE
buckets based on attention scores.

ENHANCED: Now includes debugging endpoints for the new scoring system.
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
from app.services.enhanced_attention_scoring import (
    debug_email_score,
    get_scoring_performance_stats,
    analyze_score_distribution,
    invalidate_score_cache
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
        
        # Convert to response format, using fresh score if available
        response_emails = []
        for email in emails:
            # Use fresh score if available, otherwise use stored score
            # Check if _current_attention_score exists and is a number (not a Mock)
            current_score = getattr(email, '_current_attention_score', None)
            if current_score is not None and isinstance(current_score, (int, float)):
                attention_score = current_score
            else:
                attention_score = email.attention_score
            response_email = EmailResponse(
                id=email.id,
                gmail_id=email.gmail_id,
                subject=email.subject,
                from_email=email.from_email,
                received_at=email.received_at,
                snippet=email.snippet,
                labels=email.labels,
                is_read=email.is_read,
                attention_score=attention_score,
                category=email.category
            )
            response_emails.append(response_email)
        return response_emails
        
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
        
        # Convert to response format, using fresh score if available
        response_emails = []
        for email in emails:
            # Use fresh score if available, otherwise use stored score
            # Check if _current_attention_score exists and is a number (not a Mock)
            current_score = getattr(email, '_current_attention_score', None)
            if current_score is not None and isinstance(current_score, (int, float)):
                attention_score = current_score
            else:
                attention_score = email.attention_score
            response_email = EmailResponse(
                id=email.id,
                gmail_id=email.gmail_id,
                subject=email.subject,
                from_email=email.from_email,
                received_at=email.received_at,
                snippet=email.snippet,
                labels=email.labels,
                is_read=email.is_read,
                attention_score=attention_score,
                category=email.category
            )
            response_emails.append(response_email)
        return response_emails
        
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
        
        # Convert to response format, using fresh score if available
        response_emails = []
        for email in emails:
            # Use fresh score if available, otherwise use stored score
            # Check if _current_attention_score exists and is a number (not a Mock)
            current_score = getattr(email, '_current_attention_score', None)
            if current_score is not None and isinstance(current_score, (int, float)):
                attention_score = current_score
            else:
                attention_score = email.attention_score
            response_email = EmailResponse(
                id=email.id,
                gmail_id=email.gmail_id,
                subject=email.subject,
                from_email=email.from_email,
                received_at=email.received_at,
                snippet=email.snippet,
                labels=email.labels,
                is_read=email.is_read,
                attention_score=attention_score,
                category=email.category
            )
            response_emails.append(response_email)
        return response_emails
        
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
        
        # Convert to response format, using fresh score if available
        response_emails = []
        for email in emails:
            # Use fresh score if available, otherwise use stored score
            # Check if _current_attention_score exists and is a number (not a Mock)
            current_score = getattr(email, '_current_attention_score', None)
            if current_score is not None and isinstance(current_score, (int, float)):
                attention_score = current_score
            else:
                attention_score = email.attention_score
            response_email = EmailResponse(
                id=email.id,
                gmail_id=email.gmail_id,
                subject=email.subject,
                from_email=email.from_email,
                received_at=email.received_at,
                snippet=email.snippet,
                labels=email.labels,
                is_read=email.is_read,
                attention_score=attention_score,
                category=email.category
            )
            response_emails.append(response_email)
        return response_emails
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {bucket_type} bucket emails: {str(e)}")


# ENHANCED SCORING DEBUG ENDPOINTS

@router.get("/debug/email/{email_id}/score", response_model=Dict[str, Any])
async def debug_email_score_endpoint(
    email_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed debugging information for an email's attention score.
    
    This endpoint provides a complete breakdown of how an email's attention score
    was calculated, including all components and factors considered.
    """
    try:
        # Get the email
        email = db.query(Email).filter(
            Email.id == email_id,
            Email.user_id == current_user.id
        ).first()
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get detailed score breakdown
        breakdown = debug_email_score(email)
        
        return {
            "status": "success",
            "email_id": email_id,
            "debug_info": breakdown,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error debugging email score: {str(e)}")


@router.get("/debug/performance", response_model=Dict[str, Any])
async def get_scoring_performance_endpoint(
    current_user: User = Depends(get_current_user)
):
    """
    Get performance statistics for the enhanced scoring system.
    
    This endpoint provides metrics about cache hit rates, calculation times,
    and overall scoring system performance.
    """
    try:
        stats = get_scoring_performance_stats()
        
        return {
            "status": "success",
            "performance_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance stats: {str(e)}")


@router.get("/debug/score-distribution", response_model=Dict[str, Any])
async def analyze_score_distribution_endpoint(
    bucket_type: Optional[BucketType] = Query(None, description="Analyze specific bucket only"),
    limit: int = Query(100, ge=10, le=1000, description="Number of emails to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the distribution of attention scores across emails.
    
    This endpoint provides statistical analysis of how scores are distributed,
    helping to understand if the scoring system is working as expected.
    """
    try:
        # Get emails for analysis
        query = db.query(Email).filter(Email.user_id == current_user.id)
        
        if bucket_type:
            # Filter by bucket if specified
            if bucket_type == "now":
                query = query.filter(Email.attention_score >= 60.0)
            elif bucket_type == "later":
                query = query.filter(Email.attention_score >= 30.0, Email.attention_score < 60.0)
            elif bucket_type == "reference":
                query = query.filter(Email.attention_score < 30.0)
        
        emails = query.order_by(Email.received_at.desc()).limit(limit).all()
        
        if not emails:
            return {
                "status": "success",
                "message": "No emails found for analysis",
                "analysis": {},
                "timestamp": datetime.now().isoformat()
            }
        
        # Analyze score distribution
        analysis = analyze_score_distribution(emails)
        
        return {
            "status": "success",
            "total_emails_analyzed": len(emails),
            "bucket_filter": bucket_type,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing score distribution: {str(e)}")


@router.post("/debug/invalidate-cache", response_model=Dict[str, Any])
async def invalidate_score_cache_endpoint(
    pattern: Optional[str] = Query(None, description="Pattern to match for cache invalidation"),
    current_user: User = Depends(get_current_user)
):
    """
    Invalidate cached attention scores.
    
    This endpoint allows clearing the scoring cache, which can be useful during
    development or when testing different scoring strategies.
    """
    try:
        # Only allow cache invalidation for development/testing
        # In production, you might want to restrict this to admin users
        
        invalidated = invalidate_score_cache(pattern=pattern)
        
        return {
            "status": "success",
            "invalidated_entries": invalidated,
            "pattern": pattern,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invalidating cache: {str(e)}")


@router.get("/debug/bucket-accuracy", response_model=Dict[str, Any])
async def analyze_bucket_accuracy_endpoint(
    sample_size: int = Query(50, ge=10, le=200, description="Number of emails to sample from each bucket"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze how accurately emails are placed in their current buckets.
    
    This endpoint recalculates scores for a sample of emails and checks if they
    would still be placed in the same buckets, helping to identify bucket drift.
    """
    try:
        accuracy_results = {}
        total_emails = 0
        total_accurate = 0
        
        # Check each bucket
        for bucket in ["now", "later", "reference"]:
            # Get sample emails from this bucket
            emails = query_bucket_emails(
                db, 
                user_id=current_user.id, 
                bucket=bucket, 
                limit=sample_size
            )
            
            if not emails:
                accuracy_results[bucket] = {
                    "sample_size": 0,
                    "accurate_count": 0,
                    "accuracy_percent": 0.0,
                    "score_drift": []
                }
                continue
            
            accurate_count = 0
            score_drift = []
            
            for email in emails:
                # Get fresh score breakdown
                breakdown = debug_email_score(email)
                fresh_score = breakdown.get('final_score', email.attention_score)
                stored_score = email.attention_score
                
                # Check if still belongs in same bucket
                if bucket == "now" and fresh_score >= 60.0:
                    accurate_count += 1
                elif bucket == "later" and 30.0 <= fresh_score < 60.0:
                    accurate_count += 1
                elif bucket == "reference" and fresh_score < 30.0:
                    accurate_count += 1
                else:
                    # Track score drift for misplaced emails
                    score_drift.append({
                        "email_id": str(email.id),
                        "stored_score": round(stored_score, 2),
                        "fresh_score": round(fresh_score, 2),
                        "drift": round(fresh_score - stored_score, 2)
                    })
            
            total_emails += len(emails)
            total_accurate += accurate_count
            
            accuracy_results[bucket] = {
                "sample_size": len(emails),
                "accurate_count": accurate_count,
                "accuracy_percent": round((accurate_count / len(emails)) * 100, 2),
                "score_drift": score_drift[:5]  # Show only first 5 drifted emails
            }
        
        overall_accuracy = round((total_accurate / total_emails) * 100, 2) if total_emails > 0 else 0
        
        return {
            "status": "success",
            "overall_accuracy_percent": overall_accuracy,
            "total_emails_sampled": total_emails,
            "bucket_accuracy": accuracy_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing bucket accuracy: {str(e)}")