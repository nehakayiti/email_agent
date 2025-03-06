from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from ..models.email import Email
from ..models.user import User
from email.utils import parsedate_to_datetime
import dateutil.parser
from ..utils.email_categorizer import determine_category
from uuid import UUID

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
                category = categorize_email(email_data, db, user.id)
                importance = calculate_importance(email_data, db, user.id)
                
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

def categorize_email(
    email_data: Dict[str, Any], 
    db: Session = None, 
    user_id: Optional[UUID] = None
) -> str:
    """
    Categorize email based on Gmail labels, subject content, and sender.
    
    This function uses an intelligent categorization system that considers:
    1. Gmail's built-in labels
    2. Subject line keyword matching
    3. Sender domain analysis
    
    The categorization is extensible and can be improved over time by:
    - Adding/updating keywords in email_categories.py
    - Improving the matching algorithms
    - Adding user feedback to adjust categorization
    
    When database session is provided, it uses dynamic categorization rules
    from the database that can be customized per user.
    
    Args:
        email_data: Email data dictionary containing subject, labels, etc.
        db: Optional database session for dynamic rules
        user_id: Optional user ID for personalized rules
        
    Returns:
        Category string (promotional, social, primary, etc.)
    """
    labels = email_data.get('labels', [])
    subject = email_data.get('subject', '')
    from_email = email_data.get('from_email', '')
    
    gmail_id = email_data.get('gmail_id', 'unknown')
    
    logger.info(f"[CATEGORIZER] Categorizing email {gmail_id} with subject '{subject}'")
    
    # Use the enhanced categorization system
    category = determine_category(labels, subject, from_email, db, user_id)
    
    logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as '{category}'")
    return category

def calculate_importance(
    email_data: Dict[str, Any],
    db: Session = None,
    user_id: Optional[UUID] = None
) -> int:
    """
    Calculate importance score (0-100) based on various factors
    
    Factors considered:
    - Gmail labels (IMPORTANT, etc.)
    - Email category
    - Read status
    - Important keywords in subject
    - Sender domain/address
    
    Args:
        email_data: Email data dictionary
        db: Optional database session for dynamic rules
        user_id: Optional user ID for personalized importance rules
        
    Returns:
        Importance score integer
    """
    score = 50  # Base score
    
    subject = email_data.get('subject', '')
    from_email = email_data.get('from_email', '')
    labels = email_data.get('labels', [])
    gmail_id = email_data.get('gmail_id', 'unknown')
    
    logger.info(f"[IMPORTANCE] Calculating importance for email {gmail_id}")
    
    # Adjust based on Gmail labels
    if 'IMPORTANT' in labels:
        score += 20
        logger.debug(f"[IMPORTANCE] +20 for IMPORTANT label -> {score}")
        
    # Category-based adjustments
    category = email_data.get('category', categorize_email(email_data, db, user_id))
    
    category_adjustments = {
        'important': 25,
        'personal': 20,
        'primary': 10,
        'newsletters': 5,  # Newsletters have moderate importance
        'updates': 0,
        'forums': -5,
        'social': -10,
        'promotional': -20,
        'trash': -40,
        'archive': -15
    }
    
    if category in category_adjustments:
        adjustment = category_adjustments[category]
        score += adjustment
        logger.debug(f"[IMPORTANCE] {adjustment} for category '{category}' -> {score}")
    
    # Important keywords in subject (emergency, urgent, etc.)
    important_keywords = [
        "urgent", "important", "attention", "priority", "critical", 
        "required", "action", "deadline", "immediately", "asap",
        "emergency", "alert", "security", "password", "unauthorized"
    ]
    
    if subject:
        subject_lower = subject.lower()
        for keyword in important_keywords:
            if keyword in subject_lower:
                score += 15
                logger.debug(f"[IMPORTANCE] +15 for important keyword '{keyword}' -> {score}")
                break  # Only apply once for important keywords
    
    # Adjust based on read status
    if not email_data.get('is_read', True):
        score += 10
        logger.debug(f"[IMPORTANCE] +10 for unread status -> {score}")
    
    # Sender importance (simple heuristic for demo)
    important_domains = ["boss", "ceo", "manager", "director", "hr", "payroll", "finance"]
    if from_email:
        for domain in important_domains:
            if domain in from_email.lower():
                score += 15
                logger.debug(f"[IMPORTANCE] +15 for important sender with '{domain}' -> {score}")
                break
    
    # Ensure score stays within bounds
    final_score = max(0, min(100, score))
    logger.info(f"[IMPORTANCE] Final score for email {gmail_id}: {final_score}")
    return final_score

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

