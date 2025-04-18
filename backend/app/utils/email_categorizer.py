"""
Email categorization utilities with modular categorization capabilities.

This module implements a modular and extensible approach to categorizing emails
based on their content, subject, labels, and metadata, using database-stored rules.
"""
import re
import logging
from typing import Dict, Any, Set, List, Tuple, Optional, Union, Pattern, Protocol, Callable
from sqlalchemy.orm import Session
from uuid import UUID
from ..services.category_service import get_categorization_rules
from functools import lru_cache, wraps
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule
import json
from collections import defaultdict
from datetime import datetime
import time

# Import the Naive Bayes classifier
from .naive_bayes_classifier import classify_email as nbc_classify_email, record_trash_event

# Import logging utilities first to avoid circular imports
from .logging_utils import EmailLogger, log_operation, summarize_matches, sanitize_email

# Set up logger
logger = logging.getLogger(__name__)

# Constants for weighted decision making
ML_CONFIDENCE_THRESHOLD = 0.75  # High confidence threshold for ML
TRASH_CONFIDENCE_THRESHOLD = 0.85  # Higher threshold specifically for trash classification
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

# Define protocol/interface for categorizers
class EmailCategorizer(Protocol):
    """Protocol defining the interface for email categorizers"""
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize an email and return the category with confidence
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        ...

class LabelsBasedCategorizer:
    """Categorizer that uses Gmail labels to determine email category"""
    
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None, rules: Optional[dict] = None):
        """Initialize with DB session and optional user ID or rules"""
        self.db = db
        self.user_id = user_id
        self.rules = rules if rules is not None else get_categorization_rules(db, user_id)
        
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
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize email based on Gmail labels
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        gmail_labels = email_data.get('labels', [])
        
        logger.info(f"[EMAIL_CAT_LABELS] Checking labels: {', '.join(gmail_labels) if gmail_labels else 'None'}")
        
        if not gmail_labels:
            logger.info(f"[EMAIL_CAT_LABELS] No labels found")
            return ('unknown', 0.0, 'no_labels')
            
        # Standard Gmail system labels to our categories mapping
        # Using only existing Gmail labels, not trying to create new ones
        gmail_label_to_categories = {
            # Gmail native categories if they exist
            'INBOX': ('inbox', 10),
            'TRASH': ('trash', 5),
            'SPAM': ('spam', 5),
            'SENT': ('sent', 5),
            'DRAFT': ('draft', 5),
            
            # Gmail categorization system (we read but don't set these)
            'CATEGORY_PERSONAL': ('personal', 15),
            'CATEGORY_SOCIAL': ('social', 15),
            'CATEGORY_PROMOTIONS': ('promotional', 15),
            'CATEGORY_UPDATES': ('updates', 15),
            'CATEGORY_FORUMS': ('forums', 15)
        }
        
        # Handle special case: archive (no INBOX label)
        if 'INBOX' not in gmail_labels:
            if 'SENT' in gmail_labels or 'DRAFT' in gmail_labels:
                logger.info(f"[EMAIL_CAT_LABELS] Email is SENT or DRAFT, not archive")
                # Skip archive for sent or draft emails
                pass
            else:
                # Not in inbox and not sent/draft = archive
                logger.info(f"[EMAIL_CAT_LABELS] Email not in INBOX, categorizing as 'archive'")
                return ('archive', 0.9, 'no_inbox_label')
        
        # Apply Gmail category labels
        matched_categories = []
        for label in gmail_labels:
            if label in gmail_label_to_categories:
                category_name, priority = gmail_label_to_categories[label]
                # Gmail categories have high confidence - Change from 0.9 to 1.0
                matched_categories.append((category_name, 1.0, f'gmail_label:{label}', priority))
                logger.info(f"[EMAIL_CAT_LABELS] Matched label '{label}' to category '{category_name}'")
        
        if matched_categories:
            # Sort by priority (lower number = higher priority)
            matched_categories.sort(key=lambda x: x[3])
            best_match = matched_categories[0]
            logger.info(f"[EMAIL_CAT_LABELS] Best match: '{best_match[0]}' ({best_match[2]})")
            return (best_match[0], best_match[1], best_match[2])
            
        # Default to inbox for emails that have the INBOX label but no other category
        if 'INBOX' in gmail_labels:
            logger.info(f"[EMAIL_CAT_LABELS] Email has INBOX label, defaulting to 'inbox'")
            # Update this confidence from 0.7 to 1.0 as well
            return ('inbox', 1.0, 'inbox_label')
        
        # Default unknown for everything else
        logger.info(f"[EMAIL_CAT_LABELS] No category matches found")
        return ('unknown', 0.3, 'no_category_matches')

