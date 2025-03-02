from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Optional, Tuple
import logging
from google.auth.transport.requests import Request
import time
import random

logger = logging.getLogger(__name__)

def create_gmail_service(credentials_dict: Dict[str, Any]):
    """
    Create a Gmail API service instance from stored credentials.
    Refreshes the token if needed.
    """
    try:
        # Build credentials using the stored token values
        credentials = Credentials(
            token=credentials_dict['token'],
            refresh_token=credentials_dict['refresh_token'],
            token_uri=credentials_dict['token_uri'],
            client_id=credentials_dict['client_id'],
            client_secret=credentials_dict['client_secret']
        )
        
        # Refresh token if it has expired
        if credentials.expired:
            logger.info("[GMAIL] Credentials expired, refreshing token")
            credentials.refresh(Request())
            credentials_dict['token'] = credentials.token
        
        return build('gmail', 'v1', credentials=credentials, cache_discovery=False)
    except Exception as e:
        logger.error(f"[GMAIL] Error creating Gmail service: {str(e)}", exc_info=True)
        raise

def get_message_history_id(service, message_id: str) -> Optional[str]:
    """
    Get the historyId of a specific message.
    """
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='minimal'
        ).execute()
        return message.get('historyId')
    except Exception as e:
        logger.error(f"[GMAIL] Error getting historyId for message {message_id}: {str(e)}")
        return None

def retry_with_backoff(func, max_retries=5, base_delay=1, jitter=True):
    """
    Decorator for retrying a function with exponential backoff.
    Retries on rate limit or server errors.
    """
    def wrapper(*args, **kwargs):
        retry_count = 0
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                retry_count += 1
                
                # Check if error is due to rate limiting or server issues
                is_rate_limit = "Resource has been exhausted" in error_msg or "rate limit" in error_msg.lower()
                is_server_error = error_msg[:3].isdigit() and error_msg.startswith("5")
                
                if (is_rate_limit or is_server_error) and retry_count < max_retries:
                    delay = base_delay * (2 ** (retry_count - 1))
                    if jitter:
                        delay += random.uniform(0, min(1, delay * 0.1))
                    logger.warning(f"[GMAIL] Rate limit/server error, retrying in {delay:.2f} seconds (attempt {retry_count}/{max_retries})")
                    time.sleep(delay)
                else:
                    if retry_count >= max_retries:
                        logger.error(f"[GMAIL] Maximum retries ({max_retries}) exceeded")
                    raise
    return wrapper

