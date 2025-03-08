from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import uuid

class EmailTrashEvent(Base):
    """
    Model for storing email trash events for ML training
    
    This table captures all instances of emails being moved to or from trash,
    along with relevant features that might be useful for training a 
    Naive Bayes classifier to better identify trash emails.
    
    Attributes:
        id: Primary key UUID
        email_id: Foreign key to the email
        user_id: Foreign key to the user who owns the email
        event_type: Type of event (moved_to_trash, restored_from_trash)
        sender_email: Email address of the sender
        sender_domain: Domain part of the sender email
        subject: Email subject
        snippet: Email snippet/preview
        keywords: Extracted keywords from the email
        is_auto_categorized: Whether the email was automatically categorized
        categorization_source: Source of categorization (rules, ml, user)
        confidence_score: Confidence score (if ML model was used)
        email_metadata: Additional email metadata useful for training
        created_at: When the event was recorded
    """
    __tablename__ = "email_trash_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey('emails.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String(50), nullable=False)  # moved_to_trash, restored_from_trash
    sender_email = Column(String, nullable=False)
    sender_domain = Column(String, nullable=False)
    subject = Column(String)
    snippet = Column(Text)
    keywords = Column(ARRAY(String))
    is_auto_categorized = Column(Boolean, default=False)
    categorization_source = Column(String(20))  # rules, ml, user
    confidence_score = Column(Float)
    email_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    email = relationship("Email")
    user = relationship("User")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_email_trash_events_user_id', user_id),
        Index('ix_email_trash_events_email_id', email_id),
        Index('ix_email_trash_events_event_type', event_type),
        Index('ix_email_trash_events_sender_domain', sender_domain),
        Index('ix_email_trash_events_created_at', created_at),
        Index('ix_email_trash_events_categorization_source', categorization_source),
    )
    
    def __repr__(self):
        return f"<EmailTrashEvent id={self.id} email_id={self.email_id} event_type={self.event_type}>" 