class KeywordBasedCategorizer:
    """Categorizer that uses subject line keywords to determine email category"""
    
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None, rules: Optional[dict] = None):
        """Initialize with DB session and optional user ID or rules"""
        self.db = db
        self.user_id = user_id
        self.rules = rules if rules is not None else get_categorization_rules(db, user_id)
        
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
        
        # Compile regex patterns for better performance
        self._compile_regex_patterns()
        
        # Sort categories by priority for faster processing
        self.sorted_categories = sorted(
            [(cat_id, details) for cat_id, details in self.rules["categories"].items()],
            key=lambda x: x[1]["priority"]
        )
    
    def _compile_regex_patterns(self):
        """Pre-compile regex patterns for better performance"""
        self.compiled_regexes = {}
        
        for cat_id, keywords in self.rules.get("keywords", {}).items():
            self.compiled_regexes[cat_id] = []
            for kw_data in keywords:
                if kw_data.get("is_regex", False):
                    pattern = compile_regex(kw_data["keyword"])
                    self.compiled_regexes[cat_id].append((pattern, kw_data.get("weight", 1)))
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize email based on subject line keywords
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        subject = email_data.get('subject', '[No Subject]')
        
        logger.info(f"[EMAIL_CAT_KEYWORDS] Checking subject: '{subject}'")
        
        if not subject:
            logger.info(f"[EMAIL_CAT_KEYWORDS] No subject found")
            return ('unknown', 0.0, 'no_subject')
        
        matches = self.get_subject_category_matches(subject)
        if not matches:
            logger.info(f"[EMAIL_CAT_KEYWORDS] No keyword matches found in subject")
            return ('unknown', 0.0, 'no_keyword_matches')
        
        # Log all matches found
        for match in matches:
            logger.info(f"[EMAIL_CAT_KEYWORDS] Match: '{match[0]}' ({match[2]})")
            
        # Sort by priority (lower number = higher priority)
        matches.sort(key=lambda x: x[1])
        best_match = matches[0]
        category_name = best_match[0]
        match_type = best_match[2]
        
        # Calculate confidence based on match type
        confidence = 0.0
        if "subject_keyword" in match_type:
            confidence = 0.8
        elif "subject_regex" in match_type:
            confidence = 0.7
        
        logger.info(f"[EMAIL_CAT_KEYWORDS] Best match: '{category_name}' with confidence {confidence} ({match_type})")
        return (category_name, confidence, match_type)
    
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

