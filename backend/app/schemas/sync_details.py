from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class SyncDetailsSchema(BaseModel):
    id: Optional[int]
    user_id: str
    account_email: str
    direction: Literal['Gmail → EA', 'EA → Gmail', 'Bi-directional']
    sync_type: Literal['Manual', 'Automatic']
    sync_started_at: datetime
    sync_completed_at: datetime
    duration_sec: float
    status: Literal['success', 'error']
    error_message: Optional[str] = None
    emails_synced: int
    changes_detected: int
    changes_applied: int
    pending_ea_changes: Optional[List[str]] = None
    backend_version: Optional[str] = None
    data_freshness_sec: Optional[int] = None

    class Config:
        orm_mode = True 