#!/usr/bin/env python3
"""
Gmail Test Data Seeder

This script creates deterministic test emails in the test Gmail account
for integration testing purposes. It uses the Gmail API to create emails
with specific subjects, bodies, senders, and labels.

Usage:
    python backend/scripts/seed_test_gmail.py
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.gmail import create_gmail_service

# Load test environment variables
load_dotenv(dotenv_path='backend/.env.test')

# Test email data - deterministic for consistent testing
TEST_EMAILS = [
    {
        "subject": "Test Newsletter - Tech Updates",
        "body": "This is a test newsletter about the latest technology updates. It should be categorized as a newsletter.",
        "from_email": "newsletter@techmeme.com",
        "labels": ["INBOX"],
        "category": "Newsletters"
    },
    {
        "subject": "Important Meeting Tomorrow",
        "body": "Hi, we have an important meeting scheduled for tomorrow at 2 PM. Please prepare your presentation.",
        "from_email": "boss@company.com",
        "labels": ["INBOX"],
        "category": "Important"
    },
    {
        "subject": "Your Order #12345 has shipped",
        "body": "Great news! Your order has been shipped and is on its way. Track your package here.",
        "from_email": "orders@amazon.com",
        "labels": ["INBOX"],
        "category": "Promotions"
    },
    {
        "subject": "Social Media Update",
        "body": "You have 5 new notifications on your social media account. Check them out!",
        "from_email": "notifications@facebook.com",
        "labels": ["INBOX"],
        "category": "Social"
    },
    {
        "subject": "Spam Test Email",
        "body": "CONGRATULATIONS! You've won a million dollars! Click here to claim your prize!",
        "from_email": "spam@fakewebsite.com",
        "labels": ["INBOX"],
        "category": "Spam"
    }
]

def create_message(to: str, subject: str, message_text: str, from_email: str) -> str:
    """
    Create a base64url encoded email message for Gmail API.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = from_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw

def create_test_email(gmail_service, email_data: Dict[str, Any]) -> str:
    """
    Create a test email in Gmail using the Gmail API.
    Args:
        gmail_service: Initialized Gmail service
        email_data: Dictionary containing email details
    Returns:
        The Gmail message ID of the created email
    """
    # Create the email message
    message = {
        'raw': create_message(
            to="me",  # Send to self
            subject=email_data["subject"],
            message_text=email_data["body"],
            from_email=email_data["from_email"]
        )
    }
    
    # Insert the message into Gmail
    try:
        result = gmail_service.users().messages().insert(
            userId='me',
            body=message
        ).execute()
        # Add labels if needed
        if email_data.get("labels"):
            gmail_service.users().messages().modify(
                userId='me',
                id=result['id'],
                body={"addLabelIds": email_data["labels"]}
            ).execute()
        print(f"Created email: {email_data['subject']} (ID: {result['id']})")
        return result['id']
    except Exception as e:
        print(f"Error creating email '{email_data['subject']}': {e}")
        return None

def seed_test_gmail():
    """
    Seed the test Gmail account with deterministic test emails.
    """
    print("Starting Gmail test data seeding...")
    
    # Check if required environment variables are set
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set these variables in your .env.test file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    # Get Google credentials from environment
    credentials = Credentials(
        token=os.environ.get("GOOGLE_ACCESS_TOKEN"),
        refresh_token=os.environ.get("GOOGLE_REFRESH_TOKEN"),
        token_uri=os.environ.get("GOOGLE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        client_id=os.environ.get("GOOGLE_CLIENT_ID"),
        client_secret=os.environ.get("GOOGLE_CLIENT_SECRET")
    )
    
    # Initialize Gmail service
    try:
        gmail_service = create_gmail_service({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret
        })
        print("Gmail service initialized successfully")
    except Exception as e:
        print(f"Error initializing Gmail service: {e}")
        return False
    
    # Create test emails
    created_emails = []
    for email_data in TEST_EMAILS:
        message_id = create_test_email(gmail_service, email_data)
        if message_id:
            created_emails.append({
                "message_id": message_id,
                "subject": email_data["subject"],
                "category": email_data["category"]
            })
    
    print(f"\nSeeding complete! Created {len(created_emails)} test emails:")
    for email in created_emails:
        print(f"  - {email['subject']} ({email['category']})")
    
    # Save the created email IDs for test reference
    with open("backend/tests/test_email_ids.json", "w") as f:
        json.dump(created_emails, f, indent=2)
    
    print(f"\nTest email IDs saved to backend/tests/test_email_ids.json")
    return True

if __name__ == "__main__":
    success = seed_test_gmail()
    sys.exit(0 if success else 1)