def sync_gmail_changes(
    credentials: Dict[str, Any],
    last_history_id: str
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Dict[str, List[str]]], str]:
    """
    Sync changes using Gmail's history API since the provided history ID.
    
    Returns a tuple of:
      - New emails (list of processed email data)
      - Deleted email IDs (list)
      - Label changes (dictionary mapping message IDs to {'added': [...], 'removed': [...]})
      - New history ID (string)
    """
    service = create_gmail_service(credentials)
    
    new_emails = []
    deleted_message_ids = []
    label_changes = {}
    
    # Global set to track processed messages across all pages
    processed_messages = set()
    
    @retry_with_backoff
    def fetch_history_page(params):
        return service.users().history().list(userId='me', **params).execute()
    
    history_params = {
        'startHistoryId': last_history_id,
        'historyTypes': ['messageAdded', 'messageDeleted', 'labelAdded', 'labelRemoved']
    }
    
    total_history_events = 0
    page_number = 0
    new_history_id = None
    
    try:
        # Loop through all pages of history
        while True:
            page_number += 1
            logger.info(f"[GMAIL] Fetching history page {page_number} starting at history ID {last_history_id}")
            history_response = fetch_history_page(history_params)
            
            # Update the new history ID from the latest response
            if 'historyId' in history_response:
                new_history_id = history_response['historyId']
                logger.debug(f"[GMAIL] New history ID updated to {new_history_id}")
            
            if 'history' in history_response:
                history_items = history_response['history']
                total_history_events += len(history_items)
                logger.info(f"[GMAIL] Page {page_number} contains {len(history_items)} history events")
                
                for item in history_items:
                    # Log full item for debugging
                    logger.debug(f"[GMAIL] Processing history event: {item.keys()}")
                    
                    # Process new messages
                    if 'messagesAdded' in item:
                        for message in item['messagesAdded']:
                            msg_data = message.get('message', {})
                            msg_id = msg_data.get('id')
                            if msg_id and msg_id not in processed_messages:
                                processed_messages.add(msg_id)
                                logger.info(f"[GMAIL] New message detected with ID {msg_id}")
                                labels = msg_data.get('labelIds', [])
                                if 'INBOX' in labels and 'TRASH' not in labels and 'SPAM' not in labels:
                                    try:
                                        full_message = service.users().messages().get(
                                            userId='me', id=msg_id, format='full'
                                        ).execute()
                                        email_data = process_message_data(full_message)
                                        if email_data:
                                            new_emails.append(email_data)
                                    except Exception as e:
                                        logger.error(f"[GMAIL] Error fetching full message {msg_id}: {str(e)}")
                    
                    # Process deleted messages
                    if 'messagesDeleted' in item:
                        for message in item['messagesDeleted']:
                            msg_data = message.get('message', {})
                            msg_id = msg_data.get('id')
                            if msg_id and msg_id not in deleted_message_ids:
                                # Log only the first few deletions to avoid spam
                                if len(deleted_message_ids) < 3:
                                    logger.info(f"[GMAIL] Deleted message detected: {msg_data}")
                                deleted_message_ids.append(msg_id)
                    
                    # Process label additions
                    if 'labelsAdded' in item:
                        for label_data in item['labelsAdded']:
                            msg_data = label_data.get('message', {})
                            msg_id = msg_data.get('id')
                            label_ids = label_data.get('labelIds', [])
                            if msg_id and label_ids:
                                if msg_id not in label_changes:
                                    label_changes[msg_id] = {'added': [], 'removed': []}
                                for label in label_ids:
                                    if label not in label_changes[msg_id]['added']:
                                        label_changes[msg_id]['added'].append(label)
                                        logger.info(f"[GMAIL] Label '{label}' added to message {msg_id}")
                    
                    # Process label removals
                    if 'labelsRemoved' in item:
                        for label_data in item['labelsRemoved']:
                            msg_data = label_data.get('message', {})
                            msg_id = msg_data.get('id')
                            label_ids = label_data.get('labelIds', [])
                            if msg_id and label_ids:
                                if msg_id not in label_changes:
                                    label_changes[msg_id] = {'added': [], 'removed': []}
                                for label in label_ids:
                                    if label not in label_changes[msg_id]['removed']:
                                        label_changes[msg_id]['removed'].append(label)
                                        logger.info(f"[GMAIL] Label '{label}' removed from message {msg_id}")
            
            # Continue with next page if available
            if 'nextPageToken' in history_response:
                history_params['pageToken'] = history_response['nextPageToken']
                time.sleep(0.5)
            else:
                break
        
        logger.info(f"[GMAIL] Sync complete: {total_history_events} history events, {len(new_emails)} new emails, "
                    f"{len(deleted_message_ids)} deleted emails, and {len(label_changes)} messages with label changes")
        
    except Exception as e:
        error_msg = str(e)
        if "Invalid startHistoryId" in error_msg:
            logger.warning(f"[GMAIL] Invalid history ID: {last_history_id}. A full sync may be needed.")
            raise ValueError(f"Invalid startHistoryId: {last_history_id}")
        elif "Start history ID is too old" in error_msg:
            logger.warning(f"[GMAIL] History ID too old: {last_history_id}. A full sync may be needed.")
            raise ValueError(f"History ID too old: {last_history_id}")
        else:
            logger.error(f"[GMAIL] Error during sync: {error_msg}", exc_info=True)
            raise
    
    return new_emails, deleted_message_ids, label_changes, new_history_id

