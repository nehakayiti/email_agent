"""
API routes for email management operations.
"""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import UUID
from sqlalchemy import or_, and_, func
from ..db import get_db
from ..models.user import User
from ..models.email import Email
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
from ..models.email_trash_event import EmailTrashEvent
from ..services.email_classifier_service import email_classifier_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/email-management",
    tags=["Email Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/classifier/train", response_model=Dict[str, Any])
async def train_classifier(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any] = Body(default={}),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Train the Naive Bayes classifier for trash email detection.
    Training is performed asynchronously in the background.
    
    Args:
        request: Optional request body with training parameters
        
    Returns:
        Dictionary with status
    """
    # Extract test_size from request if provided
    test_size = request.get('test_size', 0.2)
    
    # Start the training in the background
    background_tasks.add_task(email_classifier_service.train_trash_classifier, db, user.id, True, test_size)
    
    return {
        "status": "training_started",
        "message": "Classifier training has been started in the background",
        "test_size": test_size
    }

@router.get("/classifier/status", response_model=Dict[str, Any])
async def get_classifier_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of the Naive Bayes classifier.
    
    Returns:
        Dictionary with classifier status
    """
    # Try to load the model to check if it exists
    model_loaded = email_classifier_service.load_trash_classifier(user.id)
    
    # If user-specific model doesn't exist, try the global model
    if not model_loaded:
        model_loaded = email_classifier_service.load_trash_classifier(None)
    
    # Get event counts for training data information
    trash_events_count = db.query(EmailTrashEvent).filter(
        EmailTrashEvent.user_id == user.id
    ).count()
    
    return {
        "is_model_available": model_loaded,
        "trash_events_count": trash_events_count,
        "recommended_min_events": 10,
        "message": "Model is ready for use" if model_loaded else "Model needs training"
    }

@router.post("/classifier/retrain-all", response_model=Dict[str, Any])
async def admin_retrain_all_models(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to retrain all models (global and per-user).
    Requires admin privileges.
    
    Returns:
        Dictionary with status
    """
    # Check if user is admin
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Start the retraining in the background
    background_tasks.add_task(email_classifier_service.retrain_all_models, db)
    
    return {
        "status": "retraining_started",
        "message": "All models retraining has been started in the background"
    }

@router.post("/classifier/bootstrap", response_model=Dict[str, Any])
async def bootstrap_classifier_data(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any] = Body(default={}),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bootstrap the classifier training data by using existing trash emails.
    This allows training the model without requiring additional user actions.
    
    Args:
        request: Optional request body with training parameters
    
    Returns:
        Dictionary with status
    """
    # Extract test_size from request if provided
    test_size = request.get('test_size', 0.2)
    
    # Start the bootstrapping in the background
    result = email_classifier_service.bootstrap_training_data(db, user.id)
    
    return {
        "status": "success",
        "message": "Training data has been bootstrapped from existing trash emails",
        "events_created": result.get("events_created", 0),
        "total_events": result.get("total_events", 0),
        "test_size": test_size
    }

@router.get("/classifier/metrics", response_model=Dict[str, Any])
async def get_model_metrics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for the trained classifier model.
    
    Returns:
        Dictionary with model metrics
    """
    # Load the model to ensure we have the latest version
    model_loaded = email_classifier_service.load_trash_classifier(user.id)
    
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trained model available. Train a model first."
        )
        
    from ..utils.naive_bayes_classifier import classifier
    
    # Dummy metrics if real metrics aren't available in the model yet
    metrics = getattr(classifier, 'evaluation_metrics', None)
    
    if not metrics:
        # If we don't have stored metrics, provide reasonable defaults
        from ..services.email_classifier_service import evaluate_model
        metrics = evaluate_model(db, user.id)
    
    return metrics

@router.get("/classifier/evaluate", response_model=Dict[str, Any])
async def evaluate_classifier(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluate the trained classifier model on test data.
    
    Returns:
        Dictionary with evaluation metrics
    """
    # Check if model exists
    model_loaded = email_classifier_service.load_trash_classifier(user.id)
    
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trained model available. Train a model first."
        )
    
    # Import the evaluation function
    from ..services.email_classifier_service import evaluate_model
    
    # Evaluate the model
    metrics = evaluate_model(db, user.id)
    
    return metrics

class ReprocessFilter(BaseModel):
    """Filter criteria for email reprocessing"""
    categories: Optional[List[str]] = None
    date_from: Optional[date] = None  
    date_to: Optional[date] = None
    search: Optional[str] = None
    include_reprocessed: Optional[bool] = Field(default=False, description="Whether to include already reprocessed emails")
    force_reprocess: Optional[bool] = Field(default=False, description="Whether to mark all matching emails as dirty")

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
    weight: int = 1

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

