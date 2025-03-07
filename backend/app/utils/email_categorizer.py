"""
Email categorization utilities with keyword matching capabilities.

This module implements efficient algorithms for categorizing emails
based on their content, subject, and metadata, using database-stored rules.
"""
import re
import logging
from typing import Dict, Any, Set, List, Tuple, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..services.category_service import get_categorization_rules

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
        """Pre-compile regex patterns for better performance"""
        self.compiled_regexes = {}
        
        for cat_id, keywords in self.rules.get("keywords", {}).items():
            self.compiled_regexes[cat_id] = []
            for kw_data in keywords:
                if kw_data.get("is_regex", False):
                    try:
                        pattern = re.compile(kw_data["keyword"], re.IGNORECASE)
                        self.compiled_regexes[cat_id].append(pattern)
                    except re.error:
                        logger.warning(f"Invalid regex pattern: {kw_data['keyword']}")
    
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
        
        # Check each category's keywords
        for cat_id, keywords in self.rules.get("keywords", {}).items():
            category_name = self.category_id_to_name.get(cat_id)
            if not category_name:
                continue
                
            priority = self.category_priorities.get(category_name, 50)
            
            # Check non-regex keywords
            for kw_data in keywords:
                if not kw_data.get("is_regex", False):
                    keyword = kw_data["keyword"].lower()
                    weight = kw_data.get("weight", 1)
                    
                    if keyword in subject:
                        matches.append((category_name, priority - weight, f'subject_keyword:{keyword}'))
            
            # Check regex patterns
            for pattern in self.compiled_regexes.get(cat_id, []):
                if pattern.search(subject):
                    matches.append(
                        (category_name, priority - 1, f'subject_regex:{pattern.pattern}')
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
        local_part, domain = from_email.lower().split('@', 1)
        
        # Check each category's sender rules
        for cat_id, sender_rules in self.rules.get("senders", {}).items():
            category_name = self.category_id_to_name.get(cat_id)
            if not category_name:
                continue
                
            priority = self.category_priorities.get(category_name, 50)
            
            for rule in sender_rules:
                pattern = rule["pattern"].lower()
                weight = rule.get("weight", 1)
                is_domain = rule.get("is_domain", True)
                
                if is_domain:
                    # Domain matching (exact or subdomain)
                    if domain == pattern or domain.endswith('.' + pattern):
                        matches.append(
                            (category_name, priority - weight, f'sender_domain:{pattern}')
                        )
                else:
                    # Substring matching in either part
                    if pattern in local_part or pattern in domain:
                        matches.append(
                            (category_name, priority - weight, f'sender_substring:{pattern}')
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
        
        # First check Gmail labels (highest precedence)
        if 'TRASH' in gmail_labels:
            return 'trash'
        elif 'IMPORTANT' in gmail_labels:
            # Find the important category ID
            for cat_id, details in self.rules["categories"].items():
                if details["name"] == "important":
                    candidate_categories.append((details["name"], details["priority"] - 1, 'gmail_label'))
                    break
        
        # Check Gmail category labels - map these to our database categories
        gmail_label_to_categories = {}
        
        # Dynamically build the mapping based on database categories
        for cat_id, details in self.rules["categories"].items():
            category_name = details["name"].lower()
            gmail_category = f'CATEGORY_{category_name.upper()}'
            gmail_label_to_categories[gmail_category] = category_name
        
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
                        gmail_label_to_categories[label] = mapped_name
                        break
        
        # Apply Gmail category labels
        for label, category_name in gmail_label_to_categories.items():
            if label in gmail_labels:
                priority = self.category_priorities.get(category_name, 50)
                candidate_categories.append((category_name, priority, 'gmail_category'))
        
        # Check subject keywords
        subject_matches = self.get_subject_category_matches(subject)
        candidate_categories.extend(subject_matches)
        
        # Check sender patterns
        sender_matches = self.get_sender_category_matches(from_email)
        candidate_categories.extend(sender_matches)
        
        # Default to primary if no matches
        if not candidate_categories:
            # Find primary category if it exists
            for cat_id, details in self.rules["categories"].items():
                if details["name"] == "primary":
                    return details["name"]
            # If no primary category exists, return the first category or a default
            return next(iter(self.category_id_to_name.values()), "primary")
        
        # Sort by priority (lower is higher priority) and return the highest priority match
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
    # Always use the dynamic categorizer with database rules
    categorizer = DynamicEmailCategorizer(db, user_id)
    return categorizer.categorize_email(gmail_labels, subject, from_email)


def categorize_email(email_data: Dict[str, Any], db: Session, user_id: Optional[UUID] = None) -> str:
    """
    Helper function to categorize an email from standard email data dictionary.
    
    Args:
        email_data: Dictionary containing email data
        db: Database session
        user_id: Optional user ID
        
    Returns:
        Category string
    """
    gmail_labels = email_data.get('labels', [])
    subject = email_data.get('subject', '')
    from_email = email_data.get('from_email', '')
    
    return determine_category(gmail_labels, subject, from_email, db, user_id) 