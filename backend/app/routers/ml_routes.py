"""
Machine Learning routes for model training and management.
"""
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.user import User
from ..dependencies import get_current_user
from ..services.email_classifier_service import email_classifier_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ml",
    tags=["machine-learning"],
    responses={404: {"description": "Not found"}},
)

@router.post("/train", response_model=Dict[str, Any])
async def train_model(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a balanced trash classifier model"""
    try:
        # Start training in the background
        background_tasks.add_task(
            email_classifier_service.train_balanced_trash_classifier,
            db=db,
            user_id=user.id,
            save_model=True
        )
        
        return {
            "status": "training_started",
            "message": "Model training has been started in the background"
        }
    except Exception as e:
        logger.error(f"Error starting model training: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting model training: {str(e)}"
        )

@router.get("/status", response_model=Dict[str, Any])
async def get_model_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of the ML model"""
    try:
        # Check if model exists
        model_loaded = email_classifier_service.load_trash_classifier(user.id)
        
        if not model_loaded:
            # Try global model
            model_loaded = email_classifier_service.load_trash_classifier(None)
        
        # Get available models
        available_models = email_classifier_service.find_available_models()
        
        return {
            "is_model_available": model_loaded,
            "available_models": [str(p) for p in available_models],
            "message": "Model is ready" if model_loaded else "No model available"
        }
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking model status: {str(e)}"
        )

@router.post("/retrain", response_model=Dict[str, Any])
async def retrain_model(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrain the model with latest data"""
    try:
        # Start retraining in the background
        background_tasks.add_task(
            email_classifier_service.train_trash_classifier,
            db=db,
            user_id=user.id,
            save_model=True
        )
        
        return {
            "status": "retraining_started",
            "message": "Model retraining has been started in the background"
        }
    except Exception as e:
        logger.error(f"Error starting model retraining: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting model retraining: {str(e)}"
        )

@router.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_model(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate the current model's performance"""
    try:
        # Check if model exists
        model_loaded = email_classifier_service.load_trash_classifier(user.id)
        
        if not model_loaded:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No trained model available"
            )
        
        # Evaluate the model
        metrics = email_classifier_service.evaluate_model(db, user.id)
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating model: {str(e)}"
        ) 