"""
Tests for Flow Buckets API

This module tests the REST API endpoints for flow bucket functionality.
Tests cover all endpoints with different scenarios and error conditions.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.email import Email


class TestFlowBucketsAPI:
    """Test flow buckets API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies."""
        
        # Mock database session
        mock_db = Mock()
        
        # Mock current user
        mock_user = Mock()
        mock_user.id = "test-user-id"
        
        # Override dependencies
        app.dependency_overrides[get_db] = lambda: mock_db
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        client = TestClient(app)
        yield client
        
        # Clean up
        app.dependency_overrides.clear()
    
    def test_get_now_bucket_emails(self, client):
        """Test getting NOW bucket emails."""
        # Mock email data
        mock_emails = [
            Mock(
                id="550e8400-e29b-41d4-a716-446655440001",  # Valid UUID
                gmail_id="gmail-1",
                subject="Urgent: Meeting Today",
                from_email="boss@company.com",
                received_at="2024-01-01T10:00:00Z",
                snippet="Important meeting today",
                labels=["IMPORTANT"],
                is_read=False,
                attention_score=85.0,
                category="Important"
            ),
            Mock(
                id="550e8400-e29b-41d4-a716-446655440002",  # Valid UUID 
                gmail_id="gmail-2",
                subject="High Priority Task",
                from_email="project@company.com",
                received_at="2024-01-01T09:00:00Z",
                snippet="Task needs attention",
                labels=["STARRED"],
                is_read=False,
                attention_score=75.0,
                category="Work"
            )
        ]
        
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.return_value = mock_emails
            
            response = client.get("/flow/buckets/now")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["subject"] == "Urgent: Meeting Today"
            assert data[0]["attention_score"] == 85.0
            assert data[1]["attention_score"] == 75.0
            
            # Verify service was called correctly
            mock_query.assert_called_once()
            call_args = mock_query.call_args
            assert call_args[1]["bucket"] == "now"
            assert call_args[1]["limit"] == 50  # default
            assert call_args[1]["offset"] == 0  # default
    
    def test_get_later_bucket_emails(self, client):
        """Test getting LATER bucket emails."""
        mock_emails = [
            Mock(
                id="550e8400-e29b-41d4-a716-446655440003",  # Valid UUID
                gmail_id="gmail-3", 
                subject="Newsletter Update",
                from_email="news@example.com",
                received_at="2024-01-01T08:00:00Z",
                snippet="Weekly newsletter",
                labels=[],
                is_read=False,
                attention_score=45.0,
                category="Newsletters"
            )
        ]
        
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.return_value = mock_emails
            
            response = client.get("/flow/buckets/later?limit=25&offset=10")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["attention_score"] == 45.0
            
            # Verify query parameters were passed
            call_args = mock_query.call_args
            assert call_args[1]["bucket"] == "later"
            assert call_args[1]["limit"] == 25
            assert call_args[1]["offset"] == 10
    
    def test_get_reference_bucket_emails(self, client):
        """Test getting REFERENCE bucket emails."""
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.return_value = []
            
            response = client.get("/flow/buckets/reference")
            
            assert response.status_code == 200
            data = response.json()
            assert data == []
            
            call_args = mock_query.call_args
            assert call_args[1]["bucket"] == "reference"
    
    def test_get_bucket_counts(self, client):
        """Test getting bucket counts."""
        mock_counts = {"now": 5, "later": 12, "reference": 45}
        
        with patch('app.routers.flow_buckets.get_bucket_counts') as mock_get_counts:
            mock_get_counts.return_value = mock_counts
            
            response = client.get("/flow/bucket-counts")
            
            assert response.status_code == 200
            data = response.json()
            assert data == mock_counts
            
            mock_get_counts.assert_called_once()
    
    def test_get_bucket_summary(self, client):
        """Test getting comprehensive bucket summary."""
        mock_summary = {
            "buckets": {"now": 10, "later": 20, "reference": 70},
            "percentages": {"now": 10.0, "later": 20.0, "reference": 70.0},
            "total_emails": 100,
            "classification_rules": {
                "now": "attention_score >= 60 (High priority)",
                "later": "30 <= attention_score < 60 (Medium priority)",
                "reference": "attention_score < 30 (Low priority)"
            }
        }
        
        with patch('app.routers.flow_buckets.get_bucket_summary') as mock_get_summary:
            mock_get_summary.return_value = mock_summary
            
            response = client.get("/flow/bucket-summary")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_emails"] == 100
            assert data["buckets"]["now"] == 10
            assert data["percentages"]["reference"] == 70.0
            assert "classification_rules" in data
    
    def test_get_bucket_emails_generic(self, client):
        """Test generic bucket endpoint with different bucket types."""
        mock_emails = []
        
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.return_value = mock_emails
            
            # Test each bucket type
            for bucket_type in ["now", "later", "reference"]:
                response = client.get(f"/flow/buckets/{bucket_type}")
                
                assert response.status_code == 200
                data = response.json()
                assert isinstance(data, list)
    
    def test_bucket_emails_with_custom_ordering(self, client):
        """Test bucket emails with different ordering options."""
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.return_value = []
            
            # Test different order_by values
            for order_by in ["attention_score", "date", "subject"]:
                response = client.get(f"/flow/buckets/now?order_by={order_by}")
                
                assert response.status_code == 200
                
                # Verify order_by was passed to service
                call_args = mock_query.call_args
                assert call_args[1]["order_by"] == order_by
    
    def test_bucket_emails_pagination_validation(self, client):
        """Test validation of pagination parameters."""
        # Test invalid limit (too high)
        response = client.get("/flow/buckets/now?limit=200")
        assert response.status_code == 422  # Validation error
        
        # Test invalid offset (negative)  
        response = client.get("/flow/buckets/now?offset=-1")
        assert response.status_code == 422  # Validation error
        
        # Test invalid limit (too low)
        response = client.get("/flow/buckets/now?limit=0")
        assert response.status_code == 422  # Validation error
    
    def test_service_error_handling(self, client):
        """Test API error handling when service throws exceptions."""
        with patch('app.routers.flow_buckets.query_bucket_emails') as mock_query:
            mock_query.side_effect = Exception("Database connection error")
            
            response = client.get("/flow/buckets/now")
            
            assert response.status_code == 500
            data = response.json()
            assert "Error retrieving NOW bucket emails" in data["detail"]
        
        with patch('app.routers.flow_buckets.get_bucket_counts') as mock_counts:
            mock_counts.side_effect = Exception("Database error")
            
            response = client.get("/flow/bucket-counts")
            
            assert response.status_code == 500
            data = response.json()
            assert "Error retrieving bucket counts" in data["detail"]
    
    def test_invalid_bucket_type(self, client):
        """Test handling of invalid bucket types."""
        response = client.get("/flow/buckets/invalid")
        
        # Should return 422 validation error for invalid bucket type
        assert response.status_code == 422


class TestEmailResponseModel:
    """Test the EmailResponse model serialization."""
    
    def test_email_response_from_orm(self):
        """Test conversion of Email model to EmailResponse."""
        from app.routers.flow_buckets import EmailResponse
        
        # Create a mock email that behaves like an ORM model
        mock_email = Mock()
        mock_email.id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID
        mock_email.gmail_id = "gmail-123"
        mock_email.subject = "Test Subject"
        mock_email.from_email = "test@example.com"
        mock_email.received_at = "2024-01-01T10:00:00Z"
        mock_email.snippet = "Test snippet"
        mock_email.labels = ["INBOX", "UNREAD"]
        mock_email.is_read = False
        mock_email.attention_score = 75.5
        mock_email.category = "Primary"
        
        # Test that EmailResponse can be created from the mock
        # Note: In a real test, you'd use actual ORM models
        response = EmailResponse(
            id=mock_email.id,
            gmail_id=mock_email.gmail_id,
            subject=mock_email.subject,
            from_email=mock_email.from_email,
            received_at=mock_email.received_at,
            snippet=mock_email.snippet,
            labels=mock_email.labels,
            is_read=mock_email.is_read,
            attention_score=mock_email.attention_score,
            category=mock_email.category
        )
        
        assert str(response.id) == "550e8400-e29b-41d4-a716-446655440000"
        assert response.attention_score == 75.5
        assert response.labels == ["INBOX", "UNREAD"]
        assert response.is_read is False


class TestBucketResponseModels:
    """Test bucket response models."""
    
    def test_bucket_counts_response_model(self):
        """Test BucketCountsResponse model."""
        from app.routers.flow_buckets import BucketCountsResponse
        
        response = BucketCountsResponse(now=5, later=12, reference=45)
        
        assert response.now == 5
        assert response.later == 12
        assert response.reference == 45
    
    def test_bucket_summary_response_model(self):
        """Test BucketSummaryResponse model."""
        from app.routers.flow_buckets import BucketSummaryResponse, BucketCountsResponse
        
        buckets = BucketCountsResponse(now=10, later=20, reference=70)
        percentages = {"now": 10.0, "later": 20.0, "reference": 70.0}
        rules = {
            "now": "High priority",
            "later": "Medium priority",
            "reference": "Low priority"
        }
        
        response = BucketSummaryResponse(
            buckets=buckets,
            percentages=percentages,
            total_emails=100,
            classification_rules=rules
        )
        
        assert response.total_emails == 100
        assert response.buckets.now == 10
        assert response.percentages["reference"] == 70.0
        assert "now" in response.classification_rules