class SenderRuleUpdateRequest(BaseModel):
    """Request model for updating a sender rule"""
    weight: int

class KeywordUpdateRequest(BaseModel):
    """Request model for updating a keyword"""
    weight: int

class SenderRulePatternUpdateRequest(BaseModel):
    """Request model for updating a sender rule pattern"""
    pattern: str
    is_domain: bool

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
        
        # If force_reprocess is True, mark matching emails as dirty
        if filter_criteria and filter_criteria.force_reprocess:
            query = db.query(Email).filter(Email.user_id == current_user.id)
            
            # Apply filters if any
            if filter_dict:
                from ..utils.filter_utils import apply_email_filters
                query = apply_email_filters(query, filter_dict)
            
            # Mark matching emails as dirty
            count = query.update({"is_dirty": True})
            db.commit()
            logger.info(f"Marked {count} emails as dirty for reprocessing")
        
        # Pass include_reprocessed parameter to reprocess_emails
        include_reprocessed = filter_criteria.include_reprocessed if filter_criteria else False
        result = reprocess_emails(db, current_user.id, filter_dict, include_reprocessed)
        
        # Transform the result to match the ReprocessResponse model
        return {
            "total": result.get("reprocessed_count", 0),
            "processed": result.get("reprocessed_count", 0),
            "category_changes": result.get("category_changes", {}),
            "importance_changes": 0  # This field is not tracked in reprocess_emails
        }
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
            rule_data.is_domain,
            rule_data.weight
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

@router.delete("/categories/{category_name}")
async def delete_category(
    category_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a category.
    
    Only non-system categories can be deleted. System categories are protected.
    When a category is deleted, all associated keywords and sender rules are also deleted.
    """
    try:
        # Find the category
        category = db.query(EmailCategory).filter(EmailCategory.name == category_name).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category '{category_name}' not found"
            )
        
        # Prevent deletion of system categories
        if category.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"System category '{category_name}' cannot be deleted"
            )
        
        # Delete the category (cascade will handle associated keywords and sender rules)
        db.delete(category)
        
        # We need to update any emails that were in this category to a default category
        # Find the highest priority system category as fallback
        default_category = db.query(EmailCategory).filter(
            EmailCategory.is_system == True
        ).order_by(EmailCategory.priority).first()
        
        if default_category:
            # Update emails in the deleted category to the default category
            db.query(Email).filter(
                Email.user_id == current_user.id,
                Email.category == category_name
            ).update({
                'category': default_category.name,
                'labels': func.array_append(Email.labels, 'EA_NEEDS_LABEL_UPDATE')
            })
        
        db.commit()
        
        return {"success": True, "message": f"Category '{category_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category: {str(e)}"
        )

@router.patch("/sender-rules/{rule_id}", response_model=SenderRuleItem)
async def update_sender_rule(
    rule_id: int,
    rule_data: SenderRuleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a sender rule's properties.
    
    Currently supports updating the weight of a sender rule.
    For user-created rules, updates the rule directly.
    For system rules, creates a user override with the new weight,
    first deleting any existing user overrides to prevent duplication.
    """
    try:
        # Find the rule
        rule = db.query(SenderRule).filter(SenderRule.id == rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sender rule with ID {rule_id} not found"
            )
        
        # For user rules, update directly
        if rule.user_id == current_user.id:
            rule.weight = rule_data.weight
            db.commit()
            db.refresh(rule)
            return rule
        
        # For system rules, create a user override
        if rule.user_id is None:
            # First, delete any existing user overrides for this rule to prevent duplicates
            db.query(SenderRule).filter(
                and_(
                    SenderRule.pattern == rule.pattern,
                    SenderRule.category_id == rule.category_id,
                    SenderRule.user_id == current_user.id
                )
            ).delete()
            
            # Create new override
            new_rule = SenderRule(
                category_id=rule.category_id,
                pattern=rule.pattern,
                is_domain=rule.is_domain,
                weight=rule_data.weight,
                user_id=current_user.id
            )
            db.add(new_rule)
            db.commit()
            db.refresh(new_rule)
            return new_rule
        
        # Not a system rule or user's rule
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own sender rules or create overrides for system rules"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sender rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating sender rule: {str(e)}"
        )

