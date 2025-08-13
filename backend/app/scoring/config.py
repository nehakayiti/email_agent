"""
Scoring Configuration Module

Centralized configuration for the email attention scoring system.
Provides environment-specific configurations with sensible defaults.
"""

from dataclasses import dataclass, field
from typing import Dict, Callable
from enum import Enum
import os


class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class ScoringConfig:
    """
    Base configuration for email attention scoring.
    All scoring parameters are centralized here for easy tuning.
    """
    
    # Base scoring by category (0-50 points)
    CATEGORY_BASE_SCORES: Dict[str, float] = field(default_factory=lambda: {
        'important': 35.0,
        'newsletters': 15.0,
        'promotions': 8.0,
        'social': 12.0,
        'archive': 5.0,
        'trash': 0.0,
        'primary': 20.0,  # Default fallback
    })
    
    # Engagement signal bonuses (0-20 points total)
    UNREAD_BONUS: float = 8.0
    IMPORTANT_LABEL_BONUS: float = 12.0
    STARRED_BONUS: float = 8.0
    
    # Context boost parameters (0-15 points total)
    BUSINESS_HOURS_IMPORTANT_BOOST: float = 5.0
    EVENING_NEWSLETTER_BOOST: float = 3.0
    WEEKEND_PERSONAL_BOOST: float = 4.0
    DEADLINE_URGENCY_BOOST: float = 12.0
    
    # Sender authority adjustments
    PERSONAL_DOMAIN_BOOST: float = 6.0
    AUTHORITY_DOMAIN_BOOST: float = 8.0
    MARKETING_SENDER_PENALTY: float = -5.0
    
    # Cache TTL settings (seconds)
    CACHE_TTL_MAP: Dict[str, int] = field(default_factory=lambda: {
        'promotions': 3600 * 6,    # 6 hours (fast decay)
        'newsletters': 3600 * 24,  # 24 hours (medium decay)
        'important': 3600 * 24,    # 24 hours (slow decay)
        'social': 3600 * 12,       # 12 hours (medium-fast decay)
        'archive': 3600 * 168,     # 1 week (very slow decay)
        'trash': 3600 * 24,        # 24 hours (no decay needed but cache anyway)
        'default': 3600 * 24       # 24 hours default
    })
    
    # Temporal decay functions - mathematical formulas for performance
    TEMPORAL_DECAY_FUNCTIONS: Dict[str, Callable[[float], float]] = field(default_factory=lambda: {
        'promotions': lambda h: max(0.1, 1.0 * (0.8 ** (h / 12))),      # Aggressive decay: 20% every 12h
        'newsletters': lambda h: max(0.2, 1.0 * (0.9 ** (h / 24))),     # Medium decay: 10% per day
        'important': lambda h: max(0.5, 1.0 * (0.98 ** (h / 24))),      # Slow decay: 2% per day, floor 50%
        'social': lambda h: max(0.3, 1.0 * (0.85 ** (h / 18))),         # Medium-fast decay: 15% every 18h
        'archive': lambda h: max(0.2, 1.0 * (0.95 ** (h / 168))),       # Very slow: 5% per week
        'trash': lambda h: 0.1,                                          # Constant low relevance
        'default': lambda h: max(0.3, 1.0 * (0.95 ** (h / 24)))         # Standard: 5% per day
    })
    
    # Logging configuration
    LOG_SCORE_CALCULATIONS: bool = True
    LOG_CACHE_OPERATIONS: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    
    # Performance tuning
    BATCH_SIZE_SCORE_UPDATES: int = 1000
    MAX_CACHE_ENTRIES: int = 100000
    SCORE_CALCULATION_TIMEOUT_MS: int = 100
    
    def get_cache_ttl(self, category: str) -> int:
        """Get cache TTL for a specific email category."""
        return self.CACHE_TTL_MAP.get(category.lower(), self.CACHE_TTL_MAP['default'])
    
    def get_temporal_decay_function(self, category: str) -> Callable[[float], float]:
        """Get temporal decay function for a specific email category."""
        return self.TEMPORAL_DECAY_FUNCTIONS.get(category.lower(), self.TEMPORAL_DECAY_FUNCTIONS['default'])
    
    def get_base_score(self, category: str) -> float:
        """Get base score for a specific email category."""
        return self.CATEGORY_BASE_SCORES.get(category.lower(), self.CATEGORY_BASE_SCORES['primary'])


