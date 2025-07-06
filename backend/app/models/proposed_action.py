from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..db import Base
import uuid

class ProposedActionStatus(str, Enum):
    """Enum representing proposed action status"""
    PENDING = "pending"      # Waiting for user approval/rejection
    APPROVED = "approved"    # User approved, converted to EmailOperation
    REJECTED = "rejected"    # User rejected the proposal
    EXPIRED = "expired"      # Proposal expired (e.g., email was deleted)

class ProposedAction(Base):
    """
    Model for tracking proposed email actions that require user approval
    
    This table stores actions that the Action Engine has identified as
    potentially beneficial but require explicit user approval before
    execution. This ensures user trust and prevents unwanted automated
    actions.
    
    Attributes:
        id: Primary key UUID
        email_id: Foreign key to the email being operated on
        user_id: Foreign key to the user who owns the email
        category_id: Foreign key to the category that triggered the action
        action_type: Type of action (ARCHIVE, TRASH, etc.)
        reason: Human-readable explanation of why action is proposed
        email_age_days: How old the email is in days
        created_at: When the proposal was created
        status: Current status of the proposal
    """
    __tablename__ = "proposed_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey('emails.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('email_categories.id', ondelete='CASCADE'), nullable=False)
    action_type = Column(String(50), nullable=False)  # ARCHIVE, TRASH, etc.
    reason = Column(Text, nullable=False)  # Explanation of why action is proposed
    email_age_days = Column(Integer, nullable=False)  # How old the email is
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), default=ProposedActionStatus.PENDING, nullable=False)
    
    # Relationships
    email = relationship("Email", back_populates="proposed_actions")
    user = relationship("User")
    category = relationship("EmailCategory")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_proposed_actions_status', status),
        Index('ix_proposed_actions_user_id', user_id),
        Index('ix_proposed_actions_email_id', email_id),
        Index('ix_proposed_actions_category_id', category_id),
        Index('ix_proposed_actions_created_at', created_at),
        Index('ix_proposed_actions_action_type', action_type),
        Index('ix_proposed_actions_user_status', user_id, status),  # For filtering by user and status
    )
    
    def __repr__(self):
        return f"<ProposedAction id={self.id} action={self.action_type} status={self.status}>"
    
    @property
    def is_pending(self) -> bool:
        """Check if the proposal is still pending approval"""
        return self.status == ProposedActionStatus.PENDING
    
    @property
    def is_approved(self) -> bool:
        """Check if the proposal has been approved"""
        return self.status == ProposedActionStatus.APPROVED
    
    @property
    def is_rejected(self) -> bool:
        """Check if the proposal has been rejected"""
        return self.status == ProposedActionStatus.REJECTED
    
    @property
    def is_expired(self) -> bool:
        """Check if the proposal has expired"""
        return self.status == ProposedActionStatus.EXPIRED 