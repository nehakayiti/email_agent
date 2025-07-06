from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func
import uuid
from ..db import Base
from .sender_rule import SenderRule  # Import SenderRule from its own module

class EmailCategory(Base):
    """
    Base email category model
    """
    __tablename__ = "email_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, default=50)  # Lower numbers = higher priority
    is_system = Column(Boolean, default=False)  # System categories cannot be deleted
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())  # Timestamps with timezone
    
    # Action Engine fields
    action = Column(String(50), nullable=True)  # ARCHIVE, TRASH, etc.
    action_delay_days = Column(Integer, nullable=True)  # Days to wait before applying action
    action_enabled = Column(Boolean, default=False)  # Whether action is enabled for this category
    
    # Relationships
    keywords = relationship("CategoryKeyword", back_populates="category", cascade="all, delete-orphan")
    sender_rules = relationship("SenderRule", back_populates="category", cascade="all, delete-orphan")
    proposed_actions = relationship("ProposedAction", back_populates="category", cascade="all, delete-orphan")
    
    # Users can share the same category names, but system categories must be unique
    __table_args__ = (
        UniqueConstraint('name', 'is_system', name='uq_category_name_system'),
        Index('idx_email_category_name', 'name'),
    )
    
    def __repr__(self):
        return f"<EmailCategory {self.name}>"
    
    def has_action_rule(self) -> bool:
        """Check if this category has an action rule configured"""
        return (
            self.action is not None and 
            self.action_delay_days is not None and 
            self.action_enabled
        )
    
    def get_action_rule(self) -> dict:
        """Get the action rule configuration for this category"""
        if not self.has_action_rule():
            return None
        return {
            'action': self.action,
            'delay_days': self.action_delay_days,
            'enabled': self.action_enabled
        }
    
    def set_action_rule(self, action: str, delay_days: int, enabled: bool = True) -> None:
        """Set the action rule configuration for this category"""
        self.action = action
        self.action_delay_days = delay_days
        self.action_enabled = enabled
    
    def clear_action_rule(self) -> None:
        """Clear the action rule configuration for this category"""
        self.action = None
        self.action_delay_days = None
        self.action_enabled = False


class CategoryKeyword(Base):
    """
    Keywords associated with email categories for subject line matching
    """
    __tablename__ = "category_keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("email_categories.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String, nullable=False)
    is_regex = Column(Boolean, default=False)  # If true, keyword is a regex pattern
    weight = Column(Integer, default=1)  # Higher weight = stronger influence
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Null = applies to all users
    
    # Relationships
    category = relationship("EmailCategory", back_populates="keywords")
    
    # Indexing for fast lookup
    __table_args__ = (
        Index('idx_category_keyword', 'keyword'),
        Index('idx_category_keyword_category', 'category_id'),
        Index('idx_category_keyword_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<CategoryKeyword {self.keyword} for {self.category.name}>" 