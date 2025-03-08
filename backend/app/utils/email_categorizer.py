"""
Email categorization utilities with keyword matching capabilities.

This module implements efficient algorithms for categorizing emails
based on their content, subject, and metadata, using database-stored rules.
"""
import re
import logging
from typing import Dict, Any, Set, List, Tuple, Optional, Union, Pattern
from sqlalchemy.orm import Session
from uuid import UUID
from ..services.category_service import get_categorization_rules
from functools import lru_cache
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule
import json

# Import the Naive Bayes classifier
from .naive_bayes_classifier import classify_email as nbc_classify_email, record_trash_event

logger = logging.getLogger(__name__)

# Constants for weighted decision making
ML_CONFIDENCE_THRESHOLD = 0.75  # High confidence threshold for ML
RULES_CONFIDENCE_THRESHOLD = 0.7  # Threshold for rules-based approach
ML_RULES_WEIGHT = 0.7  # Weight for ML decision when combining with rules

# LRU cache for compiled regex patterns to improve performance
@lru_cache(maxsize=100)
def compile_regex(pattern: str, is_case_sensitive: bool = False) -> Pattern:
    """
    Compile and cache regex patterns to avoid recompilation.
    
    Args:
        pattern: The regex pattern to compile
        is_case_sensitive: Whether the pattern should be case sensitive
        
    Returns:
        Compiled regex pattern
    """
    try:
        flags = 0 if is_case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)
    except re.error as e:
        logger.warning(f"Invalid regex pattern '{pattern}': {str(e)}")
        # Return a pattern that won't match anything as a fallback
        return re.compile(r'$^')

