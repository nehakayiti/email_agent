"""
Flow Buckets Service

This module provides pure functions for classifying emails into flow buckets
and querying emails by bucket type. These functions operate on email data
and attention scores to organize emails by urgency.
"""

from typing import Literal, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from app.models.email import Email

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
        >>> len(emails)  # Up to 10 high-priority emails
    """
    # Define score ranges for each bucket
    bucket_filters = {
        "now": Email.attention_score >= 60.0,
        "later": and_(Email.attention_score >= 30.0, Email.attention_score < 60.0),
        "reference": Email.attention_score < 30.0
    }
    
    # Base query for user's emails in the bucket
    query = session.query(Email).filter(
        Email.user_id == user_id,
        bucket_filters[bucket]
    )
    
    # Add ordering
    if order_by == "attention_score":
        query = query.order_by(desc(Email.attention_score))
    elif order_by == "date":
        query = query.order_by(desc(Email.received_at))
    elif order_by == "subject":
        query = query.order_by(asc(Email.subject))
    else:
        # Default to attention score if invalid order_by
        query = query.order_by(desc(Email.attention_score))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    return query.all()


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