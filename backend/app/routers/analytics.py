from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session


from app.db import get_db
from app.services.analytics.sentiment_service import analyze_sentiment
from app.services.analytics.response_time_service import analyze_response_time
from app.services.analytics.volume_service import analyze_email_volume
from app.services.analytics.contacts_service import analyze_top_contacts

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

# Make sure router is properly exported
__all__ = ['router'] 