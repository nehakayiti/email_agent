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

# Add this function for a more robust retry mechanism with exponential backoff
def retry_with_backoff(func, max_retries=5, base_delay=1, jitter=True):
    """
    Decorator for retrying a function with exponential backoff on specific exceptions.
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        jitter: Whether to add random jitter to the delay
        
    Returns:
        The decorated function
    """
    def wrapper(*args, **kwargs):
        retry_count = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                retry_count += 1
                
                # Check if this is a rate limit error (429) or a server error (5xx)
                is_rate_limit = "Resource has been exhausted" in error_msg or "rate limit" in error_msg.lower()
                is_server_error = "5" in error_msg[:3] if error_msg.isdigit() else False
                
                if (is_rate_limit or is_server_error) and retry_count < max_retries:
                    # Calculate delay with exponential backoff
                    delay = base_delay * (2 ** (retry_count - 1))
                    
                    # Add jitter to prevent thundering herd problem
                    if jitter:
                        delay += random.uniform(0, min(1, delay * 0.1))
                    
                    logger.warning(f"[GMAIL] Rate limit or server error, retrying in {delay:.2f} seconds (attempt {retry_count}/{max_retries})")
                    time.sleep(delay)
                else:
                    if retry_count >= max_retries:
                        logger.error(f"[GMAIL] Maximum retries ({max_retries}) exceeded")
                    raise
    
    return wrapper

# Update the sync_gmail_changes function to optimize the batching of requests
def sync_gmail_changes(
    credentials: Dict[str, Any],
    last_history_id: str
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, List[str]], str]:
    """
    Use Gmail's history API to efficiently sync changes since last_history_id
    
    Args:
        credentials: OAuth credentials dictionary
        last_history_id: Last history ID from previous sync
        
    Returns:
        Tuple of (new_emails, deleted_emails, label_changes, new_history_id)
    """
    service = create_gmail_service(credentials)
    
    new_emails = []
    deleted_message_ids = []
    label_changes = {}
    
    @retry_with_backoff
    def fetch_history_page(params):
        return service.users().history().list(userId='me', **params).execute()
    
    # Set up initial history request
    history_params = {
        'startHistoryId': last_history_id,
        'historyTypes': ['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved']
    }
    
    # Track total history items and messages
    total_history_events = 0
    page_number = 0
    new_history_id = None
    
    try:
        # Get history pages until no more available
        while True:
            page_number += 1
            logger.info(f"[GMAIL] Fetching history page {page_number} since history ID {last_history_id}")
            
            history_response = fetch_history_page(history_params)
            
            # Store the history ID (we'll use the most recent one)
            if 'historyId' in history_response:
                new_history_id = history_response['historyId']
            
            # Process history items
            if 'history' in history_response:
                history_items = history_response['history']
                total_history_events += len(history_items)
                logger.info(f"[GMAIL] Found {len(history_items)} history events on page {page_number}")
                
                # Track message IDs to avoid duplicates
                processed_messages = set()
                
                # Process each history item
                for item in history_items:
                    # Check for new messages
                    if 'messagesAdded' in item:
                        for message in item['messagesAdded']:
                            msg_data = message.get('message', {})
                            msg_id = msg_data.get('id')
                            
                            if msg_id and msg_id not in processed_messages:
                                processed_messages.add(msg_id)
                                
                                # Only process messages with INBOX label (unless you want all mail)
                                labels = msg_data.get('labelIds', [])
                                if 'INBOX' in labels and 'TRASH' not in labels and 'SPAM' not in labels:
                                    # Fetch full message details
                                    try:
                                        full_message = service.users().messages().get(
                                            userId='me', id=msg_id, format='full'
                                        ).execute()
                                        
                                        # Process message data
                                        email_data = process_message_data(full_message)
                                        if email_data:
                                            new_emails.append(email_data)
                                    except Exception as e:
                                        logger.error(f"[GMAIL] Error fetching new message {msg_id}: {str(e)}")
                    
                    # Check for deleted messages
                    if 'messagesDeleted' in item:
                        for message in item['messagesDeleted']:
                            msg_data = message.get('message', {})
                            msg_id = msg_data.get('id')
                            
                            if msg_id and msg_id not in deleted_message_ids:
                                deleted_message_ids.append(msg_id)
                    
                    # Track label changes (added)
                    if 'labelsAdded' in item:
                        for label_data in item['labelsAdded']:
                            msg_data = label_data.get('message', {})
                            msg_id = msg_data.get('id')
                            label_ids = label_data.get('labelIds', [])
                            
                            if msg_id and label_ids:
                                if msg_id not in label_changes:
                                    label_changes[msg_id] = {'added': [], 'removed': []}
                                
                                # Add the new labels
                                for label in label_ids:
                                    if label not in label_changes[msg_id]['added']:
                                        label_changes[msg_id]['added'].append(label)
                    
                    # Track label changes (removed)
                    if 'labelsRemoved' in item:
                        for label_data in item['labelsRemoved']:
                            msg_data = label_data.get('message', {})
                            msg_id = msg_data.get('id')
                            label_ids = label_data.get('labelIds', [])
                            
                            if msg_id and label_ids:
                                if msg_id not in label_changes:
                                    label_changes[msg_id] = {'added': [], 'removed': []}
                                
                                # Add the removed labels
                                for label in label_ids:
                                    if label not in label_changes[msg_id]['removed']:
                                        label_changes[msg_id]['removed'].append(label)
            
            # Check for more history pages
            if 'nextPageToken' in history_response:
                history_params['pageToken'] = history_response['nextPageToken']
                # Add a small delay to avoid rate limits
                time.sleep(0.5)
            else:
                break
        
        logger.info(f"[GMAIL] Sync complete - Found {total_history_events} history events, {len(new_emails)} new emails, {len(deleted_message_ids)} deleted emails, and {len(label_changes)} label changes")
        
    except Exception as e:
        error_msg = str(e)
        if "Invalid startHistoryId" in error_msg:
            logger.warning(f"[GMAIL] Invalid history ID: {last_history_id}. Need to perform full sync.")
            raise ValueError(f"Invalid startHistoryId: {last_history_id}")
        elif "Start history ID is too old" in error_msg:
            logger.warning(f"[GMAIL] History ID too old: {last_history_id}. Need to perform full sync.")
            raise ValueError(f"History ID too old: {last_history_id}")
        else:
            logger.error(f"[GMAIL] Error syncing Gmail changes: {error_msg}", exc_info=True)
            raise
    
    return new_emails, deleted_message_ids, label_changes, new_history_id

