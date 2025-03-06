"""
Email categorization utilities with keyword matching capabilities.

This module implements efficient algorithms for categorizing emails
based on their content, subject, and metadata.
"""
import re
import logging
from typing import Dict, Any, Set, List, Tuple, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..constants.email_categories import (
    CATEGORY_KEYWORDS, 
    SENDER_DOMAINS,
    CATEGORY_PRIORITY
)
from ..services.category_service import get_categorization_rules
from ..models.user import User

logger = logging.getLogger(__name__)

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
        
        logger.info(f"Initialized dynamic categorizer with {len(self.rules['categories'])} categories, "
                   f"{sum(len(kws) for kws in self.rules['keywords'].values())} keywords, and "
                   f"{sum(len(srs) for srs in self.rules['senders'].values())} sender rules")
    
    def _compile_regex_patterns(self):
        """Compile regex patterns for better performance"""
        # Compile regex patterns for keywords
        for category_id, keywords in self.rules["keywords"].items():
            for i, keyword_data in enumerate(keywords):
                if keyword_data.get("is_regex", False):
                    try:
                        pattern = re.compile(keyword_data["keyword"], re.IGNORECASE)
                        self.rules["keywords"][category_id][i]["compiled_pattern"] = pattern
                    except re.error as e:
                        logger.error(f"Invalid regex pattern '{keyword_data['keyword']}': {e}")
                else:
                    # For regular keywords, create a word boundary pattern
                    pattern = r'\b' + re.escape(keyword_data["keyword"].lower()) + r'\b'
                    try:
                        self.rules["keywords"][category_id][i]["compiled_pattern"] = re.compile(pattern, re.IGNORECASE)
                    except re.error as e:
                        logger.error(f"Error compiling pattern for '{keyword_data['keyword']}': {e}")
    
    def get_subject_category_matches(self, subject: str) -> Dict[int, List[Dict[str, Any]]]:
        """
        Find keyword matches in the email subject for each category.
        
        Args:
            subject: Email subject line
            
        Returns:
            Dictionary mapping category IDs to lists of matched keywords with weights
        """
        if not subject:
            return {}
        
        # Normalize subject for matching
        normalized_subject = subject.lower()
        
        # Dictionary to store matches by category ID
        matches: Dict[int, List[Dict[str, Any]]] = {}
        
        # Check each category's keywords
        for category_id, keywords in self.rules["keywords"].items():
            category_matches = []
            
            for keyword_data in keywords:
                # Skip invalid keywords
                if "compiled_pattern" not in keyword_data:
                    continue
                
                pattern = keyword_data["compiled_pattern"]
                
                if pattern.search(normalized_subject):
                    match_data = {
                        "keyword": keyword_data["keyword"],
                        "weight": keyword_data.get("weight", 1)
                    }
                    category_matches.append(match_data)
                    
                    category_name = self.category_id_to_name.get(category_id, f"category_{category_id}")
                    logger.debug(f"Matched keyword '{keyword_data['keyword']}' in subject: '{subject}' "
                                f"for category '{category_name}'")
            
            # Only add categories with matches
            if category_matches:
                matches[category_id] = category_matches
        
        return matches
    
    def get_sender_category(self, from_email: str) -> Optional[Tuple[int, float]]:
        """
        Determine email category based on sender domain or address pattern.
        
        Args:
            from_email: Email address of the sender
            
        Returns:
            Tuple of (category_id, weight) or None if no match
        """
        if not from_email or '@' not in from_email:
            return None
        
        # Extract domain and local part, lowercase for matching
        try:
            local_part, domain = from_email.lower().split('@', 1)
            best_match = None
            best_weight = 0
            
            # Check each category's sender rules
            for category_id, rules in self.rules["senders"].items():
                for rule in rules:
                    pattern = rule["pattern"].lower()
                    weight = rule.get("weight", 1)
                    
                    if rule.get("is_domain", True):
                        # Full domain matching
                        if domain == pattern:
                            # Exact domain match has highest priority
                            category_name = self.category_id_to_name.get(category_id, f"category_{category_id}")
                            logger.debug(f"Matched sender domain '{domain}' to category '{category_name}'")
                            return (category_id, weight * 1.5)  # Boost exact matches
                        elif domain.endswith("." + pattern):
                            # Subdomain match
                            if not best_match or weight > best_weight:
                                best_match = (category_id, weight)
                                best_weight = weight
                    else:
                        # Substring matching in either domain or local part
                        if pattern in domain or pattern in local_part:
                            if not best_match or weight > best_weight:
                                best_match = (category_id, weight)
                                best_weight = weight
            
            if best_match:
                category_id, weight = best_match
                category_name = self.category_id_to_name.get(category_id, f"category_{category_id}")
                logger.debug(f"Matched sender pattern in '{from_email}' to category '{category_name}'")
                return best_match
                
        except Exception as e:
            logger.warning(f"Error parsing email '{from_email}': {str(e)}")
        
        return None
    
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
        
        # First check Gmail labels (highest precedence)
        if 'TRASH' in gmail_labels:
            return 'trash'
        elif 'IMPORTANT' in gmail_labels:
            # Find the important category ID
            for cat_id, details in self.rules["categories"].items():
                if details["name"] == "important":
                    candidate_categories.append((details["name"], details["priority"] - 1, 'gmail_label'))
                    break
        
        # Check Gmail category labels
        label_mapping = {
            'CATEGORY_PROMOTIONS': 'promotional',
            'CATEGORY_SOCIAL': 'social',
            'CATEGORY_UPDATES': 'updates',
            'CATEGORY_FORUMS': 'forums',
            'CATEGORY_PERSONAL': 'personal'
        }
        
        for label, category_name in label_mapping.items():
            if label in gmail_labels:
                # Find the priority for this category
                priority = self.category_priorities.get(category_name, 50)
                candidate_categories.append((category_name, priority, 'gmail_category'))
        
        # Check subject keywords
        subject_matches = self.get_subject_category_matches(subject)
        for category_id, matches in subject_matches.items():
            if category_id not in self.category_id_to_name:
                continue
                
            category_name = self.category_id_to_name[category_id]
            
            # Calculate total weight of matches
            total_weight = sum(match["weight"] for match in matches)
            
            # More matches increase the priority within the category
            base_priority = self.category_priorities.get(category_name, 50)
            adjusted_priority = base_priority - (0.1 * total_weight)
            
            matched_keywords = ",".join(match["keyword"] for match in matches)
            candidate_categories.append((
                category_name, 
                adjusted_priority, 
                f'subject_keywords:{matched_keywords}'
            ))
        
        # Check sender domain/patterns
        sender_match = self.get_sender_category(from_email)
        if sender_match:
            category_id, weight = sender_match
            if category_id in self.category_id_to_name:
                category_name = self.category_id_to_name[category_id]
                base_priority = self.category_priorities.get(category_name, 50)
                adjusted_priority = base_priority - (0.2 * weight)  # Sender has slightly higher weight
                
                candidate_categories.append((
                    category_name, 
                    adjusted_priority, 
                    f'sender:{from_email}'
                ))
        
        # Sort by priority (lower is better)
        candidate_categories.sort(key=lambda x: x[1])
        
        # Log all possible categorizations for debugging
        if candidate_categories:
            logger.debug(f"Categorization candidates: {candidate_categories}")
            category, _, reason = candidate_categories[0]
            logger.info(f"Selected category '{category}' based on {reason}")
            return category
        
        # Default cases from original function
        if 'INBOX' not in gmail_labels:
            # If email doesn't have INBOX label, it's archived
            return 'archive'
        else:
            return 'primary'

