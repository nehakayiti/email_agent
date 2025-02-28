from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional, Tuple, Set
import logging
from google.auth.transport.requests import Request
import time
import random

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

def sync_gmail_changes(
    credentials: Dict[str, Any],
    last_history_id: str
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, List[str]], str]:
    """
    Sync Gmail changes using the history API. This function retrieves new emails,
    identifies deleted emails, and tracks label changes since the last sync.
    
    Args:
        credentials: Dictionary containing OAuth credentials.
        last_history_id: The last recorded history ID from your previous sync.
    
    Returns:
        Tuple (new_emails, deleted_email_ids, label_changes, new_history_id)
        - new_emails: A list of detailed new email data
        - deleted_email_ids: A list of Gmail message IDs that have been deleted
        - label_changes: A dict with message_id keys and lists of modified labels
        - new_history_id: The latest history ID for the next sync
    """
    # Create the Gmail service
    service = create_gmail_service(credentials)
    
    new_email_ids = set()
    deleted_email_ids = set()
    label_changes = {}  # track label changes by message ID
    history_events = []
    new_history_id = last_history_id
    page_token = None

    logger.info(f"[GMAIL] Starting sync with history ID: {last_history_id}")

    # Set up the parameters for the history call
    # historyTypes values: messageAdded, messageDeleted, labelAdded, labelRemoved
    params = {
        'userId': 'me',
        'startHistoryId': last_history_id,
        'historyTypes': ['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved']
    }
    
    # Loop through history pages
    try:
        # Use exponential backoff for rate limiting
        max_retries = 5
        base_delay = 1  # initial backoff of 1 second
        
        while True:
            if page_token:
                params['pageToken'] = page_token
            
            # Try the API call with exponential backoff
            for retry in range(max_retries):
                try:
                    logger.debug(f"[GMAIL] Calling history.list with params: {params}")
                    response = service.users().history().list(**params).execute()
                    break  # Success, exit retry loop
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check if this is a rate limit error (429)
                    if "Resource has been exhausted" in error_msg or "rate limit" in error_msg.lower():
                        if retry < max_retries - 1:
                            delay = base_delay * (2 ** retry) + random.uniform(0, 1)
                            logger.warning(f"[GMAIL] Rate limit hit, retrying in {delay:.2f} seconds (attempt {retry+1}/{max_retries})")
                            time.sleep(delay)
                        else:
                            logger.error(f"[GMAIL] Rate limit persisted after {max_retries} retries")
                            raise
                    else:
                        # Not a rate limit error, handle specific errors
                        if "historyTypes" in error_msg:
                            logger.error("[GMAIL] The historyTypes parameter contains invalid values")
                        elif "Invalid startHistoryId" in error_msg:
                            logger.error("[GMAIL] The startHistoryId is invalid or too old. Need full sync.")
                        elif "Invalid Credentials" in error_msg:
                            logger.error("[GMAIL] The credentials are invalid or expired")
                        raise
            
            # Update the new_history_id with the latest value
            if 'historyId' in response:
                new_history_id = response['historyId']
                logger.debug(f"[GMAIL] Updated history ID to {new_history_id}")
            
            current_history_events = response.get('history', [])
            history_events.extend(current_history_events)
            page_token = response.get('nextPageToken')
            
            logger.info(f"[GMAIL] Retrieved {len(current_history_events)} history events, total: {len(history_events)}")
            
            if not page_token:
                logger.debug("[GMAIL] No more pages to retrieve")
                break

        logger.info(f"[GMAIL] Processing {len(history_events)} history events")
        
        # Process each history event
        event_counts = {"messageAdded": 0, "messageDeleted": 0, "labelAdded": 0, "labelRemoved": 0}
        
        # Debug information: log some sample history events for debugging
        if history_events:
            sample_size = min(2, len(history_events))
            for i in range(sample_size):
                logger.debug(f"[GMAIL] Sample history event {i+1}: {history_events[i]}")
        
        for event in history_events:
            # Track messageAdded events (new emails)
            if 'messagesAdded' in event:  # Note: the API actually uses 'messagesAdded', not 'messageAdded'
                for msg_added in event.get('messagesAdded', []):
                    msg_id = msg_added['message']['id']
                    
                    # Check if this is a new message in the INBOX or other relevant label
                    # Messages with CHAT, DRAFT, SENT labels should be ignored as they're not new incoming emails
                    message_labels = set(msg_added['message'].get('labelIds', []))
                    system_labels = {'CHAT', 'DRAFT', 'SENT'}
                    
                    # Only consider it a new email if it's not a chat, draft, or sent message
                    # or if it explicitly has the INBOX label
                    if 'INBOX' in message_labels or not message_labels.intersection(system_labels):
                        new_email_ids.add(msg_id)
                        event_counts["messageAdded"] += 1
                        logger.debug(f"[GMAIL] New message detected: {msg_id} with labels: {message_labels}")
            
            # Also check 'messages' field which might contain added messages
            if 'messages' in event:
                for message in event.get('messages', []):
                    msg_id = message['id']
                    # We'll process these messages later to see if they're actually new
                    # (Gmail API sometimes includes messages here that should be considered)
                    new_email_ids.add(msg_id)
                    event_counts["messageAdded"] += 1
                    logger.debug(f"[GMAIL] Potential new message from 'messages' field: {msg_id}")
            
            # Track messageDeleted events
            if 'messagesDeleted' in event:  # Note: the API uses 'messagesDeleted', not 'messageDeleted'
                for msg_deleted in event.get('messagesDeleted', []):
                    msg_id = msg_deleted['message']['id']
                    deleted_email_ids.add(msg_id)
                    event_counts["messageDeleted"] += 1
                    logger.debug(f"[GMAIL] Deleted message detected: {msg_id}")
            
            # Track labelAdded events (includes emails moved to Trash)
            if 'labelsAdded' in event:  # Note: the API uses 'labelsAdded', not 'labelAdded'
                for label_event in event.get('labelsAdded', []):
                    msg_id = label_event['message']['id']
                    label_ids = label_event.get('labelIds', [])
                    
                    # If TRASH label was added, count as deleted
                    if 'TRASH' in label_ids:
                        deleted_email_ids.add(msg_id)
                        logger.debug(f"[GMAIL] Message {msg_id} moved to TRASH")
                    
                    # Track all label changes
                    if msg_id not in label_changes:
                        label_changes[msg_id] = {'added': [], 'removed': []}
                    label_changes[msg_id]['added'].extend(label_ids)
                    
                    event_counts["labelAdded"] += 1
                    logger.debug(f"[GMAIL] Labels added to message {msg_id}: {label_ids}")
            
            # Track labelRemoved events
            if 'labelsRemoved' in event:  # Note: the API uses 'labelsRemoved', not 'labelRemoved'
                for label_event in event.get('labelsRemoved', []):
                    msg_id = label_event['message']['id']
                    label_ids = label_event.get('labelIds', [])
                    
                    # Track all label changes
                    if msg_id not in label_changes:
                        label_changes[msg_id] = {'added': [], 'removed': []}
                    label_changes[msg_id]['removed'].extend(label_ids)
                    
                    event_counts["labelRemoved"] += 1
                    logger.debug(f"[GMAIL] Labels removed from message {msg_id}: {label_ids}")
        
        logger.info(f"[GMAIL] Processed events: {event_counts}")
        
        # Remove any new emails that were also deleted
        overlap_count = len(new_email_ids.intersection(deleted_email_ids))
        new_email_ids.difference_update(deleted_email_ids)
        
        logger.info(f"[GMAIL] Found {len(new_email_ids)} new emails and {len(deleted_email_ids)} deleted emails (overlap: {overlap_count})")
        logger.info(f"[GMAIL] Found {len(label_changes)} emails with label changes")
        
        # Fetch detailed data for new emails in batches
        new_emails = []
        if new_email_ids:
            new_email_ids_list = list(new_email_ids)
            batch_size = 10  # Smaller batch size to avoid rate limits
            
            for i in range(0, len(new_email_ids_list), batch_size):
                batch_ids = new_email_ids_list[i:i + batch_size]
                logger.info(f"[GMAIL] Processing batch {i//batch_size + 1}/{(len(new_email_ids_list) + batch_size - 1)//batch_size} of new emails")
                
                batch_emails = []
                retry_ids = []
                
                def new_email_callback(request_id, response, exception):
                    if exception:
                        logger.warning(f"[GMAIL] Error fetching email {request_id}: {exception}")
                        # Add to retry list if rate limited
                        if "Resource has been exhausted" in str(exception):
                            retry_ids.append(request_id)
                    else:
                        batch_emails.append(process_message_data(response))
                
                batch_request = service.new_batch_http_request(callback=new_email_callback)
                
                # Add each message to the batch with its ID as the request_id
                for msg_id in batch_ids:
                    batch_request.add(
                        service.users().messages().get(userId='me', id=msg_id, format='full'),
                        request_id=msg_id
                    )
                
                try:
                    batch_request.execute()
                    
                    # Handle rate-limited messages with exponential backoff
                    if retry_ids:
                        for backoff in range(1, max_retries + 1):
                            if not retry_ids:
                                break
                                
                            delay = base_delay * (2 ** (backoff - 1))
                            logger.warning(f"[GMAIL] Rate limited, retrying {len(retry_ids)} messages with {delay}s delay (attempt {backoff}/{max_retries})")
                            time.sleep(delay)
                            
                            # Create a new batch for retries
                            current_retry_ids = retry_ids.copy()
                            retry_ids = []
                            retry_batch = service.new_batch_http_request(callback=new_email_callback)
                            
                            for msg_id in current_retry_ids:
                                retry_batch.add(
                                    service.users().messages().get(userId='me', id=msg_id, format='full'),
                                    request_id=msg_id
                                )
                            
                            try:
                                retry_batch.execute()
                            except Exception as e:
                                logger.error(f"[GMAIL] Retry batch failed: {e}")
                    
                    # Add processed emails to the result list
                    new_emails.extend(batch_emails)
                    logger.info(f"[GMAIL] Successfully processed {len(batch_emails)} emails in batch")
                    
                    # Pause between batches to avoid rate limits
                    time.sleep(2)
                except Exception as e:
                    logger.error(f"[GMAIL] Batch retrieval error: {e}")
        
        logger.info(f"[GMAIL] Sync completed successfully. New emails: {len(new_emails)}, Deleted emails: {len(deleted_email_ids)}, Label changes: {len(label_changes)}, New history ID: {new_history_id}")
        return new_emails, list(deleted_email_ids), label_changes, new_history_id
        
    except Exception as e:
        logger.error(f"[GMAIL] Unexpected error in sync_gmail_changes: {str(e)}", exc_info=True)
        return [], [], {}, last_history_id