class DynamicEmailCategorizer:
    """
    Dynamic email categorization engine that uses database-stored rules.
    
    This class loads categorization rules from the database and efficiently
    categorizes emails based on multiple factors including:
    - Gmail labels
    - Subject line content
    - Sender information
    
    It supports both system-wide rules and user-specific customizations.
    """
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        """Initialize the categorizer with rules from the database"""
        self.db = db
        self.user_id = user_id
        self.rules = get_categorization_rules(db, user_id)
        
        # Compile regex patterns for better performance
        self._compile_regex_patterns()
        
        # Map category IDs to names for easier access
        self.category_id_to_name = {
            cat_id: details["name"] 
            for cat_id, details in self.rules["categories"].items()
        }
        
        # Map category names to priorities
        self.category_priorities = {
            details["name"]: details["priority"] 
            for cat_id, details in self.rules["categories"].items()
        }
        
        # Sort categories by priority for faster processing
        self.sorted_categories = sorted(
            [(cat_id, details) for cat_id, details in self.rules["categories"].items()],
            key=lambda x: x[1]["priority"]
        )
        
        logger.info(f"Initialized dynamic categorizer with {len(self.rules['categories'])} categories, "
                   f"{sum(len(kws) for kws in self.rules.get('keywords', {}).values())} keywords, and "
                   f"{sum(len(srs) for srs in self.rules.get('senders', {}).values())} sender rules")
    
    def _compile_regex_patterns(self):
        """Pre-compile regex patterns for better performance"""
        self.compiled_regexes = {}
        
        for cat_id, keywords in self.rules.get("keywords", {}).items():
            self.compiled_regexes[cat_id] = []
            for kw_data in keywords:
                if kw_data.get("is_regex", False):
                    pattern = compile_regex(kw_data["keyword"])
                    self.compiled_regexes[cat_id].append((pattern, kw_data.get("weight", 1)))
    
    def get_subject_category_matches(self, subject: str) -> List[Tuple[str, int, str]]:
        """
        Find categories matching the subject line.
        
        Args:
            subject: Email subject line
            
        Returns:
            List of (category_name, priority, match_type) tuples
        """
        if not subject:
            return []
        
        # Normalize subject to lowercase for case-insensitive matching
        subject = subject.lower()
        matches = []
        
        # Process categories in priority order
        for cat_id, details in self.sorted_categories:
            category_name = self.category_id_to_name.get(cat_id)
            if not category_name:
                continue
                
            priority = self.category_priorities.get(category_name, 50)
            
            # Check non-regex keywords first (faster)
            keywords = self.rules.get("keywords", {}).get(cat_id, [])
            for kw_data in keywords:
                if not kw_data.get("is_regex", False):
                    keyword = kw_data["keyword"].lower()
                    weight = kw_data.get("weight", 1)
                    
                    if keyword in subject:
                        match_priority = priority - weight  # Lower value = higher priority
                        matches.append((category_name, match_priority, f'subject_keyword:{keyword}'))
            
            # Check regex patterns (slower, but more powerful)
            for pattern, weight in self.compiled_regexes.get(cat_id, []):
                if pattern.search(subject):
                    match_priority = priority - weight
                    matches.append(
                        (category_name, match_priority, f'subject_regex:{pattern.pattern}')
                    )
        
        return matches
    
    def get_sender_category_matches(self, from_email: str) -> List[Tuple[str, int, str]]:
        """
        Find categories matching the sender email.
        
        Args:
            from_email: Email address of the sender
            
        Returns:
            List of (category_name, priority, match_type) tuples
        """
        if not from_email or '@' not in from_email:
            return []
        
        matches = []
        try:
            local_part, domain = from_email.lower().split('@', 1)
        except ValueError:
            logger.warning(f"Invalid email format: {from_email}")
            return []
        
        # Process categories in priority order
        for cat_id, details in self.sorted_categories:
            category_name = self.category_id_to_name.get(cat_id)
            if not category_name:
                continue
                
            priority = self.category_priorities.get(category_name, 50)
            
            # Check sender rules
            sender_rules = self.rules.get("senders", {}).get(cat_id, [])
            for rule in sender_rules:
                pattern = rule["pattern"].lower()
                weight = rule.get("weight", 1)
                is_domain = rule.get("is_domain", True)
                
                if is_domain:
                    # Domain matching (exact or subdomain) - higher priority
                    if domain == pattern:
                        # Exact domain match gets extra weight
                        matches.append(
                            (category_name, priority - (weight * 1.5), f'sender_domain_exact:{pattern}')
                        )
                    elif domain.endswith('.' + pattern):
                        # Subdomain match
                        matches.append(
                            (category_name, priority - weight, f'sender_domain:{pattern}')
                        )
                else:
                    # Substring matching in either part - lower priority
                    if pattern in local_part or pattern in domain:
                        matches.append(
                            (category_name, priority - (weight * 0.8), f'sender_substring:{pattern}')
                        )
        
        return matches
    
    def categorize_email(
        self,
        gmail_labels: List[str], 
        subject: str,
        from_email: str
    ) -> str:
        """
        Determine email category based on Gmail labels, subject keywords, and sender.
        
        Uses a priority-based approach to resolve conflicts when multiple categories match.
        
        Args:
            gmail_labels: List of Gmail labels
            subject: Email subject line
            from_email: Email address of the sender
            
        Returns:
            Category name string
        """
        candidate_categories = []
        
        # Check Gmail labels first (highest precedence)
        if gmail_labels and 'TRASH' in gmail_labels:
            return 'trash'
        elif gmail_labels and 'IMPORTANT' in gmail_labels:
            # Find the important category
            for cat_id, details in self.rules["categories"].items():
                if details["name"].lower() == "important":
                    candidate_categories.append((details["name"], details["priority"] - 2, 'gmail_label_important'))
                    break
        
        # Check Gmail category labels - map these to our database categories
        if gmail_labels:
            gmail_label_to_categories = {}
            
            # Dynamically build the mapping based on database categories
            for cat_id, details in self.rules["categories"].items():
                category_name = details["name"].lower()
                gmail_category = f'CATEGORY_{category_name.upper()}'
                gmail_label_to_categories[gmail_category] = (category_name, details["priority"])
            
            # Handle special cases that might have different naming
            special_mappings = {
                'CATEGORY_PROMOTIONS': 'promotional',
                'CATEGORY_UPDATES': 'updates'
            }
            
            for label, mapped_name in special_mappings.items():
                if label not in gmail_label_to_categories:
                    # Check if we have this category in the database
                    for cat_id, details in self.rules["categories"].items():
                        if details["name"].lower() == mapped_name:
                            gmail_label_to_categories[label] = (mapped_name, details["priority"])
                            break
            
            # Apply Gmail category labels
            for label in gmail_labels:
                if label in gmail_label_to_categories:
                    category_name, priority = gmail_label_to_categories[label]
                    # Gmail categories have high precedence
                    candidate_categories.append((category_name, priority - 1, f'gmail_category:{label}'))
        
        # Check subject keywords and sender patterns in parallel for better performance
        subject_matches = self.get_subject_category_matches(subject)
        sender_matches = self.get_sender_category_matches(from_email)
        
        # Combine all matches
        candidate_categories.extend(subject_matches)
        candidate_categories.extend(sender_matches)
        
        # If no matches, try to find a default category
        if not candidate_categories:
            # Find primary category if it exists
            for cat_id, details in self.sorted_categories:
                if details["name"].lower() == "primary":
                    return details["name"]
            # If no primary category exists, return the first category (highest priority) or a default
            return self.sorted_categories[0][1]["name"] if self.sorted_categories else "primary"
        
        # Sort by priority (lower number = higher priority) and return the highest priority match
        candidate_categories.sort(key=lambda x: x[1])
        best_match = candidate_categories[0]
        
        logger.debug(f"Category matches: {candidate_categories}, selected: {best_match}")
        return best_match[0]


