"""
Concrete Scoring Strategy Implementations

This module contains the actual scoring algorithms that implement the ScoringStrategy interface.
Each strategy can have different approaches to calculating email attention scores.
"""

import logging
import re
from datetime import datetime
from typing import List, Set
from app.models.email import Email
from app.scoring.config import ScoringConfig
from app.scoring.interfaces import ScoringStrategy


class EnhancedScoringStrategy:
    """
    Advanced email attention scoring strategy with multiple factors.
    
    This strategy implements our sophisticated scoring algorithm that considers:
    - Category-based base scoring
    - Temporal decay curves
    - Engagement signals
    - Sender authority
    - Content urgency indicators
    - Contextual relevance
    """
    
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Precompiled regex patterns for performance
        self._urgent_patterns = [
            re.compile(r'\b(urgent|asap|deadline|expires?|final\s+notice)\b', re.IGNORECASE),
            re.compile(r'\b(action\s+required|time\s+sensitive|immediate)\b', re.IGNORECASE),
            re.compile(r'\b(expires?\s+(today|tomorrow|soon))\b', re.IGNORECASE)
        ]
        
        # Sender authority domain sets
        self._personal_domains = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 
            'icloud.com', 'protonmail.com', 'aol.com'
        }
        
        self._authority_domains = {
            'github.com', 'stripe.com', 'paypal.com', 'apple.com',
            'google.com', 'microsoft.com', 'amazon.com', 'adobe.com',
            'salesforce.com', 'slack.com', 'zoom.us', 'dropbox.com'
        }
        
        self._marketing_indicators = {
            'noreply', 'no-reply', 'donotreply', 'marketing', 'newsletter',
            'promotions', 'offers', 'deals', 'sales', 'support+',
            'notifications', 'alerts', 'updates'
        }
    
    def calculate_base_score(self, email: Email) -> float:
        """
        Calculate base attention score based on static email properties.
        
        This method is deterministic and cacheable - given the same email,
        it will always return the same base score.
        """
        score = 0.0
        email_id = getattr(email, 'gmail_id', 'unknown')
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.debug(f"[SCORE_BASE] Starting base calculation for {email_id}")
        
        # 1. CATEGORY-BASED SCORING (0-40 points)
        category_score = self.config.get_base_score(email.category or 'primary')
        score += category_score
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.debug(f"[SCORE_BASE] Category '{email.category}' score: +{category_score:.1f} = {score:.1f}")
        
        # 2. ENGAGEMENT SIGNALS (0-20 points total)
        engagement_score = self._calculate_engagement_score(email)
        score += engagement_score
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.debug(f"[SCORE_BASE] Engagement score: +{engagement_score:.1f} = {score:.1f}")
        
        # 3. SENDER AUTHORITY (0-10 points)
        sender_score = self._calculate_sender_authority(email)
        score += sender_score
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.debug(f"[SCORE_BASE] Sender authority: +{sender_score:.1f} = {score:.1f}")
        
        # 4. CONTENT URGENCY (0-5 points) 
        urgency_score = self._calculate_content_urgency(email)
        score += urgency_score
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.debug(f"[SCORE_BASE] Content urgency: +{urgency_score:.1f} = {score:.1f}")
            self.logger.info(f"[SCORE_BASE] Final base score for {email_id}: {score:.1f}")
        
        return score
    
    def calculate_temporal_multiplier(self, email: Email, age_hours: float) -> float:
        """
        Calculate how email relevance changes over time based on category.
        
        Uses mathematical decay functions for fast, consistent calculations.
        """
        category = (email.category or 'primary').lower()
        decay_function = self.config.get_temporal_decay_function(category)
        multiplier = decay_function(age_hours)
        
        if self.config.LOG_SCORE_CALCULATIONS:
            email_id = getattr(email, 'gmail_id', 'unknown')
            self.logger.debug(
                f"[SCORE_TEMPORAL] {email_id} ({category}, {age_hours:.1f}h): "
                f"multiplier = {multiplier:.3f}"
            )
        
        return multiplier
    
    def calculate_context_boost(self, email: Email, current_time: datetime) -> float:
        """
        Calculate contextual relevance boost based on current situation.
        """
        boost = 0.0
        current_hour = current_time.hour
        day_of_week = current_time.weekday()  # 0=Monday, 6=Sunday
        is_business_hours = 9 <= current_hour <= 17 and day_of_week < 5
        is_weekend = day_of_week >= 5
        
        category = (email.category or 'primary').lower()
        
        # Time-of-day adjustments
        if is_business_hours:
            if category == 'important':
                boost += self.config.BUSINESS_HOURS_IMPORTANT_BOOST
        elif current_hour >= 18 or current_hour <= 7:  # Evening/night
            if category in ['newsletters', 'social']:
                boost += self.config.EVENING_NEWSLETTER_BOOST
        
        # Weekend adjustments
        if is_weekend:
            if category in ['social', 'newsletters']:
                boost += self.config.WEEKEND_PERSONAL_BOOST
        
        # Deadline urgency boost (time-sensitive)
        if self._has_deadline_urgency(email, current_time):
            boost += self.config.DEADLINE_URGENCY_BOOST
        
        if self.config.LOG_SCORE_CALCULATIONS and boost > 0:
            email_id = getattr(email, 'gmail_id', 'unknown')
            self.logger.debug(f"[SCORE_CONTEXT] {email_id}: context boost = +{boost:.1f}")
        
        return boost
    
    def _calculate_engagement_score(self, email: Email) -> float:
        """Calculate score based on user engagement signals."""
        score = 0.0
        
        # Unread emails need attention
        if not email.is_read:
            score += self.config.UNREAD_BONUS
        
        # Check Gmail labels for importance signals
        labels = email.labels or []
        if 'IMPORTANT' in labels:
            score += self.config.IMPORTANT_LABEL_BONUS
        if 'STARRED' in labels:
            score += self.config.STARRED_BONUS
        
        return score
    
    def _calculate_sender_authority(self, email: Email) -> float:
        """Calculate score adjustment based on sender authority."""
        if not email.from_email:
            return 0.0
        
        from_email = email.from_email.lower()
        domain = from_email.split('@')[-1] if '@' in from_email else ''
        
        # Authority domain boost
        if domain in self._authority_domains:
            return self.config.AUTHORITY_DOMAIN_BOOST
        
        # Personal domain boost (but lower than authority)
        if domain in self._personal_domains:
            return self.config.PERSONAL_DOMAIN_BOOST
        
        # Marketing sender penalty
        if any(indicator in from_email for indicator in self._marketing_indicators):
            return self.config.MARKETING_SENDER_PENALTY
        
        return 0.0
    
    def _calculate_content_urgency(self, email: Email) -> float:
        """Calculate urgency score based on email content."""
        if not email.subject:
            return 0.0
        
        # Check for urgent keywords using precompiled patterns
        for pattern in self._urgent_patterns:
            if pattern.search(email.subject):
                return 5.0  # Fixed urgency boost
        
        return 0.0
    
    def _has_deadline_urgency(self, email: Email, current_time: datetime) -> bool:
        """Check if email has time-sensitive deadline urgency."""
        if not email.subject:
            return False
        
        subject_lower = email.subject.lower()
        
        # Look for deadline indicators
        deadline_indicators = [
            'expires today', 'deadline today', 'due today',
            'expires tomorrow', 'deadline tomorrow', 'due tomorrow',
            'final notice', 'last chance', 'expires soon'
        ]
        
        return any(indicator in subject_lower for indicator in deadline_indicators)


