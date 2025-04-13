from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..db import Base

class EmailCategorizationDecision(Base):
    __tablename__ = "email_categorization_decisions"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email_id = Column(UUID, ForeignKey("emails.id"), nullable=False)
    category_to = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    decision_type = Column(String, nullable=False)  # 'automatic', 'user_override', 'rule_based'
    decision_factors = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    email = relationship("Email", back_populates="categorization_decisions") 