class SenderBasedCategorizer:
    """Categorizer that uses sender email domain to determine email category"""
    
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None, rules: Optional[dict] = None):
        """Initialize with DB session and optional user ID or rules"""
        self.db = db
        self.user_id = user_id
        self.rules = rules if rules is not None else get_categorization_rules(db, user_id)
        
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
        
        # Initialize logger (will be set from composite categorizer)
        self.email_logger = None
    
    @log_operation("sender_categorization")
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """Categorize email based on sender email domain"""
        from_email = email_data.get('from_email', '[No Sender]')
        
        self.email_logger.debug("Processing sender", details={"from_email": sanitize_email(from_email)})
        
        if not from_email or '@' not in from_email:
            self.email_logger.warning(
                "Invalid sender email",
                details={"reason": "missing_at_symbol" if from_email else "empty_email"}
            )
            return ('unknown', 0.0, 'invalid_sender')
        
        matches = self.get_sender_category_matches(from_email)
        if not matches:
            self.email_logger.debug("No sender matches found")
            return ('unknown', 0.0, 'no_sender_matches')
        
        # Sort by priority and weight
        matches.sort(key=lambda x: (x[1], -float(x[2].split(':')[-1])))
        best_match = matches[0]
        category_name = best_match[0]
        match_type = best_match[2]
        
        # Calculate confidence based on match type
        confidence = self._calculate_confidence(match_type)
        
        self.email_logger.info(
            "Sender categorization complete",
            details={
                "category": category_name,
                "confidence": confidence,
                "match_type": match_type
            }
        )
        
        return (category_name, confidence, match_type)
    
    def _calculate_confidence(self, match_type: str) -> float:
        """Calculate confidence score based on match type."""
        if "user_rule" in match_type:
            if "sender_domain_exact" in match_type:
                return 0.95  # Highest confidence for user-specific exact domain matches
            elif "sender_domain" in match_type:
                return 0.9   # High confidence for user-specific domain matches
            elif "sender_substring" in match_type:
                return 0.85  # Good confidence for user-specific substring matches
        else:
            if "sender_domain_exact" in match_type:
                return 0.8   # Good confidence for system exact domain matches
            elif "sender_domain" in match_type:
                return 0.7   # Moderate confidence for system domain matches
            elif "sender_substring" in match_type:
                return 0.6   # Lower confidence for system substring matches
        return 0.5  # Default confidence
    
    @log_operation("sender_matching")
    def get_sender_category_matches(self, from_email: str) -> List[Tuple[str, int, str]]:
        """Find categories matching the sender email."""
        if not from_email or '@' not in from_email:
            self.email_logger.warning(
                "Invalid email format",
                details={
                    "from_email": sanitize_email(from_email),
                    "reason": "missing_at_symbol" if from_email else "empty_email"
                }
            )
            return []
        
        matches = []
        try:
            local_part, domain = from_email.lower().split('@', 1)
        except ValueError:
            self.email_logger.error(
                "Email split error",
                Exception(f"Invalid email format: {sanitize_email(from_email)}")
            )
            return []
        
        self.email_logger.debug(
            "Processing email parts",
            details={
                "domain": domain,
                "local_part_length": len(local_part)
            }
        )
        
        # Process categories in priority order
        for cat_id, details in self.sorted_categories:
            category_name = self.category_id_to_name.get(cat_id)
            if not category_name:
                continue
            
            priority = self.category_priorities.get(category_name, 50)
            sender_rules = self.rules.get("senders", {}).get(cat_id, [])
            
            self.email_logger.debug(
                "Processing category rules",
                details={
                    "category": category_name,
                    "priority": priority,
                    "num_rules": len(sender_rules)
                }
            )
            
            # Check exact domain matches first (highest confidence)
            exact_match_found = False
            for rule in sender_rules:
                if not rule.get("is_domain", True):
                    continue
                    
                pattern = rule["pattern"].lower()
                weight = rule.get("weight", 1)
                is_user_rule = rule.get("user_id") is not None
                
                if domain == pattern:
                    match_info = self._create_match_info(
                        category_name, priority, weight,
                        "sender_domain_exact", pattern, is_user_rule
                    )
                    matches.append(match_info)
                    self.email_logger.debug(
                        "Exact domain match found",
                        details={
                            "category": category_name,
                            "pattern": pattern,
                            "is_user_rule": is_user_rule
                        }
                    )
                    exact_match_found = True
            
            # Check for subdomain or domain base matches
            if not exact_match_found:
                for rule in sender_rules:
                    if not rule.get("is_domain", True):
                        continue
                        
                    pattern = rule["pattern"].lower()
                    weight = rule.get("weight", 1)
                    is_user_rule = rule.get("user_id") is not None
                    
                    # Check for subdomain matches
                    if domain.endswith('.' + pattern) or pattern.endswith('.' + domain):
                        match_info = self._create_match_info(
                            category_name, priority, weight * 1.5,
                            "sender_domain", pattern, is_user_rule
                        )
                        matches.append(match_info)
                        self.email_logger.debug(
                            "Subdomain match found",
                            details={
                                "category": category_name,
                                "pattern": pattern,
                                "is_user_rule": is_user_rule,
                                "match_type": "subdomain"
                            }
                        )
                    
                    # Check base domain match
                    domain_parts = domain.split('.')
                    pattern_parts = pattern.split('.')
                    if len(domain_parts) >= 2 and len(pattern_parts) >= 2:
                        domain_base = '.'.join(domain_parts[-2:])
                        pattern_base = '.'.join(pattern_parts[-2:])
                        if domain_base == pattern_base:
                            match_info = self._create_match_info(
                                category_name, priority, weight,
                                "sender_domain_base", pattern, is_user_rule
                            )
                            matches.append(match_info)
                            self.email_logger.debug(
                                "Base domain match found",
                                details={
                                    "category": category_name,
                                    "pattern": pattern,
                                    "domain_base": domain_base,
                                    "is_user_rule": is_user_rule
                                }
                            )
        
            # Check for substring matches (always check regardless of domain matches)
            for rule in sender_rules:
                if rule.get("is_domain", True):
                    continue
                    
                pattern = rule["pattern"].lower()
                weight = rule.get("weight", 1)
                is_user_rule = rule.get("user_id") is not None
                
                if pattern in local_part or pattern in domain:
                    match_location = "local_part" if pattern in local_part else "domain"
                    match_info = self._create_match_info(
                        category_name, priority, weight,
                        "sender_substring", pattern, is_user_rule
                    )
                    matches.append(match_info)
                    self.email_logger.debug(
                        "Substring match found",
                        details={
                            "category": category_name,
                            "pattern": pattern,
                            "match_location": match_location,
                            "is_user_rule": is_user_rule
                        }
                    )
        
        if matches:
            self.email_logger.info(
                "Sender matching complete",
                details={"matches": summarize_matches(matches)}
            )
        
        return matches
    
    def _create_match_info(
        self, category: str, priority: int, weight: float,
        match_type: str, pattern: str, is_user_rule: bool
    ) -> Tuple[str, int, str]:
        """Create a standardized match info tuple."""
        rule_type = "user_rule" if is_user_rule else "system_rule"
        return (
            category,
            priority - (weight if match_type != "sender_substring" else 0),
            f"{rule_type}:{match_type}:{pattern}:{weight}"
        )

