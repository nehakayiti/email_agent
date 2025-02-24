"""
Analytics module for email metrics and insights.
This module provides various services for analyzing email data.
"""

from .sentiment_service import analyze_sentiment
from .response_time_service import analyze_response_time
from .volume_service import analyze_email_volume
from .contacts_service import analyze_top_contacts

__all__ = [
    "analyze_sentiment",
    "analyze_response_time",
    "analyze_email_volume",
    "analyze_top_contacts"
] 