"""
Tests for Flow Buckets Service

This module tests the pure functions for classifying emails into flow buckets
and querying emails by bucket type. Tests cover classification logic,
query composition, and edge cases.
"""

import pytest
from unittest.mock import Mock, MagicMock
from app.services.flow_buckets import (
    classify_bucket,
    classify_bucket_from_score,
    query_bucket_emails,
    get_bucket_counts,
    get_bucket_summary
)


class TestBucketClassification:
    """Test bucket classification logic."""
    
    def test_classify_bucket_now(self):
        """Test classification of high priority emails to NOW bucket."""
        # Create mock email with high attention score
        email = Mock()
        email.attention_score = 75.0
        
        result = classify_bucket(email)
        assert result == "now"
    
    def test_classify_bucket_later(self):
        """Test classification of medium priority emails to LATER bucket."""
        # Create mock email with medium attention score
        email = Mock()
        email.attention_score = 45.0
        
        result = classify_bucket(email)
        assert result == "later"
    
    def test_classify_bucket_reference(self):
        """Test classification of low priority emails to REFERENCE bucket."""
        # Create mock email with low attention score
        email = Mock()
        email.attention_score = 15.0
        
        result = classify_bucket(email)
        assert result == "reference"
    
    def test_classify_bucket_boundary_conditions(self):
        """Test boundary conditions for bucket classification."""
        # Test exact boundary values
        test_cases = [
            (100.0, "now"),    # Maximum score
            (60.0, "now"),     # NOW boundary (inclusive)
            (59.9, "later"),   # Just below NOW boundary
            (30.0, "later"),   # LATER boundary (inclusive)
            (29.9, "reference"), # Just below LATER boundary
            (0.0, "reference") # Minimum score
        ]
        
        for score, expected_bucket in test_cases:
            email = Mock()
            email.attention_score = score
            result = classify_bucket(email)
            assert result == expected_bucket, f"Score {score} should be in '{expected_bucket}' bucket"
    
    def test_classify_bucket_from_score(self):
        """Test bucket classification using score directly."""
        assert classify_bucket_from_score(85.0) == "now"
        assert classify_bucket_from_score(45.0) == "later"
        assert classify_bucket_from_score(10.0) == "reference"
        assert classify_bucket_from_score(60.0) == "now"  # Boundary
        assert classify_bucket_from_score(30.0) == "later"  # Boundary


class TestQueryBucketEmails:
    """Test database query functions for bucket emails."""
    
    def test_query_bucket_emails_now(self):
        """Test querying NOW bucket emails."""
        # Mock session and query chain
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        
        # Mock email results
        mock_emails = [Mock(), Mock(), Mock()]
        query_mock.all.return_value = mock_emails
        
        result = query_bucket_emails(session, user_id=1, bucket="now", limit=10, offset=0)
        
        # Verify query was constructed correctly
        session.query.assert_called_once()
        query_mock.filter.assert_called_once()
        query_mock.order_by.assert_called_once()
        query_mock.offset.assert_called_once_with(0)
        query_mock.limit.assert_called_once_with(10)
        query_mock.all.assert_called_once()
        
        assert result == mock_emails
    
    def test_query_bucket_emails_later(self):
        """Test querying LATER bucket emails."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        
        result = query_bucket_emails(session, user_id=1, bucket="later")
        
        # Verify function completes without error
        assert isinstance(result, list)
    
    def test_query_bucket_emails_reference(self):
        """Test querying REFERENCE bucket emails."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        
        result = query_bucket_emails(session, user_id=1, bucket="reference")
        
        # Verify function completes without error
        assert isinstance(result, list)
    
    def test_query_bucket_emails_pagination(self):
        """Test pagination parameters."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        
        # Test custom pagination
        query_bucket_emails(session, user_id=1, bucket="now", limit=25, offset=50)
        
        query_mock.offset.assert_called_with(50)
        query_mock.limit.assert_called_with(25)
    
    def test_query_bucket_emails_ordering(self):
        """Test different ordering options."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.order_by.return_value = query_mock
        query_mock.offset.return_value = query_mock
        query_mock.limit.return_value = query_mock
        query_mock.all.return_value = []
        
        # Test different order_by values
        test_orders = ["attention_score", "date", "subject", "invalid_field"]
        
        for order in test_orders:
            query_bucket_emails(session, user_id=1, bucket="now", order_by=order)
            # Each call should result in order_by being called
            assert query_mock.order_by.called


