import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics.sentiment_service import analyze_sentiment
from app.services.analytics.response_time_service import analyze_response_time
from app.services.analytics.volume_service import analyze_email_volume
from app.services.analytics.contacts_service import analyze_top_contacts

@pytest.mark.asyncio
async def test_sentiment_analysis(db_session: AsyncSession):
    """Test sentiment analysis service with actual database data."""
    result = await analyze_sentiment(db_session, days=30)
    
    assert isinstance(result, dict)
    assert "positive" in result
    assert "neutral" in result
    assert "negative" in result
    assert "total_analyzed" in result
    
    # Verify percentages sum to approximately 100%
    total = result["positive"] + result["neutral"] + result["negative"]
    assert abs(100 - total) < 0.1 or total == 0

@pytest.mark.asyncio
async def test_response_time_analysis(db_session: AsyncSession):
    """Test response time analysis service with actual database data."""
    result = await analyze_response_time(db_session, periods=[7, 30, 90])
    
    assert isinstance(result, dict)
    assert "periods" in result
    assert "unit" in result
    assert result["unit"] == "hours"
    
    # Check all periods are present
    for period in [7, 30, 90]:
        assert f"{period}_days" in result["periods"]
        assert isinstance(result["periods"][f"{period}_days"], float)
        assert result["periods"][f"{period}_days"] >= 0

@pytest.mark.asyncio
async def test_email_volume_analysis(db_session: AsyncSession):
    """Test email volume analysis service with actual database data."""
    days = 30
    result = await analyze_email_volume(db_session, days=days)
    
    assert isinstance(result, dict)
    assert "daily_volume" in result
    assert "total_days" in result
    assert "total_emails" in result
    
    assert result["total_days"] == days
    assert isinstance(result["daily_volume"], list)
    
    # Verify daily volume entries
    for entry in result["daily_volume"]:
        assert "date" in entry
        assert "count" in entry
        assert isinstance(entry["count"], int)
        assert entry["count"] >= 0

@pytest.mark.asyncio
async def test_top_contacts_analysis(db_session: AsyncSession):
    """Test top contacts analysis service with actual database data."""
    limit = 10
    result = await analyze_top_contacts(db_session, limit=limit, days=30)
    
    assert isinstance(result, dict)
    assert "top_contacts" in result
    assert "period_days" in result
    assert "total_contacts" in result
    
    assert len(result["top_contacts"]) <= limit
    
    # Verify contact entries
    for contact in result["top_contacts"]:
        assert "email" in contact
        assert "count" in contact
        assert isinstance(contact["count"], int)
        assert contact["count"] > 0
        
    # Verify contacts are ordered by count
    counts = [contact["count"] for contact in result["top_contacts"]]
    assert counts == sorted(counts, reverse=True) 