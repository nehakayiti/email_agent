"""
Categorization Service - Email categorization logic

This service consolidates all categorization logic for emails.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.email import Email
from ..models.user import User
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule
from ..utils.email_categorizer import categorize_email as categorize_email_util, RuleBasedCategorizer
from ..utils.email_utils import set_email_category_and_labels
from uuid import UUID
import uuid

logger = logging.getLogger(__name__)

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
    
    # Use the categorization function from email_categorizer
    category = categorize_email_util(email_data, db, user_id)
    
    logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as '{category}'")
    return category

def categorize_emails_batch(
    db: Session,
    emails: List[Email],
    user_id: UUID
) -> int:
    """
    Categorize a batch of emails
    
    Args:
        db: Database session
        emails: List of Email model instances to categorize
        user_id: User ID for personalized rules
        
    Returns:
        Number of emails categorized
    """
    if not emails:
        return 0
        
    categorized_count = 0
    logger.info(f"[CATEGORIZER] Categorizing {len(emails)} emails for user {user_id}")
    
    for email in emails:
        try:
            # Skip if already categorized
            if email.category:
                continue
                
            # Prepare email data for categorization
            email_data = {
                'gmail_id': email.gmail_id,
                'subject': email.subject,
                'from_email': email.from_email,
                'labels': email.labels,
                'snippet': email.snippet,
                'is_read': email.is_read
            }
            
            # Categorize the email
            category = categorize_email(email_data, db, user_id)
            email.category = category
            categorized_count += 1
            
            logger.debug(f"[CATEGORIZER] Categorized email {email.gmail_id} as '{category}'")
            
        except Exception as e:
            logger.error(f"[CATEGORIZER] Error categorizing email {email.gmail_id}: {str(e)}")
            continue
    
    # Commit changes
    try:
        db.commit()
        logger.info(f"[CATEGORIZER] Successfully categorized {categorized_count} emails")
    except Exception as e:
        db.rollback()
        logger.error(f"[CATEGORIZER] Error committing categorizations: {str(e)}")
        raise
    
    return categorized_count

def recategorize_email_on_label_change(
    db: Session,
    email: Email,
    user_id: UUID,
    added_labels: List[str],
    removed_labels: List[str]
) -> bool:
    """
    Recategorize an email when its labels change
    
    Args:
        db: Database session
        email: Email model instance
        user_id: User ID for personalized rules
        added_labels: Labels that were added
        removed_labels: Labels that were removed
        
    Returns:
        True if category changed, False otherwise
    """
    # Check if any relevant labels changed
    categorizer = RuleBasedCategorizer(db, user_id)
    rule_labels = set()
    for rule in categorizer.rules:
        if rule["type"] == "label":
            rule_labels.add(rule["value"].upper())
    # Always consider INBOX and TRASH as relevant
    rule_labels.update(["INBOX", "TRASH"])
    
    def is_relevant_label_change(added, removed):
        # Only recategorize if any added/removed label is relevant
        for label in (added or []) + (removed or []):
            if label.upper() in rule_labels:
                return True
        return False
    
    if not is_relevant_label_change(added_labels, removed_labels):
        return False
    
    # Prepare email data for recategorization
    email_data = {
        'id': email.id,
        'gmail_id': email.gmail_id,
        'labels': email.labels,
        'subject': email.subject,
        'from_email': email.from_email,
        'snippet': email.snippet,
        'is_read': email.is_read
    }
    
    # Recategorize
    old_category = email.category
    new_category = categorize_email_util(email_data, db, user_id)
    
    if email.category != new_category:
        logger.info(f"[CATEGORIZER] Recategorized email from '{old_category}' to '{new_category}' after label changes: {email.gmail_id}")
        email.category = new_category
        return True
    
    return False

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
    category = email_data.get('category')
    if not category:
        # Only call categorize_email if we don't have a category already
        logger.debug(f"[IMPORTANCE] No category available, categorizing email {gmail_id}")
        category = categorize_email_util(email_data, db, user_id)
    
    # Get category priority
    category_obj = db.query(EmailCategory).filter(EmailCategory.name == category).first()
    if category_obj:
        # Lower priority number = higher importance
        priority = category_obj.priority
        if priority <= 10:
            score += 15
        elif priority <= 20:
            score += 10
        elif priority <= 30:
            score += 5
        elif priority >= 50:
            score -= 10
            
        logger.debug(f"[IMPORTANCE] Category '{category}' (priority {priority}) -> {score}")
    
    # Read status adjustment
    if email_data.get('is_read', False):
        score -= 5
        logger.debug(f"[IMPORTANCE] -5 for read status -> {score}")
    
    # Subject keyword analysis
    subject_lower = subject.lower()
    important_keywords = ['urgent', 'important', 'critical', 'asap', 'deadline', 'expires']
    for keyword in important_keywords:
        if keyword in subject_lower:
            score += 10
            logger.debug(f"[IMPORTANCE] +10 for keyword '{keyword}' -> {score}")
            break
    
    # Sender-based adjustments
    if from_email:
        # Check for personal domains
        personal_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        domain = from_email.split('@')[-1].lower() if '@' in from_email else ''
        
        if domain in personal_domains:
            score += 5
            logger.debug(f"[IMPORTANCE] +5 for personal domain '{domain}' -> {score}")
    
    # Clamp score to 0-100 range
    score = max(0, min(100, score))
    
    logger.info(f"[IMPORTANCE] Final importance score for {gmail_id}: {score}")
    return score

def update_email_category_and_labels(
    db: Session,
    email: Email,
    new_category: str,
    user_id: UUID
) -> bool:
    """
    Update an email's category and ensure proper label consistency
    
    Args:
        db: Database session
        email: Email model instance
        new_category: New category to assign
        user_id: User ID for the email owner
        
    Returns:
        True if changes were made, False otherwise
    """
    try:
        # Use the utility function to handle category and label updates
        changed = set_email_category_and_labels(email, new_category, db)
        
        if changed:
            logger.info(f"[CATEGORIZER] Updated email {email.gmail_id} category to '{new_category}'")
            
        return changed
        
    except Exception as e:
        logger.error(f"[CATEGORIZER] Error updating category for email {email.gmail_id}: {str(e)}")
        raise

def get_categorization_rules(
    db: Session, 
    user_id: Optional[UUID] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Get all categorization rules for a user
    
    Args:
        db: Database session
        user_id: User ID (if None, returns system rules only)
        
    Returns:
        Dictionary of categorization rules
    """
    rules = {}
    
    # Get categories
    categories_query = db.query(EmailCategory)
    if user_id:
        # Get both system and user categories
        categories = categories_query.filter(
            (EmailCategory.is_system == True) | 
            (EmailCategory.user_id == user_id)
        ).all()
    else:
        # Get only system categories
        categories = categories_query.filter(EmailCategory.is_system == True).all()
    
    for category in categories:
        rules[category.name] = {
            'id': category.id,
            'name': category.name,
            'display_name': category.display_name,
            'priority': category.priority,
            'is_system': category.is_system,
            'keywords': [],
            'sender_rules': []
        }
    
    # Get keywords for each category
    for category_name, rule_data in rules.items():
        category_id = rule_data['id']
        
        # Get keywords
        keywords_query = db.query(CategoryKeyword).filter(CategoryKeyword.category_id == category_id)
        if user_id:
            keywords = keywords_query.filter(
                (CategoryKeyword.user_id == None) | 
                (CategoryKeyword.user_id == user_id)
            ).all()
        else:
            keywords = keywords_query.filter(CategoryKeyword.user_id == None).all()
            
        rule_data['keywords'] = [
            {
                'id': kw.id,
                'keyword': kw.keyword,
                'is_regex': kw.is_regex,
                'weight': kw.weight,
                'user_id': kw.user_id
            }
            for kw in keywords
        ]
        
        # Get sender rules
        sender_rules_query = db.query(SenderRule).filter(SenderRule.category_id == category_id)
        if user_id:
            sender_rules = sender_rules_query.filter(
                (SenderRule.user_id == None) | 
                (SenderRule.user_id == user_id)
            ).all()
        else:
            sender_rules = sender_rules_query.filter(SenderRule.user_id == None).all()
            
        rule_data['sender_rules'] = [
            {
                'id': rule.id,
                'pattern': rule.pattern,
                'is_domain': rule.is_domain,
                'weight': rule.weight,
                'user_id': rule.user_id
            }
            for rule in sender_rules
        ]
    
    return rules 