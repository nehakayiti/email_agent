"""
Tests for attention scoring service.
"""

import pytest
from app.services.attention_scoring import (
    calculate_attention_score,
    calculate_attention_score_from_data,
    get_attention_level,
    get_attention_color
)
from app.models.email import Email


class TestAttentionScoring:
    """Test cases for attention scoring functionality."""

    def test_base_score(self):
        """Test that base score is 50.0 for read emails with no special labels."""
        email = Email(is_read=True, labels=[])
        score = calculate_attention_score(email)
        assert score == 50.0

    def test_unread_bonus(self):
        """Test that unread emails get +15 bonus."""
        email = Email(is_read=False, labels=[])
        score = calculate_attention_score(email)
        assert score == 65.0  # 50 + 15

    def test_important_label_bonus(self):
        """Test that IMPORTANT label adds +30 points."""
        email = Email(is_read=True, labels=['IMPORTANT'])
        score = calculate_attention_score(email)
        assert score == 80.0  # 50 + 30

    def test_starred_label_bonus(self):
        """Test that STARRED label adds +20 points."""
        email = Email(is_read=True, labels=['STARRED'])
        score = calculate_attention_score(email)
        assert score == 70.0  # 50 + 20

    def test_multiple_labels(self):
        """Test that multiple labels stack correctly."""
        email = Email(is_read=True, labels=['IMPORTANT', 'STARRED'])
        score = calculate_attention_score(email)
        assert score == 100.0  # 50 + 30 + 20

    def test_unread_with_labels(self):
        """Test combination of unread status and labels."""
        email = Email(is_read=False, labels=['IMPORTANT'])
        score = calculate_attention_score(email)
        assert score == 95.0  # 50 + 15 + 30

    def test_maximum_score(self):
        """Test that score is clamped to maximum of 100.0."""
        email = Email(is_read=False, labels=['IMPORTANT', 'STARRED', 'URGENT'])
        score = calculate_attention_score(email)
        assert score == 100.0  # Clamped to max

    def test_none_labels(self):
        """Test handling of None labels."""
        email = Email(is_read=True, labels=None)
        score = calculate_attention_score(email)
        assert score == 50.0  # Base score only

    def test_empty_labels(self):
        """Test handling of empty labels list."""
        email = Email(is_read=True, labels=[])
        score = calculate_attention_score(email)
        assert score == 50.0  # Base score only

    def test_case_insensitive_labels(self):
        """Test that label matching is case-sensitive (IMPORTANT vs important)."""
        email = Email(is_read=True, labels=['important'])  # lowercase
        score = calculate_attention_score(email)
        assert score == 50.0  # No bonus for lowercase

        email = Email(is_read=True, labels=['IMPORTANT'])  # uppercase
        score = calculate_attention_score(email)
        assert score == 80.0  # Bonus for uppercase

    def test_partial_label_match(self):
        """Test that partial label matches don't trigger bonuses."""
        email = Email(is_read=True, labels=['IMPORTANT_MEETING'])
        score = calculate_attention_score(email)
        assert score == 50.0  # No bonus for partial match


class TestAttentionScoringFromData:
    """Test cases for calculate_attention_score_from_data function."""

    def test_from_data_base_score(self):
        """Test base score calculation from raw data."""
        score = calculate_attention_score_from_data(is_read=True, labels=[])
        assert score == 50.0

    def test_from_data_unread(self):
        """Test unread bonus from raw data."""
        score = calculate_attention_score_from_data(is_read=False, labels=[])
        assert score == 65.0

    def test_from_data_with_labels(self):
        """Test label bonuses from raw data."""
        score = calculate_attention_score_from_data(
            is_read=True, 
            labels=['IMPORTANT', 'STARRED']
        )
        assert score == 100.0

    def test_from_data_none_labels(self):
        """Test handling of None labels in data function."""
        score = calculate_attention_score_from_data(is_read=True, labels=None)
        assert score == 50.0

    def test_from_data_defaults(self):
        """Test default parameter values."""
        score = calculate_attention_score_from_data()  # No parameters
        assert score == 65.0  # Default is_read=False, labels=None