# For backward compatibility, provide functions that use the class internally
def get_subject_category_matches(subject: str) -> Dict[str, List[str]]:
    """
    Legacy function for finding keyword matches in subject.
    Uses the static rules from constants for backward compatibility.
    
    Args:
        subject: Email subject line
        
    Returns:
        Dictionary mapping categories to lists of matched keywords
    """
    if not subject:
        return {}
    
    # Normalize subject for case-insensitive matching
    normalized_subject = subject.lower()
    
    # Dictionary to store matches
    matches: Dict[str, List[str]] = {}
    
    # Check each category's keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        # Find all keyword matches in the subject
        category_matches = []
        
        for keyword in keywords:
            # Use word boundary regex pattern for whole word matching
            # This avoids matching substrings within words
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            
            if re.search(pattern, normalized_subject):
                category_matches.append(keyword)
                logger.debug(f"Matched keyword '{keyword}' in subject: '{subject}'")
        
        # Only add categories with matches
        if category_matches:
            matches[category] = category_matches
    
    return matches

def get_sender_category(from_email: str) -> Optional[str]:
    """
    Legacy function for determining email category based on sender.
    Uses the static rules from constants for backward compatibility.
    
    Args:
        from_email: Email address of the sender
        
    Returns:
        Category string or None if no match
    """
    if not from_email or '@' not in from_email:
        return None
    
    # Extract domain and lowercase for matching
    try:
        # Extract both the local part and domain
        local_part, domain = from_email.lower().split('@', 1)
        
        # Check if the domain directly matches
        if domain in SENDER_DOMAINS:
            matched_category = SENDER_DOMAINS[domain]
            logger.debug(f"Matched sender domain '{domain}' to category '{matched_category}'")
            return matched_category
        
        # Check for substrings in either domain or local part
        for key, category in SENDER_DOMAINS.items():
            if key in domain or key in local_part:
                logger.debug(f"Matched sender pattern '{key}' in '{from_email}' to category '{category}'")
                return category
                
    except Exception as e:
        logger.warning(f"Error parsing email '{from_email}': {str(e)}")
    
    return None

