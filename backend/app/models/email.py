from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import uuid

class Email(Base):
    """
    Email model for storing Gmail messages
    
    Attributes:
        id: Primary key UUID
        user_id: Foreign key to user who owns the email
        gmail_id: Gmail's message ID
        thread_id: Gmail's thread ID
        subject: Email subject
        from_email: Sender's email address
        received_at: When email was received
        snippet: Short preview of email content
        labels: Gmail labels
        is_read: Whether email has been read
        is_processed: Whether email has been processed by our system
        importance_score: Calculated importance (0-100)
        category: Classified category (promotional, social, primary, etc.)
        raw_data: Complete email data for future processing
    """
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    gmail_id = Column(String, nullable=False)
    thread_id = Column(String, nullable=False)
    subject = Column(String)
    from_email = Column(String)
    received_at = Column(DateTime(timezone=True))
    snippet = Column(String)
    labels = Column(ARRAY(String))
    is_read = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    importance_score = Column(Integer)
    category = Column(String)
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="emails")
    operations = relationship("EmailOperation", back_populates="email", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_emails_user_id_received_at', user_id, received_at.desc()),
        Index('ix_emails_gmail_id', gmail_id),
        Index('ix_emails_category', category),
    ) 