# Add this function to optimize fetching email details in batches
def _fetch_email_details_in_batches(service, email_ids, batch_size=20):
    """
    Fetch detailed email data in batches to minimize API calls
    
    Args:
        service: Gmail API service
        email_ids: List of Gmail message IDs to fetch
        batch_size: Number of emails to fetch in each batch
        
    Returns:
        List of processed email data
    """
    if not email_ids:
        return []
    
    logger.info(f"[GMAIL] Fetching details for {len(email_ids)} emails in batches of {batch_size}")
    
    # Process in batches to avoid hitting rate limits
    results = []
    errors = []
    total_batches = (len(email_ids) + batch_size - 1) // batch_size
    
    for i in range(0, len(email_ids), batch_size):
        batch_ids = email_ids[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        logger.info(f"[GMAIL] Processing batch {batch_num}/{total_batches} ({len(batch_ids)} emails)")
        
        # Create a new batch request
        batch = service.new_batch_http_request()
        
        # For storing responses and tracking which IDs had errors
        batch_results = {}
        batch_errors = {}
        
        # Add each email to the batch
        for j, msg_id in enumerate(batch_ids):
            request_id = f"msg{j}"
            
            # Define callback for each request
            def create_callback(request_id, msg_id):
                def callback(id_, response, exception):
                    if exception is not None:
                        logger.warning(f"[GMAIL] Error fetching message {msg_id}: {str(exception)}")
                        batch_errors[msg_id] = str(exception)
                    else:
                        # Process the message data
                        try:
                            processed_data = process_message_data(response)
                            batch_results[msg_id] = processed_data
                        except Exception as e:
                            logger.error(f"[GMAIL] Error processing message {msg_id}: {str(e)}")
                            batch_errors[msg_id] = str(e)
                return callback
            
            # Add the request to the batch
            batch.add(
                service.users().messages().get(userId='me', id=msg_id, format='full'),
                request_id=request_id,
                callback=create_callback(request_id, msg_id)
            )
        
        # Execute the batch
        try:
            @retry_with_backoff
            def execute_batch():
                batch.execute()
                return batch_results, batch_errors
            
            batch_results, batch_errors = execute_batch()
            
            # Add successful results to our list
            for msg_id, data in batch_results.items():
                results.append(data)
            
            # Check for errors and attempt to retry individual messages
            for msg_id, error in batch_errors.items():
                logger.warning(f"[GMAIL] Retrying individual fetch for message {msg_id} after batch error")
                try:
                    @retry_with_backoff
                    def get_single_message():
                        result = service.users().messages().get(
                            userId='me', id=msg_id, format='full'
                        ).execute()
                        return result
                    
                    message_data = get_single_message()
                    processed_data = process_message_data(message_data)
                    results.append(processed_data)
                    logger.info(f"[GMAIL] Successfully retrieved message {msg_id} with individual fetch")
                except Exception as e:
                    logger.error(f"[GMAIL] Failed to fetch message {msg_id} on individual retry: {str(e)}")
                    errors.append({"id": msg_id, "error": str(e)})
            
            # Add a small delay between batches to avoid rate limits
            if i + batch_size < len(email_ids):
                time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"[GMAIL] Error executing batch {batch_num}: {str(e)}")
            errors.extend([{"id": msg_id, "error": str(e)} for msg_id in batch_ids])
    
    if errors:
        logger.warning(f"[GMAIL] Completed with {len(errors)} errors out of {len(email_ids)} emails")
    
    return results

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

