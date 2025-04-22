from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.email import Email
from ..models.user import User
from ..models.email_category import EmailCategory
from email.utils import parsedate_to_datetime
import dateutil.parser
from ..utils.email_categorizer import determine_category, categorize_email as categorize_email_util, RuleBasedCategorizer
from uuid import UUID
import time
import math
import json
from ..services.email_classifier_service import email_classifier_service
from ..utils.filter_utils import apply_email_filters
from ..utils.email_utils import set_email_category_and_labels

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
    
    logger.info(f"[PROCESSOR] Processing {len(emails)} emails for user {user.id}")
    
    for i, email_data in enumerate(emails):
        try:
            gmail_id = email_data.get('gmail_id', 'unknown')
            subject = email_data.get('subject', 'No Subject')[:30]
            from_email = email_data.get('from_email', 'unknown')
            received_at = email_data.get('received_at', 'unknown')
            
            logger.debug(f"[PROCESSOR] Email {i+1}/{len(emails)}: ID={gmail_id}, Subject='{subject}...', From={from_email}, Received={received_at}")
            
            # Check if email already exists
            existing_email = db.query(Email).filter(
                Email.user_id == user.id,
                Email.gmail_id == email_data['gmail_id']
            ).first()
            
            if existing_email:
                logger.debug(f"[PROCESSOR] Email {gmail_id} already exists, updating")
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
                logger.debug(f"[PROCESSOR] Email {gmail_id} is new, creating")
                # Create new email
                category = categorize_email_util(email_data, db, user.id)
                email_data['category'] = category  # Prevent double categorization
                importance = calculate_importance(email_data, db, user.id)
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
                set_email_category_and_labels(email, category, db)
                db.add(email)
                email._is_new = True
                new_emails_count += 1
            processed_emails.append(email)
        except Exception as e:
            logger.error(f"[PROCESSOR] Error processing email {email_data.get('gmail_id', 'unknown')}: {str(e)}", exc_info=True)
            continue
    try:
        db.commit()
        logger.info(f"[PROCESSOR] Processed {len(processed_emails)} emails (new: {new_emails_count}, updated: {updated_emails_count}) for user {user.id}")
    except Exception as e:
        logger.error(f"[PROCESSOR] Error committing emails to database: {str(e)}", exc_info=True)
        db.rollback()
        raise
    return processed_emails

def categorize_email(
    email_data: Dict[str, Any], 
    db: Session, 
    user_id: Optional[UUID] = None
) -> str:
    """
    Categorize email based on Gmail labels, subject content, and sender.
    
    This function uses a modular categorization system that considers:
    1. Gmail's built-in labels
    2. Subject line keyword matching
    3. Sender domain analysis
    4. ML-based trash detection
    
    The categorization is database-driven and can be customized through 
    the categories management interface.
    
    Args:
        email_data: Email data dictionary containing subject, labels, etc.
        db: Database session for fetching category rules (required)
        user_id: Optional user ID for personalized rules
        
    Returns:
        Category string
    """
    if db is None:
        raise ValueError("Database session is required for email categorization")
        
    gmail_id = email_data.get('gmail_id', 'unknown')
    subject = email_data.get('subject', '')
    
    logger.debug(f"[CATEGORIZER] Categorizing email {gmail_id} (subject: '{subject[:40]}')")
    
    # Use the categorization function from email_categorizer - now using modular approach
    category = categorize_email_util(email_data, db, user_id)
    
    logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as '{category}'")
    return category