def process_message_data(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a raw Gmail message into a structured email data dictionary
    
    Args:
        msg: Raw Gmail message data
        
    Returns:
        Structured email data dictionary
    """
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
    
    return email_data

def fetch_emails_from_gmail(
    credentials: Dict[str, Any], 
    max_results: int = 100, 
    query: str = None,
    reference_email_id: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail API with detailed information
    
    This function can work in two modes:
    1. If reference_email_id is provided, it will use the history API to efficiently fetch only new emails
    2. Otherwise, it will use the traditional list/get approach with the provided query
    
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
        
        # If we have a reference email ID, try to use historyId for more efficient fetching
        if reference_email_id:
            try:
                history_id = get_message_history_id(service, reference_email_id)
                if history_id:
                    logger.info(f"[GMAIL] Using historyId {history_id} from reference email {reference_email_id}")
                    
                    # Use the sync_gmail_changes function to efficiently fetch only new emails
                    new_emails, deleted_ids, label_changes, new_history_id = sync_gmail_changes(credentials, history_id)
                    
                    if new_emails:
                        logger.info(f"[GMAIL] Found {len(new_emails)} new emails using history API")
                        return new_emails
                    else:
                        logger.info(f"[GMAIL] No new emails found using history API")
                        return []
                else:
                    logger.warning(f"[GMAIL] Could not get historyId for reference email {reference_email_id}")
                    # Fall back to traditional approach
            except Exception as e:
                logger.warning(f"[GMAIL] Error using history API: {str(e)}")
                # Fall back to traditional approach
        
        # Traditional approach using list/get
        logger.info(f"[GMAIL] Using traditional list/get approach with params: maxResults={max_results}, query='{query}'")
        
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
            # Gmail requires certain escaping for special characters in time-based queries
            # Replace spaces with actual space characters to ensure proper formatting
            query = query.replace(" ", " ")
            params['q'] = query
            logger.info(f"[GMAIL] Using formatted query: '{query}'")
        
        # Fetch email list with metadata
        try:
            logger.info(f"[GMAIL] Executing messages.list with params: {params}")
            results = service.users().messages().list(**params).execute()
            
            messages = results.get('messages', [])
            message_count = len(messages)
            logger.info(f"[GMAIL] Found {message_count} messages matching query")
            
            if message_count == 0:
                # When no emails are found, log more details to help diagnose issues
                if query:
                    logger.info(f"[GMAIL] No messages found for query: '{query}'. This could mean no new emails or the query may need adjustment.")
                    
                    # Try a simpler query to see if there are any emails at all
                    try:
                        # Get a small sample with just INBOX label to check if API is working 
                        test_params = {
                            'userId': 'me',
                            'maxResults': 5,
                            'labelIds': ['INBOX']
                        }
                        test_results = service.users().messages().list(**test_params).execute()
                        test_count = len(test_results.get('messages', []))
                        
                        if test_count > 0:
                            logger.info(f"[GMAIL] Test query returned {test_count} messages, suggesting the original query may be too restrictive.")
                        else:
                            logger.info("[GMAIL] Test query also returned no results. Inbox may be empty or there may be access issues.")
                    except Exception as test_e:
                        logger.warning(f"[GMAIL] Error running test query: {str(test_e)}")
                else:
                    logger.info("[GMAIL] No messages found with default INBOX label.")
                
                return []
        except Exception as e:
            logger.error(f"[GMAIL] Error listing messages: {str(e)}")
            return []
        
        emails = []
        logger.info(f"[GMAIL] Fetching detailed data for {message_count} messages")
        
        # Process in batches to avoid rate limits
        batch_size = 25
        for i in range(0, message_count, batch_size):
            batch = messages[i:i+batch_size]
            logger.info(f"[GMAIL] Processing batch {i//batch_size + 1}/{(message_count + batch_size - 1)//batch_size}")
            
            batch_emails = []
            
            def message_callback(request_id, response, exception):
                if exception:
                    logger.warning(f"[GMAIL] Error fetching message: {exception}")
                else:
                    # Skip reference email if provided
                    if reference_email_id and response['id'] == reference_email_id:
                        return
                    
                    batch_emails.append(process_message_data(response))
            
            batch_request = service.new_batch_http_request(callback=message_callback)
            
            for message in batch:
                message_id = message['id']
                batch_request.add(
                    service.users().messages().get(
                        userId='me',
                        id=message_id,
                        format='full'
                    )
                )
            
            try:
                batch_request.execute()
                emails.extend(batch_emails)
                # Add a small delay between batches to avoid rate limits
                time.sleep(1)
            except Exception as batch_error:
                logger.error(f"[GMAIL] Batch request error: {str(batch_error)}")
                # Continue with the next batch
        
        logger.info(f"[GMAIL] Successfully fetched {len(emails)} emails")
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
        
        # Execute the modification with retry logic for rate limiting
        max_retries = 5
        base_delay = 1  # Initial delay in seconds
        
        for retry in range(max_retries):
            try:
                result = service.users().messages().modify(
                    userId='me',
                    id=gmail_id,
                    body=body
                ).execute()
                
                logger.info(f"[GMAIL] Labels updated successfully for message {gmail_id}")
                return result
            
            except Exception as e:
                error_msg = str(e)
                
                # Check if this is a rate limit error
                if "Resource has been exhausted" in error_msg or "rate limit" in error_msg.lower():
                    if retry < max_retries - 1:
                        delay = base_delay * (2 ** retry) + random.uniform(0, 1)
                        logger.warning(f"[GMAIL] Rate limit hit, retrying in {delay:.2f} seconds (attempt {retry+1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        logger.error(f"[GMAIL] Rate limit persisted after {max_retries} retries")
                        raise
                else:
                    # Not a rate limit error
                    logger.error(f"[GMAIL] Error updating labels for message {gmail_id}: {error_msg}", exc_info=True)
                    raise
        
    except Exception as e:
        logger.error(f"[GMAIL] Error updating labels for message {gmail_id}: {str(e)}", exc_info=True)
        raise

def check_deleted_emails(
    credentials: Dict[str, Any],
    gmail_ids: List[str],
    force_full_check: bool = False
) -> Dict[str, bool]:
    """
    Check which emails have been deleted in Gmail.
    
    When force_full_check is False (default), this function will only check a small 
    sample of emails to verify if we need to do a full scan, which helps avoid rate limiting.
    
    Args:
        credentials: User's OAuth credentials dictionary
        gmail_ids: List of Gmail message IDs to check
        force_full_check: If True, always check all emails regardless of count
        
    Returns:
        Dictionary mapping Gmail IDs to boolean (True if deleted)
    """
    if not gmail_ids:
        return {}
        
    try:
        # If we have many emails to check, sample a few first to see if we need a full check
        sample_size = 5
        if len(gmail_ids) > 20 and not force_full_check:
            logger.info(f"[GMAIL] Large number of emails ({len(gmail_ids)}), checking sample of {sample_size} first")
            
            # Take a sample from different parts of the list
            sample_indices = [
                0,  # First email
                len(gmail_ids) // 4,  
                len(gmail_ids) // 2,  # Middle email
                (3 * len(gmail_ids)) // 4,
                len(gmail_ids) - 1  # Last email
            ]
            sample_ids = [gmail_ids[i] for i in sample_indices if i < len(gmail_ids)][:sample_size]
            
            # Check the sample
            sample_results = _check_deleted_emails_batch(credentials, sample_ids)
            
            # If no deletions in sample, assume no deletions in full list
            if not any(sample_results.values()):
                logger.info(f"[GMAIL] No deletions found in sample, skipping full check of {len(gmail_ids)} emails")
                return {gmail_id: False for gmail_id in gmail_ids}
            
            logger.info(f"[GMAIL] Deletions found in sample, proceeding with full check")
        
        return _check_deleted_emails_batch(credentials, gmail_ids)
    
    except Exception as e:
        logger.error(f"[GMAIL] Error in check_deleted_emails: {str(e)}", exc_info=True)
        # Return all as not deleted in case of error
        return {gmail_id: False for gmail_id in gmail_ids}

def _check_deleted_emails_batch(
    credentials: Dict[str, Any],
    gmail_ids: List[str]
) -> Dict[str, bool]:
    """
    Implementation of batch deletion checking with retry logic and rate limit handling.
    """
    logger.info(f"[GMAIL] Checking deleted status for {len(gmail_ids)} messages")
    service = create_gmail_service(credentials)
    
    deleted_status = {gmail_id: False for gmail_id in gmail_ids}
    batch_size = 20  # Smaller batch size to reduce rate limiting
    
    # Rate limiting parameters
    max_retries = 5
    base_delay = 1  # Initial backoff delay in seconds
    
    for i in range(0, len(gmail_ids), batch_size):
        batch = gmail_ids[i:i+batch_size]
        logger.info(f"[GMAIL] Processing batch {i//batch_size + 1}/{(len(gmail_ids) + batch_size - 1)//batch_size}")
        
        # Create a batch request
        batch_request = service.new_batch_http_request()
        retry_ids = []
        
        # Add each message to the batch
        def create_callback(msg_id):
            def callback(request_id, response, exception):
                if exception:
                    error_message = str(exception).lower()
                    if 'not found' in error_message or '404' in error_message:
                        logger.info(f"[GMAIL] Message {msg_id} was deleted in Gmail")
                        deleted_status[msg_id] = True
                    elif 'resource has been exhausted' in error_message:
                        # Rate limited, add to retry list
                        retry_ids.append(msg_id)
                    else:
                        logger.warning(f"[GMAIL] Error checking message {msg_id}: {str(exception)}")
            return callback
        
        for gmail_id in batch:
            batch_request.add(
                service.users().messages().get(userId='me', id=gmail_id, format='minimal'),
                callback=create_callback(gmail_id),
                request_id=gmail_id
            )
        
        try:
            batch_request.execute()
            
            # Handle rate-limited messages with exponential backoff
            if retry_ids:
                for backoff in range(1, max_retries + 1):
                    if not retry_ids:
                        break
                    
                    delay = base_delay * (2 ** (backoff - 1))
                    logger.warning(f"[GMAIL] Rate limited, retrying {len(retry_ids)} messages with {delay}s delay (attempt {backoff}/{max_retries})")
                    time.sleep(delay)
                    
                    # Create a new batch for retries
                    current_retry_ids = retry_ids.copy()
                    retry_ids = []
                    retry_batch = service.new_batch_http_request()
                    
                    for msg_id in current_retry_ids:
                        retry_batch.add(
                            service.users().messages().get(userId='me', id=msg_id, format='minimal'),
                            callback=create_callback(msg_id),
                            request_id=msg_id
                        )
                    
                    try:
                        retry_batch.execute()
                    except Exception as e:
                        logger.error(f"[GMAIL] Retry batch failed: {e}")
        
        except Exception as e:
            logger.error(f"[GMAIL] Batch request error: {str(e)}")
        
        # Add a longer delay between batches to avoid rate limits
        time.sleep(2)
    
    deleted_count = sum(deleted_status.values())
    logger.info(f"[GMAIL] Found {deleted_count} deleted messages out of {len(gmail_ids)}")
    return deleted_status 

def setup_push_notifications(
    credentials: Dict[str, Any],
    webhook_url: str,
    topic_name: str = None
) -> Dict[str, Any]:
    """
    Set up Gmail push notifications to a webhook endpoint.
    
    This allows Gmail to notify your application in real-time when new emails arrive,
    which is more efficient than polling for changes.
    
    Args:
        credentials: Dictionary containing OAuth credentials
        webhook_url: HTTPS URL that will receive the notifications
        topic_name: Optional topic name (defaults to "gmail_<random>")
        
    Returns:
        Dictionary with setup information including expiration
    """
    try:
        logger.info(f"[GMAIL] Setting up push notifications to webhook: {webhook_url}")
        service = create_gmail_service(credentials)
        
        # Create a unique topic name if not provided
        if not topic_name:
            # Create a unique ID based on timestamp and random number
            unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
            topic_name = f"gmail_{unique_id}"
        
        # Set up the watch request
        watch_request = {
            'topicName': topic_name,
            'labelIds': ['INBOX'],  # Watch for changes to INBOX
            'labelFilterAction': 'include'  # Only include specified labels
        }
        
        # Execute the watch request
        watch_response = service.users().watch(
            userId='me',
            body=watch_request
        ).execute()
        
        logger.info(f"[GMAIL] Successfully set up push notifications: {watch_response}")
        
        # Add webhook URL to the response
        watch_response['webhook_url'] = webhook_url
        watch_response['topic_name'] = topic_name
        
        return watch_response
        
    except Exception as e:
        logger.error(f"[GMAIL] Error setting up push notifications: {str(e)}", exc_info=True)
        raise

def stop_push_notifications(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stop Gmail push notifications that were previously set up.
    
    Args:
        credentials: Dictionary containing OAuth credentials
        
    Returns:
        Success status
    """
    try:
        logger.info(f"[GMAIL] Stopping push notifications")
        service = create_gmail_service(credentials)
        
        # Execute the stop command
        service.users().stop(userId='me').execute()
        
        logger.info(f"[GMAIL] Successfully stopped push notifications")
        
        return {
            "status": "success",
            "message": "Push notifications stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"[GMAIL] Error stopping push notifications: {str(e)}", exc_info=True)
        raise

def get_gmail_profile(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get Gmail profile information which includes account details and metadata.
    
    Args:
        credentials: Dictionary containing OAuth credentials
        
    Returns:
        Dictionary with Gmail profile information
    """
    try:
        logger.info(f"[GMAIL] Retrieving Gmail profile information")
        service = create_gmail_service(credentials)
        
        # Get the profile data
        profile = service.users().getProfile(userId='me').execute()
        
        logger.info(f"[GMAIL] Successfully retrieved profile: {profile}")
        
        return profile
        
    except Exception as e:
        logger.error(f"[GMAIL] Error retrieving Gmail profile: {str(e)}", exc_info=True)
        raise 