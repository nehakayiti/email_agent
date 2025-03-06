"""
Service for managing email categories and categorization rules.
"""
import logging
from typing import Dict, List, Set, Optional, Any, Tuple, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule
from ..models.user import User
from ..constants.email_categories import (
    CATEGORY_KEYWORDS,
    SENDER_DOMAINS,
    CATEGORY_PRIORITY
)
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def initialize_system_categories(db: Session) -> List[EmailCategory]:
    """
    Initialize the database with default system categories.
    This is typically called on first setup or during migrations.
    
    Args:
        db: Database session
        
    Returns:
        List of created category instances
    """
    # Define system categories with display names
    system_categories = [
        {
            "name": "important",
            "display_name": "Important",
            "description": "High-priority and time-sensitive emails",
            "priority": CATEGORY_PRIORITY.get("important", 1)
        },
        {
            "name": "personal",
            "display_name": "Personal",
            "description": "Emails from personal contacts",
            "priority": CATEGORY_PRIORITY.get("personal", 2)
        },
        {
            "name": "primary",
            "display_name": "Primary",
            "description": "Default primary inbox emails",
            "priority": CATEGORY_PRIORITY.get("primary", 3)
        },
        {
            "name": "newsletters",
            "display_name": "Newsletters",
            "description": "News, periodicals, and subscription digests",
            "priority": CATEGORY_PRIORITY.get("newsletters", 4)
        },
        {
            "name": "updates",
            "display_name": "Updates",
            "description": "Updates and notifications from services",
            "priority": CATEGORY_PRIORITY.get("updates", 5)
        },
        {
            "name": "forums",
            "display_name": "Forums",
            "description": "Forum posts and discussions",
            "priority": CATEGORY_PRIORITY.get("forums", 6)
        },
        {
            "name": "social",
            "display_name": "Social",
            "description": "Messages from social networks",
            "priority": CATEGORY_PRIORITY.get("social", 7)
        },
        {
            "name": "promotional",
            "display_name": "Promotional",
            "description": "Promotions, marketing, and deals",
            "priority": CATEGORY_PRIORITY.get("promotional", 8)
        },
        {
            "name": "trash",
            "display_name": "Trash",
            "description": "Emails in trash",
            "priority": CATEGORY_PRIORITY.get("trash", 9)
        },
        {
            "name": "archive",
            "display_name": "Archive",
            "description": "Archived emails",
            "priority": CATEGORY_PRIORITY.get("archive", 10)
        }
    ]
    
    created_categories = []
    
    # Create or update categories
    for category_data in system_categories:
        # Check if category exists
        category = db.query(EmailCategory).filter(
            and_(
                EmailCategory.name == category_data["name"],
                EmailCategory.is_system == True
            )
        ).first()
        
        if not category:
            # Create new category
            logger.info(f"Creating system category: {category_data['name']}")
            category = EmailCategory(
                name=category_data["name"],
                display_name=category_data["display_name"],
                description=category_data["description"],
                priority=category_data["priority"],
                is_system=True,
                created_at={"timestamp": datetime.utcnow().isoformat()}
            )
            db.add(category)
            db.flush()
        else:
            # Update existing category
            logger.info(f"Updating system category: {category_data['name']}")
            category.display_name = category_data["display_name"]
            category.description = category_data["description"]
            category.priority = category_data["priority"]
        
        created_categories.append(category)
    
    db.commit()
    return created_categories

def populate_system_keywords(db: Session) -> int:
    """
    Populate the database with default system keywords for categories.
    
    Args:
        db: Database session
        
    Returns:
        Number of keywords created
    """
    # Get all system categories
    categories = db.query(EmailCategory).filter(EmailCategory.is_system == True).all()
    
    # Create a mapping of category name to ID
    category_map = {cat.name: cat.id for cat in categories}
    
    keywords_count = 0
    
    # Add keywords for each category
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if category_name in category_map:
            category_id = category_map[category_name]
            
            # Delete existing system keywords for this category (with no user_id)
            db.query(CategoryKeyword).filter(
                and_(
                    CategoryKeyword.category_id == category_id,
                    CategoryKeyword.user_id == None
                )
            ).delete()
            
            # Add new keywords
            for keyword in keywords:
                db.add(CategoryKeyword(
                    category_id=category_id,
                    keyword=keyword,
                    is_regex=False,
                    weight=1,
                    user_id=None  # System-wide keyword
                ))
                keywords_count += 1
    
    db.commit()
    logger.info(f"Added {keywords_count} system keywords")
    return keywords_count