def _fetch_email_details_in_batches(service, email_ids, batch_size=20):
    """
    Fetch email details in batches to reduce API calls.
    """
    if not email_ids:
        return []
    
    logger.info(f"[GMAIL] Fetching details for {len(email_ids)} emails in batches of {batch_size}")
    results = []
    errors = []
    total_batches = (len(email_ids) + batch_size - 1) // batch_size
    
    for i in range(0, len(email_ids), batch_size):
        batch_ids = email_ids[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        logger.info(f"[GMAIL] Processing batch {batch_num}/{total_batches} with {len(batch_ids)} emails")
        
        batch = service.new_batch_http_request()
        batch_results = {}
        batch_errors = {}
        
        for j, msg_id in enumerate(batch_ids):
            request_id = f"msg{j}"
            def create_callback(request_id, msg_id):
                def callback(id_, response, exception):
                    if exception is not None:
                        logger.warning(f"[GMAIL] Error fetching message {msg_id}: {str(exception)}")
                        batch_errors[msg_id] = str(exception)
                    else:
                        try:
                            processed_data = process_message_data(response)
                            batch_results[msg_id] = processed_data
                        except Exception as e:
                            logger.error(f"[GMAIL] Error processing message {msg_id}: {str(e)}")
                            batch_errors[msg_id] = str(e)
                return callback
            
            batch.add(
                service.users().messages().get(userId='me', id=msg_id, format='full'),
                request_id=request_id,
                callback=create_callback(request_id, msg_id)
            )
        
        try:
            @retry_with_backoff
            def execute_batch():
                batch.execute()
                return batch_results, batch_errors
            
            batch_results, batch_errors = execute_batch()
            
            for msg_id, data in batch_results.items():
                results.append(data)
            
            # Retry individual messages that failed in the batch
            for msg_id, error in batch_errors.items():
                logger.warning(f"[GMAIL] Retrying individual fetch for message {msg_id} due to batch error")
                try:
                    @retry_with_backoff
                    def get_single_message():
                        return service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                    
                    message_data = get_single_message()
                    processed_data = process_message_data(message_data)
                    results.append(processed_data)
                    logger.info(f"[GMAIL] Successfully fetched message {msg_id} on individual retry")
                except Exception as e:
                    logger.error(f"[GMAIL] Failed to fetch message {msg_id} individually: {str(e)}")
                    errors.append({"id": msg_id, "error": str(e)})
            
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
    Process a raw Gmail message into a structured dictionary.
    """
    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
    from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
    date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
    
    try:
        received_date = parsedate_to_datetime(date_str)
        if received_date.tzinfo is None:
            received_date = received_date.replace(tzinfo=timezone.utc)
        received_iso = received_date.isoformat()
    except Exception as e:
        logger.warning(f"[GMAIL] Error parsing date '{date_str}': {str(e)}")
        received_iso = datetime.now(timezone.utc).isoformat()
    
    email_data = {
        'gmail_id': msg['id'],
        'thread_id': msg['threadId'],
        'subject': subject,
        'from_email': from_email,
        'received_at': received_iso,
        'snippet': msg.get('snippet', ''),
        'labels': msg.get('labelIds', []),
        'is_read': 'UNREAD' not in msg.get('labelIds', []),
        'raw_data': msg
    }
    
    return email_data

def fetch_emails_from_gmail(
    credentials: Dict[str, Any], 
    max_results: int = 100, 
    query: str = None,
    reference_email_id: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch emails using the Gmail API and process them.
    Falls back to the traditional list/get approach if history sync fails.
    """
    logger.info("[GMAIL] Creating Gmail service with credentials")
    service = create_gmail_service(credentials)
    
    start_history_id = None
    if reference_email_id:
        logger.info(f"[GMAIL] Using reference email ID: {reference_email_id}")
        start_history_id = get_message_history_id(service, reference_email_id)
        if start_history_id:
            logger.info(f"[GMAIL] Obtained history ID {start_history_id} from reference email")
    
    if start_history_id:
        logger.info(f"[GMAIL] Using history API with history ID: {start_history_id}")
        try:
            new_emails, _, _, new_history_id = sync_gmail_changes(credentials, start_history_id)
            logger.info(f"[GMAIL] Retrieved {len(new_emails)} emails via history API")
            return new_emails
        except Exception as e:
            logger.error(f"[GMAIL] Error with history API: {str(e)}", exc_info=True)
            logger.info("[GMAIL] Falling back to traditional approach")
    
    logger.info(f"[GMAIL] Using traditional approach with maxResults={max_results}, query='{query}'")
    params = {'userId': 'me', 'maxResults': min(max_results, 500)}
    
    if query:
        params['q'] = query
    else:
        params['labelIds'] = ['INBOX']

    try:
        @retry_with_backoff
        def list_messages():
            logger.info(f"[GMAIL] Listing messages with params: {params}")
            return service.users().messages().list(**params).execute()
        
        messages_response = list_messages()
        messages = messages_response.get('messages', [])
        
        if not messages:
            logger.info("[GMAIL] No messages found matching criteria")
            return []
        
        logger.info(f"[GMAIL] Found {len(messages)} messages")
        message_ids = [msg['id'] for msg in messages]
        logger.info(f"[GMAIL] Fetching details for {len(message_ids)} messages")
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
    Update email labels.
    """
    try:
        logger.info(f"[GMAIL] Updating labels for message {gmail_id}")
        service = create_gmail_service(credentials)
        body = {}
        if add_labels:
            body['addLabelIds'] = add_labels
            logger.info(f"[GMAIL] Labels to add: {add_labels}")
        if remove_labels:
            body['removeLabelIds'] = remove_labels
            logger.info(f"[GMAIL] Labels to remove: {remove_labels}")
        
        max_retries = 5
        base_delay = 1
        for retry in range(max_retries):
            try:
                result = service.users().messages().modify(
                    userId='me',
                    id=gmail_id,
                    body=body
                ).execute()
                logger.info(f"[GMAIL] Successfully updated labels for {gmail_id}")
                return result
            except Exception as e:
                error_msg = str(e)
                if "Resource has been exhausted" in error_msg or "rate limit" in error_msg.lower():
                    if retry < max_retries - 1:
                        delay = base_delay * (2 ** retry) + random.uniform(0, 1)
                        logger.warning(f"[GMAIL] Rate limit hit, retrying in {delay:.2f} seconds (attempt {retry+1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        logger.error(f"[GMAIL] Rate limit persisted after {max_retries} retries")
                        raise
                else:
                    logger.error(f"[GMAIL] Error updating labels for {gmail_id}: {error_msg}", exc_info=True)
                    raise
    except Exception as e:
        logger.error(f"[GMAIL] Error updating labels for {gmail_id}: {str(e)}", exc_info=True)
        raise

def check_deleted_emails(
    credentials: Dict[str, Any],
    gmail_ids: List[str],
    force_full_check: bool = False
) -> Dict[str, bool]:
    """
    Check if emails have been deleted from Gmail.
    Returns a dictionary mapping Gmail IDs to True if deleted.
    """
    if not gmail_ids:
        return {}
        
    service = create_gmail_service(credentials)
    total_ids = len(gmail_ids)
    deleted_statuses = {}
    
    if total_ids <= 25 or force_full_check:
        logger.info(f"[GMAIL] Checking deleted status for {total_ids} messages in small batches")
        batch_size = 10
        for i in range(0, total_ids, batch_size):
            batch_ids = gmail_ids[i:i+batch_size]
            batch_number = i // batch_size + 1
            total_batches = (total_ids + batch_size - 1) // batch_size
            logger.info(f"[GMAIL] Processing batch {batch_number}/{total_batches}")
            batch_statuses = _check_deleted_emails_batch_with_retry(service, batch_ids)
            deleted_statuses.update(batch_statuses)
            if i + batch_size < total_ids:
                time.sleep(0.5)
    else:
        sample_size = min(5, total_ids)
        logger.info(f"[GMAIL] Large number of messages ({total_ids}); checking a sample of {sample_size} first")
        step = max(1, total_ids // sample_size)
        sample_ids = [gmail_ids[i] for i in range(0, total_ids, step)][:sample_size]
        logger.info(f"[GMAIL] Checking deleted status for {len(sample_ids)} sample messages")
        sample_statuses = _check_deleted_emails_batch_with_retry(service, sample_ids)
        deleted_statuses.update(sample_statuses)
        deleted_count = sum(1 for is_deleted in sample_statuses.values() if is_deleted)
        
        if deleted_count > 0:
            logger.info(f"[GMAIL] Found {deleted_count} deletions in sample; checking remaining messages")
            # Define batch size for remaining checks
            batch_size = 10
            remaining_ids = [msg_id for msg_id in gmail_ids if msg_id not in sample_statuses]
            for i in range(0, len(remaining_ids), batch_size):
                batch_ids = remaining_ids[i:i+batch_size]
                batch_number = i // batch_size + 1
                total_batches = (len(remaining_ids) + batch_size - 1) // batch_size
                logger.info(f"[GMAIL] Processing remaining batch {batch_number}/{total_batches}")
                batch_statuses = _check_deleted_emails_batch_with_retry(service, batch_ids)
                deleted_statuses.update(batch_statuses)
                if i + batch_size < len(remaining_ids):
                    time.sleep(0.5)
        else:
            logger.info(f"[GMAIL] No deletions found in sample; skipping full check")
    
    total_deleted = sum(1 for is_deleted in deleted_statuses.values() if is_deleted)
    logger.info(f"[GMAIL] Checked {len(deleted_statuses)} messages; {total_deleted} found deleted")
    return deleted_statuses

@retry_with_backoff
def _check_deleted_emails_batch_with_retry(service, gmail_ids):
    """
    Check a batch of emails for deletion with retry support.
    """
    return _check_deleted_emails_batch(service, gmail_ids)

def _check_deleted_emails_batch(
    service,
    gmail_ids: List[str]
) -> Dict[str, bool]:
    """
    Check if messages are deleted by trying to fetch minimal details.
    A 404 error indicates deletion.
    """
    if not gmail_ids:
        return {}
    
    results = {msg_id: False for msg_id in gmail_ids}
    batch = service.new_batch_http_request()
    
    for i, msg_id in enumerate(gmail_ids):
        request_id = f"msg{i}"
        def create_callback(msg_id):
            def callback(request_id, response, exception):
                if exception is not None:
                    if hasattr(exception, 'resp') and exception.resp.status == 404:
                        results[msg_id] = True
                    else:
                        logger.warning(f"[GMAIL] Error checking deletion for message {msg_id}: {str(exception)}")
            return callback
        
        batch.add(
            service.users().messages().get(userId='me', id=msg_id, format='minimal'),
            request_id=request_id,
            callback=create_callback(msg_id)
        )
    
    try:
        batch.execute()
    except Exception as e:
        logger.error(f"[GMAIL] Batch execution error while checking deletions: {str(e)}")
    
    return results

def setup_push_notifications(
    credentials: Dict[str, Any],
    webhook_url: str,
    topic_name: str = None
) -> Dict[str, Any]:
    """
    Set up Gmail push notifications to the given webhook URL.
    """
    try:
        logger.info(f"[GMAIL] Setting up push notifications to {webhook_url}")
        service = create_gmail_service(credentials)
        
        if not topic_name:
            unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
            topic_name = f"gmail_{unique_id}"
        
        watch_request = {
            'topicName': topic_name,
            'labelIds': ['INBOX'],
            'labelFilterAction': 'include'
        }
        
        watch_response = service.users().watch(userId='me', body=watch_request).execute()
        logger.info(f"[GMAIL] Push notifications set up: {watch_response}")
        watch_response['webhook_url'] = webhook_url
        watch_response['topic_name'] = topic_name
        
        return watch_response
        
    except Exception as e:
        logger.error(f"[GMAIL] Error setting up push notifications: {str(e)}", exc_info=True)
        raise

def stop_push_notifications(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stop Gmail push notifications.
    """
    try:
        logger.info("[GMAIL] Stopping push notifications")
        service = create_gmail_service(credentials)
        service.users().stop(userId='me').execute()
        logger.info("[GMAIL] Successfully stopped push notifications")
        return {"status": "success", "message": "Push notifications stopped successfully"}
    except Exception as e:
        logger.error(f"[GMAIL] Error stopping push notifications: {str(e)}", exc_info=True)
        raise

def get_gmail_profile(credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve the Gmail profile information.
    """
    try:
        logger.info("[GMAIL] Retrieving Gmail profile")
        service = create_gmail_service(credentials)
        profile = service.users().getProfile(userId='me').execute()
        logger.info(f"[GMAIL] Profile retrieved: {profile}")
        return profile
    except Exception as e:
        logger.error(f"[GMAIL] Error retrieving Gmail profile: {str(e)}", exc_info=True)
        raise
