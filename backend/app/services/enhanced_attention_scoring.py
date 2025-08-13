"""
Enhanced Attention Scoring Service

This service provides the new enhanced attention scoring system while maintaining
backward compatibility with the existing simple scoring service.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.email import Email
from app.scoring import (
    EmailScoringEngine, 
    ScoringEngineFactory, 
    current_config,
    EmailScoringDebugger
)

# Global scoring engine instance
_scoring_engine: Optional[EmailScoringEngine] = None
_debugger: Optional[EmailScoringDebugger] = None

logger = logging.getLogger(__name__)


def get_scoring_engine() -> EmailScoringEngine:
    """
    Get the global scoring engine instance.
    
    This function implements lazy initialization and caching of the scoring engine
    to avoid expensive setup on every import.
    
    Returns:
        Configured EmailScoringEngine instance
    """
    global _scoring_engine
    
    if _scoring_engine is None:
        try:
            config = current_config()
            
            # Try to create engine with Redis cache if available
            try:
                import redis
                from app.config import get_settings
                
                settings = get_settings()
                redis_client = redis.Redis.from_url(settings.REDIS_URL) if hasattr(settings, 'REDIS_URL') else None
                
                if redis_client:
                    _scoring_engine = ScoringEngineFactory.create_engine(
                        config,
                        strategy_type="enhanced",
                        cache_type="multi_tier",
                        redis_client=redis_client
                    )
                    logger.info("[ENHANCED_SCORING] Initialized with Redis multi-tier cache")
                else:
                    raise ImportError("Redis not available")
                    
            except (ImportError, Exception) as e:
                # Fallback to in-memory cache
                _scoring_engine = ScoringEngineFactory.create_engine(
                    config,
                    strategy_type="enhanced", 
                    cache_type="memory"
                )
                logger.info(f"[ENHANCED_SCORING] Initialized with in-memory cache (Redis unavailable: {e})")
                
        except Exception as e:
            logger.error(f"[ENHANCED_SCORING] Failed to initialize scoring engine: {e}")
            # Ultimate fallback to default
            _scoring_engine = ScoringEngineFactory.create_default_engine(current_config())
    
    return _scoring_engine


def get_debugger() -> EmailScoringDebugger:
    """Get the global scoring debugger instance."""
    global _debugger
    
    if _debugger is None:
        _debugger = EmailScoringDebugger(get_scoring_engine())
    
    return _debugger


def calculate_enhanced_attention_score(email: Email, current_time: Optional[datetime] = None) -> float:
    """
    Calculate enhanced attention score for an email.
    
    This is the main entry point for the new scoring system. It uses the
    sophisticated multi-factor scoring algorithm instead of the simple heuristics.
    
    Args:
        email: Email object to score
        current_time: Current timestamp (defaults to now)
        
    Returns:
        Enhanced attention score (0.0-100.0)
    """
    try:
        engine = get_scoring_engine()
        score = engine.get_current_score(email, current_time)
        
        logger.debug(f"[ENHANCED_SCORING] Score for email {email.id}: {score:.1f}")
        return score
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error calculating score for email {email.id}: {e}")
        # Fallback to simple scoring
        from app.services.attention_scoring import calculate_attention_score
        return calculate_attention_score(email)


def calculate_scores_batch(emails: List[Email], current_time: Optional[datetime] = None) -> Dict[str, float]:
    """
    Calculate enhanced attention scores for multiple emails efficiently.
    
    Args:
        emails: List of emails to score
        current_time: Current timestamp (defaults to now)
        
    Returns:
        Dictionary mapping email IDs to scores
    """
    try:
        engine = get_scoring_engine()
        scores = engine.get_scores_batch(emails, current_time)
        
        logger.info(f"[ENHANCED_SCORING] Batch scored {len(emails)} emails")
        return scores
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error in batch scoring: {e}")
        # Fallback to individual scoring
        result = {}
        for email in emails:
            try:
                result[str(email.id)] = calculate_enhanced_attention_score(email, current_time)
            except Exception as email_error:
                logger.error(f"[ENHANCED_SCORING] Error scoring email {email.id}: {email_error}")
                result[str(email.id)] = 50.0  # Safe default
        return result


def invalidate_score_cache(email_ids: Optional[List[str]] = None, pattern: Optional[str] = None) -> int:
    """
    Invalidate cached attention scores.
    
    Args:
        email_ids: Specific email IDs to invalidate (optional)
        pattern: Pattern to match for bulk invalidation (optional)
        
    Returns:
        Number of cache entries invalidated
    """
    try:
        engine = get_scoring_engine()
        invalidated = engine.invalidate_cache(email_ids, pattern)
        
        logger.info(f"[ENHANCED_SCORING] Invalidated {invalidated} cache entries")
        return invalidated
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error invalidating cache: {e}")
        return 0


def get_scoring_performance_stats() -> Dict[str, Any]:
    """
    Get performance statistics for the scoring system.
    
    Returns:
        Dictionary with performance metrics
    """
    try:
        engine = get_scoring_engine()
        return engine.get_performance_stats()
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error getting performance stats: {e}")
        return {'error': str(e)}


def debug_email_score(email: Email, current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get detailed debugging information for an email's score calculation.
    
    Args:
        email: Email to debug
        current_time: Current timestamp (defaults to now)
        
    Returns:
        Detailed score breakdown and analysis
    """
    try:
        debugger = get_debugger()
        breakdown = debugger.debug_score_calculation(email, current_time)
        
        return {
            'email_id': breakdown.email_id,
            'gmail_id': breakdown.gmail_id,
            'category': breakdown.category,
            'age_hours': breakdown.age_hours,
            'components': breakdown.components,
            'factors': breakdown.factors,
            'final_score': breakdown.final_score,
            'calculation_time_ms': breakdown.calculation_time_ms,
            'cache_hit': breakdown.cache_hit
        }
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error debugging email score: {e}")
        return {'error': str(e)}