def populate_system_sender_rules(db: Session) -> int:
    """
    Populate the database with default system sender rules.
    
    Args:
        db: Database session
        
    Returns:
        Number of sender rules created
    """
    # Get all system categories
    categories = db.query(EmailCategory).filter(EmailCategory.is_system == True).all()
    
    # Create a mapping of category name to ID
    category_map = {cat.name: cat.id for cat in categories}
    
    rules_count = 0
    
    # Delete existing system sender rules (with no user_id)
    for category_name in category_map.keys():
        db.query(SenderRule).filter(
            and_(
                SenderRule.category_id == category_map[category_name],
                SenderRule.user_id == None
            )
        ).delete()
    
    # Add sender domain rules
    for domain, category_name in SENDER_DOMAINS.items():
        if category_name in category_map:
            category_id = category_map[category_name]
            
            is_domain = "." in domain  # Simple heuristic to detect if it's a domain
            
            db.add(SenderRule(
                category_id=category_id,
                pattern=domain,
                is_domain=is_domain,
                weight=1,
                user_id=None  # System-wide rule
            ))
            rules_count += 1
    
    db.commit()
    logger.info(f"Added {rules_count} system sender rules")
    return rules_count

def get_user_categories(db: Session, user_id: UUID) -> List[Dict[str, Any]]:
    """
    Get all categories available to a user (system + user-specific).
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of category dictionaries with keyword and sender rule counts
    """
    # Get all system categories and user-specific categories
    categories = db.query(EmailCategory).filter(
        or_(
            EmailCategory.is_system == True,
            and_(
                EmailCategory.is_system == False,
                # TODO: Add user ownership check once implemented
            )
        )
    ).all()
    
    result = []
    
    for category in categories:
        # Count keywords for this category (system + user-specific)
        keyword_count = db.query(CategoryKeyword).filter(
            and_(
                CategoryKeyword.category_id == category.id,
                or_(
                    CategoryKeyword.user_id == None,
                    CategoryKeyword.user_id == user_id
                )
            )
        ).count()
        
        # Count sender rules for this category (system + user-specific)
        sender_rule_count = db.query(SenderRule).filter(
            and_(
                SenderRule.category_id == category.id,
                or_(
                    SenderRule.user_id == None,
                    SenderRule.user_id == user_id
                )
            )
        ).count()
        
        result.append({
            "id": category.id,
            "name": category.name,
            "display_name": category.display_name,
            "description": category.description,
            "priority": category.priority,
            "is_system": category.is_system,
            "keyword_count": keyword_count,
            "sender_rule_count": sender_rule_count
        })
    
    return result

def add_user_keyword(
    db: Session, 
    user_id: UUID, 
    category_name: str, 
    keyword: str
) -> Optional[CategoryKeyword]:
    """
    Add a user-specific keyword for a category.
    
    Args:
        db: Database session
        user_id: User ID
        category_name: Category name
        keyword: Keyword to add
        
    Returns:
        Created CategoryKeyword instance or None if failed
    """
    # Find category
    category = db.query(EmailCategory).filter(EmailCategory.name == category_name).first()
    
    if not category:
        logger.error(f"Category not found: {category_name}")
        return None
    
    # Check if keyword already exists for this user and category
    existing = db.query(CategoryKeyword).filter(
        and_(
            CategoryKeyword.category_id == category.id,
            CategoryKeyword.user_id == user_id,
            CategoryKeyword.keyword == keyword
        )
    ).first()
    
    if existing:
        logger.info(f"Keyword already exists: {keyword} for user {user_id} in category {category_name}")
        return existing
    
    # Create new keyword
    new_keyword = CategoryKeyword(
        category_id=category.id,
        keyword=keyword,
        user_id=user_id,
        weight=1
    )
    
    db.add(new_keyword)
    db.commit()
    
    logger.info(f"Added user keyword: {keyword} for user {user_id} in category {category_name}")
    return new_keyword

