"""
Cache Provider Implementations

This module provides different caching backends for email scores.
All implementations follow the CacheProvider interface for easy swapping.
"""

import time
import json
import logging
import pickle
from typing import Optional, Dict, Any
from collections import OrderedDict
from app.scoring.interfaces import BaseCacheProvider


class InMemoryCacheProvider(BaseCacheProvider):
    """
    In-memory cache provider for development and testing.
    
    This provider stores scores in memory with TTL support. It's useful for
    development environments where you don't want to set up Redis, and for
    testing where you need predictable, isolated cache behavior.
    """
    
    def __init__(self, key_prefix: str = "email_score", max_entries: int = 10000):
        super().__init__(key_prefix)
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.max_entries = max_entries
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get(self, key: str) -> Optional[float]:
        """Retrieve a cached score with TTL checking."""
        cache_key = self._make_key(key)
        
        if cache_key not in self.cache:
            self.logger.debug(f"[CACHE_MISS] Key not found: {key}")
            return None
        
        entry = self.cache[cache_key]
        current_time = time.time()
        
        # Check if entry has expired
        if current_time > entry['expires_at']:
            self.logger.debug(f"[CACHE_EXPIRED] Key expired: {key}")
            del self.cache[cache_key]
            return None
        
        # Move to end for LRU behavior
        self.cache.move_to_end(cache_key)
        
        score = entry['value']
        self.logger.debug(f"[CACHE_HIT] {key}: {score}")
        return score
    
    def set(self, key: str, value: float, ttl: int) -> None:
        """Store a score with TTL."""
        cache_key = self._make_key(key)
        expires_at = time.time() + ttl
        
        self.cache[cache_key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        # Move to end for LRU behavior
        self.cache.move_to_end(cache_key)
        
        # Evict oldest entries if we exceed max size
        while len(self.cache) > self.max_entries:
            oldest_key = next(iter(self.cache))
            self.logger.debug(f"[CACHE_EVICT] Evicting oldest entry: {oldest_key}")
            del self.cache[oldest_key]
        
        self.logger.debug(f"[CACHE_SET] {key}: {value} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> None:
        """Remove a cached score."""
        cache_key = self._make_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
            self.logger.debug(f"[CACHE_DEL] Deleted: {key}")
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear entries matching a pattern."""
        # Simple pattern matching for in-memory cache
        import fnmatch
        
        keys_to_delete = []
        for cache_key in self.cache.keys():
            # Remove prefix for pattern matching
            clean_key = cache_key.replace(f"{self.key_prefix}:", "", 1)
            if fnmatch.fnmatch(clean_key, pattern):
                keys_to_delete.append(cache_key)
        
        for cache_key in keys_to_delete:
            del self.cache[cache_key]
        
        self.logger.debug(f"[CACHE_CLEAR] Cleared {len(keys_to_delete)} entries matching '{pattern}'")
        return len(keys_to_delete)
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        current_time = time.time()
        keys_to_delete = []
        
        for cache_key, entry in self.cache.items():
            if current_time > entry['expires_at']:
                keys_to_delete.append(cache_key)
        
        for cache_key in keys_to_delete:
            del self.cache[cache_key]
        
        self.logger.debug(f"[CACHE_CLEANUP] Removed {len(keys_to_delete)} expired entries")
        return len(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        expired_count = sum(1 for entry in self.cache.values() 
                          if current_time > entry['expires_at'])
        
        return {
            'total_entries': len(self.cache),
            'expired_entries': expired_count,
            'active_entries': len(self.cache) - expired_count,
            'max_entries': self.max_entries,
            'memory_usage_estimate': len(self.cache) * 100  # Rough estimate in bytes
        }


class RedisCacheProvider(BaseCacheProvider):
    """
    Redis-based cache provider for production use.
    
    This provider uses Redis for distributed caching with automatic TTL handling.
    It's the recommended choice for production environments.
    """
    
    def __init__(self, redis_client, key_prefix: str = "email_score"):
        super().__init__(key_prefix)
        self.redis = redis_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get(self, key: str) -> Optional[float]:
        """Retrieve a cached score from Redis."""
        try:
            cache_key = self._make_key(key)
            value = self.redis.get(cache_key)
            
            if value is None:
                self.logger.debug(f"[REDIS_MISS] Key not found: {key}")
                return None
            
            score = float(value)
            self.logger.debug(f"[REDIS_HIT] {key}: {score}")
            return score
            
        except Exception as e:
            self.logger.error(f"[REDIS_ERROR] Get failed for {key}: {e}")
            return None
    
    def set(self, key: str, value: float, ttl: int) -> None:
        """Store a score in Redis with TTL."""
        try:
            cache_key = self._make_key(key)
            self.redis.setex(cache_key, ttl, value)
            self.logger.debug(f"[REDIS_SET] {key}: {value} (TTL: {ttl}s)")
            
        except Exception as e:
            self.logger.error(f"[REDIS_ERROR] Set failed for {key}: {e}")
    
    def delete(self, key: str) -> None:
        """Remove a cached score from Redis."""
        try:
            cache_key = self._make_key(key)
            deleted = self.redis.delete(cache_key)
            if deleted:
                self.logger.debug(f"[REDIS_DEL] Deleted: {key}")
            
        except Exception as e:
            self.logger.error(f"[REDIS_ERROR] Delete failed for {key}: {e}")
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear Redis entries matching a pattern."""
        try:
            # Use Redis SCAN for efficient pattern matching
            cache_pattern = self._make_key(pattern)
            cursor = 0
            deleted_count = 0
            
            while True:
                cursor, keys = self.redis.scan(cursor, match=cache_pattern, count=1000)
                if keys:
                    deleted = self.redis.delete(*keys)
                    deleted_count += deleted
                
                if cursor == 0:
                    break
            
            self.logger.debug(f"[REDIS_CLEAR] Cleared {deleted_count} entries matching '{pattern}'")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"[REDIS_ERROR] Clear pattern failed for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = self.redis.info()
            
            # Count keys with our prefix
            cursor = 0
            key_count = 0
            pattern = self._make_key("*")
            
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=1000)
                key_count += len(keys)
                if cursor == 0:
                    break
            
            return {
                'total_keys': key_count,
                'redis_memory_used': info.get('used_memory', 0),
                'redis_memory_human': info.get('used_memory_human', 'Unknown'),
                'redis_connected_clients': info.get('connected_clients', 0),
                'redis_hits': info.get('keyspace_hits', 0),
                'redis_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
            
        except Exception as e:
            self.logger.error(f"[REDIS_ERROR] Stats failed: {e}")
            return {'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate from Redis info."""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100


class NullCacheProvider(BaseCacheProvider):
    """
    Null cache provider that doesn't cache anything.
    
    This is useful for testing scenarios where you want to disable caching
    entirely, or as a fallback when other cache providers fail.
    """
    
    def __init__(self, key_prefix: str = "email_score"):
        super().__init__(key_prefix)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get(self, key: str) -> Optional[float]:
        """Always return None (cache miss)."""
        self.logger.debug(f"[NULL_CACHE] Miss (no caching): {key}")
        return None
    
    def set(self, key: str, value: float, ttl: int) -> None:
        """Do nothing (no caching)."""
        self.logger.debug(f"[NULL_CACHE] No-op set: {key}: {value}")
    
    def delete(self, key: str) -> None:
        """Do nothing (no caching)."""
        self.logger.debug(f"[NULL_CACHE] No-op delete: {key}")
    
    def clear_pattern(self, pattern: str) -> int:
        """Do nothing (no caching)."""
        self.logger.debug(f"[NULL_CACHE] No-op clear: {pattern}")
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Return null cache stats."""
        return {
            'cache_type': 'null',
            'total_entries': 0,
            'hit_rate': 0.0,
            'message': 'Caching disabled'
        }


class MultiTierCacheProvider(BaseCacheProvider):
    """
    Multi-tier cache provider that combines in-memory and Redis caching.
    
    This provider implements a two-tier caching strategy:
    1. Fast in-memory cache for frequently accessed scores
    2. Redis cache for persistence and sharing across instances
    
    This provides the best of both worlds: speed and persistence.
    """
    
    def __init__(
        self, 
        redis_client, 
        key_prefix: str = "email_score",
        memory_cache_size: int = 1000
    ):
        super().__init__(key_prefix)
        self.memory_cache = InMemoryCacheProvider(key_prefix, memory_cache_size)
        self.redis_cache = RedisCacheProvider(redis_client, key_prefix)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get(self, key: str) -> Optional[float]:
        """Try memory cache first, then Redis."""
        # Try memory cache first
        score = self.memory_cache.get(key)
        if score is not None:
            self.logger.debug(f"[MULTI_TIER] Memory hit: {key}: {score}")
            return score
        
        # Try Redis cache
        score = self.redis_cache.get(key)
        if score is not None:
            # Promote to memory cache with shorter TTL
            self.memory_cache.set(key, score, 300)  # 5 minutes in memory
            self.logger.debug(f"[MULTI_TIER] Redis hit, promoted to memory: {key}: {score}")
            return score
        
        self.logger.debug(f"[MULTI_TIER] Miss both tiers: {key}")
        return None
    
    def set(self, key: str, value: float, ttl: int) -> None:
        """Set in both memory and Redis."""
        # Set in Redis with full TTL
        self.redis_cache.set(key, value, ttl)
        
        # Set in memory with shorter TTL for faster access
        memory_ttl = min(ttl, 3600)  # Max 1 hour in memory
        self.memory_cache.set(key, value, memory_ttl)
        
        self.logger.debug(f"[MULTI_TIER] Set both tiers: {key}: {value}")
    
    def delete(self, key: str) -> None:
        """Delete from both tiers."""
        self.memory_cache.delete(key)
        self.redis_cache.delete(key)
        self.logger.debug(f"[MULTI_TIER] Deleted both tiers: {key}")
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear from both tiers."""
        memory_cleared = self.memory_cache.clear_pattern(pattern)
        redis_cleared = self.redis_cache.clear_pattern(pattern)
        
        total_cleared = memory_cleared + redis_cleared
        self.logger.debug(f"[MULTI_TIER] Cleared {total_cleared} entries ({memory_cleared} memory, {redis_cleared} Redis)")
        return total_cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics from both tiers."""
        memory_stats = self.memory_cache.get_stats()
        redis_stats = self.redis_cache.get_stats()
        
        return {
            'cache_type': 'multi_tier',
            'memory_tier': memory_stats,
            'redis_tier': redis_stats,
            'total_tiers': 2
        }


def create_cache_provider(cache_type: str, **kwargs) -> BaseCacheProvider:
    """
    Factory function to create the appropriate cache provider.
    
    Args:
        cache_type: Type of cache ('memory', 'redis', 'null', 'multi_tier')
        **kwargs: Additional arguments for cache provider construction
    
    Returns:
        Configured cache provider instance
    """
    if cache_type == 'memory':
        return InMemoryCacheProvider(**kwargs)
    elif cache_type == 'redis':
        return RedisCacheProvider(**kwargs)
    elif cache_type == 'null':
        return NullCacheProvider(**kwargs)
    elif cache_type == 'multi_tier':
        return MultiTierCacheProvider(**kwargs)
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")