from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
import uuid
from ..db import Base

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
    created_at = Column(JSONB, nullable=True)  # Timestamps with timezone
    
    # Relationships
    keywords = relationship("CategoryKeyword", back_populates="category", cascade="all, delete-orphan")
    sender_rules = relationship("SenderRule", back_populates="category", cascade="all, delete-orphan")
    
    # Users can share the same category names, but system categories must be unique
    __table_args__ = (
        UniqueConstraint('name', 'is_system', name='uq_category_name_system'),
        Index('idx_email_category_name', 'name'),
    )
    
    def __repr__(self):
        return f"<EmailCategory {self.name}>"


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


class SenderRule(Base):
    """
    Rules for categorizing emails based on sender information
    """
    __tablename__ = "sender_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("email_categories.id", ondelete="CASCADE"), nullable=False)
    pattern = Column(String, nullable=False)  # Domain or pattern to match in sender email
    is_domain = Column(Boolean, default=True)  # True if pattern is a full domain, False if substring
    weight = Column(Integer, default=1)  # Higher weight = stronger influence
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Null = applies to all users
    
    # Relationships
    category = relationship("EmailCategory", back_populates="sender_rules")
    
    # Indexing for fast lookup
    __table_args__ = (
        Index('idx_sender_rule_pattern', 'pattern'),
        Index('idx_sender_rule_category', 'category_id'),
        Index('idx_sender_rule_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<SenderRule {self.pattern} for {self.category.name}>" 