def calculate_importance(
    email_data: Dict[str, Any],
    db: Session,
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
        db: Database session for fetching category priorities
        user_id: Optional user ID for personalized importance rules
        
    Returns:
        Importance score integer
    """
    if db is None:
        raise ValueError("Database session is required for importance calculation")
        
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
    # Use existing category if available, avoiding duplicate categorization
    category = email_data.get('category')
    if not category:
        # Only call categorize_email if we don't have a category already
        logger.debug(f"[IMPORTANCE] No category available, categorizing email {gmail_id}")
        category = categorize_email_util(email_data, db, user_id)
        # Store category in email_data to avoid future recategorization
        email_data['category'] = category
    
    # Fetch category priorities from the database
    # Get priorities for all categories
    categories = db.query(EmailCategory).all()
    category_priorities = {cat.name.lower(): cat.priority for cat in categories}
    
    # Default adjustments based on priority (lower priority number = higher importance)
    # We'll convert the priority (1-10) to an importance adjustment (-20 to +25)
    if category and category.lower() in category_priorities:
        priority = category_priorities[category.lower()]
        # Inverse mapping: priority 1 (highest) = +25, priority 10 (lowest) = -20
        adjustment = 30 - (5 * priority)
        score += adjustment
        logger.debug(f"[IMPORTANCE] {adjustment} for category '{category}' (priority {priority}) -> {score}")
    
    # Important keywords in subject (emergency, urgent, etc.)
    important_keywords = [
        "urgent", "important", "attention", "priority", "critical", 
        "required", "action", "deadline", "immediately", "asap",
        "emergency", "alert", "security", "password", "unauthorized"
    ]
    
    # Check for important keywords in subject
    for keyword in important_keywords:
        if keyword.lower() in subject.lower():
            score += 15
            logger.debug(f"[IMPORTANCE] +15 for important keyword '{keyword}' in subject -> {score}")
            break  # Only apply once even if multiple keywords match
    
    # Adjust based on read status
    if not email_data.get('is_read', True):
        score += 5
        logger.debug(f"[IMPORTANCE] +5 for unread status -> {score}")
    
    # Cap the score between 0 and 100
    score = max(0, min(100, score))
    
    logger.info(f"[IMPORTANCE] Final score for email {gmail_id}: {score}")
    return score

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
    filter_params: Dict[str, Any] = None,
    include_reprocessed: bool = False
) -> Dict[str, Any]:
    """
    Reprocess emails by updating their categories and other derived attributes
    
    Args:
        db: Database session
        user_id: User ID who owns the emails
        filter_params: Optional filters to select specific emails
        include_reprocessed: Whether to include already reprocessed emails
        
    Returns:
        Dictionary with reprocessing statistics
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"[REPROCESS] Starting reprocessing for user {user_id}")
    if filter_params:
        logger.info(f"[REPROCESS] Filters: {filter_params}")
    classifier_loaded = email_classifier_service.load_trash_classifier(user_id)
    if not classifier_loaded:
        logger.warning(f"[REPROCESS] No classifier model for user {user_id}, using rules-based categorization")
    query = db.query(Email).filter(Email.user_id == user_id)
    if not include_reprocessed:
        query = query.filter(or_(Email.last_reprocessed_at.is_(None), Email.is_dirty.is_(True)))
    if filter_params:
        query = apply_email_filters(query, filter_params)
    total_emails = query.count()
    logger.info(f"[REPROCESS] {total_emails} emails to reprocess")
    if total_emails == 0:
        logger.info(f"[REPROCESS] No emails to reprocess. Exiting.")
        return {"status": "success", "message": "No emails to reprocess", "reprocessed_count": 0, "duration": 0}
    
    # Process emails in batches to avoid memory issues
    batch_size = 100
    total_batches = math.ceil(total_emails / batch_size)
    reprocessed_count = 0
    category_changes = {}

    # Instantiate categorizer once for the batch
    categorizer = RuleBasedCategorizer(db, user_id)

    logger.info(f"[REPROCESS] Processing {total_emails} emails in {total_batches} batches of {batch_size}")

    for batch_num in range(total_batches):
        offset = batch_num * batch_size
        batch_query = query.order_by(Email.received_at.desc()).offset(offset).limit(batch_size)
        batch_emails = batch_query.all()

        logger.info(f"[REPROCESS] Processing batch {batch_num + 1}/{total_batches} ({len(batch_emails)} emails)")

        # Process each email in the batch
        for email in batch_emails:
            old_category = email.category

            # Reprocess the email
            logger.debug(f"[REPROCESS] Reprocessing email {email.id} (Gmail ID: {email.gmail_id})")
            logger.debug(f"[REPROCESS] Current category: {old_category}")

            # If we have labels, use them to categorize
            if email.labels:
                try:
                    # Create full email data for better categorization
                    email_data = {
                        'id': email.id,
                        'gmail_id': email.gmail_id,
                        'labels': json.loads(email.labels) if isinstance(email.labels, str) else email.labels,
                        'subject': email.subject,
                        'from_email': email.from_email,
                        'snippet': email.snippet,
                        'is_read': email.is_read
                    }

                    logger.info(f"[CLASSIFICATION] Classifying email {email.id} using modular categorizer")
                    # Use the cached categorizer instance
                    new_category = categorize_email_util(email_data, db, user_id, categorizer=categorizer)

                    # Always enforce label/category consistency
                    # Ensure labels is a list before updating
                    if isinstance(email.labels, str):
                        try:
                            email.labels = json.loads(email.labels)
                        except Exception:
                            email.labels = [email.labels]
                    set_email_category_and_labels(email, new_category, db)
                    if new_category != old_category:
                        category_changes[new_category] = category_changes.get(new_category, 0) + 1
                        logger.info(f"[REPROCESS] Email {email.id} category changed: {old_category} → {new_category} and labels updated for consistency")
                    else:
                        logger.debug(f"[REPROCESS] Email {email.id} category unchanged ({new_category}), labels updated for consistency")
                except Exception as e:
                    logger.error(f"[REPROCESS] Error categorizing email {email.id}: {str(e)}")
            else:
                logger.debug(f"[REPROCESS] Email {email.id} has no labels, skipping categorization")

            # Mark as clean and store reprocessing timestamp
            email.is_dirty = False
            email.last_reprocessed_at = datetime.now(timezone.utc)
            reprocessed_count += 1

        # Commit each batch separately
        db.commit()
        logger.info(f"[REPROCESS] Batch {batch_num + 1} completed - {reprocessed_count}/{total_emails} emails processed")

    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info(f"[REPROCESS] Completed reprocessing {reprocessed_count} emails in {duration:.2f}s. Category changes: {category_changes}")
    return {
        "status": "success",
        "message": f"Reprocessed {reprocessed_count} emails",
        "reprocessed_count": reprocessed_count,
        "duration": round(duration, 2),
        "category_changes": category_changes
    }

