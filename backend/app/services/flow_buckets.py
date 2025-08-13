"""
Flow Buckets Service

This module provides pure functions for classifying emails into flow buckets
and querying emails by bucket type. These functions operate on email data
and attention scores to organize emails by urgency.

ENHANCED: Now uses the new enhanced attention scoring system for better
email prioritization and more accurate bucket classification.
"""

import logging
from datetime import datetime
from typing import Literal, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from app.models.email import Email
from app.services.enhanced_attention_scoring import calculate_enhanced_attention_score, calculate_scores_batch

logger = logging.getLogger(__name__)

BucketType = Literal["now", "later", "reference"]


def classify_bucket(email: Email) -> BucketType:
    """
    Classify an email into a flow bucket based on attention score.
    
    Classification Rules:
    - NOW: attention_score >= 60 (High priority, needs immediate attention)
    - LATER: 30 <= attention_score < 60 (Medium priority, can be delayed)
    - REFERENCE: attention_score < 30 (Low priority, reference material)
    
    Args:
        email: Email object with attention_score property
        
    Returns:
        BucketType: "now", "later", or "reference"
        
    Example:
        >>> email = Email(attention_score=75.0)
        >>> bucket = classify_bucket(email)
        >>> print(bucket)  # "now"
    """
    if email.attention_score >= 60.0:
        return "now"
    elif email.attention_score >= 30.0:
        return "later"
    else:
        return "reference"


def classify_bucket_from_score(attention_score: float) -> BucketType:
    """
    Classify a bucket based on attention score alone (useful for testing).
    
    Args:
        attention_score: Attention score (0.0-100.0)
        
    Returns:
        BucketType: "now", "later", or "reference"
    """
    if attention_score >= 60.0:
        return "now"
    elif attention_score >= 30.0:
        return "later"
    else:
        return "reference"


def query_bucket_emails(
    session: Session,
    user_id: int,
    bucket: BucketType,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "attention_score"
) -> List[Email]:
    """
    Query emails in a specific bucket for a user.
    
    IMPORTANT: This function now prioritizes consistency between bucket counts
    and email retrieval by using stored attention scores for bucket filtering.
    Fresh scores are calculated for display purposes only but don't affect
    which bucket an email is shown in.
    
    Args:
        session: SQLAlchemy database session
        user_id: ID of the user to query emails for
        bucket: Bucket type to query ("now", "later", "reference")
        limit: Maximum number of emails to return
        offset: Number of emails to skip (for pagination)
        order_by: Field to order by ("attention_score", "date", "subject")
        
    Returns:
        List of Email objects in the specified bucket
        
    Example:
        >>> emails = query_bucket_emails(session, user_id=1, bucket="now", limit=10)
        >>> len(emails)  # Up to 10 high-priority emails based on stored scores
    """
    logger.debug(f"[FLOW_BUCKETS] Querying {bucket} bucket for user {user_id}, limit={limit}, offset={offset}")
    
    bucket_filters = {
        "now": Email.attention_score >= 60.0,
        "later": and_(Email.attention_score >= 30.0, Email.attention_score < 60.0),
        "reference": Email.attention_score < 30.0
    }
    
    # Base query for user's emails in the bucket (using stored scores for consistency)
    base_query = session.query(Email).filter(
        Email.user_id == user_id,
        bucket_filters[bucket]
    )
    
    # Apply ordering
    if order_by == "attention_score":
        base_query = base_query.order_by(desc(Email.attention_score))
    elif order_by == "date":
        base_query = base_query.order_by(desc(Email.received_at))
    elif order_by == "subject":
        base_query = base_query.order_by(asc(Email.subject))
    
    # Apply pagination
    base_query = base_query.offset(offset).limit(limit)
    emails = base_query.all()
    
    if not emails:
        logger.debug(f"[FLOW_BUCKETS] No emails found for {bucket} bucket")
        return []
    
    # Calculate fresh scores for display purposes (but don't filter by them)
    try:
        logger.debug(f"[FLOW_BUCKETS] Calculating fresh scores for {len(emails)} emails (display only)")
        fresh_scores = calculate_scores_batch(emails)
        
        # Update email objects with fresh scores for display (temporary, not persisted)
        for email in emails:
            email_id = str(email.id)
            if email_id in fresh_scores:
                fresh_score = fresh_scores[email_id]
                # Store fresh score for display purposes
                email._current_attention_score = fresh_score
                logger.debug(f"[FLOW_BUCKETS] Email {email_id}: stored={email.attention_score:.1f}, fresh={fresh_score:.1f}")
        
        # Re-sort by fresh scores if attention_score ordering was requested
        if order_by == "attention_score":
            emails.sort(key=lambda e: getattr(e, '_current_attention_score', e.attention_score), reverse=True)
        
        logger.info(f"[FLOW_BUCKETS] Returning {len(emails)} emails for {bucket} bucket with fresh scores")
        return emails
        
    except Exception as e:
        logger.error(f"[FLOW_BUCKETS] Error calculating fresh scores, using stored scores: {e}")
        # Fallback to stored scores only
        logger.info(f"[FLOW_BUCKETS] Returning {len(emails)} emails for {bucket} bucket (stored scores only)")
        return emails


