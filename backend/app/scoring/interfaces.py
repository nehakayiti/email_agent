"""
Scoring System Interfaces

Defines the contracts for all scoring system components.
This enables dependency injection and easy testing/swapping of implementations.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, Dict, Any, List
from datetime import datetime
from app.models.email import Email


class ScoringStrategy(Protocol):
    """
    Interface for email scoring algorithms.
    
    This protocol defines the contract that all scoring strategies must implement.
    It separates the base scoring logic from temporal decay calculations for modularity.
    """
    
    def calculate_base_score(self, email: Email) -> float:
        """
        Calculate the base attention score for an email (static component).
        
        This score should be based on factors that don't change over time:
        - Email category
        - Sender authority
        - Content indicators
        - User engagement signals
        
        Args:
            email: Email model instance
            
        Returns:
            Base score (typically 0-50 range)
        """
        ...
    
    def calculate_temporal_multiplier(self, email: Email, age_hours: float) -> float:
        """
        Calculate how the email's relevance changes over time.
        
        This multiplier is applied to the base score to account for email aging.
        Different email types should age differently (e.g., promotions decay fast,
        important emails decay slowly).
        
        Args:
            email: Email model instance
            age_hours: Age of the email in hours
            
        Returns:
            Temporal multiplier (typically 0.1-1.0 range)
        """
        ...
    
    def calculate_context_boost(self, email: Email, current_time: datetime) -> float:
        """
        Calculate contextual relevance boost based on current situation.
        
        This accounts for factors like:
        - Time of day (business hours vs evening)
        - Day of week (weekday vs weekend)
        - Urgency indicators in content
        - Upcoming deadlines
        
        Args:
            email: Email model instance
            current_time: Current timestamp
            
        Returns:
            Context boost points (typically 0-15 range)
        """
        ...


class CacheProvider(Protocol):
    """
    Interface for caching email scores.
    
    This allows swapping between different caching backends (Redis, in-memory, etc.)
    while maintaining the same interface throughout the scoring system.
    """
    
    def get(self, key: str) -> Optional[float]:
        """
        Retrieve a cached score.
        
        Args:
            key: Cache key (typically email ID)
            
        Returns:
            Cached score if found and not expired, None otherwise
        """
        ...
    
    def set(self, key: str, value: float, ttl: int) -> None:
        """
        Store a score in cache with TTL.
        
        Args:
            key: Cache key (typically email ID)
            value: Score to cache
            ttl: Time-to-live in seconds
        """
        ...
    
    def delete(self, key: str) -> None:
        """
        Remove a cached score.
        
        Args:
            key: Cache key to remove
        """
        ...
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "email:*")
            
        Returns:
            Number of entries cleared
        """
        ...


class ScoreUpdater(Protocol):
    """
    Interface for background score updating strategies.
    
    This handles the logic of when and how to update email scores in batches,
    allowing for different update strategies (time-based, event-based, etc.).
    """
    
    def should_update(self, email: Email) -> bool:
        """
        Determine if an email's score should be updated.
        
        Args:
            email: Email to check
            
        Returns:
            True if score needs updating, False otherwise
        """
        ...
    
    def get_update_priority(self, email: Email) -> int:
        """
        Get the priority level for updating this email's score.
        
        Args:
            email: Email to prioritize
            
        Returns:
            Priority level (higher = more urgent)
        """
        ...
    
    def update_scores_batch(self, emails: List[Email]) -> Dict[str, Any]:
        """
        Update scores for a batch of emails.
        
        Args:
            emails: List of emails to update
            
        Returns:
            Update result metrics
        """
        ...


class ScoreDebugger(Protocol):
    """
    Interface for score debugging and analysis tools.
    
    This provides methods to analyze and debug the scoring system,
    helping developers understand why emails received certain scores.
    """
    
    def debug_score_calculation(self, email: Email) -> Dict[str, Any]:
        """
        Get detailed breakdown of how a score was calculated.
        
        Args:
            email: Email to analyze
            
        Returns:
            Detailed scoring breakdown
        """
        ...
    
    def analyze_score_distribution(self, emails: List[Email]) -> Dict[str, Any]:
        """
        Analyze score distribution across multiple emails.
        
        Args:
            emails: List of emails to analyze
            
        Returns:
            Statistical analysis of scores
        """
        ...
    
    def compare_scoring_strategies(
        self, 
        email: Email, 
        strategies: List[ScoringStrategy]
    ) -> Dict[str, Any]:
        """
        Compare how different scoring strategies would score the same email.
        
        Args:
            email: Email to score
            strategies: List of strategies to compare
            
        Returns:
            Comparison results
        """
        ...


class PerformanceMonitor(Protocol):
    """
    Interface for monitoring scoring system performance.
    
    This tracks metrics like calculation times, cache hit rates, and error rates
    to help optimize the scoring system in production.
    """
    
    def record_calculation_time(self, duration_ms: float, email_category: str) -> None:
        """Record how long a score calculation took."""
        ...
    
    def record_cache_hit(self, key: str) -> None:
        """Record a cache hit."""
        ...
    
    def record_cache_miss(self, key: str) -> None:
        """Record a cache miss."""
        ...
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        ...


# Abstract base classes for common functionality

class BaseScoreUpdater(ABC):
    """
    Abstract base class providing common score updater functionality.
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    @abstractmethod
    def should_update(self, email: Email) -> bool:
        pass
    
    def get_update_priority(self, email: Email) -> int:
        """Default priority based on email category."""
        priority_map = {
            'promotions': 10,  # High priority (fast decay)
            'social': 8,
            'newsletters': 5,
            'important': 3,
            'archive': 1,
            'trash': 0
        }
        return priority_map.get(email.category, 5)


class BaseCacheProvider(ABC):
    """
    Abstract base class providing common cache functionality.
    """
    
    def __init__(self, key_prefix: str = "email_score"):
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """Create a prefixed cache key."""
        return f"{self.key_prefix}:{key}"
    
    @abstractmethod
    def get(self, key: str) -> Optional[float]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: float, ttl: int) -> None:
        pass
    
    def delete(self, key: str) -> None:
        """Default implementation - can be overridden."""
        pass
    
    def clear_pattern(self, pattern: str) -> int:
        """Default implementation - can be overridden."""
        return 0