class MLBasedCategorizer:
    """Categorizer that uses ML model to determine if an email is trash"""
    
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None, rules: Optional[dict] = None):
        """Initialize with DB session and optional user ID or rules"""
        self.db = db
        self.user_id = user_id
        self.rules = rules if rules is not None else get_categorization_rules(db, user_id)
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize email using ML model (specifically for trash detection)
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        subject = email_data.get('subject', '[No Subject]')
        from_email = email_data.get('from_email', '[No Sender]')
        
        logger.info(f"[EMAIL_CAT_ML] Running ML classification")
        
        try:
            # Use the Naive Bayes classifier for trash detection
            # Pass user_id to ensure the correct model is loaded
            ml_category, confidence = nbc_classify_email(email_data, self.user_id)
            
            logger.info(f"[EMAIL_CAT_ML] ML prediction: '{ml_category}' with confidence {confidence:.4f}")
            
            if ml_category == 'trash':
                # Extract features that contributed to the classification
                features_used = self.extract_classification_features(email_data, 'trash')
                features_str = ", ".join(features_used)
                
                logger.info(f"[EMAIL_CAT_ML] Trash classification features: {features_str}")
                
                # Apply stricter confidence threshold for trash classification
                if confidence >= TRASH_CONFIDENCE_THRESHOLD:
                    logger.info(f"[EMAIL_CAT_ML] High confidence trash classification ({confidence:.4f} >= {TRASH_CONFIDENCE_THRESHOLD})")
                    reason = f"ml_prediction:trash:{features_str}"
                    return ('trash', confidence, reason)
                else:
                    logger.info(f"[EMAIL_CAT_ML] Trash classification below threshold ({confidence:.4f} < {TRASH_CONFIDENCE_THRESHOLD})")
                    reason = f"ml_low_confidence:trash:{confidence:.4f}:{features_str}"
                    # Return unknown with 0 confidence to allow other categorizers to decide
                    return ('unknown', 0.0, reason)
            elif ml_category != 'unknown' and confidence > 0:
                # ML model classified as a non-trash category
                features_used = self.extract_classification_features(email_data, ml_category)
                features_str = ", ".join(features_used)
                
                logger.info(f"[EMAIL_CAT_ML] ML classification as '{ml_category}': {features_str}")
                reason = f"ml_prediction:{ml_category}:{features_str}"
                
                # Only return non-trash categories if confidence is high enough
                if confidence >= ML_CONFIDENCE_THRESHOLD:
                    return (ml_category, confidence, reason)
                else:
                    # Low confidence, default to unknown
                    return ('unknown', 0.0, f'ml_low_confidence:{ml_category}:{confidence:.2f}')
            else:
                # ML model didn't classify with enough confidence
                logger.info(f"[EMAIL_CAT_ML] Not classified with sufficient confidence")
                return ('unknown', 0.0, 'ml_insufficient_confidence')
        except Exception as e:
            logger.error(f"[EMAIL_CAT_ML] Error in ML categorization: {str(e)}", exc_info=True)
            return ('unknown', 0.0, f'ml_error:{str(e)}')
    
    def extract_classification_features(self, email_data: Dict[str, Any], category: str) -> List[str]:
        """
        Extract the key features that likely contributed to the ML classification.
        Uses database category rules to identify relevant features.
        
        Args:
            email_data: Email data including subject, labels, etc.
            category: The category predicted by ML
            
        Returns:
            List of feature descriptions that likely contributed to the classification
        """
        features = []
        
        # Get category ID for this category name
        category_id = None
        for cat_id, details in self.rules["categories"].items():
            if details["name"].lower() == category.lower():
                category_id = cat_id
                break
        
        # Extract sender domain and check against sender rules
        from_email = email_data.get('from_email', '')
        if '@' in from_email:
            domain = from_email.split('@')[1]
            
            # Check if this domain is in the sender rules for this category
            sender_match = False
            if category_id:
                for rule in self.rules.get("senders", {}).get(category_id, []):
                    pattern = rule["pattern"].lower()
                    if pattern in domain or (rule.get("is_domain", True) and domain.endswith('.' + pattern)):
                        sender_match = True
                        features.append(f"sender:{pattern}")
            
            # If no sender rule matches, just add the domain
            if not sender_match:
                features.append(f"sender:{domain}")
        
        # Check subject against keyword rules
        subject = email_data.get('subject', '')
        if subject and category_id:
            subject_lower = subject.lower()
            keyword_match = False
            
            # Check against database keywords for this category
            for kw_data in self.rules.get("keywords", {}).get(category_id, []):
                keyword = kw_data["keyword"].lower()
                is_regex = kw_data.get("is_regex", False)
                
                if is_regex:
                    pattern = compile_regex(keyword)
                    if pattern.search(subject_lower):
                        keyword_match = True
                        features.append(f"subject_regex:{keyword}")
                elif keyword in subject_lower:
                    keyword_match = True
                    features.append(f"subject:{keyword}")
            
            # If no explicit keyword match, try to extract common words
            if not keyword_match:
                important_words = extract_important_words(subject, 3)
                for word in important_words:
                    features.append(f"subject_word:{word}")
        
        # Extract from snippet
        snippet = email_data.get('snippet', '')
        if snippet:
            # Look for common signals in content
            for signal in ["unsubscribe", "view in browser", "privacy policy", "email preferences"]:
                if signal in snippet.lower():
                    features.append(f"content:{signal}")
            
            # Extract important words from snippet if no specific signals
            if not any(f.startswith("content:") for f in features):
                important_words = extract_important_words(snippet, 3)
                for word in important_words:
                    features.append(f"content_word:{word}")
        
        # If we couldn't extract specific features, provide a generic explanation
        if not features:
            features.append("complex_pattern")
        
        return features

