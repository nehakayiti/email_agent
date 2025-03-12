from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.orm import Session
import os
from pathlib import Path
from uuid import UUID
from ..models.email import Email
from ..models.email_operation import EmailOperation, OperationType
from ..models.email_trash_event import EmailTrashEvent
from ..utils.naive_bayes_classifier import classifier, train_classifier, record_trash_event
import time

logger = logging.getLogger(__name__)

# Get the absolute path to the project root directory
PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
# Directory to store trained models (absolute path)
MODELS_DIR = PROJECT_ROOT / "models"

def ensure_models_directory():
    """Create models directory if it doesn't exist"""
    try:
        # Make sure the models directory exists
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # Check if the directory is writable
        test_file_path = MODELS_DIR / ".write_test"
        try:
            with open(test_file_path, 'w') as f:
                f.write('test')
            os.remove(test_file_path)
            logger.info(f"[ML-SERVICE] Models directory exists and is writable at {MODELS_DIR}")
        except Exception as e:
            logger.error(f"[ML-SERVICE] Models directory exists but is not writable: {str(e)}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"[ML-SERVICE] Error creating models directory: {str(e)}")
        return False

def get_model_path(user_id: Optional[UUID] = None) -> Path:
    """
    Get the path to the model file for a user
    
    Args:
        user_id: Optional UUID of the user, or None for global model
        
    Returns:
        Path object for the model file
    """
    ensure_models_directory()
    if user_id:
        logger.debug(f"[ML-SERVICE] Using user-specific model for user {user_id}")
        return MODELS_DIR / f"trash_classifier_{user_id}.pkl"
    else:
        logger.debug(f"[ML-SERVICE] Using global model")
        return MODELS_DIR / "trash_classifier_global.pkl"

def train_trash_classifier(
    db: Session, 
    user_id: Optional[UUID] = None,
    save_model: bool = True
) -> Dict[str, Any]:
    """
    Train a Naive Bayes classifier for predicting if emails should be moved to trash
    
    Args:
        db: Database session
        user_id: Optional user ID to train a user-specific model
        save_model: Whether to save the trained model to disk
        
    Returns:
        Dictionary with training results
    """
    logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
    logger.info(f"║                  TRAINING EMAIL CLASSIFIER                               ║")
    logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
    
    start_time = time.time()
    logger.info(f"[ML-SERVICE] Starting trash classifier training for {'user ' + str(user_id) if user_id else 'global model'}")
    
    # Get training data from the database
    query = db.query(EmailTrashEvent)
    if user_id:
        query = query.filter(EmailTrashEvent.user_id == user_id)
    
    trash_events = query.all()
    total_events = len(trash_events)
    
    if total_events < 5:
        logger.warning(f"[ML-SERVICE] Insufficient training data: only {total_events} events available (minimum 5 required)")
        return {
            "status": "error",
            "message": f"Insufficient training data ({total_events} events)",
            "trained": False,
            "events_count": total_events
        }
    
    logger.info(f"[ML-SERVICE] Training with {total_events} trash events")
    
    # Extract features and labels from trash events
    features = []
    labels = []
    
    for event in trash_events:
        features.append({
            "sender": event.sender_email,
            "subject": event.subject,
            "snippet": event.snippet
        })
        labels.append(1 if event.event_type == 'moved_to_trash' else 0)
    
    # Train the classifier
    try:
        accuracy = train_classifier(features, labels, user_id)
        
        # Save the model if requested
        if save_model:
            model_path = get_model_path(user_id)
            logger.info(f"[ML-SERVICE] Saving trained model to {model_path}")
            classifier.save_model(str(model_path))
    
        training_time = time.time() - start_time
        logger.info(f"[ML-SERVICE] Training completed in {training_time:.2f}s with accuracy: {accuracy:.4f}")
        logger.info(f"[ML-SERVICE] Model is now ready for classification")
        
        return {
            "status": "success",
            "message": "Classifier trained successfully",
            "trained": True,
            "events_count": total_events,
            "accuracy": accuracy,
            "training_time": f"{training_time:.2f}s"
        }
    except Exception as e:
        logger.error(f"[ML-SERVICE] Error training classifier: {str(e)}")
        return {
            "status": "error",
            "message": f"Error training classifier: {str(e)}",
            "trained": False,
            "events_count": total_events
        }

def load_trash_classifier(user_id: Optional[UUID] = None) -> bool:
    """
    Load a trained classifier from disk
    
    Args:
        user_id: Optional user ID to load a user-specific model
        
    Returns:
        True if the model was loaded successfully, False otherwise
    """
    model_path = get_model_path(user_id)
    
    if not model_path.exists():
        logger.warning(f"[ML-SERVICE] No trained model found at {model_path}")
        
        # If user model doesn't exist, try loading global model
        if user_id:
            logger.info(f"[ML-SERVICE] Attempting to load global model as fallback")
            global_model_path = get_model_path(None)
            
            if not global_model_path.exists():
                logger.warning(f"[ML-SERVICE] No global model found at {global_model_path}")
                return False
                
            try:
                classifier.load_model(str(global_model_path))
                logger.info(f"[ML-SERVICE] Successfully loaded global model as fallback")
                return True
            except Exception as e:
                logger.error(f"[ML-SERVICE] Error loading global model: {str(e)}")
                return False
        
        return False
        
    try:
        classifier.load_model(str(model_path))
        logger.info(f"[ML-SERVICE] Successfully loaded model for {'user ' + str(user_id) if user_id else 'global model'}")
        return True
    except Exception as e:
        logger.error(f"[ML-SERVICE] Error loading model: {str(e)}")
        return False

def record_trash_operations(db: Session, operations: List[EmailOperation]) -> None:
    """
    Record trash events based on email operations for future ML training.
    
    Args:
        db: Database session
        operations: List of completed email operations
    """
    for operation in operations:
        # Only process delete operations (trash)
        if operation.operation_type != OperationType.DELETE:
            continue
        
        # Get the email
        email = operation.email
        if not email:
            continue
        
        # Prepare email data
        email_data = {
            'id': email.id,
            'gmail_id': email.gmail_id,
            'subject': email.subject,
            'from_email': email.from_email,
            'snippet': email.snippet,
            'labels': email.labels,
            'is_read': email.is_read,
            'raw_data': email.raw_data
        }
        
        # Record the trash event
        record_trash_event(
            db=db,
            email_id=email.id,
            user_id=email.user_id,
            event_type='moved_to_trash',
            email_data=email_data,
            is_auto_categorized=False,
            categorization_source='user'
        )
        
        logger.info(f"Recorded trash event for email {email.id} from operation {operation.id}")

def retrain_all_models(db: Session) -> Dict[str, Any]:
    """
    Retrain all trash classifier models (global and per-user).
    
    This is useful after collecting a significant amount of new training data.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with training results
    """
    results = {}
    
    # Train global model
    global_results = train_trash_classifier(db, save_model=True)
    results['global'] = global_results
    
    # TODO: Uncomment to train per-user models when needed
    # # Train user-specific models for active users
    # # Get users with enough trash events for personalized models
    # users_query = db.query(EmailTrashEvent.user_id,
    #                        func.count(EmailTrashEvent.id).label('event_count')) \
    #                 .group_by(EmailTrashEvent.user_id) \
    #                 .having(func.count(EmailTrashEvent.id) >= 100)  # Minimum events threshold
    # 
    # users_with_data = users_query.all()
    # 
    # for user_id, event_count in users_with_data:
    #     user_results = train_trash_classifier(db, user_id, save_model=True)
    #     results[str(user_id)] = user_results
    
    return results 

def bootstrap_training_data(db: Session, user_id: UUID) -> Dict[str, Any]:
    """
    Bootstrap the training data by creating trash events for all existing trash emails.
    This allows using existing emails in trash for training without requiring new user actions.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Dictionary with results
    """
    logger.info(f"[ML-TRAINING] 🚀 Bootstrapping training data for user {user_id}")
    
    # Find all emails in trash category that don't have a corresponding trash event
    subquery = db.query(EmailTrashEvent.email_id)
    trash_emails = db.query(Email).filter(
        Email.user_id == user_id,
        Email.category == 'trash',
        ~Email.id.in_(subquery)
    ).all()
    
    logger.info(f"[ML-TRAINING] Found {len(trash_emails)} existing trash emails without events")
    
    # Create trash events for these emails
    created_count = 0
    for email in trash_emails:
        try:
            # Create a simplified email_data dict
            email_data = {
                'id': email.id,
                'gmail_id': email.gmail_id,
                'subject': email.subject,
                'from_email': email.from_email,
                'snippet': email.snippet,
                'labels': email.labels,
                'is_read': email.is_read,
                'raw_data': email.raw_data
            }
            
            # Record as a trash event
            from ..utils.naive_bayes_classifier import record_trash_event
            record_trash_event(
                db=db,
                email_id=email.id,
                user_id=user_id,
                event_type='moved_to_trash',
                email_data=email_data,
                is_auto_categorized=False,  # Assume user classified these
                categorization_source='bootstrap',  # Mark as bootstrapped
                confidence_score=1.0  # High confidence since they're explicitly in trash
            )
            created_count += 1
            
            # Log progress every 50 emails
            if created_count % 50 == 0:
                logger.info(f"[ML-TRAINING] Bootstrapped {created_count}/{len(trash_emails)} emails")
                db.commit()  # Periodic commit to avoid long transactions
                
        except Exception as e:
            logger.error(f"[ML-TRAINING] Error bootstrapping email {email.id}: {str(e)}")
    
    # Final commit
    db.commit()
    
    # Get updated count
    event_count = db.query(EmailTrashEvent).filter(
        EmailTrashEvent.user_id == user_id
    ).count()
    
    logger.info(f"[ML-TRAINING] ✅ Bootstrapping complete. Created {created_count} events. Total events now: {event_count}")
    
    return {
        "status": "success",
        "existing_trash_emails": len(trash_emails),
        "created_events": created_count,
        "total_events": event_count
    } 