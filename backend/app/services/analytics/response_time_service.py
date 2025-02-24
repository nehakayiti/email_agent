from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
import logging

from app.models.email import Email

logger = logging.getLogger(__name__)

def analyze_response_time(
    db: Session,
    periods: List[int] = [7, 30, 90]
) -> Dict[str, Any]:
    """
    Calculate average response times over specified periods.
    
    Args:
        db: Session - Synchronous Database session
        periods: List[int] - List of day periods to analyze
        
    Returns:
        Dict containing average response times (in hours) for each period.
    """
    logger.debug("Starting response time analysis for periods: %s", periods)
    
    response_times = {}

    for days in periods:
        logger.debug("Analyzing response time for the last %d days", days)
        lower_bound = datetime.utcnow() - timedelta(days=days)
        
        # Build a subquery that computes response times between emails in the same thread.
        subquery = (
            select(
                Email.received_at,
                Email.from_email,
                Email.thread_id,
                func.extract(
                    'epoch',
                    Email.received_at - func.lag(Email.received_at).over(
                        partition_by=Email.thread_id,
                        order_by=Email.received_at
                    )
                ).label('time_diff'),
                func.lag(Email.from_email).over(
                    partition_by=Email.thread_id,
                    order_by=Email.received_at
                ).label('prev_sender')
            )
            .where(
                and_(
                    Email.thread_id.isnot(None),
                    Email.received_at >= lower_bound
                )
            )
            .subquery()
        )

        # Query: average response time for rows where the sender is different
        # from the previous sender, time_diff is positive, and under 7 days.
        query = (
            select(func.avg(subquery.c.time_diff).label('avg_time'))
            .where(
                and_(
                    subquery.c.time_diff.isnot(None),
                    subquery.c.time_diff > 0,
                    subquery.c.time_diff < 7 * 24 * 3600,
                    subquery.c.from_email != subquery.c.prev_sender
                )
            )
        )
        
        # Execute query synchronously.
        result = db.execute(query)
        rows = result.fetchall()  # Get all rows as a list.
        avg_time = rows[0][0] if rows and rows[0][0] is not None else 0
        # Convert seconds to hours and round to two decimals.
        response_times[f"{days}_days"] = round(avg_time / 3600, 2)

    return {
        "periods": response_times,
        "unit": "hours"
    }