def extract_important_words(text: str, max_words: int = 3) -> List[str]:
    """
    Extract important words from text, filtering out common stop words.
    
    Args:
        text: The text to analyze
        max_words: Maximum number of words to return
        
    Returns:
        List of important words
    """
    # Basic list of common English stop words to filter out
    stop_words = {
        "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
        "when", "where", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
        "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain",
        "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn",
        "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren",
        "won", "wouldn", "to", "from", "for", "with", "in", "on", "at"
    }
    
    # Clean and tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words and count word frequencies
    word_counts = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top words
    important_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in important_words[:max_words]]

class CompositeCategorizer:
    """
    Composite categorizer that combines multiple categorization approaches
    with priority-based resolution.
    """
    
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None, use_ml: bool = True, rules: Optional[dict] = None):
        """
        Initialize with DB session and optional user ID or rules
        """
        self.db = db
        self.user_id = user_id
        self.use_ml = use_ml
        self.rules = rules if rules is not None else get_categorization_rules(db, user_id)
        self.label_categorizer = LabelsBasedCategorizer(db, user_id, self.rules)
        self.keyword_categorizer = KeywordBasedCategorizer(db, user_id, self.rules)
        self.sender_categorizer = SenderBasedCategorizer(db, user_id, self.rules)
        if use_ml:
            self.ml_categorizer = MLBasedCategorizer(db, user_id, self.rules)
        self.category_priorities = {
            details["name"]: details["priority"] 
            for cat_id, details in self.rules["categories"].items()
        }
        self.email_logger = None

    @log_operation("combine_matches")
    def _combine_matches(self, matches: List[Tuple[str, float, str]]) -> List[Tuple[str, float, str]]:
        """Combine and deduplicate matches, keeping the highest confidence match for each category."""
        # Group matches by category
        category_matches = defaultdict(list)
        for category, confidence, match_type in matches:
            category_matches[category].append((confidence, match_type))
            self.email_logger.debug(
                "Processing match",
                details={
                    "category": category,
                    "confidence": confidence,
                    "match_type": match_type
                }
            )
        
        # For each category, keep the match with highest confidence
        combined = []
        for category, cat_matches in category_matches.items():
            # Sort by confidence (higher is better)
            cat_matches.sort(key=lambda x: x[0], reverse=True)
            best_match = cat_matches[0]
            combined.append((category, best_match[0], best_match[1]))
            
            # Log category summary
            self.email_logger.debug(
                "Category matches summary",
                details={
                    "category": category,
                    "best_match_confidence": best_match[0],
                    "best_match_type": best_match[1],
                    "priority": self.category_priorities.get(category, 50),
                    "matches": summarize_matches(cat_matches)
                }
            )
        
        # Sort by confidence and then by category priority
        combined.sort(
            key=lambda x: (x[1], -self.category_priorities.get(x[0], 50)),
            reverse=True
        )
        
        if combined:
            self.email_logger.info(
                "Combined matches",
                details={"best_match": combined[0]},
                metrics={"num_categories": len(combined)}
            )
        
        return combined

    @log_operation("categorize_email")
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """Categorize an email using all available categorizers."""
        # Initialize logger with email correlation ID
        self.email_logger = EmailLogger(
            correlation_id=email_data.get('gmail_id', 'unknown'),
            component="EMAIL_CAT_COMPOSITE",
            user_id=self.user_id
        )
        
        # Share the email_logger with component categorizers
        self.sender_categorizer.email_logger = self.email_logger
        self.keyword_categorizer.email_logger = self.email_logger
        self.label_categorizer.email_logger = self.email_logger
        if self.use_ml:
            self.ml_categorizer.email_logger = self.email_logger
        
        # Log start of categorization
        self.email_logger.info(
            "Starting categorization",
            details={
                "subject": email_data.get('subject', '[No Subject]'),
                "from_email": sanitize_email(email_data.get('from_email', '[No Sender]'))
            }
        )
        
        all_matches = []
        
        # Get matches from sender rules
        try:
            self.email_logger.start_operation("sender_matching")
            sender_matches = self.sender_categorizer.get_sender_category_matches(
                email_data.get('from_email', '')
            )
            if sender_matches:
                all_matches.extend(sender_matches)
                self.email_logger.info(
                    "Sender matches found",
                    details={"matches": summarize_matches(sender_matches)}
                )
            self.email_logger.end_operation()
        except Exception as e:
            self.email_logger.error("Error in sender categorization", e)
        
        # Get matches from keyword rules
        try:
            self.email_logger.start_operation("keyword_matching")
            keyword_matches = self.keyword_categorizer.get_subject_category_matches(
                email_data.get('subject', '')
            )
            if keyword_matches:
                all_matches.extend(keyword_matches)
                self.email_logger.info(
                    "Keyword matches found",
                    details={"matches": summarize_matches(keyword_matches)}
                )
            self.email_logger.end_operation()
        except Exception as e:
            self.email_logger.error("Error in keyword categorization", e)
        
        # Get matches from ML classifier if available
        if self.use_ml:
            try:
                self.email_logger.start_operation("ml_classification")
                ml_matches = self.ml_categorizer.categorize(email_data)
                if ml_matches:
                    all_matches.extend([ml_matches])  # ML returns single tuple
                    self.email_logger.info(
                        "ML match found",
                        details={
                            "category": ml_matches[0],
                            "confidence": ml_matches[1],
                            "reason": ml_matches[2]
                        }
                    )
                self.email_logger.end_operation()
            except Exception as e:
                self.email_logger.error("Error in ML categorization", e)
        
        if not all_matches:
            self.email_logger.info(
                "No matches found, using default category",
                details={"default_category": "inbox"}
            )
            return ("inbox", 1.0, "default")
        
        # Combine and sort matches
        combined = self._combine_matches(all_matches)
        
        # Get final result
        if combined:
            final_category, final_confidence, final_reason = combined[0]
            self.email_logger.info(
                "Categorization complete",
                details={
                    "category": final_category,
                    "confidence": final_confidence,
                    "reason": final_reason
                },
                metrics={
                    "num_total_matches": len(all_matches),
                    "num_combined_matches": len(combined)
                }
            )
            return combined[0]
        
        self.email_logger.info(
            "No valid matches after combining, using default",
            details={"default_category": "inbox"}
        )
        return ("inbox", 1.0, "default")