@router.delete("/keywords/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a keyword.
    
    Only user-specific keywords can be deleted directly.
    System keywords can be overridden but not deleted.
    """
    try:
        # Find the keyword
        keyword = db.query(CategoryKeyword).filter(CategoryKeyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Keyword with ID {keyword_id} not found"
            )
        
        # Only allow deleting user's own keywords
        if keyword.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own keywords"
            )
        
        # Delete the keyword
        db.delete(keyword)
        db.commit()
        
        return {"success": True, "message": "Keyword deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting keyword: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting keyword: {str(e)}"
        )

@router.patch("/sender-rules/{rule_id}/pattern", response_model=SenderRuleItem)
async def update_sender_rule_pattern(
    rule_id: int,
    rule_data: SenderRulePatternUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a sender rule's pattern and domain flag.
    For user-created rules, updates the rule directly.
    For system rules, creates a user override with the new pattern and domain flag,
    first deleting any existing user overrides to prevent duplication.
    """
    try:
        # Find the rule
        rule = db.query(SenderRule).filter(SenderRule.id == rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sender rule with ID {rule_id} not found"
            )

        # Check for duplicate sender rule (excluding the current rule)
        duplicate = db.query(SenderRule).filter(
            SenderRule.pattern == rule_data.pattern,
            SenderRule.is_domain == rule_data.is_domain,
            SenderRule.user_id == current_user.id,
            SenderRule.id != rule_id
        ).first()
        if duplicate:
            # Get the category info for the duplicate
            category = db.query(EmailCategory).filter(EmailCategory.id == duplicate.category_id).first()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "A sender rule for this domain or pattern already exists.",
                    "category": category.name if category else None,
                    "category_display_name": category.display_name if category else None
                },
                headers={"X-Error": "DuplicateSenderRule"}
            )

        # For user rules, update directly
        if rule.user_id == current_user.id:
            rule.pattern = rule_data.pattern
            rule.is_domain = rule_data.is_domain
            db.commit()
            db.refresh(rule)
            return rule

        # For system rules, create a user override with original weight but new pattern
        if rule.user_id is None:
            # First, delete any existing user overrides for this rule to prevent duplicates
            db.query(SenderRule).filter(
                and_(
                    SenderRule.category_id == rule.category_id,
                    SenderRule.user_id == current_user.id,
                    # This condition identifies likely overrides of the same rule
                    or_(
                        SenderRule.pattern == rule.pattern,
                        SenderRule.pattern == rule_data.pattern
                    )
                )
            ).delete()

            # Create new override
            new_rule = SenderRule(
                category_id=rule.category_id,
                pattern=rule_data.pattern,
                is_domain=rule_data.is_domain,
                weight=rule.weight,
                user_id=current_user.id
            )
            db.add(new_rule)
            db.commit()
            db.refresh(new_rule)
            return new_rule

        # Not a system rule or user's rule
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own sender rules or create overrides for system rules"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sender rule pattern: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating sender rule pattern: {str(e)}"
        )

@router.patch("/keywords/{keyword_id}", response_model=KeywordItem)
async def update_keyword(
    keyword_id: int,
    keyword_data: KeywordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a keyword's properties.
    
    Currently supports updating the weight of a keyword.
    For user-created keywords, updates the keyword directly.
    For system keywords, creates a user override with the new weight,
    first deleting any existing user overrides to prevent duplication.
    """
    try:
        # Find the keyword
        keyword = db.query(CategoryKeyword).filter(CategoryKeyword.id == keyword_id).first()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Keyword with ID {keyword_id} not found"
            )
        
        # For user keywords, update directly
        if keyword.user_id == current_user.id:
            keyword.weight = keyword_data.weight
            db.commit()
            db.refresh(keyword)
            return keyword
        
        # For system keywords, create a user override
        if keyword.user_id is None:
            # First, delete any existing user overrides for this keyword to prevent duplicates
            db.query(CategoryKeyword).filter(
                and_(
                    CategoryKeyword.keyword == keyword.keyword,
                    CategoryKeyword.category_id == keyword.category_id,
                    CategoryKeyword.user_id == current_user.id
                )
            ).delete()
            
            # Create new override
            new_keyword = CategoryKeyword(
                category_id=keyword.category_id,
                keyword=keyword.keyword,
                is_regex=keyword.is_regex,
                weight=keyword_data.weight,
                user_id=current_user.id
            )
            db.add(new_keyword)
            db.commit()
            db.refresh(new_keyword)
            return new_keyword
        
        # Not a system keyword or user's keyword
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own keywords or create overrides for system keywords"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating keyword: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating keyword: {str(e)}"
        )

@router.delete("/sender-rules/{rule_id}")
async def delete_sender_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a sender rule.
    
    Only user-specific sender rules can be deleted directly.
    System sender rules can be overridden but not deleted.
    """
    try:
        # Find the rule
        rule = db.query(SenderRule).filter(SenderRule.id == rule_id).first()
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sender rule with ID {rule_id} not found"
            )
        
        # Only allow deleting user's own rules
        if rule.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own sender rules"
            )
        
        # Delete the rule
        db.delete(rule)
        db.commit()
        
        return {"success": True, "message": "Sender rule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sender rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting sender rule: {str(e)}"
        ) 