import pytest
from datetime import datetime
from app.services.email_processor import categorize_email

def test_simple_newsletter_categorization(db, test_user):
    email_data = {
        'gmail_id': 'simple_gmail_id_001',
        'thread_id': 'simple_thread_id_001',
        'subject': 'Your Weekly Digest is Here!',
        'from_email': 'digest@nytimes.com',
        'received_at': datetime.utcnow(),
        'snippet': 'Check out the latest news and analysis in your weekly digest.',
        'labels': ['INBOX'],
        'is_read': False,
        'is_processed': False,
        'importance_score': 50,
        'raw_data': {},
    }
    expected_category = 'newsletters'
    result = categorize_email(email_data, db, test_user.id)
    assert result.lower() == expected_category, f"Expected '{expected_category}', got '{result}'" 