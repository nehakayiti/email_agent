from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.models.sync_details import SyncDetails, SyncDirection, SyncType, SyncStatus
from app.schemas.sync_details import SyncDetailsSchema
from app.db import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/sync/details", tags=["sync-details"])

def to_schema(sync: SyncDetails) -> SyncDetailsSchema:
    # Convert SQLAlchemy model to Pydantic schema, ensuring Enums are strings
    return SyncDetailsSchema(
        id=sync.id,
        user_id=str(sync.user_id),
        account_email=sync.account_email,
        direction=sync.direction.value if sync.direction else None,
        sync_type=sync.sync_type.value if sync.sync_type else None,
        sync_started_at=sync.sync_started_at,
        sync_completed_at=sync.sync_completed_at,
        duration_sec=sync.duration_sec,
        status=sync.status.value if sync.status else None,
        error_message=sync.error_message,
        emails_synced=sync.emails_synced,
        changes_detected=sync.changes_detected,
        changes_applied=sync.changes_applied,
        pending_ea_changes=sync.pending_ea_changes,
        backend_version=sync.backend_version,
        data_freshness_sec=sync.data_freshness_sec,
    )

@router.post("/", response_model=SyncDetailsSchema)
def create_sync_details(details: SyncDetailsSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sync = SyncDetails(
        user_id=user.id,
        account_email=user.email,
        direction=SyncDirection(details.direction),
        sync_type=SyncType(details.sync_type),
        sync_started_at=details.sync_started_at,
        sync_completed_at=details.sync_completed_at,
        duration_sec=details.duration_sec,
        status=SyncStatus(details.status),
        error_message=details.error_message,
        emails_synced=details.emails_synced,
        changes_detected=details.changes_detected,
        changes_applied=details.changes_applied,
        pending_ea_changes=details.pending_ea_changes,
        backend_version=details.backend_version,
        data_freshness_sec=details.data_freshness_sec,
    )
    db.add(sync)
    db.commit()
    db.refresh(sync)
    return to_schema(sync)

@router.get("/latest", response_model=SyncDetailsSchema)
def get_latest_sync_details(db: Session = Depends(get_db), user=Depends(get_current_user)):
    sync = db.query(SyncDetails).filter(SyncDetails.user_id == str(user.id)).order_by(SyncDetails.sync_started_at.desc()).first()
    if not sync:
        raise HTTPException(status_code=404, detail="No sync details found")
    return to_schema(sync)

@router.get("/", response_model=List[SyncDetailsSchema])
def get_sync_details(limit: int = 10, db: Session = Depends(get_db), user=Depends(get_current_user)):
    syncs = db.query(SyncDetails).filter(SyncDetails.user_id == str(user.id)).order_by(SyncDetails.sync_started_at.desc()).limit(limit).all()
    return [to_schema(sync) for sync in syncs] 