def categorize_email(email_data: Dict[str, Any], db: Session, user_id: Optional[UUID] = None) -> str:
    """
    Helper function to categorize an email from standard email data dictionary.
    This function uses the composite categorizer with modular approach.
    
    Args:
        email_data: Dictionary containing email data
        db: Database session
        user_id: Optional user ID
        
    Returns:
        Category string
    """
    try:
        gmail_id = email_data.get('gmail_id', 'unknown')
        subject = email_data.get('subject', '[No Subject]')
        from_email = email_data.get('from_email', '[No Sender]')
        
        logger.info(f"[EMAIL_CAT] ========== CATEGORIZING EMAIL ==========")
        logger.info(f"[EMAIL_CAT] Email: ID={gmail_id} | From={from_email} | Subject='{subject}'")
        
        # Create a composite categorizer that uses all methods
        categorizer = CompositeCategorizer(db, user_id, use_ml=True)
        
        # Categorize the email
        category, confidence, reason = categorizer.categorize(email_data)
        
        logger.info(f"[EMAIL_CAT] RESULT: Email categorized as '{category}' with confidence {confidence:.2f}")
        logger.info(f"[EMAIL_CAT] REASON: {reason}")
        logger.info(f"[EMAIL_CAT] ========== CATEGORIZATION COMPLETE ==========")
        
        # Record trash events for ML training if applicable
        if category == 'trash' and 'id' in email_data and user_id and confidence > 0.6:
            categorization_source = 'rules'
            if 'ml_prediction' in reason:
                categorization_source = 'ml'
            
            logger.info(f"[EMAIL_CAT] Recording trash event for ML training: source={categorization_source}, confidence={confidence:.2f}")
            record_trash_event(
                db=db,
                email_id=email_data['id'],
                user_id=user_id,
                event_type='moved_to_trash',
                email_data=email_data,
                is_auto_categorized=True,
                categorization_source=categorization_source,
                confidence_score=confidence
            )
        
        return category
    except Exception as e:
        logger.error(f"[EMAIL_CAT] Error categorizing email: {str(e)}", exc_info=True)
        # Fallback to primary if an error occurs
        return "primary"

