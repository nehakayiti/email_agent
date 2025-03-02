from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text


from ..db import get_db
from ..services.analytics.sentiment_service import analyze_sentiment
from ..services.analytics.response_time_service import analyze_response_time
from ..services.analytics.volume_service import analyze_email_volume
from ..services.analytics.contacts_service import analyze_top_contacts
from ..models.user import User
from ..models.email import Email
from ..models.email_sync import EmailSync

router = APIRouter()  # Remove prefix here, it will be added in main.py

@router.get("/sentiment")
async def get_email_sentiment(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get sentiment analysis for emails over specified period."""
    return analyze_sentiment(db, days=days)

@router.get("/response-time")
async def get_response_time(
    periods: List[int] = Query(default=[7, 30, 90]),
    db: Session = Depends(get_db)
):
    """Get average response times over specified periods."""
    return analyze_response_time(db, periods=periods)

@router.get("/volume")
async def get_email_volume(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get daily email volume over specified period."""
    return analyze_email_volume(db, days=days)

@router.get("/top-contacts")
async def get_top_contacts(
    limit: int = Query(default=10, ge=1, le=100),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get most frequent email contacts over specified period."""
    return analyze_top_contacts(db, limit=limit, days=days)

@router.get("/db-insights")
async def get_db_insights(db: Session = Depends(get_db)):
    """Get database insights including user count, email count, and last sync time."""
    
    # Get user count
    user_count = db.query(func.count(User.id)).scalar()
    
    # Get email count
    email_count = db.query(func.count(Email.id)).scalar()
    
    # Get last sync time
    last_sync = db.query(EmailSync.last_fetched_at)\
        .order_by(EmailSync.last_fetched_at.desc())\
        .first()
    
    # Get last sync time by user
    user_syncs = db.query(
        User.email,
        EmailSync.last_fetched_at,
        EmailSync.sync_cadence
    ).join(EmailSync, User.id == EmailSync.user_id)\
     .order_by(EmailSync.last_fetched_at.desc())\
     .limit(10)\
     .all()
    
    # Get table sizes
    # This is PostgreSQL specific
    table_sizes_query = text("""
        SELECT
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size,
            pg_total_relation_size(quote_ident(table_name)) as raw_size
        FROM
            information_schema.tables
        WHERE
            table_schema = 'public'
        ORDER BY
            raw_size DESC
    """)
    
    try:
        table_sizes = [dict(row) for row in db.execute(table_sizes_query)]
    except Exception as e:
        table_sizes = [{"error": str(e)}]
    
    # Get a sample API token for scripts
    sample_user = db.query(User).first()
    sample_token = "Generate token via auth endpoint" if not sample_user else f"User ID: {sample_user.id}"
    
    return {
        "user_count": user_count,
        "email_count": email_count,
        "last_sync": last_sync[0] if last_sync else None,
        "user_syncs": [
            {
                "email": user_email,
                "last_fetched_at": last_fetched_at,
                "sync_cadence_minutes": sync_cadence
            } for user_email, last_fetched_at, sync_cadence in user_syncs
        ],
        "table_sizes": table_sizes,
        "sample_token": sample_token
    }

# Make sure router is properly exported
__all__ = ['router'] 