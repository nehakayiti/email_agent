"""
Email Scoring Engine

This is the main orchestrator that coordinates all scoring components.
It provides a clean, dependency-injected interface for calculating email attention scores.
"""

import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.email import Email
from app.scoring.config import ScoringConfig
from app.scoring.interfaces import ScoringStrategy, CacheProvider


class EmailScoringEngine:
    """
    Main email scoring engine that orchestrates all scoring components.
    
    This class follows the dependency injection pattern, making it easy to:
    - Test with mock components
    - Swap strategies and cache providers
    - Monitor and debug the scoring process
    """
    
    def __init__(
        self,
        scoring_strategy: ScoringStrategy,
        cache_provider: CacheProvider,
        config: ScoringConfig,
        performance_monitor: Optional[Any] = None
    ):
        self.scoring_strategy = scoring_strategy
        self.cache = cache_provider
        self.config = config
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Performance tracking
        self._calculation_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_calculation_time = 0.0
    
    def get_current_score(
        self, 
        email: Email, 
        current_time: Optional[datetime] = None,
        bypass_cache: bool = False
    ) -> float:
        """
        Get the current attention score for an email.
        
        This is the main entry point for scoring. It coordinates caching,
        calculation, and performance monitoring.
        
        Args:
            email: Email to score
            current_time: Current timestamp (defaults to now)
            bypass_cache: If True, force recalculation regardless of cache
            
        Returns:
            Current attention score (0-100)
        """
        start_time = time.time()
        current_time = current_time or datetime.now()
        email_id = str(email.id)
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.info(f"[SCORING_ENGINE] Starting score calculation for {email_id}")
        
        try:
            # 1. Try cache first (unless bypassed)
            if not bypass_cache:
                cached_score = self._get_cached_score(email_id, current_time)
                if cached_score is not None:
                    self._record_cache_hit(email_id)
                    if self.config.LOG_PERFORMANCE_METRICS:
                        cache_lookup_time = (time.time() - start_time) * 1000
                        self.logger.debug(f"[SCORING_ENGINE] Cache hit for {email_id}: {cached_score:.1f} ({cache_lookup_time:.1f}ms)")
                    return cached_score
            
            # 2. Cache miss - calculate fresh score
            self._record_cache_miss(email_id)
            fresh_score = self._calculate_fresh_score(email, current_time)
            
            # 3. Cache the result
            self._cache_score(email_id, email.category, fresh_score)
            
            # 4. Record performance metrics for actual calculations only
            calculation_time = (time.time() - start_time) * 1000
            self._record_calculation_time(calculation_time, email.category)
            
            if self.config.LOG_SCORE_CALCULATIONS:
                self.logger.info(f"[SCORING_ENGINE] Calculated fresh score for {email_id}: {fresh_score:.1f} ({calculation_time:.1f}ms)")
            
            return fresh_score
            
        except Exception as e:
            self.logger.error(f"[SCORING_ENGINE] Error calculating score for {email_id}: {e}", exc_info=True)
            # Return a safe default score
            return 50.0
    
    def get_scores_batch(
        self, 
        emails: List[Email], 
        current_time: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calculate scores for multiple emails efficiently.
        
        This method optimizes for batch operations by:
        - Checking cache for all emails first
        - Calculating missing scores in batch
        - Caching results efficiently
        
        Args:
            emails: List of emails to score
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Dictionary mapping email IDs to scores
        """
        current_time = current_time or datetime.now()
        start_time = time.time()
        
        if self.config.LOG_SCORE_CALCULATIONS:
            self.logger.info(f"[SCORING_ENGINE] Batch scoring {len(emails)} emails")
        
        results = {}
        emails_to_calculate = []
        
        # 1. Check cache for all emails
        for email in emails:
            email_id = str(email.id)
            cached_score = self._get_cached_score(email_id, current_time)
            
            if cached_score is not None:
                results[email_id] = cached_score
                self._record_cache_hit(email_id)
            else:
                emails_to_calculate.append(email)
                self._record_cache_miss(email_id)
        
        # 2. Calculate scores for cache misses
        for email in emails_to_calculate:
            email_id = str(email.id)
            try:
                score = self._calculate_fresh_score(email, current_time)
                results[email_id] = score
                
                # Cache the result
                self._cache_score(email_id, email.category, score)
                
            except Exception as e:
                self.logger.error(f"[SCORING_ENGINE] Error in batch calculation for {email_id}: {e}")
                results[email_id] = 50.0  # Safe default
        
        # 3. Log performance metrics
        total_time = (time.time() - start_time) * 1000
        cache_hit_rate = (len(emails) - len(emails_to_calculate)) / len(emails) * 100
        
        if self.config.LOG_PERFORMANCE_METRICS:
            self.logger.info(
                f"[SCORING_ENGINE] Batch complete: {len(emails)} emails, "
                f"{len(emails_to_calculate)} calculated, "
                f"{cache_hit_rate:.1f}% cache hit rate, "
                f"{total_time:.1f}ms total"
            )
        
        return results
    
    def invalidate_cache(self, email_ids: Optional[List[str]] = None, pattern: Optional[str] = None) -> int:
        """
        Invalidate cached scores.
        
        Args:
            email_ids: Specific email IDs to invalidate
            pattern: Pattern to match for bulk invalidation
            
        Returns:
            Number of entries invalidated
        """
        if email_ids:
            for email_id in email_ids:
                self.cache.delete(email_id)
            self.logger.info(f"[SCORING_ENGINE] Invalidated cache for {len(email_ids)} specific emails")
            return len(email_ids)
        
        elif pattern:
            cleared = self.cache.clear_pattern(pattern)
            self.logger.info(f"[SCORING_ENGINE] Invalidated {cleared} cache entries matching '{pattern}'")
            return cleared
        
        else:
            # Clear all our cache entries
            cleared = self.cache.clear_pattern("*")
            self.logger.info(f"[SCORING_ENGINE] Invalidated {cleared} cache entries (full clear)")
            return cleared
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the scoring engine.
        
        Returns:
            Dictionary with performance metrics
        """
        total_requests = self._cache_hits + self._cache_misses
        cache_hit_rate = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        avg_calculation_time = (self._total_calculation_time / self._calculation_count) if self._calculation_count > 0 else 0
        
        stats = {
            'total_score_requests': total_requests,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate_percent': round(cache_hit_rate, 2),
            'calculations_performed': self._calculation_count,
            'avg_calculation_time_ms': round(avg_calculation_time, 2),
            'total_calculation_time_ms': round(self._total_calculation_time, 2)
        }
        
        # Add cache provider stats if available
        try:
            cache_stats = self.cache.get_stats()
            stats['cache_provider_stats'] = cache_stats
        except:
            pass
        
        return stats
    
    def reset_performance_stats(self) -> None:
        """Reset all performance counters."""
        self._calculation_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_calculation_time = 0.0
        self.logger.info("[SCORING_ENGINE] Performance stats reset")
    
    def _calculate_fresh_score(self, email: Email, current_time: datetime) -> float:
        """
        Calculate a fresh score using the scoring strategy.
        
        This method breaks down the calculation into components for better
        debugging and monitoring.
        """
        calculation_start = time.time()
        
        # 1. Calculate base score (static component)
        base_score = self.scoring_strategy.calculate_base_score(email)
        
        # 2. Calculate temporal multiplier (dynamic component)
        if email.received_at:
            # Handle timezone-aware datetime comparison
            try:
                if email.received_at.tzinfo is not None and current_time.tzinfo is None:
                    # Email has timezone, current_time doesn't - make current_time timezone-aware (UTC)
                    from datetime import timezone
                    current_time = current_time.replace(tzinfo=timezone.utc)
                    age_hours = (current_time - email.received_at).total_seconds() / 3600
                elif email.received_at.tzinfo is None and current_time.tzinfo is not None:
                    # Current_time has timezone, email doesn't - make email timezone-aware (UTC)
                    from datetime import timezone
                    email_time = email.received_at.replace(tzinfo=timezone.utc)
                    age_hours = (current_time - email_time).total_seconds() / 3600
                else:
                    # Both have same timezone status (both aware or both naive)
                    age_hours = (current_time - email.received_at).total_seconds() / 3600
            except Exception as e:
                # If timezone handling fails, use a safe default
                self.logger.warning(f"[SCORING_ENGINE] Timezone handling failed for email {email.id}: {e}")
                age_hours = 24.0  # Default to 24 hours old
        else:
            age_hours = 0
            
        temporal_multiplier = self.scoring_strategy.calculate_temporal_multiplier(email, age_hours)
        
        # 3. Calculate context boost (situational component)
        context_boost = self.scoring_strategy.calculate_context_boost(email, current_time)
        
        # 4. Combine components
        raw_score = (base_score * temporal_multiplier) + context_boost
        final_score = max(0.0, min(100.0, raw_score))
        
        # 5. Log detailed breakdown if enabled
        if self.config.LOG_SCORE_CALCULATIONS:
            email_id = getattr(email, 'gmail_id', str(email.id))
            self.logger.debug(
                f"[SCORING_ENGINE] Score breakdown for {email_id}: "
                f"base={base_score:.1f} × temporal={temporal_multiplier:.3f} + context={context_boost:.1f} "
                f"= {raw_score:.1f} → {final_score:.1f}"
            )
        
        return final_score
    
    def _get_cached_score(self, email_id: str, current_time: datetime) -> Optional[float]:
        """
        Get score from cache with logging.
        
        This method is separated for easy mocking in tests and centralized
        cache interaction logging.
        """
        try:
            score = self.cache.get(email_id)
            if self.config.LOG_CACHE_OPERATIONS and score is not None:
                self.logger.debug(f"[SCORING_ENGINE] Cache hit: {email_id} → {score:.1f}")
            return score
        except Exception as e:
            self.logger.error(f"[SCORING_ENGINE] Cache get error for {email_id}: {e}")
            return None
    
    def _cache_score(self, email_id: str, category: str, score: float) -> None:
        """
        Cache score with appropriate TTL based on category.
        
        This method handles TTL calculation and error handling for caching.
        """
        try:
            ttl = self.config.get_cache_ttl(category or 'default')
            self.cache.set(email_id, score, ttl)
            
            if self.config.LOG_CACHE_OPERATIONS:
                self.logger.debug(f"[SCORING_ENGINE] Cached: {email_id} → {score:.1f} (TTL: {ttl}s)")
                
        except Exception as e:
            self.logger.error(f"[SCORING_ENGINE] Cache set error for {email_id}: {e}")
    
    def _record_cache_hit(self, email_id: str) -> None:
        """Record cache hit for performance tracking."""
        self._cache_hits += 1
        if self.performance_monitor:
            self.performance_monitor.record_cache_hit(email_id)
    
    def _record_cache_miss(self, email_id: str) -> None:
        """Record cache miss for performance tracking."""
        self._cache_misses += 1
        if self.performance_monitor:
            self.performance_monitor.record_cache_miss(email_id)
    
    def _record_calculation_time(self, duration_ms: float, category: str) -> None:
        """Record calculation time for performance tracking."""
        self._calculation_count += 1
        self._total_calculation_time += duration_ms
        
        if self.performance_monitor:
            self.performance_monitor.record_calculation_time(duration_ms, category or 'unknown')
        
        # Log slow calculations
        if duration_ms > self.config.SCORE_CALCULATION_TIMEOUT_MS:
            self.logger.warning(
                f"[SCORING_ENGINE] Slow calculation: {duration_ms:.1f}ms "
                f"(threshold: {self.config.SCORE_CALCULATION_TIMEOUT_MS}ms)"
            )


class ScoringEngineFactory:
    """
    Factory class for creating properly configured scoring engines.
    
    This factory handles the complex initialization of scoring engines with
    appropriate strategies, cache providers, and configuration based on
    the current environment.
    """
    
    @staticmethod
    def create_engine(
        config: ScoringConfig,
        strategy_type: str = "enhanced",
        cache_type: str = "memory",
        redis_client=None
    ) -> EmailScoringEngine:
        """
        Create a fully configured scoring engine.
        
        Args:
            config: Scoring configuration
            strategy_type: Type of scoring strategy ('enhanced', 'simple', 'category')
            cache_type: Type of cache provider ('memory', 'redis', 'null', 'multi_tier')
            redis_client: Redis client (required for Redis-based caching)
            
        Returns:
            Configured EmailScoringEngine instance
        """
        # Import here to avoid circular dependencies
        from app.scoring.strategies import (
            EnhancedScoringStrategy, 
            SimpleScoringStrategy, 
            CategoryOptimizedScoringStrategy
        )
        from app.scoring.cache_providers import create_cache_provider
        
        # Create scoring strategy
        strategy_map = {
            'enhanced': EnhancedScoringStrategy,
            'simple': SimpleScoringStrategy,
            'category': CategoryOptimizedScoringStrategy
        }
        
        if strategy_type not in strategy_map:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy = strategy_map[strategy_type](config)
        
        # Create cache provider
        cache_kwargs = {'key_prefix': 'email_score'}
        if cache_type in ['redis', 'multi_tier']:
            if redis_client is None:
                raise ValueError(f"Redis client required for cache type: {cache_type}")
            cache_kwargs['redis_client'] = redis_client
        
        cache_provider = create_cache_provider(cache_type, **cache_kwargs)
        
        # Create and return engine
        return EmailScoringEngine(
            scoring_strategy=strategy,
            cache_provider=cache_provider,
            config=config
        )
    
    @staticmethod
    def create_default_engine(config: ScoringConfig) -> EmailScoringEngine:
        """Create a default scoring engine for the current environment."""
        # Import here to avoid circular dependencies
        from app.scoring.strategies import EnhancedScoringStrategy
        from app.scoring.cache_providers import InMemoryCacheProvider
        
        strategy = EnhancedScoringStrategy(config)
        cache = InMemoryCacheProvider()
        
        return EmailScoringEngine(
            scoring_strategy=strategy,
            cache_provider=cache,
            config=config
        )