import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def create_message(sender, to, subject, message_text):
    """
    Create a message for the Gmail API.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """
    Send a message via the Gmail API.
    """
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        logger.info(f"Message Id: {message['id']} sent successfully.")
        return message
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

def get_gmail_service(credentials_dict):
    """
    Create a Gmail API service instance from stored credentials.
    Refreshes the token if needed.
    """
    credentials = Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret']
    )
    
    if credentials.expired:
        credentials.refresh(Request())
        credentials_dict['token'] = credentials.token # Update token in dict

    return build('gmail', 'v1', credentials=credentials, cache_discovery=False)

def seed_gmail_account(emails_to_send: list):
    """
    Seeds the Gmail account with a list of emails.
    """
    load_dotenv(dotenv_path='backend/.env.test')

    # These credentials should be for your TEST Gmail account
    test_client_id = os.getenv("GOOGLE_CLIENT_ID")
    test_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    test_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    test_refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN") # You'll need to get this once
    test_access_token = os.getenv("GOOGLE_ACCESS_TOKEN") # You'll need to get this once

    if not all([test_client_id, test_client_secret, test_redirect_uri, test_refresh_token, test_access_token]):
        logger.error("Missing test Gmail credentials in .env.test. Please ensure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_REFRESH_TOKEN, and GOOGLE_ACCESS_TOKEN are set.")
        print("\n--- ERROR: Missing test Gmail credentials. See logs for details. ---")
        return

    credentials_dict = {
        'token': test_access_token,
        'refresh_token': test_refresh_token,
        'token_uri': "https://oauth2.googleapis.com/token",
        'client_id': test_client_id,
        'client_secret': test_client_secret
    }

    try:
        service = get_gmail_service(credentials_dict)
        user_profile = service.users().getProfile(userId='me').execute()
        sender_email = user_profile['emailAddress']
        logger.info(f"Connected to Gmail account: {sender_email}")

        for email_data in emails_to_send:
            message = create_message(sender_email, email_data['to'], email_data['subject'], email_data['body'])
            send_message(service, 'me', message)
            
        print(f"\n--- Successfully sent {len(emails_to_send)} emails to {sender_email} ---")

    except Exception as e:
        logger.error(f"Error seeding Gmail account: {e}", exc_info=True)
        print(f"\n--- ERROR seeding Gmail account. See logs for details. ---")

if __name__ == "__main__":
    # Example usage:
    test_emails = [
        {'to': 'your_test_email@gmail.com', 'subject': 'Test Email 1 - Newsletter', 'body': 'This is a test newsletter email.'},
        {'to': 'your_test_email@gmail.com', 'subject': 'Test Email 2 - Promotion', 'body': 'This is a test promotion email with a discount.'},
        {'to': 'your_test_email@gmail.com', 'subject': 'Test Email 3 - Important', 'body': 'This is an important test email regarding your account.'},
    ]
    seed_gmail_account(test_emails)
