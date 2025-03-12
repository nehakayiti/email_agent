from typing import Dict, Any, List, Optional, Tuple
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
import glob

logger = logging.getLogger(__name__)

# Fix the path calculation
# Get the absolute path to the backend directory
BACKEND_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# Directory to store trained models (absolute path) - one level up from backend
MODELS_DIR = BACKEND_DIR.parent / "models"

logger.info(f"[ML-SERVICE] Models directory is configured at {MODELS_DIR}")

def ensure_models_directory() -> bool:
    """
    Create models directory if it doesn't exist
    
    Returns:
        bool: True if directory exists and is writable, False otherwise
    """
    try:
        logger.info(f"[ML-SERVICE] Ensuring models directory exists at {MODELS_DIR}")
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # Check if the directory is writable
        test_file_path = MODELS_DIR / ".write_test"
        try:
            with open(test_file_path, 'w') as f:
                f.write('test')
            os.remove(test_file_path)
            logger.info(f"[ML-SERVICE] Models directory exists and is writable at {MODELS_DIR}")
            return True
        except Exception as e:
            logger.error(f"[ML-SERVICE] Models directory exists but is not writable: {str(e)}")
            return False
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
    if user_id:
        logger.debug(f"[ML-SERVICE] Using user-specific model for user {user_id}")
        return MODELS_DIR / f"trash_classifier_{user_id}.pkl"
    else:
        logger.debug(f"[ML-SERVICE] Using global model")
        return MODELS_DIR / "trash_classifier_global.pkl"

def find_available_models() -> List[Path]:
    """
    Find all available trained models in the models directory
    
    Returns:
        List of paths to available models, with global model first if it exists
    """
    # Ensure directory exists
    ensure_models_directory()
    
    available_models = []
    
    # Check for global model first
    global_model = MODELS_DIR / "trash_classifier_global.pkl"
    if global_model.exists():
        available_models.append(global_model)
        logger.info(f"[ML-SERVICE] Found global model at {global_model}")
    
    # Add all user models
    user_models = [p for p in MODELS_DIR.glob("trash_classifier_*.pkl") 
                 if p.name != "trash_classifier_global.pkl"]
    if user_models:
        available_models.extend(user_models)
        logger.info(f"[ML-SERVICE] Found {len(user_models)} user-specific models")
    
    if not available_models:
        logger.warning(f"[ML-SERVICE] No models found in {MODELS_DIR}")
        
    return available_models

def load_trash_classifier(user_id: Optional[UUID] = None) -> bool:
    """
    Load trained classifier from disk
    
    Args:
        user_id: Optional user ID to load user-specific model
        
    Returns:
        bool: True if model loaded successfully, False otherwise
    """
    global classifier
    
    try:
        ensure_models_directory()
        
        model_path = get_model_path(user_id)
        
        # First try user-specific model if user_id provided
        if user_id:
            if model_path.exists():
                logger.info(f"[ML-SERVICE] Found user-specific model at {model_path}")
                classifier.load_model(str(model_path))
                logger.info(f"[ML-SERVICE] Successfully loaded user-specific model from {model_path}")
                return True
            else:
                logger.debug(f"[ML-SERVICE] User-specific model not found at {model_path}")
        
        # Fall back to global model
        global_model_path = get_model_path(None)
        if global_model_path.exists():
            logger.debug(f"[ML-SERVICE] Using global model")
            classifier.load_model(str(global_model_path))
            logger.info(f"[ML-SERVICE] Successfully loaded requested model for global use from {global_model_path}")
            return True
        else:
            # Initialize minimal model to avoid "not trained" warnings
            logger.warning(f"[ML-SERVICE] No trained model found, initializing minimal default model")
            
            # Initialize with minimal default values
            classifier.class_priors = {'trash': 0.1, 'not_trash': 0.9}  # Assume 10% trash by default
            classifier.vocabulary = set()  # Empty vocabulary
            # Empty word likelihoods with default values
            classifier.word_likelihoods = {'trash': {}, 'not_trash': {}}
            classifier.word_counts = {'trash': 1, 'not_trash': 1}
            classifier.sender_domain_counts = {'trash': {}, 'not_trash': {}}
            classifier.sender_domain_totals = {'trash': 1, 'not_trash': 1}
            classifier.is_trained = True  # Mark as trained to avoid warnings
            classifier.training_data_size = 0
            
            # Save this minimal model so it doesn't need to be recreated
            if not global_model_path.parent.exists():
                os.makedirs(global_model_path.parent, exist_ok=True)
            classifier.save_model(str(global_model_path))
            logger.info(f"[ML-SERVICE] Saved minimal default model to {global_model_path}")
            
            return True
            
    except Exception as e:
        logger.error(f"[ML-SERVICE] Error loading classifier model: {str(e)}", exc_info=True)
        return False

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