from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def create_gmail_service(credentials_dict: Dict[str, Any]):
    """
    Create Gmail API service instance from stored credentials
    
    Args:
        credentials_dict: Dictionary containing OAuth2 credentials
        
    Returns:
        Gmail API service instance
    """
    credentials = Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret']
    )
    
    return build('gmail', 'v1', credentials=credentials)

def fetch_emails_from_gmail(credentials: Dict[str, Any], max_results: int = 100, query: str = None) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail API with detailed information
    
    Args:
        credentials: User's OAuth credentials dictionary
        max_results: Maximum number of emails to fetch
        query: Optional Gmail search query (e.g., "after:2023/01/01")
        
    Returns:
        List of email dictionaries containing metadata and content
    """
    try:
        service = create_gmail_service(credentials)
        
        # Prepare request parameters
        params = {
            'userId': 'me',
            'maxResults': max_results,
            'labelIds': ['INBOX']
        }
        
        # Add query if provided
        if query:
            params['q'] = query
        
        # Fetch email list with metadata
        results = service.users().messages().list(**params).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for message in messages:
            # Fetch detailed message data
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Process email data
            email_data = {
                'gmail_id': msg['id'],
                'thread_id': msg['threadId'],
                'subject': subject,
                'from_email': from_email,
                'received_at': date_str,
                'snippet': msg.get('snippet', ''),
                'labels': msg.get('labelIds', []),
                'is_read': 'UNREAD' not in msg.get('labelIds', []),
                'raw_data': msg  # Store full message data for processing
            }
            
            emails.append(email_data)
            
        return emails
        
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise 