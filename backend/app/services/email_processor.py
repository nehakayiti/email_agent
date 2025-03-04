from typing import Dict, Any, List
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from ..models.email import Email
from ..models.user import User
from email.utils import parsedate_to_datetime
import dateutil.parser

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
    new_emails_count = 0
    updated_emails_count = 0
    
    logger.info(f"[PROCESSOR] Starting to process {len(emails)} emails for user {user.id}")
    
    for i, email_data in enumerate(emails):
        try:
            gmail_id = email_data.get('gmail_id', 'unknown')
            subject = email_data.get('subject', 'No Subject')[:30]
            from_email = email_data.get('from_email', 'unknown')
            received_at = email_data.get('received_at', 'unknown')
            
            logger.info(f"[PROCESSOR] Processing email {i+1}/{len(emails)}: ID={gmail_id}, "
                       f"Subject='{subject}...', From={from_email}, Received={received_at}")
            
            # Check if email already exists
            existing_email = db.query(Email).filter(
                Email.user_id == user.id,
                Email.gmail_id == email_data['gmail_id']
            ).first()
            
            if existing_email:
                logger.info(f"[PROCESSOR] Email {gmail_id} already exists, updating")
                # Update existing email
                for key, value in email_data.items():
                    if key == 'received_at':
                        # Parse the date string to datetime object
                        setattr(existing_email, key, parse_date(value))
                    elif hasattr(existing_email, key):
                        setattr(existing_email, key, value)
                email = existing_email
                # Mark as not new for counting purposes
                email._is_new = False
                updated_emails_count += 1
            else:
                logger.info(f"[PROCESSOR] Email {gmail_id} is new, creating")
                # Create new email
                category = categorize_email(email_data)
                importance = calculate_importance(email_data)
                
                logger.info(f"[PROCESSOR] Categorized as '{category}' with importance {importance}")
                
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
                    category=category,
                    importance_score=importance
                )
                db.add(email)
                # Mark as new for counting purposes
                email._is_new = True
                new_emails_count += 1
            
            processed_emails.append(email)
            
        except Exception as e:
            logger.error(f"[PROCESSOR] Error processing email {email_data.get('gmail_id', 'unknown')}: {str(e)}", exc_info=True)
            continue
    
    try:
        logger.info(f"[PROCESSOR] Committing {len(processed_emails)} emails to database")
        db.commit()
        logger.info(f"[PROCESSOR] Successfully processed {len(processed_emails)} emails "
                   f"({new_emails_count} new, {updated_emails_count} updated)")
    except Exception as e:
        logger.error(f"[PROCESSOR] Error committing emails to database: {str(e)}", exc_info=True)
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
    
    if 'TRASH' in labels:
        return 'trash'
    elif 'IMPORTANT' in labels:
        return 'important'
    elif 'CATEGORY_PROMOTIONS' in labels:
        return 'promotional'
    elif 'CATEGORY_SOCIAL' in labels:
        return 'social'
    elif 'CATEGORY_UPDATES' in labels:
        return 'updates'
    elif 'CATEGORY_FORUMS' in labels:
        return 'forums'
    elif 'CATEGORY_PERSONAL' in labels:
        return 'personal'
    elif 'INBOX' not in labels:
        # If email doesn't have INBOX label, it's archived
        return 'archive'
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
    """
    Parse email date string to datetime object with proper timezone handling
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Datetime object with timezone information
    """
    try:
        # First try to parse as ISO format (from our Gmail service)
        dt = dateutil.parser.parse(date_str)
        
        # Ensure timezone info is present
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        return dt
    except Exception as e:
        # Fallback to email.utils parser for RFC 2822 format
        try:
            return parsedate_to_datetime(date_str)
        except Exception as e2:
            logger.error(f"[PROCESSOR] Failed to parse date '{date_str}': {str(e2)}")
            # Last resort fallback
            return datetime.now(timezone.utc) 