def add_user_sender_rule(
    db: Session, 
    user_id: UUID, 
    category_name: str, 
    pattern: str, 
    is_domain: bool = True
) -> Optional[SenderRule]:
    """
    Add a user-specific sender rule for a category.
    
    Args:
        db: Database session
        user_id: User ID
        category_name: Category name
        pattern: Domain or pattern to match
        is_domain: Whether the pattern is a full domain
        
    Returns:
        Created SenderRule instance or None if failed
    """
    # Find category
    category = db.query(EmailCategory).filter(EmailCategory.name == category_name).first()
    
    if not category:
        logger.error(f"Category not found: {category_name}")
        return None
    
    # Check if rule already exists for this user and category
    existing = db.query(SenderRule).filter(
        and_(
            SenderRule.category_id == category.id,
            SenderRule.user_id == user_id,
            SenderRule.pattern == pattern
        )
    ).first()
    
    if existing:
        logger.info(f"Sender rule already exists: {pattern} for user {user_id} in category {category_name}")
        return existing
    
    # Create new rule
    new_rule = SenderRule(
        category_id=category.id,
        pattern=pattern,
        is_domain=is_domain,
        user_id=user_id,
        weight=1
    )
    
    db.add(new_rule)
    db.commit()
    
    logger.info(f"Added user sender rule: {pattern} for user {user_id} in category {category_name}")
    return new_rule

def get_categorization_rules(
    db: Session, 
    user_id: Optional[UUID] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Get all categorization rules (keywords and sender patterns) for the system and optionally a specific user.
    Used by the categorization engine to efficiently categorize emails.
    
    Args:
        db: Database session
        user_id: Optional user ID to include user-specific rules
        
    Returns:
        Dictionary with categorization rules
    """
    rules = {
        "categories": {},
        "keywords": {},
        "senders": {}
    }
    
    # Get all categories
    category_filter = [EmailCategory.is_system == True]
    if user_id is not None:
        # Also add user's custom categories (to be implemented)
        pass
    
    categories = db.query(EmailCategory).filter(*category_filter).all()
    
    # Create a mapping of category ID to name and details
    category_map = {
        cat.id: {
            "name": cat.name,
            "priority": cat.priority
        } for cat in categories
    }
    
    rules["categories"] = {cat_id: details for cat_id, details in category_map.items()}
    
    # Get keywords
    keyword_filter = [CategoryKeyword.user_id == None]  # System keywords
    if user_id is not None:
        # Also add user's keywords
        keyword_filter = [or_(
            CategoryKeyword.user_id == None,
            CategoryKeyword.user_id == user_id
        )]
    
    keywords = db.query(CategoryKeyword).filter(*keyword_filter).all()
    
    # Group keywords by category
    keyword_dict = {}
    for kw in keywords:
        category_id = kw.category_id
        if category_id not in keyword_dict:
            keyword_dict[category_id] = []
        
        keyword_dict[category_id].append({
            "keyword": kw.keyword,
            "is_regex": kw.is_regex,
            "weight": kw.weight
        })
    
    rules["keywords"] = keyword_dict
    
    # Get sender rules
    sender_filter = [SenderRule.user_id == None]  # System rules
    if user_id is not None:
        # Also add user's rules
        sender_filter = [or_(
            SenderRule.user_id == None,
            SenderRule.user_id == user_id
        )]
    
    senders = db.query(SenderRule).filter(*sender_filter).all()
    
    # Group sender rules by category
    sender_dict = {}
    for rule in senders:
        category_id = rule.category_id
        if category_id not in sender_dict:
            sender_dict[category_id] = []
        
        sender_dict[category_id].append({
            "pattern": rule.pattern,
            "is_domain": rule.is_domain,
            "weight": rule.weight
        })
    
    rules["senders"] = sender_dict
    
    return rules 