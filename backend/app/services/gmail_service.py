"""
Gmail Service - Pure Gmail API interaction logic

This service contains only the logic for interacting with the Gmail API.
It has no knowledge of our database models or business logic.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
from google.auth.transport.requests import Request
import time
import random
import hashlib

logger = logging.getLogger(__name__)

# Cache for Gmail service instances to reduce credential refreshes
# Format: {credentials_hash: (service, expiry_time)}
_service_cache = {}
# Service cache TTL (in seconds)
SERVICE_CACHE_TTL = 300  # 5 minutes

def _hash_credentials(credentials_dict: Dict[str, Any]) -> str:
    """Create a hash of credentials for caching purposes"""
    # Only use the refresh_token, client_id and client_secret for the hash
    # since the access token changes after refresh
    key_parts = [
        credentials_dict.get('refresh_token', '') or '',
        credentials_dict.get('client_id', '') or '',
        credentials_dict.get('client_secret', '') or ''
    ]
    hash_input = '|'.join(key_parts)
    return hashlib.md5(hash_input.encode()).hexdigest()

def create_gmail_service(credentials_dict: Dict[str, Any], on_credentials_refresh: Optional[callable] = None):
    """
    Create a Gmail service with automatic token refresh and caching.
    
    Args:
        credentials_dict: Dictionary containing OAuth credentials
        on_credentials_refresh: Optional callback function called when credentials are refreshed
                               Should accept the updated credentials_dict as parameter
    """
    try:
        now = datetime.now()
        creds_hash = _hash_credentials(credentials_dict)
        
        # Check cache first
        if creds_hash in _service_cache:
            cached_service, expiry_time = _service_cache[creds_hash]
            if now < expiry_time:
                logger.debug("[GMAIL] Using cached Gmail service")
                return cached_service
            else:
                # Remove expired cache entry
                del _service_cache[creds_hash]
        
        # Create credentials object
        credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret')
        )
        
        # Refresh token if needed
        if credentials.expired and credentials.refresh_token:
            logger.info("[GMAIL] Refreshing expired credentials")
            credentials.refresh(Request())
            
            # Update the credentials dictionary with new token
            updated_credentials = credentials_dict.copy()
            updated_credentials['token'] = credentials.token
            
            # Call the refresh callback if provided
            if on_credentials_refresh:
                try:
                    on_credentials_refresh(updated_credentials)
                except Exception as e:
                    logger.error(f"[GMAIL] Error in credentials refresh callback: {str(e)}")
        
        # Create the service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Cache the service
        expiry_time = now + timedelta(seconds=SERVICE_CACHE_TTL)
        _service_cache[creds_hash] = (service, expiry_time)
        
        logger.debug("[GMAIL] Created new Gmail service")
        return service
        
    except Exception as e:
        logger.error(f"[GMAIL] Error creating Gmail service: {str(e)}")
        raise

async def get_gmail_service(credentials_dict: Dict[str, Any], on_credentials_refresh: Optional[callable] = None):
    """
    Async wrapper for create_gmail_service.
    Creates a Gmail API service instance from stored credentials.
    
    Args:
        credentials_dict: Dictionary containing OAuth credentials
        on_credentials_refresh: Optional callback function called when credentials are refreshed
    """
    return create_gmail_service(credentials_dict, on_credentials_refresh)

def get_gmail_profile(credentials: Dict[str, Any], on_credentials_refresh: Optional[callable] = None) -> Dict[str, Any]:
    """
    Get Gmail user profile information
    
    Args:
        credentials: User's Gmail credentials
        on_credentials_refresh: Optional callback for credential refresh
        
    Returns:
        Dictionary with profile information
    """
    try:
        service = create_gmail_service(credentials, on_credentials_refresh)
        profile = service.users().getProfile(userId='me').execute()
        return profile
    except Exception as e:
        logger.error(f"[GMAIL] Error getting profile: {str(e)}")
        raise

async def fetch_history_changes(service, history_id: str, max_pages: int = 5) -> Dict[str, Any]:
    """
    Fetch changes from Gmail using the history API
    
    Args:
        service: Gmail API service instance
        history_id: History ID to start from
        max_pages: Maximum number of pages to fetch
        
    Returns:
        Dictionary with new_history_id, new_emails, deleted_ids, and label_changes
    """
    if not history_id:
        logger.warning("[GMAIL] No history ID provided, cannot fetch changes")
        return {
            "new_history_id": None,
            "new_emails": [],
            "deleted_ids": [],
            "label_changes": {}
        }
    
    logger.info(f"[GMAIL] Fetching history changes since history ID: {history_id}")
    
    try:
        # Initialize result containers
        new_emails = []
        deleted_ids = []
        label_changes = {}
        new_history_id = None
        
        # Fetch history list
        page_token = None
        pages_fetched = 0
        
        while pages_fetched < max_pages:
            pages_fetched += 1
            
            # Make the API request
            request = service.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved'],
                pageToken=page_token
            )
            
            history_response = request.execute()
            
            # Get the new history ID
            if 'historyId' in history_response:
                new_history_id = history_response['historyId']
            
            # Process history entries
            history_entries = history_response.get('history', [])
            logger.info(f"[GMAIL] Found {len(history_entries)} history entries on page {pages_fetched}")
            
            for entry in history_entries:
                # Process message additions
                for added in entry.get('messagesAdded', []):
                    message = added.get('message', {})
                    gmail_id = message.get('id')
                    
                    if gmail_id:
                        # Fetch the full message
                        try:
                            message_data = service.users().messages().get(
                                userId='me', 
                                id=gmail_id, 
                                format='full'
                            ).execute()
                            
                            # Process the message data
                            email_data = process_message_data(message_data)
                            new_emails.append(email_data)
                            logger.debug(f"[GMAIL] Added new email: {gmail_id}")
                        except Exception as e:
                            logger.error(f"[GMAIL] Error fetching added message {gmail_id}: {str(e)}")
                
                # Process message deletions
                for deleted in entry.get('messagesDeleted', []):
                    message = deleted.get('message', {})
                    gmail_id = message.get('id')
                    
                    if gmail_id and gmail_id not in deleted_ids:
                        deleted_ids.append(gmail_id)
                        logger.debug(f"[GMAIL] Marked email as deleted: {gmail_id}")
                
                # Process label additions
                for added in entry.get('labelsAdded', []):
                    message = added.get('message', {})
                    gmail_id = message.get('id')
                    label_ids = added.get('labelIds', [])
                    
                    if gmail_id and label_ids:
                        if gmail_id not in label_changes:
                            label_changes[gmail_id] = {'added': [], 'removed': []}
                        
                        for label in label_ids:
                            if label not in label_changes[gmail_id]['added']:
                                label_changes[gmail_id]['added'].append(label)
                                logger.debug(f"[GMAIL] Added label {label} to email {gmail_id}")
                
                # Process label removals
                for removed in entry.get('labelsRemoved', []):
                    message = removed.get('message', {})
                    gmail_id = message.get('id')
                    label_ids = removed.get('labelIds', [])
                    
                    if gmail_id and label_ids:
                        if gmail_id not in label_changes:
                            label_changes[gmail_id] = {'added': [], 'removed': []}
                        
                        for label in label_ids:
                            if label not in label_changes[gmail_id]['removed']:
                                label_changes[gmail_id]['removed'].append(label)
                                logger.debug(f"[GMAIL] Removed label {label} from email {gmail_id}")
            
            # Check if there are more pages
            page_token = history_response.get('nextPageToken')
            if not page_token:
                break
            
            # Sleep briefly between pages to avoid rate limits
            time.sleep(0.5)
        
        # Log summary
        logger.info(f"[GMAIL] History changes summary:")
        logger.info(f"  - New history ID: {new_history_id}")
        logger.info(f"  - New emails: {len(new_emails)}")
        logger.info(f"  - Deleted emails: {len(deleted_ids)}")
        logger.info(f"  - Emails with label changes: {len(label_changes)}")
        
        return {
            "new_history_id": new_history_id,
            "new_emails": new_emails,
            "deleted_ids": deleted_ids,
            "label_changes": label_changes
        }
    
    except HttpError as e:
        logger.error(f"[GMAIL] HttpError fetching history changes: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"[GMAIL] Error fetching history changes: {str(e)}", exc_info=True)
        raise

def process_message_data(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process raw Gmail message data into our standardized format
    
    Args:
        msg: Raw Gmail message data
        
    Returns:
        Processed email data dictionary
    """
    gmail_id = msg.get('id')
    thread_id = msg.get('threadId')
    
    # Extract headers
    headers = msg.get('payload', {}).get('headers', [])
    header_dict = {h['name'].lower(): h['value'] for h in headers}
    
    # Extract basic fields
    subject = header_dict.get('subject', 'No Subject')
    from_email = header_dict.get('from', '')
    date_str = header_dict.get('date', '')
    
    # Parse date
    received_at = None
    if date_str:
        try:
            received_at = parsedate_to_datetime(date_str)
            if received_at.tzinfo is None:
                received_at = received_at.replace(tzinfo=timezone.utc)
        except Exception as e:
            logger.warning(f"[GMAIL] Error parsing date '{date_str}' for email {gmail_id}: {str(e)}")
            received_at = datetime.now(timezone.utc)
    else:
        received_at = datetime.now(timezone.utc)
    
    # Extract snippet
    snippet = msg.get('snippet', '')
    
    # Extract labels
    labels = msg.get('labelIds', [])
    
    # Determine read status
    is_read = 'UNREAD' not in labels
    
    # Extract body content (simplified - just get the first text part)
    body = ""
    try:
        payload = msg.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    body = part.get('body', {}).get('data', '')
                    if body:
                        import base64
                        body = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
                    break
        elif payload.get('mimeType') == 'text/plain':
            body = payload.get('body', {}).get('data', '')
            if body:
                import base64
                body = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
    except Exception as e:
        logger.warning(f"[GMAIL] Error extracting body for email {gmail_id}: {str(e)}")
    
    return {
        'gmail_id': gmail_id,
        'thread_id': thread_id,
        'subject': subject,
        'from_email': from_email,
        'received_at': received_at,
        'snippet': snippet,
        'labels': labels,
        'is_read': is_read,
        'body': body,
        'raw_data': msg  # Keep the full message for future processing
    }

