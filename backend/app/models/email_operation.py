from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..db import Base
import uuid

class OperationType(str, Enum):
    """Enum representing different types of email operations"""
    DELETE = "delete"              # Move to trash
    ARCHIVE = "archive"            # Archive (remove from inbox)
    UPDATE_LABELS = "update_labels" # Change labels
    UPDATE_CATEGORY = "update_category" # Change category
    MARK_READ = "mark_read"        # Mark as read
    MARK_UNREAD = "mark_unread"    # Mark as unread

class OperationStatus(str, Enum):
    """Enum representing operation status"""
    PENDING = "pending"    # Operation waiting to be processed
    PROCESSING = "processing" # Operation currently being processed
    COMPLETED = "completed"  # Operation successfully completed
    FAILED = "failed"      # Operation failed
    RETRYING = "retrying"  # Operation is being retried

class EmailOperation(Base):
    """
    Model for tracking pending email operations that need to be synced to Gmail
    
    This table stores operations initiated in EA that need to be pushed to Gmail
    during the next sync. It enables bidirectional sync by ensuring changes made
    in EA are properly reflected in Gmail.
    
    Attributes:
        id: Primary key UUID
        email_id: Foreign key to the email being operated on
        user_id: Foreign key to the user who owns the email
        operation_type: Type of operation (delete, archive, update_labels, etc.)
        operation_data: JSON data containing operation specifics (e.g., labels to add/remove)
        status: Current status of the operation (pending, completed, failed)
        error_message: Error message if operation failed
        created_at: When the operation was created
        updated_at: When the operation was last updated
        retries: Number of retry attempts made
    """
    __tablename__ = "email_operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey('emails.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    operation_type = Column(String(50), nullable=False)
    operation_data = Column(JSONB, nullable=False)
    status = Column(String(20), default=OperationStatus.PENDING, nullable=False)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    retries = Column(Integer, default=0)
    
    # Relationships
    email = relationship("Email", back_populates="operations")
    user = relationship("User")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_email_operations_status', status),
        Index('ix_email_operations_user_id', user_id),
        Index('ix_email_operations_email_id', email_id),
        Index('ix_email_operations_created_at', created_at),
        Index('ix_email_operations_operation_type', operation_type),
    )
    
    def __repr__(self):
        return f"<EmailOperation id={self.id} type={self.operation_type} status={self.status}>" 