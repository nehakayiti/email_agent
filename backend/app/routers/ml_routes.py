from typing import Dict, Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
import logging

from ..dependencies import get_db, get_current_user
from ..services.email_classifier_service import train_balanced_trash_classifier
from ..models.user import User
from ..db import SessionLocal

router = APIRouter()

@router.post("/train-classifier-balanced", response_model=Dict[str, Any])
async def train_classifier_balanced(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Train the email classifier with an improved balanced dataset approach
    using Gmail labels as ground truth.
    """
    user_id = current_user.id
    
    # Run training in the background
    background_tasks.add_task(
        train_classifier_balanced_task,
        db,
        user_id
    )
    
    return {
        "status": "success",
        "message": "Balanced classifier training started in the background"
    }

async def train_classifier_balanced_task(db: Session, user_id: UUID):
    """Background task to train the classifier with balanced data"""
    # Create new session for background task
    new_db = SessionLocal()
    try:
        # Train classifier with improved methodology
        results = train_balanced_trash_classifier(
            db=new_db,
            user_id=user_id,
            save_model=True,
            test_size=0.2
        )
        
        logging.info(f"[ML-API] Balanced classifier training completed for user {user_id}")
        logging.info(f"[ML-API] Results: {results}")
        
        # Update user's model metadata
        user = new_db.query(User).filter(User.id == user_id).first()
        if user:
            user.ml_model_updated_at = datetime.now(timezone.utc)
            user.ml_model_metrics = results
            new_db.commit()
    
    except Exception as e:
        logging.error(f"[ML-API] Error in balanced classifier training: {str(e)}", exc_info=True)
    finally:
        new_db.close() 