async def fetch_emails_from_gmail(
    credentials: Dict[str, Any], 
    max_results: int = 100, 
    query: str = None,
    on_credentials_refresh: Optional[callable] = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail using the messages API
    
    Args:
        credentials: User's Gmail credentials
        max_results: Maximum number of emails to fetch
        query: Gmail search query (optional)
        on_credentials_refresh: Optional callback for credential refresh
        
    Returns:
        List of email data dictionaries
    """
    try:
        service = create_gmail_service(credentials, on_credentials_refresh)
        
        # Build the request
        request_params = {
            'userId': 'me',
            'maxResults': max_results
        }
        
        if query:
            request_params['q'] = query
        
        # Get message list
        messages_response = service.users().messages().list(**request_params).execute()
        messages = messages_response.get('messages', [])
        
        if not messages:
            logger.info("[GMAIL] No messages found")
            return []
        
        # Fetch full message details
        emails = []
        for message in messages:
            try:
                message_data = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = process_message_data(message_data)
                emails.append(email_data)
                
            except Exception as e:
                logger.error(f"[GMAIL] Error fetching message {message['id']}: {str(e)}")
                continue
        
        logger.info(f"[GMAIL] Fetched {len(emails)} emails from Gmail")
        return emails
        
    except Exception as e:
        logger.error(f"[GMAIL] Error fetching emails: {str(e)}")
        raise

def update_email_labels(
    credentials: Dict[str, Any],
    gmail_id: str,
    add_labels: List[str] = None,
    remove_labels: List[str] = None,
    on_credentials_refresh: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Update labels for a Gmail message
    
    Args:
        credentials: User's Gmail credentials
        gmail_id: Gmail message ID
        add_labels: Labels to add
        remove_labels: Labels to remove
        on_credentials_refresh: Optional callback for credential refresh
        
    Returns:
        Updated message data
    """
    try:
        service = create_gmail_service(credentials, on_credentials_refresh)
        
        # Prepare the request body
        body = {}
        if add_labels:
            body['addLabelIds'] = add_labels
        if remove_labels:
            body['removeLabelIds'] = remove_labels
        
        # Make the API call
        result = service.users().messages().modify(
            userId='me',
            id=gmail_id,
            body=body
        ).execute()
        
        logger.info(f"[GMAIL] Updated labels for email {gmail_id}")
        return result
        
    except Exception as e:
        logger.error(f"[GMAIL] Error updating labels for email {gmail_id}: {str(e)}")
        raise

def retry_with_backoff(func, max_retries=5, base_delay=1, jitter=True):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds
        jitter: Whether to add random jitter to delays
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    logger.error(f"[GMAIL] Max retries ({max_retries}) exceeded for {func.__name__}")
                    raise last_exception
                
                # Calculate delay with exponential backoff
                delay = base_delay * (2 ** attempt)
                if jitter:
                    delay += random.uniform(0, 0.1 * delay)
                
                logger.warning(f"[GMAIL] Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.2f}s: {str(e)}")
                time.sleep(delay)
        
        raise last_exception
    
    return wrapper 