class SimpleScoringStrategy:
    """
    Simple scoring strategy for testing and fallback scenarios.
    
    This provides a basic scoring algorithm that can be used when the enhanced
    strategy is unavailable or for comparison testing.
    """
    
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_base_score(self, email: Email) -> float:
        """Simple base scoring using only basic factors."""
        score = 30.0  # Base score
        
        # Simple unread bonus
        if not email.is_read:
            score += 15.0
        
        # Simple importance bonus
        if email.labels and 'IMPORTANT' in email.labels:
            score += 20.0
        
        if self.config.LOG_SCORE_CALCULATIONS:
            email_id = getattr(email, 'gmail_id', 'unknown')
            self.logger.debug(f"[SCORE_SIMPLE] {email_id}: base score = {score:.1f}")
        
        return score
    
    def calculate_temporal_multiplier(self, email: Email, age_hours: float) -> float:
        """Simple linear decay over time."""
        # Linear decay: 100% at 0 hours, 10% at 168 hours (1 week)
        multiplier = max(0.1, 1.0 - (age_hours / 168))
        
        if self.config.LOG_SCORE_CALCULATIONS:
            email_id = getattr(email, 'gmail_id', 'unknown')
            self.logger.debug(f"[SCORE_SIMPLE] {email_id}: temporal multiplier = {multiplier:.3f}")
        
        return multiplier
    
    def calculate_context_boost(self, email: Email, current_time: datetime) -> float:
        """Minimal context awareness."""
        return 0.0  # No context boosts in simple strategy


