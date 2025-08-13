"""
Comprehensive Test Suite for Email Scoring System

This test suite covers all components of the scoring system with various
scenarios to ensure reliability and correctness.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.models.email import Email
from app.scoring.config import ScoringConfig, TestingScoringConfig
from app.scoring.strategies import EnhancedScoringStrategy, SimpleScoringStrategy
from app.scoring.cache_providers import InMemoryCacheProvider, NullCacheProvider
from app.scoring.engine import EmailScoringEngine, ScoringEngineFactory
from app.scoring.debugger import EmailScoringDebugger


class TestScoringConfiguration:
    """Test the scoring configuration system."""
    
    def test_default_config_values(self):
        """Test that default configuration has expected values."""
        config = ScoringConfig()
        
        assert config.CATEGORY_BASE_SCORES['important'] == 35.0
        assert config.CATEGORY_BASE_SCORES['newsletters'] == 15.0
        assert config.UNREAD_BONUS == 8.0
        assert config.IMPORTANT_LABEL_BONUS == 12.0
    
    def test_testing_config_override(self):
        """Test that testing config properly overrides defaults."""
        config = TestingScoringConfig()
        
        # Testing config should have minimal cache TTLs
        assert config.CACHE_TTL_MAP['promotions'] == 1
        assert config.LOG_SCORE_CALCULATIONS == False
    
    def test_cache_ttl_getter(self):
        """Test cache TTL getter with various categories."""
        config = ScoringConfig()
        
        assert config.get_cache_ttl('promotions') == 3600 * 6
        assert config.get_cache_ttl('unknown_category') == config.CACHE_TTL_MAP['default']
    
    def test_temporal_decay_functions(self):
        """Test that temporal decay functions work correctly."""
        config = ScoringConfig()
        
        # Test promotions decay (should be aggressive)
        promo_decay = config.get_temporal_decay_function('promotions')
        assert promo_decay(0) == 1.0  # Fresh
        assert promo_decay(72) < 0.5  # Should decay significantly after 3 days
        
        # Test important decay (should be conservative)
        important_decay = config.get_temporal_decay_function('important')
        assert important_decay(0) == 1.0  # Fresh
        assert important_decay(168) >= 0.5  # Should still be above 50% after a week


class TestInMemoryCacheProvider:
    """Test the in-memory cache provider."""
    
    def test_basic_cache_operations(self):
        """Test basic get/set/delete operations."""
        cache = InMemoryCacheProvider()
        
        # Test set and get
        cache.set('test_key', 75.5, 3600)
        assert cache.get('test_key') == 75.5
        
        # Test non-existent key
        assert cache.get('non_existent') is None
        
        # Test delete
        cache.delete('test_key')
        assert cache.get('test_key') is None
    
    def test_cache_expiration(self):
        """Test that cache entries expire correctly."""
        cache = InMemoryCacheProvider()
        
        # Set with very short TTL
        cache.set('expire_test', 50.0, 1)
        assert cache.get('expire_test') == 50.0
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('expire_test') is None
    
    def test_cache_size_limit(self):
        """Test that cache respects size limits."""
        cache = InMemoryCacheProvider(max_entries=3)
        
        # Fill cache to limit
        cache.set('key1', 10.0, 3600)
        cache.set('key2', 20.0, 3600)
        cache.set('key3', 30.0, 3600)
        
        # Add one more (should evict oldest)
        cache.set('key4', 40.0, 3600)
        
        assert cache.get('key1') is None  # Should be evicted
        assert cache.get('key4') == 40.0  # Should be present
    
    def test_clear_pattern(self):
        """Test pattern-based cache clearing."""
        cache = InMemoryCacheProvider()
        
        cache.set('email:123', 50.0, 3600)
        cache.set('email:456', 60.0, 3600)
        cache.set('other:789', 70.0, 3600)
        
        cleared = cache.clear_pattern('email:*')
        assert cleared == 2
        assert cache.get('other:789') == 70.0  # Should remain


class TestEnhancedScoringStrategy:
    """Test the enhanced scoring strategy."""
    
    @pytest.fixture
    def config(self):
        return TestingScoringConfig()
    
    @pytest.fixture
    def strategy(self, config):
        return EnhancedScoringStrategy(config)
    
    @pytest.fixture
    def sample_email(self):
        email = Mock(spec=Email)
        email.id = 'test-email-123'
        email.gmail_id = 'mock_gmail_123'
        email.category = 'important'
        email.is_read = False
        email.labels = ['IMPORTANT', 'INBOX']
        email.from_email = 'user@gmail.com'
        email.subject = 'Important meeting tomorrow'
        email.received_at = datetime.now() - timedelta(hours=2)
        return email
    
    def test_base_score_calculation(self, strategy, sample_email):
        """Test base score calculation with various email properties."""
        score = strategy.calculate_base_score(sample_email)
        
        # Should include category score + engagement bonuses + sender authority
        expected = 35.0 + 8.0 + 12.0 + 6.0  # important + unread + important_label + personal_domain
        assert score == expected
    
    def test_base_score_different_categories(self, strategy, sample_email):
        """Test base scores for different email categories."""
        test_cases = [
            ('important', 35.0),
            ('newsletters', 15.0),
            ('promotions', 8.0),
            ('social', 12.0),
            ('archive', 5.0),
            ('trash', 0.0)
        ]
        
        for category, expected_base in test_cases:
            sample_email.category = category
            sample_email.labels = []  # Remove label bonuses
            sample_email.is_read = True  # Remove read bonus
            sample_email.from_email = 'user@example.com'  # Neutral sender, no bonus or penalty
            
            score = strategy.calculate_base_score(sample_email)
            assert score == expected_base
    
    def test_temporal_multiplier_promotions(self, strategy, sample_email):
        """Test temporal decay for promotional emails."""
        sample_email.category = 'promotions'
        
        # Fresh email should have full multiplier
        multiplier_fresh = strategy.calculate_temporal_multiplier(sample_email, 0.5)
        assert multiplier_fresh > 0.9
        
        # Old email should have low multiplier
        multiplier_old = strategy.calculate_temporal_multiplier(sample_email, 168)  # 1 week
        assert multiplier_old < 0.3
        
        # Multiplier should decrease over time
        assert multiplier_fresh > multiplier_old
    
    def test_temporal_multiplier_important(self, strategy, sample_email):
        """Test temporal decay for important emails."""
        sample_email.category = 'important'
        
        # Important emails should decay slowly
        multiplier_week = strategy.calculate_temporal_multiplier(sample_email, 168)  # 1 week
        assert multiplier_week >= 0.5  # Should never go below 50%
    
    def test_context_boost_business_hours(self, strategy, sample_email):
        """Test context boost during business hours."""
        # Business hours (2 PM on Tuesday)
        business_time = datetime(2024, 1, 9, 14, 0, 0)  # Tuesday 2 PM
        boost = strategy.calculate_context_boost(sample_email, business_time)
        
        assert boost >= 5.0  # Should get business hours boost for important emails
    
    def test_context_boost_evening(self, strategy, sample_email):
        """Test context boost during evening hours."""
        sample_email.category = 'newsletters'
        
        # Evening time (8 PM)
        evening_time = datetime(2024, 1, 9, 20, 0, 0)
        boost = strategy.calculate_context_boost(sample_email, evening_time)
        
        assert boost >= 3.0  # Should get evening boost for newsletters
    
    def test_urgent_content_detection(self, strategy, sample_email):
        """Test detection of urgent content in subject lines."""
        urgent_subjects = [
            'URGENT: Action required',
            'Deadline tomorrow for project',
            'ASAP response needed',
            'Final notice - expires today'
        ]
        
        for subject in urgent_subjects:
            sample_email.subject = subject
            score = strategy._calculate_content_urgency(sample_email)
            assert score == 5.0, f"Failed to detect urgency in: {subject}"
    
    def test_sender_authority_personal_domain(self, strategy, sample_email):
        """Test sender authority scoring for personal domains."""
        sample_email.from_email = 'john@gmail.com'
        authority_score = strategy._calculate_sender_authority(sample_email)
        assert authority_score == 6.0  # Personal domain boost
    
    def test_sender_authority_marketing(self, strategy, sample_email):
        """Test sender authority penalty for marketing senders."""
        sample_email.from_email = 'noreply@marketing.com'
        authority_score = strategy._calculate_sender_authority(sample_email)
        assert authority_score == -5.0  # Marketing penalty


class TestEmailScoringEngine:
    """Test the main email scoring engine."""
    
    @pytest.fixture
    def config(self):
        return TestingScoringConfig()
    
    @pytest.fixture
    def mock_strategy(self):
        strategy = Mock()
        strategy.calculate_base_score.return_value = 40.0
        strategy.calculate_temporal_multiplier.return_value = 0.9
        strategy.calculate_context_boost.return_value = 5.0
        return strategy
    
    @pytest.fixture
    def cache_provider(self):
        return InMemoryCacheProvider()
    
    @pytest.fixture
    def engine(self, mock_strategy, cache_provider, config):
        return EmailScoringEngine(mock_strategy, cache_provider, config)
    
    @pytest.fixture
    def sample_email(self):
        email = Mock(spec=Email)
        email.id = 'test-email-456'
        email.gmail_id = 'mock_gmail_456'
        email.category = 'important'
        email.received_at = datetime.now() - timedelta(hours=1)
        return email
    
    def test_fresh_score_calculation(self, engine, sample_email, mock_strategy):
        """Test calculation of fresh scores."""
        score = engine.get_current_score(sample_email)
        
        # Should be (base * temporal) + context = (40 * 0.9) + 5 = 41
        expected = 41.0
        assert score == expected
        
        # Verify strategy methods were called
        mock_strategy.calculate_base_score.assert_called_once_with(sample_email)
        mock_strategy.calculate_temporal_multiplier.assert_called_once()
        mock_strategy.calculate_context_boost.assert_called_once()
    
    def test_cache_hit_scenario(self, engine, sample_email, cache_provider):
        """Test that cached scores are returned without recalculation."""
        # Pre-populate cache
        cache_provider.set(str(sample_email.id), 75.0, 3600)
        
        score = engine.get_current_score(sample_email)
        assert score == 75.0
        
        # Strategy should not be called for cache hits
        engine.scoring_strategy.calculate_base_score.assert_not_called()
    
    def test_score_clamping(self, engine, sample_email, mock_strategy):
        """Test that scores are clamped to 0-100 range."""
        # Test upper bound clamping
        mock_strategy.calculate_base_score.return_value = 90.0
        mock_strategy.calculate_temporal_multiplier.return_value = 1.0
        mock_strategy.calculate_context_boost.return_value = 20.0  # Would result in 110
        
        score = engine.get_current_score(sample_email)
        assert score == 100.0
        
        # Test lower bound clamping
        mock_strategy.calculate_base_score.return_value = 5.0
        mock_strategy.calculate_temporal_multiplier.return_value = 0.1
        mock_strategy.calculate_context_boost.return_value = -10.0  # Would result in negative
        
        score = engine.get_current_score(sample_email, bypass_cache=True)
        assert score == 0.0
    
    def test_batch_scoring(self, engine, mock_strategy, cache_provider):
        """Test batch scoring functionality."""
        # Create multiple emails
        emails = []
        for i in range(5):
            email = Mock(spec=Email)
            email.id = f'email-{i}'
            email.category = 'newsletters'
            email.received_at = datetime.now() - timedelta(hours=i)
            emails.append(email)
        
        # Pre-cache one email
        cache_provider.set('email-0', 50.0, 3600)
        
        scores = engine.get_scores_batch(emails)
        
        assert len(scores) == 5
        assert scores['email-0'] == 50.0  # From cache
        
        # Other scores should be calculated
        for i in range(1, 5):
            assert f'email-{i}' in scores
            assert isinstance(scores[f'email-{i}'], float)
    
    def test_cache_invalidation(self, engine, cache_provider):
        """Test cache invalidation functionality."""
        # Populate cache
        cache_provider.set('email-1', 60.0, 3600)
        cache_provider.set('email-2', 70.0, 3600)
        cache_provider.set('other-1', 80.0, 3600)
        
        # Test specific email invalidation
        invalidated = engine.invalidate_cache(['email-1'])
        assert invalidated == 1
        assert cache_provider.get('email-1') is None
        assert cache_provider.get('email-2') == 70.0
        
        # Test pattern invalidation
        invalidated = engine.invalidate_cache(pattern='email-*')
        assert cache_provider.get('email-2') is None
        assert cache_provider.get('other-1') == 80.0  # Different pattern
    
    def test_performance_stats(self, engine, sample_email):
        """Test performance statistics tracking."""
        # Generate some activity
        engine.get_current_score(sample_email)  # Cache miss
        engine.get_current_score(sample_email)  # Cache hit
        
        stats = engine.get_performance_stats()
        
        assert stats['total_score_requests'] == 2
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 1
        assert stats['cache_hit_rate_percent'] == 50.0
        assert stats['calculations_performed'] == 1
    
    def test_error_handling(self, engine, sample_email, mock_strategy):
        """Test error handling in score calculation."""
        # Make strategy throw an error
        mock_strategy.calculate_base_score.side_effect = Exception("Test error")
        
        # Should return safe default without crashing
        score = engine.get_current_score(sample_email)
        assert score == 50.0  # Safe default


class TestScoringEngineFactory:
    """Test the scoring engine factory."""
    
    def test_create_default_engine(self):
        """Test creation of default engine."""
        config = TestingScoringConfig()
        engine = ScoringEngineFactory.create_default_engine(config)
        
        assert isinstance(engine, EmailScoringEngine)
        assert engine.config == config
    
    def test_create_engine_with_strategies(self):
        """Test engine creation with different strategies."""
        config = TestingScoringConfig()
        
        # Test enhanced strategy
        engine = ScoringEngineFactory.create_engine(
            config, 
            strategy_type="enhanced",
            cache_type="memory"
        )
        assert isinstance(engine.scoring_strategy, EnhancedScoringStrategy)
        
        # Test simple strategy
        engine = ScoringEngineFactory.create_engine(
            config,
            strategy_type="simple",
            cache_type="null"
        )
        assert isinstance(engine.scoring_strategy, SimpleScoringStrategy)
        assert isinstance(engine.cache, NullCacheProvider)
    
    def test_invalid_strategy_type(self):
        """Test error handling for invalid strategy types."""
        config = TestingScoringConfig()
        
        with pytest.raises(ValueError, match="Unknown strategy type"):
            ScoringEngineFactory.create_engine(config, strategy_type="invalid")


class TestEmailScoringDebugger:
    """Test the scoring debugger functionality."""
    
    @pytest.fixture
    def engine(self):
        config = TestingScoringConfig()
        return ScoringEngineFactory.create_default_engine(config)
    
    @pytest.fixture
    def debugger(self, engine):
        return EmailScoringDebugger(engine)
    
    @pytest.fixture
    def sample_email(self):
        email = Mock(spec=Email)
        email.id = 'debug-test-email'
        email.gmail_id = 'debug_gmail_123'
        email.category = 'newsletters'
        email.is_read = True
        email.labels = ['INBOX']
        email.from_email = 'newsletter@example.com'
        email.subject = 'Weekly tech digest'
        email.received_at = datetime.now() - timedelta(hours=6)
        return email
    
    def test_debug_score_calculation(self, debugger, sample_email):
        """Test detailed score calculation debugging."""
        breakdown = debugger.debug_score_calculation(sample_email)
        
        assert breakdown.email_id == 'debug-test-email'
        assert breakdown.gmail_id == 'debug_gmail_123'
        assert breakdown.category == 'newsletters'
        assert isinstance(breakdown.final_score, float)
        assert 0 <= breakdown.final_score <= 100
        assert isinstance(breakdown.components, dict)
        assert 'base_score' in breakdown.components
        assert 'temporal_multiplier' in breakdown.components
        assert 'context_boost' in breakdown.components
    
    def test_score_distribution_analysis(self, debugger):
        """Test score distribution analysis."""
        # Create diverse email set
        emails = []
        categories = ['important', 'newsletters', 'promotions']
        
        for i, category in enumerate(categories * 3):  # 9 emails total
            email = Mock(spec=Email)
            email.id = f'analysis-email-{i}'
            email.category = category
            email.is_read = i % 2 == 0
            email.labels = ['IMPORTANT'] if category == 'important' else []
            email.from_email = f'test{i}@example.com'
            email.subject = f'Test subject {i}'
            email.received_at = datetime.now() - timedelta(hours=i)
            emails.append(email)
        
        analysis = debugger.analyze_score_distribution(emails)
        
        assert len(analysis) == 3  # Three categories
        assert 'important' in analysis
        assert 'newsletters' in analysis
        assert 'promotions' in analysis
        
        for category_analysis in analysis.values():
            assert isinstance(category_analysis.count, int)
            assert isinstance(category_analysis.mean, float)
            assert isinstance(category_analysis.std_dev, float)
    
    def test_temporal_decay_analysis(self, debugger):
        """Test temporal decay analysis."""
        analysis = debugger.analyze_temporal_decay('promotions')
        
        assert analysis['category'] == 'promotions'
        assert isinstance(analysis['decay_data'], list)
        assert len(analysis['decay_data']) > 0
        
        # Check that decay data is properly structured
        first_point = analysis['decay_data'][0]
        assert first_point['hours'] == 0
        assert first_point['multiplier'] == 1.0
        
        # Multipliers should generally decrease over time
        multipliers = [point['multiplier'] for point in analysis['decay_data']]
        assert multipliers[0] >= multipliers[-1]  # Should decay over time
    
    def test_anomaly_detection(self, debugger):
        """Test anomaly detection in scoring."""
        # Create emails with mostly similar scores and one outlier
        emails = []
        
        # Normal emails (should score around 20-30)
        for i in range(10):
            email = Mock(spec=Email)
            email.id = f'normal-email-{i}'
            email.category = 'newsletters'
            email.is_read = True
            email.labels = []
            email.from_email = f'newsletter{i}@example.com'
            email.subject = f'Newsletter {i}'
            email.received_at = datetime.now() - timedelta(hours=i)
            emails.append(email)
        
        # Anomalous email (should score much higher)
        anomaly_email = Mock(spec=Email)
        anomaly_email.id = 'anomaly-email'
        anomaly_email.category = 'important'
        anomaly_email.is_read = False
        anomaly_email.labels = ['IMPORTANT', 'STARRED']
        anomaly_email.from_email = 'boss@company.com'
        anomaly_email.subject = 'URGENT: Critical system failure'
        anomaly_email.received_at = datetime.now()
        emails.append(anomaly_email)
        
        anomalies = debugger.identify_scoring_anomalies(emails)
        
        # Should detect the anomalous email
        assert len(anomalies) >= 1
        anomaly = anomalies[0]
        assert anomaly['email_id'] == 'anomaly-email'
        assert anomaly['anomaly_type'] == 'high'
    
    def test_comprehensive_report_generation(self, debugger):
        """Test comprehensive scoring report generation."""
        # Create a small set of diverse emails
        emails = []
        for i in range(5):
            email = Mock(spec=Email)
            email.id = f'report-email-{i}'
            email.category = ['important', 'newsletters'][i % 2]
            email.is_read = i % 3 == 0
            email.labels = ['IMPORTANT'] if i == 0 else []
            email.from_email = f'test{i}@example.com'
            email.subject = f'Report test {i}'
            email.received_at = datetime.now() - timedelta(hours=i)
            emails.append(email)
        
        report = debugger.generate_scoring_report(emails)
        
        assert 'summary' in report
        assert 'score_distribution' in report
        assert 'temporal_decay' in report
        assert 'anomalies' in report
        assert 'category_performance' in report
        assert 'efficiency_metrics' in report
        
        assert report['summary']['total_emails'] == 5


class TestIntegrationScenarios:
    """Integration tests for complete scoring scenarios."""
    
    def test_complete_scoring_workflow(self):
        """Test a complete scoring workflow from start to finish."""
        # Create engine with real components
        config = TestingScoringConfig()
        engine = ScoringEngineFactory.create_engine(
            config,
            strategy_type="enhanced",
            cache_type="memory"
        )
        
        # Create a realistic email
        email = Mock(spec=Email)
        email.id = 'integration-test-email'
        email.gmail_id = 'integration_gmail_123'
        email.category = 'important'
        email.is_read = False
        email.labels = ['IMPORTANT', 'INBOX']
        email.from_email = 'manager@company.com'
        email.subject = 'Project deadline tomorrow - action required'
        email.received_at = datetime.now() - timedelta(hours=2)
        
        # First calculation (cache miss)
        score1 = engine.get_current_score(email)
        assert isinstance(score1, float)
        assert 0 <= score1 <= 100
        
        # Second calculation (cache hit)
        score2 = engine.get_current_score(email)
        assert score1 == score2
        
        # Force recalculation
        score3 = engine.get_current_score(email, bypass_cache=True)
        assert isinstance(score3, float)
        
        # Verify performance stats
        stats = engine.get_performance_stats()
        assert stats['total_score_requests'] == 3
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 2
    
    def test_aging_email_score_changes(self):
        """Test that email scores change appropriately as they age."""
        config = TestingScoringConfig()
        engine = ScoringEngineFactory.create_engine(
            config,
            strategy_type="enhanced",
            cache_type="null"  # Disable caching to see real changes
        )
        
        # Create a promotional email
        email = Mock(spec=Email)
        email.id = 'aging-test-email'
        email.category = 'promotions'
        email.is_read = False
        email.labels = []
        email.from_email = 'sales@store.com'
        email.subject = '50% off sale - limited time!'
        
        # Test score at different ages
        fresh_time = datetime.now()
        email.received_at = fresh_time
        fresh_score = engine.get_current_score(email, fresh_time)
        
        # Score after 1 day
        day_old_time = fresh_time + timedelta(days=1)
        day_old_score = engine.get_current_score(email, day_old_time)
        
        # Score after 1 week
        week_old_time = fresh_time + timedelta(days=7)
        week_old_score = engine.get_current_score(email, week_old_time)
        
        # Promotional emails should decay rapidly
        assert fresh_score > day_old_score > week_old_score
        assert week_old_score < fresh_score * 0.5  # Should lose at least 50% after a week


if __name__ == "__main__":
    pytest.main([__file__, "-v"])