# Ensure backward compatibility
def determine_category(
    gmail_labels: List[str], 
    subject: str,
    from_email: str,
    db: Session,
    user_id: Optional[UUID] = None
) -> str:
    """
    Determine email category based on Gmail labels, subject keywords, and sender.
    
    Maintained for backward compatibility with existing code.
    
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
        logger.info(f"[LEGACY CATEGORIZER] Processing email: From={from_email} | Subject='{subject}'")
        logger.info(f"[LEGACY CATEGORIZER] Gmail labels: {', '.join(gmail_labels) if gmail_labels else 'None'}")
        
        # Create email_data dict for the categorizer
        email_data = {
            'labels': gmail_labels,
            'subject': subject,
            'from_email': from_email,
            'gmail_id': 'unknown'  # Not available in this context
        }
        
        # Use the new modular categorizer
        categorizer = CompositeCategorizer(db, user_id, use_ml=False)  # Skip ML for this legacy function
        category, confidence, reason = categorizer.categorize(email_data)
        
        logger.info(f"[LEGACY CATEGORIZER] Email categorized as '{category}' with confidence {confidence:.2f}: {reason}")
        return category
    except Exception as e:
        logger.error(f"[LEGACY CATEGORIZER] Error determining category: {str(e)}", exc_info=True)
        # Fallback to primary if an error occurs
        return "primary"

# Utility function for email sync service
def categorize_email_from_labels(labels: List[str], db: Session, user_id: Optional[UUID] = None) -> str:
    """
    Categorize an email based only on Gmail labels
    
    Utility function for email sync service
    
    Args:
        labels: List of Gmail labels
        db: Database session
        user_id: Optional user ID
        
    Returns:
        Category string
    """
    try:
        logger.info(f"[LABELS-ONLY CATEGORIZER] Processing email with labels: {', '.join(labels) if labels else 'None'}")
        
        # Create minimal email_data with just labels
        email_data = {
            'labels': labels,
            'subject': '',
            'from_email': '',
            'gmail_id': 'unknown_from_labels'
        }
        
        # Use only label-based categorization
        categorizer = LabelsBasedCategorizer(db, user_id)
        category, confidence, reason = categorizer.categorize(email_data)
        
        # If no category determined from labels, use default
        if category == 'unknown':
            sorted_categories = sorted(
                [(cat_id, details) for cat_id, details in get_categorization_rules(db, user_id)["categories"].items()],
                key=lambda x: x[1]["priority"]
            )
            
            # Return primary if it exists, otherwise highest priority category
            for cat_id, details in sorted_categories:
                if details["name"].lower() == "primary":
                    logger.info(f"[LABELS-ONLY CATEGORIZER] No category from labels, defaulting to 'primary'")
                    return details["name"]
            
            # If no primary category, return the highest priority one
            default_category = sorted_categories[0][1]["name"] if sorted_categories else "primary"
            logger.info(f"[LABELS-ONLY CATEGORIZER] No category from labels, no 'primary' category found, defaulting to highest priority: '{default_category}'")
            return default_category
        
        logger.info(f"[LABELS-ONLY CATEGORIZER] Email categorized as '{category}' with confidence {confidence:.2f}: {reason}")
        return category
    except Exception as e:
        logger.error(f"[LABELS-ONLY CATEGORIZER] Error categorizing from labels: {str(e)}", exc_info=True)
        return "primary"