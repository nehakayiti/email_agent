from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, Text, JSON
import enum
from sqlalchemy.dialects.postgresql import UUID
from ..db import Base

class SyncDirection(str, enum.Enum):
    GMAIL_TO_EA = 'Gmail → EA'
    EA_TO_GMAIL = 'EA → Gmail'
    BI_DIRECTIONAL = 'Bi-directional'

class SyncType(str, enum.Enum):
    MANUAL = 'Manual'
    AUTOMATIC = 'Automatic'

class SyncStatus(str, enum.Enum):
    SUCCESS = 'success'
    ERROR = 'error'

class SyncDetails(Base):
    __tablename__ = 'sync_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    account_email = Column(String, nullable=False)
    direction = Column(Enum(SyncDirection), nullable=False)
    sync_type = Column(Enum(SyncType), nullable=False)
    sync_started_at = Column(DateTime, nullable=False)
    sync_completed_at = Column(DateTime, nullable=False)
    duration_sec = Column(Float, nullable=False)
    status = Column(Enum(SyncStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    emails_synced = Column(Integer, nullable=False)
    changes_detected = Column(Integer, nullable=False)
    changes_applied = Column(Integer, nullable=False)
    pending_ea_changes = Column(JSON, nullable=True)
    backend_version = Column(String, nullable=True)
    data_freshness_sec = Column(Integer, nullable=True) 