class TestBucketCounts:
    """Test bucket counting functions."""
    
    def test_get_bucket_counts(self):
        """Test getting bucket counts for a user."""
        # Mock session with different count results for each bucket
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        
        # Mock count results for each bucket query
        count_results = [5, 12, 45]  # now, later, reference
        query_mock.count.side_effect = count_results
        
        result = get_bucket_counts(session, user_id=1)
        
        # Verify all three bucket queries were made
        assert query_mock.count.call_count == 3
        
        # Verify correct counts returned
        expected = {"now": 5, "later": 12, "reference": 45}
        assert result == expected
    
    def test_get_bucket_counts_empty(self):
        """Test bucket counts when user has no emails."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 0
        
        result = get_bucket_counts(session, user_id=1)
        
        expected = {"now": 0, "later": 0, "reference": 0}
        assert result == expected
    
    def test_get_bucket_summary(self):
        """Test comprehensive bucket summary."""
        # Mock get_bucket_counts function behavior
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        
        # Mock count results: 10 now, 20 later, 70 reference = 100 total
        count_results = [10, 20, 70]
        query_mock.count.side_effect = count_results
        
        result = get_bucket_summary(session, user_id=1)
        
        # Verify structure and calculations
        assert "buckets" in result
        assert "percentages" in result
        assert "total_emails" in result
        assert "classification_rules" in result
        
        # Verify bucket counts
        assert result["buckets"]["now"] == 10
        assert result["buckets"]["later"] == 20
        assert result["buckets"]["reference"] == 70
        
        # Verify total
        assert result["total_emails"] == 100
        
        # Verify percentages (should be 10%, 20%, 70%)
        assert result["percentages"]["now"] == 10.0
        assert result["percentages"]["later"] == 20.0
        assert result["percentages"]["reference"] == 70.0
        
        # Verify classification rules are present
        assert "now" in result["classification_rules"]
        assert "later" in result["classification_rules"]
        assert "reference" in result["classification_rules"]
    
    def test_get_bucket_summary_empty(self):
        """Test bucket summary when user has no emails."""
        session = Mock()
        query_mock = Mock()
        session.query.return_value = query_mock
        query_mock.filter.return_value = query_mock
        query_mock.count.return_value = 0
        
        result = get_bucket_summary(session, user_id=1)
        
        # Should handle division by zero gracefully
        assert result["total_emails"] == 0
        assert result["percentages"]["now"] == 0.0
        assert result["percentages"]["later"] == 0.0
        assert result["percentages"]["reference"] == 0.0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_negative_attention_score(self):
        """Test handling of negative attention scores."""
        email = Mock()
        email.attention_score = -10.0
        
        # Should classify as reference (lowest bucket)
        result = classify_bucket(email)
        assert result == "reference"
    
    def test_very_high_attention_score(self):
        """Test handling of attention scores above 100."""
        email = Mock()
        email.attention_score = 150.0
        
        # Should classify as now (highest bucket)
        result = classify_bucket(email)
        assert result == "now"
    
    def test_zero_attention_score(self):
        """Test handling of zero attention score."""
        email = Mock()
        email.attention_score = 0.0
        
        result = classify_bucket(email)
        assert result == "reference"
    
    def test_float_precision_boundaries(self):
        """Test handling of floating point precision at boundaries."""
        # Test values very close to boundaries
        test_cases = [
            (59.999999, "later"),
            (60.000001, "now"),
            (29.999999, "reference"),
            (30.000001, "later")
        ]
        
        for score, expected_bucket in test_cases:
            email = Mock()
            email.attention_score = score
            result = classify_bucket(email)
            assert result == expected_bucket, f"Score {score} should be in '{expected_bucket}' bucket"