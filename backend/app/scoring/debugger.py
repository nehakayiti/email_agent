"""
Scoring System Debugger and Analysis Tools

This module provides comprehensive debugging and analysis capabilities for the
email scoring system. It helps developers understand scoring decisions and
optimize the system performance.
"""

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
from app.models.email import Email
from app.scoring.engine import EmailScoringEngine
from app.scoring.config import ScoringConfig
from app.scoring.interfaces import ScoringStrategy


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of how a score was calculated."""
    email_id: str
    gmail_id: str
    category: str
    age_hours: float
    components: Dict[str, float]
    factors: Dict[str, Any]
    final_score: float
    calculation_time_ms: float
    cache_hit: bool


@dataclass
class ScoreDistributionAnalysis:
    """Statistical analysis of score distribution."""
    category: str
    count: int
    mean: float
    median: float
    std_dev: float
    min_score: float
    max_score: float
    percentiles: Dict[str, float]
    score_ranges: Dict[str, int]


class EmailScoringDebugger:
    """
    Comprehensive debugger for the email scoring system.
    
    This class provides detailed analysis and debugging capabilities to help
    developers understand why emails receive certain scores and optimize the
    scoring algorithms.
    """
    
    def __init__(self, engine: EmailScoringEngine):
        self.engine = engine
        self.config = engine.config
        self.logger = engine.logger
    
    def debug_score_calculation(self, email: Email, current_time: Optional[datetime] = None) -> ScoreBreakdown:
        """
        Get a detailed breakdown of how a score was calculated.
        
        This method performs the same calculation as the engine but captures
        detailed information about each step for debugging purposes.
        
        Args:
            email: Email to analyze
            current_time: Current timestamp (defaults to now)
            
        Returns:
            Detailed score breakdown
        """
        import time
        
        current_time = current_time or datetime.now()
        start_time = time.time()
        email_id = str(email.id)
        gmail_id = getattr(email, 'gmail_id', 'unknown')
        
        # Check if score is cached
        cached_score = self.engine._get_cached_score(email_id, current_time)
        cache_hit = cached_score is not None
        
        # Calculate each component separately for detailed analysis
        base_score = self.engine.scoring_strategy.calculate_base_score(email)
        
        age_hours = (current_time - email.received_at).total_seconds() / 3600 if email.received_at else 0
        temporal_multiplier = self.engine.scoring_strategy.calculate_temporal_multiplier(email, age_hours)
        
        context_boost = self.engine.scoring_strategy.calculate_context_boost(email, current_time)
        
        # Calculate final score
        raw_score = (base_score * temporal_multiplier) + context_boost
        final_score = max(0.0, min(100.0, raw_score))
        
        calculation_time = (time.time() - start_time) * 1000
        
        # Build detailed breakdown
        components = {
            'base_score': round(base_score, 2),
            'temporal_multiplier': round(temporal_multiplier, 4),
            'temporal_adjusted_score': round(base_score * temporal_multiplier, 2),
            'context_boost': round(context_boost, 2),
            'raw_score': round(raw_score, 2),
            'final_score': round(final_score, 2),
            'cached_score': round(cached_score, 2) if cached_score else None
        }
        
        factors = {
            'category': email.category,
            'is_read': email.is_read,
            'labels': email.labels or [],
            'from_email': email.from_email,
            'subject': email.subject,
            'received_at': email.received_at.isoformat() if email.received_at else None,
            'age_hours': round(age_hours, 2),
            'current_time': current_time.isoformat(),
            'strategy_type': self.engine.scoring_strategy.__class__.__name__
        }
        
        return ScoreBreakdown(
            email_id=email_id,
            gmail_id=gmail_id,
            category=email.category or 'unknown',
            age_hours=age_hours,
            components=components,
            factors=factors,
            final_score=final_score,
            calculation_time_ms=calculation_time,
            cache_hit=cache_hit
        )
    
    def analyze_score_distribution(
        self, 
        emails: List[Email], 
        group_by: str = 'category'
    ) -> Dict[str, ScoreDistributionAnalysis]:
        """
        Analyze the distribution of scores across multiple emails.
        
        Args:
            emails: List of emails to analyze
            group_by: Field to group by ('category', 'sender_domain', 'read_status')
            
        Returns:
            Statistical analysis grouped by the specified field
        """
        if not emails:
            return {}
        
        # Calculate scores for all emails
        scores_data = []
        for email in emails:
            try:
                score = self.engine.get_current_score(email)
                group_key = self._get_group_key(email, group_by)
                scores_data.append((group_key, score))
            except Exception as e:
                self.logger.error(f"Error calculating score for email {email.id}: {e}")
                continue
        
        # Group scores by the specified field
        grouped_scores = defaultdict(list)
        for group_key, score in scores_data:
            grouped_scores[group_key].append(score)
        
        # Calculate statistics for each group
        analyses = {}
        for group_key, scores in grouped_scores.items():
            if not scores:
                continue
            
            # Calculate percentiles
            percentiles = {
                'p25': self._percentile(scores, 25),
                'p50': self._percentile(scores, 50),
                'p75': self._percentile(scores, 75),
                'p90': self._percentile(scores, 90),
                'p95': self._percentile(scores, 95),
                'p99': self._percentile(scores, 99)
            }
            
            # Calculate score ranges
            score_ranges = {
                '0-20': sum(1 for s in scores if 0 <= s < 20),
                '20-40': sum(1 for s in scores if 20 <= s < 40),
                '40-60': sum(1 for s in scores if 40 <= s < 60),
                '60-80': sum(1 for s in scores if 60 <= s < 80),
                '80-100': sum(1 for s in scores if 80 <= s <= 100)
            }
            
            analysis = ScoreDistributionAnalysis(
                category=group_key,
                count=len(scores),
                mean=round(statistics.mean(scores), 2),
                median=round(statistics.median(scores), 2),
                std_dev=round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
                min_score=round(min(scores), 2),
                max_score=round(max(scores), 2),
                percentiles=percentiles,
                score_ranges=score_ranges
            )
            
            analyses[group_key] = analysis
        
        return analyses
    
    def compare_scoring_strategies(
        self, 
        email: Email, 
        strategies: List[Tuple[str, ScoringStrategy]]
    ) -> Dict[str, Any]:
        """
        Compare how different scoring strategies would score the same email.
        
        Args:
            email: Email to score
            strategies: List of (name, strategy) tuples
            
        Returns:
            Comparison results showing scores from each strategy
        """
        current_time = datetime.now()
        results = {}
        
        for strategy_name, strategy in strategies:
            try:
                # Calculate components using this strategy
                base_score = strategy.calculate_base_score(email)
                
                age_hours = (current_time - email.received_at).total_seconds() / 3600 if email.received_at else 0
                temporal_multiplier = strategy.calculate_temporal_multiplier(email, age_hours)
                
                context_boost = strategy.calculate_context_boost(email, current_time)
                
                raw_score = (base_score * temporal_multiplier) + context_boost
                final_score = max(0.0, min(100.0, raw_score))
                
                results[strategy_name] = {
                    'base_score': round(base_score, 2),
                    'temporal_multiplier': round(temporal_multiplier, 4),
                    'context_boost': round(context_boost, 2),
                    'final_score': round(final_score, 2)
                }
                
            except Exception as e:
                self.logger.error(f"Error comparing strategy {strategy_name}: {e}")
                results[strategy_name] = {'error': str(e)}
        
        # Calculate differences
        if len(results) >= 2:
            scores = [r.get('final_score', 0) for r in results.values() if 'final_score' in r]
            if scores:
                results['_comparison'] = {
                    'max_difference': round(max(scores) - min(scores), 2),
                    'coefficient_of_variation': round(statistics.stdev(scores) / statistics.mean(scores), 4) if statistics.mean(scores) > 0 else 0
                }
        
        return results
    
    def analyze_temporal_decay(
        self, 
        category: str, 
        max_hours: int = 168
    ) -> Dict[str, Any]:
        """
        Analyze how scores decay over time for a specific category.
        
        Args:
            category: Email category to analyze
            max_hours: Maximum hours to analyze (default: 1 week)
            
        Returns:
            Temporal decay analysis
        """
        # Create time points to analyze
        time_points = [0, 1, 6, 12, 24, 48, 72, 168]  # hours
        time_points = [h for h in time_points if h <= max_hours]
        
        # Get decay function for this category
        decay_function = self.config.get_temporal_decay_function(category)
        
        # Calculate multipliers for each time point
        decay_data = []
        for hours in time_points:
            multiplier = decay_function(hours)
            decay_data.append({
                'hours': hours,
                'multiplier': round(multiplier, 4),
                'days': round(hours / 24, 2)
            })
        
        # Calculate decay characteristics
        initial_multiplier = decay_data[0]['multiplier']
        final_multiplier = decay_data[-1]['multiplier']
        half_life_hours = self._calculate_half_life(decay_function, max_hours)
        
        return {
            'category': category,
            'decay_data': decay_data,
            'initial_multiplier': initial_multiplier,
            'final_multiplier': final_multiplier,
            'total_decay_percent': round((1 - final_multiplier / initial_multiplier) * 100, 1),
            'half_life_hours': half_life_hours,
            'half_life_days': round(half_life_hours / 24, 2) if half_life_hours else None
        }
    
    def identify_scoring_anomalies(
        self, 
        emails: List[Email], 
        threshold_std_devs: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Identify emails with anomalous scores (outliers).
        
        Args:
            emails: List of emails to analyze
            threshold_std_devs: Number of standard deviations to consider anomalous
            
        Returns:
            List of anomalous emails with details
        """
        if len(emails) < 10:  # Need enough data for meaningful statistics
            return []
        
        # Calculate scores for all emails
        scores = []
        email_score_map = {}
        
        for email in emails:
            try:
                score = self.engine.get_current_score(email)
                scores.append(score)
                email_score_map[str(email.id)] = (email, score)
            except Exception as e:
                self.logger.error(f"Error calculating score for anomaly detection: {e}")
                continue
        
        if len(scores) < 10:
            return []
        
        # Calculate statistics
        mean_score = statistics.mean(scores)
        std_dev = statistics.stdev(scores)
        threshold = threshold_std_devs * std_dev
        
        # Identify anomalies
        anomalies = []
        for email_id, (email, score) in email_score_map.items():
            deviation = abs(score - mean_score)
            
            if deviation > threshold:
                # Get detailed breakdown for this anomaly
                breakdown = self.debug_score_calculation(email)
                
                anomalies.append({
                    'email_id': email_id,
                    'gmail_id': getattr(email, 'gmail_id', 'unknown'),
                    'score': score,
                    'mean_score': round(mean_score, 2),
                    'deviation': round(deviation, 2),
                    'std_devs_from_mean': round(deviation / std_dev, 2),
                    'anomaly_type': 'high' if score > mean_score else 'low',
                    'breakdown': breakdown,
                    'email_summary': {
                        'category': email.category,
                        'subject': email.subject[:50] + '...' if email.subject and len(email.subject) > 50 else email.subject,
                        'from_email': email.from_email,
                        'is_read': email.is_read,
                        'received_at': email.received_at.isoformat() if email.received_at else None
                    }
                })
        
        # Sort by deviation (most anomalous first)
        anomalies.sort(key=lambda x: x['deviation'], reverse=True)
        
        return anomalies
    
    def generate_scoring_report(self, emails: List[Email]) -> Dict[str, Any]:
        """
        Generate a comprehensive scoring report for a list of emails.
        
        Args:
            emails: List of emails to analyze
            
        Returns:
            Comprehensive scoring report
        """
        if not emails:
            return {'error': 'No emails provided'}
        
        report = {
            'summary': {
                'total_emails': len(emails),
                'analysis_timestamp': datetime.now().isoformat(),
                'engine_stats': self.engine.get_performance_stats()
            }
        }
        
        try:
            # Score distribution analysis
            report['score_distribution'] = self.analyze_score_distribution(emails, 'category')
            
            # Temporal decay analysis for major categories
            categories = set(email.category for email in emails if email.category)
            report['temporal_decay'] = {}
            for category in categories:
                if category:  # Skip None categories
                    report['temporal_decay'][category] = self.analyze_temporal_decay(category)
            
            # Anomaly detection
            report['anomalies'] = self.identify_scoring_anomalies(emails)
            
            # Category performance
            report['category_performance'] = self._analyze_category_performance(emails)
            
            # Scoring efficiency metrics
            report['efficiency_metrics'] = self._calculate_efficiency_metrics(emails)
            
        except Exception as e:
            self.logger.error(f"Error generating scoring report: {e}")
            report['error'] = str(e)
        
        return report
    
    def _get_group_key(self, email: Email, group_by: str) -> str:
        """Get the grouping key for an email based on the group_by field."""
        if group_by == 'category':
            return email.category or 'uncategorized'
        elif group_by == 'sender_domain':
            if email.from_email and '@' in email.from_email:
                return email.from_email.split('@')[1].lower()
            return 'unknown_domain'
        elif group_by == 'read_status':
            return 'read' if email.is_read else 'unread'
        else:
            return 'unknown'
    
    def _percentile(self, scores: List[float], percentile: int) -> float:
        """Calculate a percentile from a list of scores."""
        if not scores:
            return 0.0
        
        sorted_scores = sorted(scores)
        index = (percentile / 100) * (len(sorted_scores) - 1)
        
        if index.is_integer():
            return round(sorted_scores[int(index)], 2)
        else:
            lower = sorted_scores[int(index)]
            upper = sorted_scores[int(index) + 1]
            return round(lower + (upper - lower) * (index - int(index)), 2)
    
    def _calculate_half_life(self, decay_function, max_hours: int) -> Optional[float]:
        """Calculate the half-life of a decay function."""
        initial_value = decay_function(0)
        target_value = initial_value * 0.5
        
        # Binary search for half-life
        low, high = 0, max_hours
        tolerance = 0.01
        
        for _ in range(100):  # Max iterations
            mid = (low + high) / 2
            current_value = decay_function(mid)
            
            if abs(current_value - target_value) < tolerance:
                return round(mid, 2)
            elif current_value > target_value:
                low = mid
            else:
                high = mid
        
        return None  # Couldn't find half-life within range
    
    def _analyze_category_performance(self, emails: List[Email]) -> Dict[str, Any]:
        """Analyze scoring performance by category."""
        category_stats = defaultdict(list)
        
        for email in emails:
            try:
                score = self.engine.get_current_score(email)
                category = email.category or 'uncategorized'
                category_stats[category].append(score)
            except:
                continue
        
        performance = {}
        for category, scores in category_stats.items():
            performance[category] = {
                'count': len(scores),
                'avg_score': round(statistics.mean(scores), 2),
                'score_consistency': round(1 / (statistics.stdev(scores) + 0.001), 2),  # Higher = more consistent
                'high_score_rate': round(sum(1 for s in scores if s >= 70) / len(scores) * 100, 1)
            }
        
        return performance
    
    def _calculate_efficiency_metrics(self, emails: List[Email]) -> Dict[str, Any]:
        """Calculate scoring system efficiency metrics."""
        start_time = datetime.now()
        
        # Sample calculation times
        sample_size = min(50, len(emails))
        sample_emails = emails[:sample_size]
        
        calculation_times = []
        for email in sample_emails:
            calc_start = datetime.now()
            self.engine.get_current_score(email, bypass_cache=True)
            calc_time = (datetime.now() - calc_start).total_seconds() * 1000
            calculation_times.append(calc_time)
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'sample_size': sample_size,
            'avg_calculation_time_ms': round(statistics.mean(calculation_times), 2),
            'max_calculation_time_ms': round(max(calculation_times), 2),
            'total_analysis_time_ms': round(total_time, 2),
            'calculations_per_second': round(sample_size / (total_time / 1000), 2)
        }