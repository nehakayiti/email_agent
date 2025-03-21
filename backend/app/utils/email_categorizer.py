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
from functools import lru_cache
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule
import json

# Import the Naive Bayes classifier
from .naive_bayes_classifier import classify_email as nbc_classify_email, record_trash_event

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
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        """Initialize with DB session and optional user ID"""
        self.db = db
        self.user_id = user_id
        self.rules = get_categorization_rules(db, user_id)
        
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
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        """Initialize with DB session and optional user ID"""
        self.db = db
        self.user_id = user_id
        self.rules = get_categorization_rules(db, user_id)
        
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
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        """Initialize with DB session and optional user ID"""
        self.db = db
        self.user_id = user_id
        self.rules = get_categorization_rules(db, user_id)
        
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
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize email based on sender email domain
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        from_email = email_data.get('from_email', '[No Sender]')
        
        logger.info(f"[EMAIL_CAT_SENDER] Checking sender: {from_email}")
        
        if not from_email or '@' not in from_email:
            logger.info(f"[EMAIL_CAT_SENDER] Invalid or missing sender email")
            return ('unknown', 0.0, 'invalid_sender')
        
        matches = self.get_sender_category_matches(from_email)
        if not matches:
            logger.info(f"[EMAIL_CAT_SENDER] No sender matches found")
            return ('unknown', 0.0, 'no_sender_matches')
        
        # Log all matches found
        for match in matches:
            logger.info(f"[EMAIL_CAT_SENDER] Match: '{match[0]}' ({match[2]})")
            
        # Sort by priority (lower number = higher priority)
        matches.sort(key=lambda x: x[1])
        best_match = matches[0]
        category_name = best_match[0]
        match_type = best_match[2]
        
        # Calculate confidence based on match type
        confidence = 0.0
        if "sender_domain_exact" in match_type:
            confidence = 0.9
            logger.info(f"[EMAIL_CAT_SENDER] Exact domain match (0.9 confidence)")
        elif "sender_domain" in match_type:
            confidence = 0.8
            logger.info(f"[EMAIL_CAT_SENDER] Domain match (0.8 confidence)")
        elif "sender_substring" in match_type:
            confidence = 0.6
            logger.info(f"[EMAIL_CAT_SENDER] Substring match (0.6 confidence)")
        
        logger.info(f"[EMAIL_CAT_SENDER] Best match: '{category_name}' with confidence {confidence} ({match_type})")
        return (category_name, confidence, match_type)
    
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