class CategoryOptimizedScoringStrategy:
    """
    Scoring strategy optimized for specific email categories.
    
    This strategy applies category-specific scoring logic that can be fine-tuned
    for different types of emails (newsletters vs promotions vs important emails).
    """
    
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def calculate_base_score(self, email: Email) -> float:
        """Category-optimized base scoring."""
        category = (email.category or 'primary').lower()
        
        if category == 'newsletters':
            return self._score_newsletter(email)
        elif category == 'promotions':
            return self._score_promotion(email)
        elif category == 'important':
            return self._score_important(email)
        elif category == 'social':
            return self._score_social(email)
        else:
            return self._score_default(email)
    
    def calculate_temporal_multiplier(self, email: Email, age_hours: float) -> float:
        """Use the same temporal logic as enhanced strategy."""
        enhanced_strategy = EnhancedScoringStrategy(self.config)
        return enhanced_strategy.calculate_temporal_multiplier(email, age_hours)
    
    def calculate_context_boost(self, email: Email, current_time: datetime) -> float:
        """Category-specific context boosts."""
        category = (email.category or 'primary').lower()
        current_hour = current_time.hour
        
        if category == 'newsletters' and 19 <= current_hour <= 23:
            return 8.0  # Reading time boost
        elif category == 'important' and 9 <= current_hour <= 17:
            return 10.0  # Business hours boost
        elif category == 'social' and (current_hour <= 8 or current_hour >= 18):
            return 5.0  # Personal time boost
        
        return 0.0
    
    def _score_newsletter(self, email: Email) -> float:
        """Specialized scoring for newsletters."""
        score = 15.0  # Base newsletter score
        
        # Newsletter-specific factors
        if email.from_email:
            domain = email.from_email.split('@')[-1].lower()
            
            # Trusted newsletter domains
            trusted_domains = {
                'nytimes.com', 'wsj.com', 'economist.com', 'bloomberg.com',
                'techcrunch.com', 'wired.com', 'theverge.com', 'medium.com'
            }
            
            if domain in trusted_domains:
                score += 10.0
        
        # Check for newsletter indicators in subject
        if email.subject:
            subject_lower = email.subject.lower()
            if any(word in subject_lower for word in ['newsletter', 'digest', 'weekly', 'daily']):
                score += 5.0
        
        return score
    
    def _score_promotion(self, email: Email) -> float:
        """Specialized scoring for promotional emails."""
        score = 8.0  # Base promotion score
        
        # Promotion-specific penalties and boosts
        if email.subject:
            subject_lower = email.subject.lower()
            
            # High-value promotion indicators
            if any(word in subject_lower for word in ['limited time', 'expires today', 'flash sale']):
                score += 12.0
            
            # Low-value promotion indicators
            elif any(word in subject_lower for word in ['newsletter', 'unsubscribe', 'marketing']):
                score -= 5.0
        
        return max(0.0, score)
    
    def _score_important(self, email: Email) -> float:
        """Specialized scoring for important emails."""
        score = 35.0  # High base score for important emails
        
        # Additional important email factors
        if not email.is_read:
            score += 15.0
        
        if email.labels and 'STARRED' in email.labels:
            score += 10.0
        
        return score
    
    def _score_social(self, email: Email) -> float:
        """Specialized scoring for social emails."""
        score = 12.0  # Base social score
        
        # Social-specific factors
        if not email.is_read:
            score += 8.0
        
        # Check for high-engagement social content
        if email.subject:
            subject_lower = email.subject.lower()
            if any(word in subject_lower for word in ['mentioned', 'tagged', 'invited', 'birthday']):
                score += 15.0
        
        return score
    
    def _score_default(self, email: Email) -> float:
        """Default scoring for uncategorized emails."""
        score = 20.0  # Medium base score
        
        if not email.is_read:
            score += 10.0
        
        if email.labels and 'IMPORTANT' in email.labels:
            score += 15.0
        
        return score