def maybe_train_classifier(db: Session, user_id: UUID) -> Dict[str, Any]:
    """
    Train the classifier if needed by checking if a model exists
    
    Args:
        db: Database session
        user_id: User ID to train model for
        
    Returns:
        Dictionary with training results
    """
    from ..utils.naive_bayes_classifier import load_classifier_model
    
    # Check if model exists
    model_loaded = load_classifier_model(user_id)
    
    if not model_loaded:
        logging.info(f"[PROCESSOR] No classifier model found for user {user_id}, training new model")
        
        try:
            # Train with balanced approach
            training_results = email_classifier_service.train_trash_classifier(
                db=db,
                user_id=user_id,
                save_model=True
            )
            
            if training_results.get("trained", False):
                training_info = f"Model trained with {training_results.get('training_samples', 0)} samples, " \
                              f"test accuracy: {training_results.get('test_accuracy', 0):.4f}"
                logging.info(f"[PROCESSOR] {training_info}")
                return training_results
            else:
                logging.warning(f"[PROCESSOR] Failed to train model: {training_results.get('message', 'Unknown error')}")
                return training_results
        except Exception as e:
            logging.error(f"[PROCESSOR] Error training classifier: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error training classifier: {str(e)}",
                "trained": False
            }
    else:
        logging.info(f"[PROCESSOR] Classifier model already exists for user {user_id}")
        return {
            "status": "success",
            "message": "Model already exists",
            "trained": False
        } 