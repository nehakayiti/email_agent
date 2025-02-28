from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import uuid

class EmailSync(Base):
    """
    EmailSync model for tracking email synchronization status
    
    Attributes:
        id: Primary key UUID
        user_id: Foreign key to user who owns the sync record
        last_fetched_at: Timestamp of last successful email fetch
        last_history_id: Gmail history ID for efficient incremental syncing
        sync_cadence: Frequency of sync in minutes
        created_at: When the record was created
        updated_at: When the record was last updated
    """
    __tablename__ = "email_syncs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    last_fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_history_id = Column(String, nullable=True)  # Gmail history ID for efficient incremental syncing
    sync_cadence = Column(Integer, nullable=False, default=60)  # Default to 60 minutes
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_sync")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_email_syncs_user_id', user_id),
        Index('ix_email_syncs_last_fetched_at', last_fetched_at),
    ) 