def determine_category(
    gmail_labels: List[str], 
    subject: str,
    from_email: str,
    db: Optional[Session] = None,
    user_id: Optional[UUID] = None
) -> str:
    """
    Determine email category based on Gmail labels, subject keywords, and sender.
    
    If db session is provided, uses the dynamic categorizer with database rules.
    Otherwise, falls back to static rules from constants.
    
    Args:
        gmail_labels: List of Gmail labels
        subject: Email subject line
        from_email: Email address of the sender
        db: Optional database session for dynamic rules
        user_id: Optional user ID for personalized rules
        
    Returns:
        Category string
    """
    # If database session is provided, use dynamic categorization
    if db is not None:
        categorizer = DynamicEmailCategorizer(db, user_id)
        return categorizer.categorize_email(gmail_labels, subject, from_email)
    
    # Otherwise, use the legacy static implementation
    candidate_categories = []
    
    # First check Gmail labels (highest precedence)
    if 'TRASH' in gmail_labels:
        return 'trash'
    elif 'IMPORTANT' in gmail_labels:
        candidate_categories.append(('important', 1, 'gmail_label'))
    
    # Check Gmail category labels
    label_mapping = {
        'CATEGORY_PROMOTIONS': 'promotional',
        'CATEGORY_SOCIAL': 'social',
        'CATEGORY_UPDATES': 'updates',
        'CATEGORY_FORUMS': 'forums',
        'CATEGORY_PERSONAL': 'personal'
    }
    
    for label, category in label_mapping.items():
        if label in gmail_labels:
            # Priority is based on pre-defined order
            priority = CATEGORY_PRIORITY.get(category, 10)
            candidate_categories.append((category, priority, 'gmail_category'))
    
    # Check subject keywords
    subject_matches = get_subject_category_matches(subject)
    for category, matches in subject_matches.items():
        # More matches increase the priority within the category
        priority = CATEGORY_PRIORITY.get(category, 10) - (0.1 * len(matches))
        candidate_categories.append((category, priority, f'subject_keywords:{",".join(matches)}'))
    
    # Check sender domain/patterns
    sender_category = get_sender_category(from_email)
    if sender_category:
        priority = CATEGORY_PRIORITY.get(sender_category, 10)
        candidate_categories.append((sender_category, priority, f'sender:{from_email}'))
    
    # Sort by priority (lower is better)
    candidate_categories.sort(key=lambda x: x[1])
    
    # Log all possible categorizations for debugging
    if candidate_categories:
        logger.debug(f"Categorization candidates: {candidate_categories}")
        category, _, reason = candidate_categories[0]
        logger.info(f"Selected category '{category}' based on {reason}")
        return category
    
    # Default cases from original function
    if 'INBOX' not in gmail_labels:
        # If email doesn't have INBOX label, it's archived
        return 'archive'
    else:
        return 'primary' 