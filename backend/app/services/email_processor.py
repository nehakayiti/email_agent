from typing import Dict, Any, List
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from ..models.email import Email
from ..models.user import User
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

def process_and_store_emails(
    db: Session,
    user: User,
    emails: List[Dict[str, Any]]
) -> List[Email]:
    """
    Process fetched emails and store them in database
    
    Args:
        db: Database session
        user: User model instance
        emails: List of email data from Gmail API
        
    Returns:
        List of created/updated Email model instances
    """
    processed_emails = []
    
    for email_data in emails:
        try:
            # Check if email already exists
            existing_email = db.query(Email).filter(
                Email.user_id == user.id,
                Email.gmail_id == email_data['gmail_id']
            ).first()
            
            if existing_email:
                # Update existing email
                for key, value in email_data.items():
                    if hasattr(existing_email, key):
                        setattr(existing_email, key, value)
                email = existing_email
            else:
                # Create new email
                email = Email(
                    user_id=user.id,
                    gmail_id=email_data['gmail_id'],
                    thread_id=email_data['thread_id'],
                    subject=email_data['subject'],
                    from_email=email_data['from_email'],
                    received_at=parse_date(email_data['received_at']),
                    snippet=email_data['snippet'],
                    labels=email_data['labels'],
                    is_read=email_data['is_read'],
                    raw_data=email_data['raw_data'],
                    category=categorize_email(email_data),
                    importance_score=calculate_importance(email_data)
                )
                db.add(email)
            
            processed_emails.append(email)
            
        except Exception as e:
            logger.error(f"Error processing email {email_data.get('gmail_id')}: {str(e)}")
            continue
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error committing emails to database: {str(e)}")
        db.rollback()
        raise
        
    return processed_emails

def categorize_email(email_data: Dict[str, Any]) -> str:
    """
    Categorize email based on Gmail labels and content
    
    Args:
        email_data: Email data dictionary
        
    Returns:
        Category string (promotional, social, primary, etc.)
    """
    labels = email_data.get('labels', [])
    
    if 'CATEGORY_PROMOTIONS' in labels:
        return 'promotional'
    elif 'CATEGORY_SOCIAL' in labels:
        return 'social'
    elif 'CATEGORY_UPDATES' in labels:
        return 'updates'
    elif 'CATEGORY_FORUMS' in labels:
        return 'forums'
    else:
        return 'primary'

def calculate_importance(email_data: Dict[str, Any]) -> int:
    """
    Calculate importance score (0-100) based on various factors
    
    Args:
        email_data: Email data dictionary
        
    Returns:
        Importance score integer
    """
    score = 50  # Base score
    
    # Adjust based on labels
    if 'IMPORTANT' in email_data.get('labels', []):
        score += 20
    if 'CATEGORY_PROMOTIONS' in email_data.get('labels', []):
        score -= 20
        
    # Adjust based on read status
    if not email_data.get('is_read', True):
        score += 10
        
    # Ensure score stays within bounds
    return max(0, min(100, score))

def parse_date(date_str: str) -> datetime:
    """Parse email date string to datetime object"""
    return parsedate_to_datetime(date_str) 