# Update the fetch_emails_from_gmail function to leverage the optimized batch processing
def fetch_emails_from_gmail(
    credentials: Dict[str, Any], 
    max_results: int = 100, 
    query: str = None,
    reference_email_id: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails from Gmail API, process them, and return structured data
    
    Args:
        credentials: Dictionary containing OAuth credentials
        max_results: Maximum number of emails to fetch
        query: Optional search query to filter emails
        reference_email_id: Optional reference email ID to search from
        
    Returns:
        List of processed email data
    """
    # Create the Gmail service
    logger.info("[GMAIL] Creating Gmail service with credentials")
    service = create_gmail_service(credentials)
    
    # Try to get a starting historyId if we're using a reference email
    start_history_id = None
    if reference_email_id:
        logger.info(f"[GMAIL] Using reference email ID: {reference_email_id}")
        start_history_id = get_message_history_id(service, reference_email_id)
        if start_history_id:
            logger.info(f"[GMAIL] Got history ID {start_history_id} from reference email")
    
    # If we have a valid history ID, use the history API for incremental sync
    if start_history_id:
        logger.info(f"[GMAIL] Using history API with history ID: {start_history_id}")
        try:
            new_emails, _, _, new_history_id = sync_gmail_changes(credentials, start_history_id)
            logger.info(f"[GMAIL] Retrieved {len(new_emails)} emails via history API")
            return new_emails
        except Exception as e:
            logger.error(f"[GMAIL] Error using history API: {str(e)}", exc_info=True)
            logger.info("[GMAIL] Falling back to traditional list/get approach")
            # Fall through to traditional approach
    
    # Use the traditional list/get approach if history API isn't available or fails
    logger.info(f"[GMAIL] Using traditional list/get approach with params: maxResults={max_results}, query='{query}'")
    
    params = {'userId': 'me', 'maxResults': min(max_results, 500)}
    
    # Add query parameter if provided, otherwise use INBOX label
    if query:
        params['q'] = query
    else:
        params['labelIds'] = ['INBOX']

    try:
        # Function to list messages with retry
        @retry_with_backoff
        def list_messages():
            logger.info(f"[GMAIL] Executing messages.list with params: {params}")
            return service.users().messages().list(**params).execute()
        
        # Get list of message IDs
        messages_response = list_messages()
        messages = messages_response.get('messages', [])
        
        if not messages:
            logger.info("[GMAIL] No messages found matching criteria")
            return []
        
        logger.info(f"[GMAIL] Found {len(messages)} messages matching query")
        
        # Extract IDs for batch retrieval
        message_ids = [msg['id'] for msg in messages]
        
        # Fetch detailed data in optimized batches
        logger.info(f"[GMAIL] Fetching detailed data for {len(message_ids)} messages")
        return _fetch_email_details_in_batches(service, message_ids)
        
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
    Check if emails have been deleted from Gmail
    
    Args:
        credentials: Dictionary containing OAuth credentials
        gmail_ids: List of Gmail message IDs to check
        force_full_check: If true, check all emails regardless of count
        
    Returns:
        Dictionary mapping Gmail IDs to deletion status (True if deleted)
    """
    if not gmail_ids:
        return {}
        
    # Create Gmail service
    service = create_gmail_service(credentials)
    
    # Determine how to handle the checking based on the number of IDs
    total_ids = len(gmail_ids)
    deleted_statuses = {}
    
    # For a small number of emails or if forced, check them all at once
    if total_ids <= 25 or force_full_check:
        # Process in smaller batches to avoid rate limits
        logger.info(f"[GMAIL] Checking deleted status for {total_ids} messages")
        batch_size = 10  # Small enough to avoid rate limits but efficient
        
        for i in range(0, total_ids, batch_size):
            batch_ids = gmail_ids[i:i+batch_size]
            batch_number = i // batch_size + 1
            total_batches = (total_ids + batch_size - 1) // batch_size
            
            logger.info(f"[GMAIL] Processing batch {batch_number}/{total_batches}")
            batch_statuses = _check_deleted_emails_batch_with_retry(service, batch_ids)
            deleted_statuses.update(batch_statuses)
            
            # Add a delay between batches to avoid rate limits
            if i + batch_size < total_ids:
                time.sleep(0.5)
    else:
        # For large numbers, check a sample first to see if any are deleted
        sample_size = min(5, total_ids)
        logger.info(f"[GMAIL] Large number of emails ({total_ids}), checking sample of {sample_size} first")
        
        # Take a sample of the IDs to check (evenly distributed)
        step = max(1, total_ids // sample_size)
        sample_ids = [gmail_ids[i] for i in range(0, total_ids, step)][:sample_size]
        
        # Check the sample
        logger.info(f"[GMAIL] Checking deleted status for {len(sample_ids)} messages")
        sample_statuses = _check_deleted_emails_batch_with_retry(service, sample_ids)
        deleted_statuses.update(sample_statuses)
        
        # Count how many were deleted in the sample
        deleted_count = sum(1 for is_deleted in sample_statuses.values() if is_deleted)
        
        if deleted_count > 0:
            # If we found deletions in the sample, check the remaining IDs
            logger.info(f"[GMAIL] Found {deleted_count} deleted messages out of {sample_size}, checking all remaining")
            
            # Get the remaining IDs (excludes the ones we already checked)
            remaining_ids = [id for id in gmail_ids if id not in sample_statuses]
            
            # Process the remaining IDs in batches
            for i in range(0, len(remaining_ids), batch_size):
                batch_ids = remaining_ids[i:i+batch_size]
                batch_number = i // batch_size + 1
                total_batches = (len(remaining_ids) + batch_size - 1) // batch_size
                
                logger.info(f"[GMAIL] Processing batch {batch_number}/{total_batches} of remaining")
                batch_statuses = _check_deleted_emails_batch_with_retry(service, batch_ids)
                deleted_statuses.update(batch_statuses)
                
                # Add a delay between batches to avoid rate limits
                if i + batch_size < len(remaining_ids):
                    time.sleep(0.5)
        else:
            logger.info(f"[GMAIL] No deletions found in sample, skipping full check of {total_ids} emails")
    
    # Overall deletion counts
    total_deleted = sum(1 for is_deleted in deleted_statuses.values() if is_deleted)
    logger.info(f"[GMAIL] Found {total_deleted} deleted messages out of {len(deleted_statuses)}")
    
    return deleted_statuses

@retry_with_backoff
def _check_deleted_emails_batch_with_retry(service, gmail_ids):
    """
    Check a batch of emails for deletion status with retry capability
    
    Args:
        service: Gmail API service instance
        gmail_ids: List of Gmail message IDs to check
        
    Returns:
        Dictionary mapping Gmail IDs to deletion status
    """
    return _check_deleted_emails_batch(service, gmail_ids)

def _check_deleted_emails_batch(
    service,
    gmail_ids: List[str]
) -> Dict[str, bool]:
    """
    Check a batch of emails to see if they've been deleted in Gmail
    
    Args:
        service: Gmail API service
        gmail_ids: List of Gmail message IDs to check
        
    Returns:
        Dictionary of message IDs to deleted status (True if deleted)
    """
    if not gmail_ids:
        return {}
    
    results = {}
    # Initialize all as not deleted
    for msg_id in gmail_ids:
        results[msg_id] = False
    
    # Create a batch request
    batch = service.new_batch_http_request()
    
    # Add each message to the batch
    for i, msg_id in enumerate(gmail_ids):
        request_id = f"msg{i}"
        
        # Define callback for this specific message
        def create_callback(msg_id):
            def callback(request_id, response, exception):
                if exception is not None:
                    # If we get a 404, the message is deleted
                    if hasattr(exception, 'resp') and exception.resp.status == 404:
                        results[msg_id] = True
                    else:
                        # Any other error, we can't determine if it's deleted
                        logger.warning(f"[GMAIL] Error checking if message {msg_id} is deleted: {str(exception)}")
            return callback
        
        # Add the request to the batch
        batch.add(
            service.users().messages().get(userId='me', id=msg_id, format='minimal'),
            request_id=request_id,
            callback=create_callback(msg_id)
        )
    
    # Execute the batch
    try:
        batch.execute()
    except Exception as e:
        logger.error(f"[GMAIL] Error executing batch to check deleted emails: {str(e)}")
    
    return results

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