class TestAttentionLevel:
    """Test cases for get_attention_level function."""

    def test_critical_level(self):
        """Test critical attention level (80.0+)."""
        assert get_attention_level(80.0) == 'Critical'
        assert get_attention_level(95.0) == 'Critical'
        assert get_attention_level(100.0) == 'Critical'

    def test_high_level(self):
        """Test high attention level (60.0-79.9)."""
        assert get_attention_level(60.0) == 'High'
        assert get_attention_level(70.0) == 'High'
        assert get_attention_level(79.9) == 'High'

    def test_medium_level(self):
        """Test medium attention level (30.0-59.9)."""
        assert get_attention_level(30.0) == 'Medium'
        assert get_attention_level(45.0) == 'Medium'
        assert get_attention_level(59.9) == 'Medium'

    def test_low_level(self):
        """Test low attention level (0.0-29.9)."""
        assert get_attention_level(0.0) == 'Low'
        assert get_attention_level(15.0) == 'Low'
        assert get_attention_level(29.9) == 'Low'

    def test_boundary_values(self):
        """Test boundary values between levels."""
        assert get_attention_level(79.9) == 'High'
        assert get_attention_level(80.0) == 'Critical'
        assert get_attention_level(59.9) == 'Medium'
        assert get_attention_level(60.0) == 'High'
        assert get_attention_level(29.9) == 'Low'
        assert get_attention_level(30.0) == 'Medium'


class TestAttentionColor:
    """Test cases for get_attention_color function."""

    def test_red_color(self):
        """Test red color for high attention (80.0+)."""
        assert get_attention_color(80.0) == 'red'
        assert get_attention_color(95.0) == 'red'
        assert get_attention_color(100.0) == 'red'

    def test_orange_color(self):
        """Test orange color for medium-high attention (60.0-79.9)."""
        assert get_attention_color(60.0) == 'orange'
        assert get_attention_color(70.0) == 'orange'
        assert get_attention_color(79.9) == 'orange'

    def test_yellow_color(self):
        """Test yellow color for medium attention (30.0-59.9)."""
        assert get_attention_color(30.0) == 'yellow'
        assert get_attention_color(45.0) == 'yellow'
        assert get_attention_color(59.9) == 'yellow'

    def test_green_color(self):
        """Test green color for low attention (0.0-29.9)."""
        assert get_attention_color(0.0) == 'green'
        assert get_attention_color(15.0) == 'green'
        assert get_attention_color(29.9) == 'green'


class TestIntegrationWithEmailModel:
    """Test integration with actual Email model instances."""

    def test_with_real_email_model(self, db_session, test_user_with_credentials):
        """Test scoring with actual Email model instance."""
        email = Email(
            user_id=test_user_with_credentials.id,
            gmail_id="test_gmail_id_scoring",
            thread_id="test_thread_id_scoring",
            subject="Test Scoring Email",
            from_email="test@example.com",
            is_read=False,
            labels=['IMPORTANT']
        )
        
        score = calculate_attention_score(email)
        assert score == 95.0  # 50 + 15 + 30
        
        level = get_attention_level(score)
        assert level == 'Critical'
        
        color = get_attention_color(score)
        assert color == 'red'

    def test_score_consistency(self):
        """Test that same email properties always produce same score."""
        email1 = Email(is_read=False, labels=['IMPORTANT'])
        email2 = Email(is_read=False, labels=['IMPORTANT'])
        
        score1 = calculate_attention_score(email1)
        score2 = calculate_attention_score(email2)
        
        assert score1 == score2
        assert score1 == 95.0

    def test_deterministic_scoring(self):
        """Test that scoring is deterministic (no randomness)."""
        email = Email(is_read=True, labels=['STARRED'])
        
        # Run multiple times to ensure consistency
        scores = [calculate_attention_score(email) for _ in range(10)]
        
        # All scores should be identical
        assert len(set(scores)) == 1
        assert scores[0] == 70.0 