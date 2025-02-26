from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
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

def get_message_history_id(service, message_id: str) -> Optional[str]:
    """
    Get the historyId of a specific message
    
    Args:
        service: Gmail API service instance
        message_id: Gmail message ID
        
    Returns:
        historyId as string or None if not found
    """
    try:
        # Get minimal message data to extract historyId
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='minimal'
        ).execute()
        
        return message.get('historyId')
    except Exception as e:
        logger.error(f"[GMAIL] Error getting historyId for message {message_id}: {str(e)}")
        return None

def fetch_emails_from_gmail(
    credentials: Dict[str, Any], 
    max_results: int = 100, 
    query: str = None,
    reference_email_id: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail API with detailed information
    
    Args:
        credentials: User's OAuth credentials dictionary
        max_results: Maximum number of emails to fetch
        query: Optional Gmail search query (e.g., "after:2023/01/01")
        reference_email_id: Optional reference email ID to fetch only newer emails
        
    Returns:
        List of email dictionaries containing metadata and content
    """
    try:
        logger.info(f"[GMAIL] Creating Gmail service with credentials")
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
        
        # If we have a reference email ID, try to use historyId for more efficient fetching
        if reference_email_id:
            history_id = get_message_history_id(service, reference_email_id)
            if history_id:
                logger.info(f"[GMAIL] Using historyId {history_id} from reference email {reference_email_id}")
                # We'll use this to sort and filter results later
                reference_history_id = int(history_id)
            else:
                logger.warning(f"[GMAIL] Could not get historyId for reference email {reference_email_id}")
                reference_history_id = None
        else:
            reference_history_id = None
            
        logger.info(f"[GMAIL] Fetching emails with params: maxResults={max_results}, query='{query}', reference_email={reference_email_id}")
        
        # Fetch email list with metadata
        results = service.users().messages().list(**params).execute()
        
        messages = results.get('messages', [])
        message_count = len(messages)
        logger.info(f"[GMAIL] Found {message_count} messages matching query")
        
        if message_count == 0:
            logger.info("[GMAIL] No messages found, returning empty list")
            return []
        
        emails = []
        logger.info(f"[GMAIL] Fetching detailed data for {message_count} messages")
        
        # Track how many messages we're skipping due to historyId
        skipped_count = 0
        
        for i, message in enumerate(messages):
            message_id = message['id']
            
            # Skip processing if this is the reference email
            if reference_email_id and message_id == reference_email_id:
                logger.debug(f"[GMAIL] Skipping reference email: {message_id}")
                skipped_count += 1
                continue
                
            # Fetch detailed message data
            msg = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # If we have a reference history ID, check if this message is newer
            if reference_history_id:
                msg_history_id = int(msg.get('historyId', 0))
                if msg_history_id <= reference_history_id:
                    logger.debug(f"[GMAIL] Skipping message {message_id} with older historyId {msg_history_id} <= {reference_history_id}")
                    skipped_count += 1
                    continue
            
            logger.info(f"[GMAIL] Processing message {i+1-skipped_count}/{message_count-skipped_count}: ID={message_id}")
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Parse the date with timezone information preserved
            try:
                received_date = parsedate_to_datetime(date_str)
                # Ensure timezone info is present
                if received_date.tzinfo is None:
                    received_date = received_date.replace(tzinfo=timezone.utc)
                # Format as ISO string with timezone
                received_iso = received_date.isoformat()
            except Exception as e:
                logger.warning(f"[GMAIL] Error parsing date '{date_str}': {str(e)}")
                # Fallback to current time if date parsing fails
                received_iso = datetime.now(timezone.utc).isoformat()
            
            logger.debug(f"[GMAIL] Message {message_id}: Subject='{subject[:30]}...', From={from_email}, Date={received_iso}")
            
            # Process email data
            email_data = {
                'gmail_id': msg['id'],
                'thread_id': msg['threadId'],
                'subject': subject,
                'from_email': from_email,
                'received_at': received_iso,
                'snippet': msg.get('snippet', ''),
                'labels': msg.get('labelIds', []),
                'is_read': 'UNREAD' not in msg.get('labelIds', []),
                'raw_data': msg  # Store full message data for processing
            }
            
            emails.append(email_data)
            
        logger.info(f"[GMAIL] Successfully fetched {len(emails)} emails (skipped {skipped_count} based on reference)")
        return emails
        
    except Exception as e:
        logger.error(f"[GMAIL] Error fetching emails: {str(e)}", exc_info=True)
        raise 