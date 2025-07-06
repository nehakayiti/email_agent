"""
Email Sync Service - Backward compatibility wrapper

This module provides backward compatibility for existing code that imports
from email_sync_service. It delegates to the new modular services.
"""

from .sync_coordinator_service import (
    sync_emails_since_last_fetch,
    perform_full_sync,
    update_user_credentials
)
from .sync_recording import record_sync_details

# Re-export the functions for backward compatibility
__all__ = [
    'sync_emails_since_last_fetch',
    'perform_full_sync', 
    'update_user_credentials',
    'record_sync_details'
] 