def reprocess_emails(
    db: Session,
    user_id: UUID,
    filter_criteria: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Reprocess existing emails with updated categorization rules.
    
    Args:
        db: Database session
        user_id: User ID
        filter_criteria: Optional filter criteria to limit which emails are reprocessed
        
    Returns:
        Dictionary with processing statistics
    """
    query = db.query(Email).filter(Email.user_id == user_id)
    
    # Apply filters if provided
    if filter_criteria:
        if 'categories' in filter_criteria:
            query = query.filter(Email.category.in_(filter_criteria['categories']))
        if 'date_from' in filter_criteria:
            query = query.filter(Email.received_at >= filter_criteria['date_from'])
        if 'date_to' in filter_criteria:
            query = query.filter(Email.received_at <= filter_criteria['date_to'])
        if 'search' in filter_criteria:
            search_term = f"%{filter_criteria['search']}%"
            query = query.filter(
                (Email.subject.ilike(search_term)) | 
                (Email.from_email.ilike(search_term)) |
                (Email.snippet.ilike(search_term))
            )
    
    # Count total emails to process
    total_emails = query.count()
    
    if total_emails == 0:
        return {
            "total": 0,
            "processed": 0,
            "category_changes": {},
            "importance_changes": 0
        }
    
    logger.info(f"[REPROCESSOR] Reprocessing {total_emails} emails for user {user_id}")
    
    # Process in reasonable sized batches
    batch_size = 100
    processed_count = 0
    category_changes = {}  # Track how many emails changed categories
    importance_changes = 0  # Track how many emails had importance changes
    
    # Get user for the logging
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    for offset in range(0, total_emails, batch_size):
        batch = query.limit(batch_size).offset(offset).all()
        
        for email in batch:
            # Create email_data dict from email model
            email_data = {
                'gmail_id': email.gmail_id,
                'subject': email.subject,
                'from_email': email.from_email,
                'labels': email.labels,
                'is_read': email.is_read,
                'snippet': email.snippet
            }
            
            # Store original values
            original_category = email.category
            original_importance = email.importance_score
            
            # Recategorize and recalculate importance
            new_category = categorize_email(email_data, db, user_id)
            new_importance = calculate_importance(email_data, db, user_id)
            
            # Track changes
            if new_category != original_category:
                email.category = new_category
                
                # Update category change counts
                change_key = f"{original_category} -> {new_category}"
                category_changes[change_key] = category_changes.get(change_key, 0) + 1
                
                logger.info(f"[REPROCESSOR] Email {email.gmail_id} category changed: {original_category} -> {new_category}")
            
            if new_importance != original_importance:
                email.importance_score = new_importance
                importance_changes += 1
                
                logger.info(f"[REPROCESSOR] Email {email.gmail_id} importance changed: {original_importance} -> {new_importance}")
            
            processed_count += 1
            
            # Log progress every 100 emails
            if processed_count % 100 == 0:
                logger.info(f"[REPROCESSOR] Processed {processed_count}/{total_emails} emails")
        
        # Commit each batch
        db.commit()
    
    logger.info(f"[REPROCESSOR] Completed reprocessing {processed_count} emails for user {user_id}")
    logger.info(f"[REPROCESSOR] Category changes: {category_changes}")
    logger.info(f"[REPROCESSOR] Importance changes: {importance_changes}")
    
    return {
        "total": total_emails,
        "processed": processed_count,
        "category_changes": category_changes,
        "importance_changes": importance_changes
    } 