"""
Attention Scoring Service

This module provides heuristic-based attention scoring for emails.
The scoring algorithm assigns attention scores based on email properties
such as read status, labels, and other urgency indicators.
"""

from typing import Union, List, Optional
from app.models.email import Email


def calculate_attention_score(email: Email) -> float:
    """
    Calculate attention score for an email using simple heuristics.
    
    Scoring Logic:
    - Base score: 50.0
    - Unread bonus: +15 points
    - IMPORTANT label: +30 points
    - STARRED label: +20 points
    - Result clamped between 0.0 and 100.0
    
    Args:
        email: Email object with properties like is_read, labels, etc.
        
    Returns:
        float: Attention score between 0.0 and 100.0
        
    Example:
        >>> email = Email(is_read=False, labels=['IMPORTANT'])
        >>> score = calculate_attention_score(email)
        >>> print(score)  # 95.0 (50 + 15 + 30)
    """
    score = 50.0  # base score
    
    # Unread emails get higher attention
    if not email.is_read:
        score += 15.0
    
    # Check for urgency labels
    if email.labels:
        if 'IMPORTANT' in email.labels:
            score += 30.0
        if 'STARRED' in email.labels:
            score += 20.0
    
    # Clamp result between 0.0 and 100.0
    return max(0.0, min(100.0, score))


def calculate_attention_score_from_data(
    is_read: bool = False,
    labels: Optional[List[str]] = None
) -> float:
    """
    Calculate attention score from raw data (useful for testing and external calls).
    
    Args:
        is_read: Whether the email has been read
        labels: List of email labels
        
    Returns:
        float: Attention score between 0.0 and 100.0
    """
    # Create a minimal email-like object for scoring
    class EmailData:
        def __init__(self, is_read: bool, labels: Optional[List[str]]):
            self.is_read = is_read
            self.labels = labels or []
    
    email_data = EmailData(is_read, labels)
    return calculate_attention_score(email_data)


def get_attention_level(score: float) -> str:
    """
    Convert attention score to human-readable level.
    
    Args:
        score: Attention score (0.0-100.0)
        
    Returns:
        str: Attention level ('Low', 'Medium', 'High', 'Critical')
    """
    if score >= 80.0:
        return 'Critical'
    elif score >= 60.0:
        return 'High'
    elif score >= 30.0:
        return 'Medium'
    else:
        return 'Low'


def get_attention_color(score: float) -> str:
    """
    Get color representation for attention score (useful for UI).
    
    Args:
        score: Attention score (0.0-100.0)
        
    Returns:
        str: Color name ('red', 'orange', 'yellow', 'green')
    """
    if score >= 80.0:
        return 'red'
    elif score >= 60.0:
        return 'orange'
    elif score >= 30.0:
        return 'yellow'
    else:
        return 'green' 