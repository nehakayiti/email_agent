from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base
import uuid

class SenderRule(Base):
    """Model for storing sender-based email categorization rules"""
    __tablename__ = "sender_rules"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("email_categories.id", ondelete="CASCADE"), nullable=False)
    pattern = Column(String, nullable=False)  # Domain or pattern to match
    is_domain = Column(Boolean, default=True)  # True if pattern is a domain, False if substring
    weight = Column(Integer, default=1)  # Higher weight = stronger influence
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Null for system rules
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rule_metadata = Column(JSON, nullable=True)  # Additional metadata about the rule

    # Relationships
    category = relationship("EmailCategory", back_populates="sender_rules")
    user = relationship("User", back_populates="sender_rules")

    def __repr__(self):
        return f"<SenderRule(id={self.id}, pattern={self.pattern}, is_domain={self.is_domain})>" 