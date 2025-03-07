"""
API routes for email management operations.
"""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import UUID
from sqlalchemy import or_, and_
from ..db import get_db
from ..models.user import User
from ..dependencies import get_current_user
from ..services.email_processor import reprocess_emails
from ..services.category_service import (
    initialize_system_categories,
    populate_system_keywords,
    populate_system_sender_rules,
    get_user_categories,
    add_user_keyword,
    add_user_sender_rule
)
from ..models.email_category import EmailCategory, CategoryKeyword, SenderRule

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/email-management",
    tags=["Email Management"],
    responses={404: {"description": "Not found"}},
)

class ReprocessFilter(BaseModel):
    """Filter criteria for email reprocessing"""
    categories: Optional[List[str]] = None
    date_from: Optional[date] = None  
    date_to: Optional[date] = None
    search: Optional[str] = None

class ReprocessResponse(BaseModel):
    """Response model for email reprocessing"""
    total: int
    processed: int
    category_changes: Dict[str, int]
    importance_changes: int

class CategoryItem(BaseModel):
    """Email category item"""
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    priority: int
    is_system: bool
    keyword_count: int
    sender_rule_count: int

class KeywordRequest(BaseModel):
    """Request model for adding a keyword"""
    category_name: str
    keyword: str

class SenderRuleRequest(BaseModel):
    """Request model for adding a sender rule"""
    category_name: str
    pattern: str
    is_domain: bool = True

class CreateCategoryRequest(BaseModel):
    """Request model for creating a new category"""
    name: str
    display_name: str
    description: Optional[str] = None
    priority: int = 50

class KeywordItem(BaseModel):
    """Category keyword item"""
    id: int
    keyword: str
    is_regex: bool
    weight: int
    user_id: Optional[UUID] = None
    
class SenderRuleItem(BaseModel):
    """Sender rule item"""
    id: int
    pattern: str
    is_domain: bool
    weight: int
    user_id: Optional[UUID] = None

@router.post("/reprocess", response_model=ReprocessResponse)
async def reprocess_user_emails(
    filter_criteria: Optional[ReprocessFilter] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reprocess existing emails with updated categorization rules.
    
    Applies the latest categorization and importance calculation rules to
    existing emails, allowing for updating classifications after rule changes.
    
    Can be filtered to only reprocess certain email categories, date ranges,
    or emails matching a search term.
    """
    try:
        if filter_criteria is None:
            filter_dict = None
        else:
            filter_dict = filter_criteria.dict(exclude_none=True)
            
            # Convert date objects to datetime
            if filter_dict.get('date_from'):
                filter_dict['date_from'] = datetime.combine(
                    filter_dict['date_from'], datetime.min.time()
                )
            if filter_dict.get('date_to'):
                filter_dict['date_to'] = datetime.combine(
                    filter_dict['date_to'], datetime.max.time()
                )
        
        result = reprocess_emails(db, current_user.id, filter_dict)
        return result
    except Exception as e:
        logger.error(f"Error reprocessing emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reprocessing emails: {str(e)}"
        )

@router.get("/categories", response_model=List[CategoryItem])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all categories available to the current user.
    
    Returns both system categories and user-specific categories,
    along with the count of keywords and sender rules for each.
    """
    try:
        categories = get_user_categories(db, current_user.id)
        return categories
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories: {str(e)}"
        )

@router.post("/keywords")
async def add_keyword(
    keyword_data: KeywordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new keyword to a category for the current user.
    
    This allows users to customize categorization based on 
    keywords that are important to them.
    """
    try:
        result = add_user_keyword(
            db, 
            current_user.id, 
            keyword_data.category_name, 
            keyword_data.keyword
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add keyword. Category '{keyword_data.category_name}' may not exist."
            )
        
        return {"success": True, "message": "Keyword added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding keyword: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding keyword: {str(e)}"
        )

@router.post("/sender-rules")
async def add_sender_rule(
    rule_data: SenderRuleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a new sender rule to a category for the current user.
    
    This allows users to categorize emails from specific domains
    or sender patterns according to their preferences.
    """
    try:
        result = add_user_sender_rule(
            db, 
            current_user.id, 
            rule_data.category_name, 
            rule_data.pattern,
            rule_data.is_domain
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add sender rule. Category '{rule_data.category_name}' may not exist."
            )
        
        return {"success": True, "message": "Sender rule added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding sender rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding sender rule: {str(e)}"
        )

@router.post("/initialize-categories", status_code=status.HTTP_201_CREATED)
async def initialize_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize system categories, keywords, and sender rules.
    
    This is an admin-only endpoint that populates the database with
    the default categorization rules. It should be called during system
    setup or when resetting to defaults.
    
    Note: In production, this should be restricted to admin users only.
    """
    # TODO: Add proper admin check
    try:
        categories = initialize_system_categories(db)
        keywords_count = populate_system_keywords(db)
        rules_count = populate_system_sender_rules(db)
        
        return {
            "success": True,
            "categories_count": len(categories),
            "keywords_count": keywords_count,
            "sender_rules_count": rules_count
        }
    except Exception as e:
        logger.error(f"Error initializing categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing categories: {str(e)}"
        )

@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CreateCategoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new custom category for the current user.
    
    This allows users to create their own organizational structure
    for emails beyond the default system categories.
    """
    try:
        # Check if a category with this name already exists
        existing = db.query(EmailCategory).filter(
            EmailCategory.name == category_data.name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists"
            )
        
        # Create new category
        new_category = EmailCategory(
            name=category_data.name,
            display_name=category_data.display_name,
            description=category_data.description,
            priority=category_data.priority,
            is_system=False,  # User-created categories are not system categories
            created_at={"timestamp": datetime.utcnow().isoformat(), "user_id": str(current_user.id)}
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        # Return the created category
        return {
            "id": new_category.id,
            "name": new_category.name,
            "display_name": new_category.display_name,
            "description": new_category.description,
            "priority": new_category.priority,
            "is_system": new_category.is_system,
            "keyword_count": 0,
            "sender_rule_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating category: {str(e)}"
        )

@router.get("/categories/{category_name}/keywords", response_model=List[KeywordItem])
async def get_category_keywords(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all keywords for a specific category.
    
    Returns both system keywords and user-specific keywords for the category.
    """
    try:
        # Find the category
        category = db.query(EmailCategory).filter(EmailCategory.name == category_name).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_name}' not found"
            )
        
        # Get keywords for this category (system + user-specific)
        keywords = db.query(CategoryKeyword).filter(
            and_(
                CategoryKeyword.category_id == category.id,
                or_(
                    CategoryKeyword.user_id == None,
                    CategoryKeyword.user_id == current_user.id
                )
            )
        ).all()
        
        return keywords
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category keywords: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category keywords: {str(e)}"
        )

@router.get("/categories/{category_name}/sender-rules", response_model=List[SenderRuleItem])
async def get_category_sender_rules(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all sender rules for a specific category.
    
    Returns both system sender rules and user-specific sender rules for the category.
    """
    try:
        # Find the category
        category = db.query(EmailCategory).filter(EmailCategory.name == category_name).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_name}' not found"
            )
        
        # Get sender rules for this category (system + user-specific)
        sender_rules = db.query(SenderRule).filter(
            and_(
                SenderRule.category_id == category.id,
                or_(
                    SenderRule.user_id == None,
                    SenderRule.user_id == current_user.id
                )
            )
        ).all()
        
        return sender_rules
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category sender rules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category sender rules: {str(e)}"
        ) 