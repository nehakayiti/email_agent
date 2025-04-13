from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db import Base

class CategorizationFeedback(Base):
    __tablename__ = "categorization_feedback"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email_id = Column(UUID, ForeignKey("emails.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    original_category = Column(String, nullable=True)
    new_category = Column(String, nullable=False)
    feedback_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    feedback_metadata = Column(JSON, nullable=True)

    # Relationships
    email = relationship("Email", back_populates="categorization_feedback")
    user = relationship("User", back_populates="categorization_feedback") 