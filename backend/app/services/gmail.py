from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional
import logging
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

def create_gmail_service(credentials_dict: Dict[str, Any]):
    """
    Create Gmail API service instance from stored credentials
    
    Args:
        credentials_dict: Dictionary containing OAuth2 credentials
        
    Returns:
        Gmail API service instance
    """
    try:
        # Create credentials without specifying scopes - use the ones from the token
        credentials = Credentials(
            token=credentials_dict['token'],
            refresh_token=credentials_dict['refresh_token'],
            token_uri=credentials_dict['token_uri'],
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret']
        )
        
        # Proactively refresh the token if it's expired
        if credentials.expired:
            logger.info("[GMAIL] Credentials expired, refreshing token")
            credentials.refresh(Request())
            
            # Update the token in the credentials_dict for future use
            credentials_dict['token'] = credentials.token
        
        return build('gmail', 'v1', credentials=credentials, cache_discovery=False)
    except Exception as e:
        logger.error(f"[GMAIL] Error creating Gmail service: {str(e)}", exc_info=True)
        raise

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
            'maxResults': max_results
        }
        
        # Only add labelIds if we're not using a specific query
        # This allows more flexibility in custom queries
        if not query:
            params['labelIds'] = ['INBOX']
        
        # Add query if provided
        if query:
            params['q'] = query
        
        # If we have a reference email ID, try to use historyId for more efficient fetching
        reference_history_id = None
        if reference_email_id:
            try:
                history_id = get_message_history_id(service, reference_email_id)
                if history_id:
                    logger.info(f"[GMAIL] Using historyId {history_id} from reference email {reference_email_id}")
                    # We'll use this to sort and filter results later
                    reference_history_id = int(history_id)
                else:
                    logger.warning(f"[GMAIL] Could not get historyId for reference email {reference_email_id}")
            except Exception as e:
                logger.warning(f"[GMAIL] Error getting historyId: {str(e)}")
                # Continue without historyId
            
        logger.info(f"[GMAIL] Fetching emails with params: maxResults={max_results}, query='{query}', reference_email={reference_email_id}")
        
        # Fetch email list with metadata
        try:
            results = service.users().messages().list(**params).execute()
            
            messages = results.get('messages', [])
            message_count = len(messages)
            logger.info(f"[GMAIL] Found {message_count} messages matching query")
            
            if message_count == 0:
                logger.info("[GMAIL] No messages found, returning empty list")
                return []
        except Exception as e:
            logger.error(f"[GMAIL] Error listing messages: {str(e)}")
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
            
            try:    
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
            except Exception as msg_error:
                logger.error(f"[GMAIL] Error processing message {message_id}: {str(msg_error)}")
                # Continue with the next message
            
        logger.info(f"[GMAIL] Successfully fetched {len(emails)} emails (skipped {skipped_count} based on reference)")
        return emails
        
    except Exception as e:
        logger.error(f"[GMAIL] Error fetching emails: {str(e)}", exc_info=True)
        raise

def update_email_labels(
    credentials: Dict[str, Any],
    gmail_id: str,
    add_labels: List[str] = None,
    remove_labels: List[str] = None
) -> Dict[str, Any]:
    """
    Update the labels of an email in Gmail
    
    Args:
        credentials: User's OAuth credentials dictionary
        gmail_id: Gmail message ID
        add_labels: List of labels to add
        remove_labels: List of labels to remove
        
    Returns:
        Updated message data
    """
    try:
        logger.info(f"[GMAIL] Updating labels for message {gmail_id}")
        service = create_gmail_service(credentials)
        
        # Prepare the label modification request
        body = {}
        if add_labels:
            body['addLabelIds'] = add_labels
            logger.info(f"[GMAIL] Adding labels: {add_labels}")
        
        if remove_labels:
            body['removeLabelIds'] = remove_labels
            logger.info(f"[GMAIL] Removing labels: {remove_labels}")
        
        # Execute the modification
        result = service.users().messages().modify(
            userId='me',
            id=gmail_id,
            body=body
        ).execute()
        
        logger.info(f"[GMAIL] Labels updated successfully for message {gmail_id}")
        return result
        
    except Exception as e:
        logger.error(f"[GMAIL] Error updating labels for message {gmail_id}: {str(e)}", exc_info=True)
        raise