def analyze_score_distribution(emails: List[Email]) -> Dict[str, Any]:
    """
    Analyze score distribution across a list of emails.
    
    Args:
        emails: List of emails to analyze
        
    Returns:
        Statistical analysis of score distribution
    """
    try:
        debugger = get_debugger()
        analysis = debugger.analyze_score_distribution(emails)
        
        # Convert dataclass objects to dictionaries for JSON serialization
        result = {}
        for category, stats in analysis.items():
            result[category] = {
                'category': stats.category,
                'count': stats.count,
                'mean': stats.mean,
                'median': stats.median,
                'std_dev': stats.std_dev,
                'min_score': stats.min_score,
                'max_score': stats.max_score,
                'percentiles': stats.percentiles,
                'score_ranges': stats.score_ranges
            }
        
        return result
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error analyzing score distribution: {e}")
        return {'error': str(e)}


def update_email_attention_scores(emails: List[Email], force_update: bool = False) -> Dict[str, Any]:
    """
    Update attention scores for a list of emails and save to database.
    
    This function recalculates scores and updates the database. It's useful for
    batch processing and migration scenarios.
    
    Args:
        emails: List of emails to update
        force_update: If True, bypass cache and recalculate all scores
        
    Returns:
        Update results and statistics
    """
    try:
        updated_count = 0
        error_count = 0
        total_time = 0.0
        
        logger.info(f"[ENHANCED_SCORING] Starting batch update of {len(emails)} email scores")
        
        start_time = datetime.now()
        
        for email in emails:
            try:
                # Calculate new score
                if force_update:
                    # Bypass cache to force recalculation
                    engine = get_scoring_engine()
                    new_score = engine.get_current_score(email, bypass_cache=True)
                else:
                    new_score = calculate_enhanced_attention_score(email)
                
                # Update the email object
                old_score = email.attention_score
                email.attention_score = new_score
                
                updated_count += 1
                
                if abs(new_score - (old_score or 0)) > 5.0:  # Significant change
                    logger.debug(f"[ENHANCED_SCORING] Score change for {email.id}: {old_score} → {new_score}")
                
            except Exception as e:
                logger.error(f"[ENHANCED_SCORING] Error updating score for email {email.id}: {e}")
                error_count += 1
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            'total_emails': len(emails),
            'updated_count': updated_count,
            'error_count': error_count,
            'success_rate': round((updated_count / len(emails)) * 100, 2) if emails else 0,
            'total_time_seconds': round(total_time, 2),
            'emails_per_second': round(len(emails) / total_time, 2) if total_time > 0 else 0,
            'force_update': force_update
        }
        
        logger.info(f"[ENHANCED_SCORING] Batch update complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"[ENHANCED_SCORING] Error in batch update: {e}")
        return {'error': str(e)}


# Backward compatibility functions
def calculate_attention_score(email: Email) -> float:
    """
    Backward compatibility wrapper for the original scoring function.
    
    This function provides the same interface as the original but uses the
    enhanced scoring system under the hood.
    """
    return calculate_enhanced_attention_score(email)


def get_attention_level(score: float) -> str:
    """
    Convert attention score to human-readable level.
    
    This maintains the same interface as the original function.
    """
    if score >= 80.0:
        return 'Critical'
    elif score >= 60.0:
        return 'High'
    elif score >= 30.0:
        return 'Medium'
    else:
        return 'Low'


def get_attention_color(score: float) -> str:
    """
    Get color representation for attention score.
    
    This maintains the same interface as the original function.
    """
    if score >= 80.0:
        return 'red'
    elif score >= 60.0:
        return 'orange'
    elif score >= 30.0:
        return 'yellow'
    else:
        return 'green'