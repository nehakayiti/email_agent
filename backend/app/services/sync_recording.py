from sqlalchemy.orm import Session
from datetime import datetime
from ..models.user import User
from ..models.sync_details import SyncDetails, SyncDirection, SyncType, SyncStatus
from ..config import settings
from typing import Optional, List

def record_sync_details(
    db: Session,
    user: User,
    direction: SyncDirection,
    sync_type: SyncType,
    sync_started_at: datetime,
    sync_completed_at: datetime,
    duration_sec: float,
    status: SyncStatus,
    error_message: Optional[str] = None,
    emails_synced: int = 0,
    changes_detected: int = 0,
    changes_applied: int = 0,
    pending_ea_changes: Optional[List] = None,
    data_freshness_sec: Optional[int] = None,
) -> SyncDetails:
    """
    Create and persist a SyncDetails record for any sync direction.
    """
    sync_details = SyncDetails(
        user_id=user.id,
        account_email=user.email,
        direction=direction,
        sync_type=sync_type,
        sync_started_at=sync_started_at,
        sync_completed_at=sync_completed_at,
        duration_sec=duration_sec,
        status=status,
        error_message=error_message,
        emails_synced=emails_synced,
        changes_detected=changes_detected,
        changes_applied=changes_applied,
        pending_ea_changes=pending_ea_changes or [],
        backend_version=settings.VERSION,
        data_freshness_sec=data_freshness_sec,
    )
    db.add(sync_details)
    db.commit()
    db.refresh(sync_details)
    return sync_details 