def check_deleted_emails(
    credentials: Dict[str, Any],
    gmail_ids: List[str]
) -> Dict[str, bool]:
    """
    Check which emails have been deleted in Gmail using batch requests
    
    Args:
        credentials: User's OAuth credentials dictionary
        gmail_ids: List of Gmail message IDs to check
        
    Returns:
        Dictionary mapping Gmail IDs to boolean (True if deleted)
    """
    try:
        logger.info(f"[GMAIL] Checking deleted status for {len(gmail_ids)} messages")
        service = create_gmail_service(credentials)
        
        deleted_status = {gmail_id: False for gmail_id in gmail_ids}
        batch_size = 50  # Process in batches to avoid API limits
        
        # If batch requests fail, fall back to individual requests
        use_batch = True
        
        # Try with batch requests first
        if use_batch:
            try:
                # Create a batch request object
                from googleapiclient.http import BatchHttpRequest
                
                for i in range(0, len(gmail_ids), batch_size):
                    batch = gmail_ids[i:i+batch_size]
                    logger.info(f"[GMAIL] Processing batch {i//batch_size + 1}/{(len(gmail_ids) + batch_size - 1)//batch_size}")
                    
                    # Create a new batch request for each group
                    batch_request = service.new_batch_http_request()
                    
                    # Define callback function for each response
                    def create_callback(msg_id):
                        def callback(request_id, response, exception):
                            if exception:
                                error_message = str(exception).lower()
                                if 'not found' in error_message or '404' in error_message:
                                    logger.info(f"[GMAIL] Message {msg_id} was deleted in Gmail")
                                    deleted_status[msg_id] = True
                                else:
                                    logger.warning(f"[GMAIL] Error checking message {msg_id}: {str(exception)}")
                            # If no exception, message exists (not deleted)
                        return callback
                    
                    # Add each message to the batch request
                    for gmail_id in batch:
                        batch_request.add(
                            service.users().messages().get(userId='me', id=gmail_id, format='minimal'),
                            callback=create_callback(gmail_id)
                        )
                    
                    # Execute the batch request
                    try:
                        batch_request.execute()
                    except Exception as batch_error:
                        logger.error(f"[GMAIL] Batch request error: {str(batch_error)}")
                        # If batch request fails, fall back to individual requests
                        use_batch = False
                        break
                
                # If we successfully processed all batches, return the results
                if use_batch:
                    deleted_count = sum(deleted_status.values())
                    logger.info(f"[GMAIL] Found {deleted_count} deleted messages out of {len(gmail_ids)}")
                    return deleted_status
            
            except Exception as e:
                logger.error(f"[GMAIL] Error with batch requests: {str(e)}")
                use_batch = False
        
        # Fall back to individual requests if batch requests failed
        if not use_batch:
            logger.info(f"[GMAIL] Falling back to individual requests for {len(gmail_ids)} messages")
            
            # Reset deleted_status
            deleted_status = {gmail_id: False for gmail_id in gmail_ids}
            
            # Process in smaller batches for individual requests
            smaller_batch_size = 20
            
            for i in range(0, len(gmail_ids), smaller_batch_size):
                batch = gmail_ids[i:i+smaller_batch_size]
                logger.info(f"[GMAIL] Processing individual batch {i//smaller_batch_size + 1}/{(len(gmail_ids) + smaller_batch_size - 1)//smaller_batch_size}")
                
                for gmail_id in batch:
                    try:
                        # Try to get the message
                        service.users().messages().get(
                            userId='me',
                            id=gmail_id,
                            format='minimal'
                        ).execute()
                        
                        # If we get here, the message exists
                        deleted_status[gmail_id] = False
                        
                    except Exception as e:
                        # Check if this is a "not found" error (message was deleted)
                        error_message = str(e).lower()
                        if 'not found' in error_message or '404' in error_message:
                            logger.info(f"[GMAIL] Message {gmail_id} was deleted in Gmail")
                            deleted_status[gmail_id] = True
                        else:
                            # Some other error occurred
                            logger.warning(f"[GMAIL] Error checking message {gmail_id}: {str(e)}")
                            # Keep as False for non-404 errors
        
        deleted_count = sum(deleted_status.values())
        logger.info(f"[GMAIL] Found {deleted_count} deleted messages out of {len(gmail_ids)}")
        return deleted_status
        
    except Exception as e:
        logger.error(f"[GMAIL] Error checking deleted emails: {str(e)}", exc_info=True)
        raise 