class MLBasedCategorizer:
    """Categorizer that uses ML model to determine if an email is trash"""
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        """Initialize with DB session and optional user ID"""
        self.db = db
        self.user_id = user_id
        # Get category rules for better feature extraction
        self.rules = get_categorization_rules(db, user_id)
    
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
    
    def __init__(self, db: Session, user_id: Optional[UUID] = None, use_ml: bool = True):
        """
        Initialize with DB session and optional user ID
        
        Args:
            db: Database session
            user_id: Optional user ID
            use_ml: Whether to use ML-based categorization
        """
        self.db = db
        self.user_id = user_id
        self.use_ml = use_ml
        
        # Create component categorizers
        self.label_categorizer = LabelsBasedCategorizer(db, user_id)
        self.keyword_categorizer = KeywordBasedCategorizer(db, user_id)
        self.sender_categorizer = SenderBasedCategorizer(db, user_id)
        
        if use_ml:
            self.ml_categorizer = MLBasedCategorizer(db, user_id)
        
        # Get category priorities from the database
        self.rules = get_categorization_rules(db, user_id)
        self.category_priorities = {
            details["name"]: details["priority"] 
            for cat_id, details in self.rules["categories"].items()
        }
    
    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize email using multiple approaches and resolve based on confidence and priority
        
        Args:
            email_data: Email data including subject, labels, etc.
            
        Returns:
            Tuple of (category_name, confidence_score, reason)
        """
        subject = email_data.get('subject', '[No Subject]')
        from_email = email_data.get('from_email', '[No Sender]')
        gmail_id = email_data.get('gmail_id', '[No ID]')
        
        logger.info(f"[EMAIL_CAT_COMPOSITE] Starting categorization process")
        
        # Initialize empty list for candidate categories
        candidate_categories = []
        
        # Apply label-based categorization first (highest precedence)
        logger.info(f"[EMAIL_CAT_COMPOSITE] Checking Gmail labels...")
        label_category, label_confidence, label_reason = self.label_categorizer.categorize(email_data)
        if label_category != 'unknown' and label_confidence > 0:
            # Prepare label-based category tuple: (name, confidence, reason, priority adjustment)
            # Lower priority number = higher priority
            priority_adjustment = -10  # Highest precedence
            candidate_categories.append((label_category, label_confidence, label_reason, priority_adjustment))
            logger.info(f"[EMAIL_CAT_COMPOSITE] Labels match: '{label_category}' with confidence {label_confidence:.2f} ({label_reason})")
        else:
            logger.info(f"[EMAIL_CAT_COMPOSITE] No matching Gmail labels found")
        
        # Apply keyword-based categorization
        logger.info(f"[EMAIL_CAT_COMPOSITE] Checking subject keywords...")
        keyword_category, keyword_confidence, keyword_reason = self.keyword_categorizer.categorize(email_data)
        if keyword_category != 'unknown' and keyword_confidence > 0:
            # Prepare keyword-based category tuple
            priority_adjustment = -5
            candidate_categories.append((keyword_category, keyword_confidence, keyword_reason, priority_adjustment))
            logger.info(f"[EMAIL_CAT_COMPOSITE] Subject keywords match: '{keyword_category}' with confidence {keyword_confidence:.2f} ({keyword_reason})")
        else:
            logger.info(f"[EMAIL_CAT_COMPOSITE] No matching subject keywords found")
        
        # Apply sender-based categorization
        logger.info(f"[EMAIL_CAT_COMPOSITE] Checking sender patterns...")
        sender_category, sender_confidence, sender_reason = self.sender_categorizer.categorize(email_data)
        if sender_category != 'unknown' and sender_confidence > 0:
            # Prepare sender-based category tuple
            priority_adjustment = -3
            candidate_categories.append((sender_category, sender_confidence, sender_reason, priority_adjustment))
            logger.info(f"[EMAIL_CAT_COMPOSITE] Sender match: '{sender_category}' with confidence {sender_confidence:.2f} ({sender_reason})")
        else:
            logger.info(f"[EMAIL_CAT_COMPOSITE] No matching sender patterns found")
        
        # Apply ML-based categorization for trash detection (if enabled)
        if self.use_ml:
            logger.info(f"[EMAIL_CAT_COMPOSITE] Checking ML classification...")
            ml_category, ml_confidence, ml_reason = self.ml_categorizer.categorize(email_data)
            if ml_category == 'trash' and ml_confidence >= ML_CONFIDENCE_THRESHOLD:
                # ML trash detection with high confidence overrides other rules
                # This could be made configurable if needed
                logger.info(f"[EMAIL_CAT_COMPOSITE] ML classified as trash with high confidence ({ml_confidence:.2f}): {ml_reason}")
                return (ml_category, ml_confidence, ml_reason)
            elif ml_category == 'trash' and ml_confidence >= 0.6:
                # Add as a candidate for borderline cases
                priority_adjustment = 0  # Standard priority for ML
                candidate_categories.append((ml_category, ml_confidence, ml_reason, priority_adjustment))
                logger.info(f"[EMAIL_CAT_COMPOSITE] ML trash match: confidence {ml_confidence:.2f} ({ml_reason})")
            else:
                logger.info(f"[EMAIL_CAT_COMPOSITE] ML did not classify as trash")
        
        # If no categories were determined, default to 'primary' or first category
        if not candidate_categories:
            sorted_categories = sorted(
                [(name, priority) for name, priority in self.category_priorities.items()],
                key=lambda x: x[1]
            )
            default_category = next((cat for cat in sorted_categories if cat[0] == 'primary'), sorted_categories[0])
            logger.info(f"[EMAIL_CAT_COMPOSITE] No matches found, defaulting to '{default_category[0]}'")
            return (default_category[0], 0.5, 'default_category')
        
        # Select the best category based on:
        # 1. Base category priority (from database)
        # 2. Method-specific priority adjustment
        # 3. Confidence score as a tiebreaker
        selected_categories = []
        
        logger.info(f"[EMAIL_CAT_COMPOSITE] Found {len(candidate_categories)} potential categories, resolving...")
        
        for cat_name, confidence, reason, adjustment in candidate_categories:
            # Get the base priority for this category (lower = higher priority)
            base_priority = self.category_priorities.get(cat_name, 50)
            # Apply the method-specific adjustment
            adjusted_priority = base_priority + adjustment
            # Add to selection list
            selected_categories.append((cat_name, confidence, reason, adjusted_priority))
            logger.info(f"[EMAIL_CAT_COMPOSITE] Candidate: '{cat_name}' (priority={adjusted_priority}, confidence={confidence:.2f})")
        
        # Sort by adjusted priority (lower = higher priority)
        # and then by confidence (higher = better) for ties
        selected_categories.sort(key=lambda x: (x[3], -x[1]))
        
        # Return the best match
        best_match = selected_categories[0]
        logger.info(f"[EMAIL_CAT_COMPOSITE] Selected: '{best_match[0]}' with confidence {best_match[1]:.2f} ({best_match[2]})")
        return (best_match[0], best_match[1], best_match[2])

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