@dataclass 
class DevelopmentScoringConfig(ScoringConfig):
    """
    Development configuration - optimized for testing and debugging.
    """
    
    # Shorter cache times for easier testing
    CACHE_TTL_MAP: Dict[str, int] = field(default_factory=lambda: {
        'promotions': 60,      # 1 minute
        'newsletters': 300,    # 5 minutes
        'important': 300,      # 5 minutes
        'social': 180,         # 3 minutes
        'default': 300         # 5 minutes default
    })
    
    # More verbose logging
    LOG_SCORE_CALCULATIONS: bool = True
    LOG_CACHE_OPERATIONS: bool = True
    LOG_PERFORMANCE_METRICS: bool = True
    
    # Smaller batch sizes for testing
    BATCH_SIZE_SCORE_UPDATES: int = 10
    MAX_CACHE_ENTRIES: int = 1000


@dataclass
class TestingScoringConfig(ScoringConfig):
    """
    Testing configuration - optimized for unit tests.
    """
    
    # Minimal caching in tests for predictable behavior
    CACHE_TTL_MAP: Dict[str, int] = field(default_factory=lambda: {
        'promotions': 60,    # 1 minute for cache performance tests
        'newsletters': 60,   # 1 minute for cache performance tests 
        'important': 60,     # 1 minute for cache performance tests
        'social': 1,
        'default': 1
    })
    
    # Minimal logging in tests
    LOG_SCORE_CALCULATIONS: bool = False
    LOG_CACHE_OPERATIONS: bool = False
    LOG_PERFORMANCE_METRICS: bool = False
    
    # Small batch sizes
    BATCH_SIZE_SCORE_UPDATES: int = 5
    MAX_CACHE_ENTRIES: int = 100


@dataclass
class ProductionScoringConfig(ScoringConfig):
    """
    Production configuration - optimized for performance and scale.
    """
    
    # Longer cache times for better performance
    CACHE_TTL_MAP: Dict[str, int] = field(default_factory=lambda: {
        'promotions': 3600 * 8,    # 8 hours
        'newsletters': 3600 * 48,  # 48 hours
        'important': 3600 * 48,    # 48 hours
        'social': 3600 * 24,       # 24 hours
        'archive': 3600 * 336,     # 2 weeks
        'default': 3600 * 48       # 48 hours default
    })
    
    # Reduced logging for performance
    LOG_SCORE_CALCULATIONS: bool = False
    LOG_CACHE_OPERATIONS: bool = False
    LOG_PERFORMANCE_METRICS: bool = True  # Keep for monitoring
    
    # Larger batch sizes for efficiency
    BATCH_SIZE_SCORE_UPDATES: int = 5000
    MAX_CACHE_ENTRIES: int = 1000000


def get_config(environment: str = None) -> ScoringConfig:
    """
    Factory function to get the appropriate configuration for the current environment.
    
    Args:
        environment: Environment name (development/testing/production)
                    If None, reads from EMAIL_AGENT_ENV environment variable
    
    Returns:
        Appropriate ScoringConfig instance for the environment
    """
    if environment is None:
        environment = os.getenv('EMAIL_AGENT_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentScoringConfig,
        'testing': TestingScoringConfig,
        'production': ProductionScoringConfig
    }
    
    config_class = config_map.get(environment, DevelopmentScoringConfig)
    return config_class()


# Convenience function for getting current config
def current_config() -> ScoringConfig:
    """Get the configuration for the current environment."""
    return get_config()