from typing import Dict, List, Any
from textblob import TextBlob
from sqlalchemy import select, func
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.email import Email

def analyze_sentiment(db: Session, days: int = 30) -> Dict[str, Any]:
    """
    Analyze sentiment of emails over the specified period using TextBlob.
    
    Args:
        db: AsyncSession - Database session
        days: int - Number of days to analyze
    
    Returns:
        Dict containing sentiment analysis results including trends
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query to get emails within the specified time period
    stmt = (
        select(Email)
        .where(Email.created_at >= cutoff_date)
        .order_by(Email.created_at)
    )
    
    # Execute query asynchronously and fetch all results
    result = db.execute(stmt)
    emails = result.scalars().all()
    
    # Initialize sentiment metrics
    sentiment_data = {
        "total_emails": len(emails),
        "period_days": days,
        "average_sentiment": 0.0,
        "sentiment_distribution": {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        },
        "sentiment_trend": []
    }
    
    if emails:
        total_sentiment = 0.0
        valid_emails = 0
        
        for email in emails:
            # Skip if no content
            if not email.snippet:
                continue
                
            valid_emails += 1
            
            # Analyze sentiment using TextBlob
            blob = TextBlob(email.snippet)
            sentiment_score = blob.sentiment.polarity
            
            # Update total sentiment for average calculation
            total_sentiment += sentiment_score
            
            # Categorize sentiment
            if sentiment_score > 0.1:
                sentiment_data["sentiment_distribution"]["positive"] += 1
            elif sentiment_score < -0.1:
                sentiment_data["sentiment_distribution"]["negative"] += 1
            else:
                sentiment_data["sentiment_distribution"]["neutral"] += 1
            
            # Add to sentiment trend
            sentiment_data["sentiment_trend"].append({
                "date": email.created_at.isoformat(),
                "sentiment": round(sentiment_score, 3)
            })
        
        # Calculate average sentiment only for valid emails
        if valid_emails > 0:
            sentiment_data["average_sentiment"] = round(total_sentiment / valid_emails, 3)
        
        # Convert counts to percentages
        total = sum(sentiment_data["sentiment_distribution"].values())
        if total > 0:
            for key in sentiment_data["sentiment_distribution"]:
                sentiment_data["sentiment_distribution"][key] = round(
                    (sentiment_data["sentiment_distribution"][key] / total) * 100, 2
                )
    
    return sentiment_data 