def determine_category(
    gmail_labels: List[str], 
    subject: str,
    from_email: str,
    db: Session,
    user_id: Optional[UUID] = None
) -> str:
    """
    Determine email category based on Gmail labels, subject keywords, and sender.
    
    Uses the dynamic categorizer with database rules.
    
    Args:
        gmail_labels: List of Gmail labels
        subject: Email subject line
        from_email: Email address of the sender
        db: Database session for fetching category rules
        user_id: Optional user ID for personalized rules
        
    Returns:
        Category string
    """
    try:
        # Always use the dynamic categorizer with database rules
        categorizer = DynamicEmailCategorizer(db, user_id)
        return categorizer.categorize_email(gmail_labels, subject, from_email)
    except Exception as e:
        logger.error(f"Error determining category: {str(e)}", exc_info=True)
        # Fallback to primary if an error occurs
        return "primary"


def categorize_email(email_data: Dict[str, Any], db: Session, user_id: Optional[UUID] = None) -> str:
    """
    Helper function to categorize an email from standard email data dictionary.
    This is an enhanced version that combines rule-based categorization with 
    machine learning for trash detection.
    
    Args:
        email_data: Dictionary containing email data
        db: Database session
        user_id: Optional user ID
        
    Returns:
        Category string
    """
    try:
        gmail_labels = email_data.get('labels', [])
        subject = email_data.get('subject', '')
        from_email = email_data.get('from_email', '')
        gmail_id = email_data.get('gmail_id', 'unknown')
        
        # Fast path: Gmail already marked it as trash
        if 'TRASH' in gmail_labels:
            logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as 'trash' based on Gmail TRASH label")
            return "trash"
        
        # First try the rules-based approach
        rules_category = determine_category(gmail_labels, subject, from_email, db, user_id)
        
        # If the rules-based approach determined it's trash, we're done
        if rules_category == "trash":
            logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as 'trash' based on rules")
            
            # Record the event for ML training if we have an email ID
            if 'id' in email_data and user_id:
                record_trash_event(
                    db=db,
                    email_id=email_data['id'],
                    user_id=user_id,
                    event_type='moved_to_trash',
                    email_data=email_data,
                    is_auto_categorized=True,
                    categorization_source='rules',
                    confidence_score=RULES_CONFIDENCE_THRESHOLD
                )
            
            return "trash"
        
        # Next, try the ML-based approach for trash identification
        try:
            ml_category, confidence = nbc_classify_email(email_data)
            
            # If ML model predicts trash with high confidence, use it
            if ml_category == 'trash' and confidence >= ML_CONFIDENCE_THRESHOLD:
                logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as 'trash' by ML model with confidence {confidence:.2f}")
                
                # Record the event for ML training if we have an email ID
                if 'id' in email_data and user_id:
                    record_trash_event(
                        db=db,
                        email_id=email_data['id'],
                        user_id=user_id,
                        event_type='moved_to_trash',
                        email_data=email_data,
                        is_auto_categorized=True,
                        categorization_source='ml',
                        confidence_score=confidence
                    )
                
                return "trash"
            
            # For borderline cases, use weighted decision
            if ml_category == 'trash' and confidence >= 0.6:
                # Log for inspection
                logger.info(f"[CATEGORIZER] Borderline trash case: {gmail_id}, ML confidence: {confidence:.2f}")
                
                # Use rules as default in borderline cases
                return rules_category
                
        except Exception as e:
            logger.error(f"[CATEGORIZER] Error in ML categorization for {gmail_id}: {str(e)}", exc_info=True)
            # Continue with rules-based categorization on ML error
        
        # If we get here, use the rules-based categorization result
        logger.info(f"[CATEGORIZER] Email {gmail_id} categorized as '{rules_category}' based on rules")
        return rules_category
        
    except Exception as e:
        logger.error(f"Error categorizing email: {str(e)}", exc_info=True)
        # Fallback to primary if an error occurs
        return "primary" 