def _email_belongs_in_bucket(score: float, bucket: BucketType) -> bool:
    """
    Check if an email with the given score belongs in the specified bucket.
    
    Args:
        score: Attention score (0-100)
        bucket: Bucket type to check
        
    Returns:
        True if email belongs in bucket, False otherwise
    """
    if bucket == "now":
        return score >= 60.0
    elif bucket == "later":
        return 30.0 <= score < 60.0
    elif bucket == "reference":
        return score < 30.0
    else:
        return False


def get_bucket_counts(session: Session, user_id: int) -> Dict[BucketType, int]:
    """
    Get the count of emails in each bucket for a user.
    
    Args:
        session: SQLAlchemy database session
        user_id: ID of the user to count emails for
        
    Returns:
        Dictionary with bucket counts: {"now": 5, "later": 12, "reference": 45}
        
    Example:
        >>> counts = get_bucket_counts(session, user_id=1)
        >>> print(counts["now"])  # 5
    """
    # Count emails in NOW bucket (attention_score >= 60)
    now_count = session.query(Email).filter(
        Email.user_id == user_id,
        Email.attention_score >= 60.0
    ).count()
    
    # Count emails in LATER bucket (30 <= attention_score < 60)
    later_count = session.query(Email).filter(
        Email.user_id == user_id,
        and_(Email.attention_score >= 30.0, Email.attention_score < 60.0)
    ).count()
    
    # Count emails in REFERENCE bucket (attention_score < 30)
    reference_count = session.query(Email).filter(
        Email.user_id == user_id,
        Email.attention_score < 30.0
    ).count()
    
    return {
        "now": now_count,
        "later": later_count,
        "reference": reference_count
    }


def get_bucket_summary(session: Session, user_id: int) -> Dict[str, Any]:
    """
    Get a comprehensive summary of all buckets for a user.
    
    Args:
        session: SQLAlchemy database session
        user_id: ID of the user to get summary for
        
    Returns:
        Dictionary with bucket counts and metadata
        
    Example:
        >>> summary = get_bucket_summary(session, user_id=1)
        >>> summary["total_emails"]  # 62
        >>> summary["buckets"]["now"]  # 5
    """
    counts = get_bucket_counts(session, user_id)
    total_emails = sum(counts.values())
    
    # Calculate bucket percentages
    percentages = {}
    if total_emails > 0:
        for bucket, count in counts.items():
            percentages[bucket] = round((count / total_emails) * 100, 1)
    else:
        percentages = {"now": 0.0, "later": 0.0, "reference": 0.0}
    
    return {
        "buckets": counts,
        "percentages": percentages,
        "total_emails": total_emails,
        "classification_rules": {
            "now": "attention_score >= 60 (High priority)",
            "later": "30 <= attention_score < 60 (Medium priority)", 
            "reference": "attention_score < 30 (Low priority)"
        }
    }