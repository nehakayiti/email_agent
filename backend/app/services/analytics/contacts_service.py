from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.email import Email

def analyze_top_contacts(
    db: Session,
    limit: int = 10,
    days: int = 30
) -> Dict[str, List]:
    """
    Identify most frequent email contacts over a specified period.
    
    Args:
        db: Session - Synchronous Database session.
        limit: int - Number of top contacts to return.
        days: int - Number of days to analyze.
        
    Returns:
        Dict containing a list of top contacts and their email counts.
    """
    # Compute the lower bound using Python's datetime and timedelta.
    lower_bound = datetime.utcnow() - timedelta(days=days)
    
    # Build the query using the computed lower_bound.
    query = (
        select(
            Email.from_email,
            func.count(Email.id).label('email_count')
        )
        .where(Email.created_at >= lower_bound)
        .group_by(Email.from_email)
        .order_by(func.count(Email.id).desc())
        .limit(limit)
    )
    
    result = db.execute(query)
    top_senders = result.fetchall()
    
    return {
        "top_contacts": [
            {
                "email": row.from_email,
                "count": row.email_count
            }
            for row in top_senders
        ],
        "period_days": days,
        "total_contacts": len(top_senders)
    }
