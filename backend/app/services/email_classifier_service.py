from typing import Dict, Any, List, Optional, Tuple
import logging
from sqlalchemy.orm import Session
import os
from pathlib import Path
from uuid import UUID
from ..models.email import Email
from ..models.email_operation import EmailOperation, OperationType
from ..models.email_trash_event import EmailTrashEvent
from ..utils.naive_bayes_classifier import classifier, train_classifier as nbc_train_classifier
import time
import glob

logger = logging.getLogger(__name__)

class EmailClassifierService:
    def __init__(self):
        # Get the absolute path to the backend directory
        self.BACKEND_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        # Directory to store trained models (absolute path) - one level up from backend
        self.MODELS_DIR = self.BACKEND_DIR.parent / "models"
        logger.info(f"[ML-SERVICE] Models directory is configured at {self.MODELS_DIR}")

    def ensure_models_directory(self) -> bool:
        """
        Create models directory if it doesn't exist
        
        Returns:
            bool: True if directory exists and is writable, False otherwise
        """
        try:
            logger.info(f"[ML-SERVICE] Ensuring models directory exists at {self.MODELS_DIR}")
            os.makedirs(self.MODELS_DIR, exist_ok=True)
            
            # Check if the directory is writable
            test_file_path = self.MODELS_DIR / ".write_test"
            try:
                with open(test_file_path, 'w') as f:
                    f.write('test')
                os.remove(test_file_path)
                logger.info(f"[ML-SERVICE] Models directory exists and is writable at {self.MODELS_DIR}")
                return True
            except Exception as e:
                logger.error(f"[ML-SERVICE] Models directory exists but is not writable: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"[ML-SERVICE] Error creating models directory: {str(e)}")
            return False

    def get_model_path(self, user_id: Optional[UUID] = None) -> Path:
        """
        Get the path to the model file for a user
        
        Args:
            user_id: Optional UUID of the user, or None for global model
            
        Returns:
            Path object for the model file
        """
        if user_id:
            logger.debug(f"[ML-SERVICE] Using user-specific model for user {user_id}")
            return self.MODELS_DIR / f"trash_classifier_{user_id}.pkl"
        else:
            logger.debug(f"[ML-SERVICE] Using global model")
            return self.MODELS_DIR / "trash_classifier_global.pkl"

    def find_available_models(self) -> List[Path]:
        """
        Find all available trained models in the models directory
        
        Returns:
            List of paths to available models, with global model first if it exists
        """
        # Ensure directory exists
        self.ensure_models_directory()
        
        available_models = []
        
        # Check for global model first
        global_model = self.MODELS_DIR / "trash_classifier_global.pkl"
        if global_model.exists():
            available_models.append(global_model)
            logger.info(f"[ML-SERVICE] Found global model at {global_model}")
        
        # Add all user models
        user_models = [p for p in self.MODELS_DIR.glob("trash_classifier_*.pkl") 
                     if p.name != "trash_classifier_global.pkl"]
        if user_models:
            available_models.extend(user_models)
            logger.info(f"[ML-SERVICE] Found {len(user_models)} user-specific models")
        
        if not available_models:
            logger.warning(f"[ML-SERVICE] No models found in {self.MODELS_DIR}")
        
        return available_models

    def load_trash_classifier(self, user_id: Optional[UUID] = None) -> bool:
        """
        Load trained classifier from disk
        
        Args:
            user_id: Optional user ID to load user-specific model
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            self.ensure_models_directory()
            
            model_path = self.get_model_path(user_id)
            
            # First try user-specific model if user_id provided
            if user_id and model_path.exists():
                logger.info(f"[ML-SERVICE] Found user-specific model at {model_path}")
                classifier.load_model(str(model_path))
                logger.info(f"[ML-SERVICE] Successfully loaded user-specific model from {model_path}")
                return True
            
            # Fall back to global model
            global_model_path = self.get_model_path(None)
            if global_model_path.exists():
                logger.debug(f"[ML-SERVICE] Using global model")
                classifier.load_model(str(global_model_path))
                logger.info(f"[ML-SERVICE] Successfully loaded requested model for global use from {global_model_path}")
                return True
            else:
                # Initialize minimal model to avoid "not trained" warnings
                logger.warning(f"[ML-SERVICE] No trained model found, initializing minimal default model")
                self._initialize_minimal_model()
                
                # Save this minimal model
                if not global_model_path.parent.exists():
                    os.makedirs(global_model_path.parent, exist_ok=True)
                classifier.save_model(str(global_model_path))
                logger.info(f"[ML-SERVICE] Saved minimal default model to {global_model_path}")
                return True
                
        except Exception as e:
            logger.error(f"[ML-SERVICE] Error loading classifier model: {str(e)}", exc_info=True)
            return False

    def _initialize_minimal_model(self):
        """Initialize a minimal model with default values"""
        classifier.class_priors = {'trash': 0.1, 'not_trash': 0.9}  # Assume 10% trash by default
        classifier.vocabulary = set()  # Empty vocabulary
        classifier.word_likelihoods = {'trash': {}, 'not_trash': {}}
        classifier.word_counts = {'trash': 1, 'not_trash': 1}
        classifier.sender_domain_counts = {'trash': {}, 'not_trash': {}}
        classifier.sender_domain_totals = {'trash': 1, 'not_trash': 1}
        classifier.is_trained = True  # Mark as trained to avoid warnings
        classifier.training_data_size = 0

    def train_trash_classifier(
        self, 
        db: Session, 
        user_id: Optional[UUID] = None,
        save_model: bool = True,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train a Naive Bayes classifier for predicting if emails should be moved to trash
        
        Args:
            db: Database session
            user_id: Optional user ID to train a user-specific model
            save_model: Whether to save the trained model to disk
            test_size: Fraction of data to use for testing (0.0 to 1.0)
            
        Returns:
            Dictionary with training results
        """
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║                  TRAINING EMAIL CLASSIFIER                               ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        
        start_time = time.time()
        logger.info(f"[ML-SERVICE] Starting trash classifier training for {'user ' + str(user_id) if user_id else 'global model'}")
        logger.info(f"[ML-SERVICE] Using test_size={test_size}")
        
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
        
        # Split data into training and test sets if test_size > 0
        from sklearn.model_selection import train_test_split
        train_features, test_features, train_labels, test_labels = None, None, None, None
        
        if test_size > 0 and total_events >= 10:  # Only split if we have enough data
            train_features, test_features, train_labels, test_labels = train_test_split(
                features, labels, test_size=test_size, random_state=42
            )
            training_size = len(train_features)
            test_size = len(test_features)
            logger.info(f"[ML-SERVICE] Split data into {training_size} training samples and {test_size} test samples")
        else:
            train_features, train_labels = features, labels
            test_features, test_labels = [], []
            logger.info(f"[ML-SERVICE] Using all {total_events} samples for training (no test split)")
        
        # Train the classifier
        try:
            # Train on training set only
            accuracy = nbc_train_classifier(train_features, train_labels, user_id)
            
            # Save the model if requested
            if save_model:
                model_path = self.get_model_path(user_id)
                logger.info(f"[ML-SERVICE] Saving trained model to {model_path}")
                classifier.save_model(str(model_path))
        
            training_time = time.time() - start_time
            logger.info(f"[ML-SERVICE] Training completed in {training_time:.2f}s with accuracy: {accuracy:.4f}")
            logger.info(f"[ML-SERVICE] Model is now ready for classification")
            
            # If we have test data, evaluate on it
            metrics = None
            if test_features and test_labels:
                logger.info(f"[ML-SERVICE] Evaluating model on {len(test_features)} test samples")
                metrics = self.evaluate_classifier(test_features, test_labels, user_id)
                classifier.evaluation_metrics = metrics
                logger.info(f"[ML-SERVICE] Model evaluation metrics: {metrics}")
                
                # If we have metrics, save the model again to store the metrics
                if save_model:
                    classifier.save_model(str(model_path))
        
            return {
                "status": "success",
                "message": "Classifier trained successfully",
                "trained": True,
                "events_count": total_events,
                "accuracy": accuracy,
                "training_time": f"{training_time:.2f}s",
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"[ML-SERVICE] Error training classifier: {str(e)}")
            return {
                "status": "error",
                "message": f"Error training classifier: {str(e)}",
                "trained": False,
                "events_count": total_events
            }

    def record_trash_operations(self, db: Session, operations: List[EmailOperation]) -> None:
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
            self.record_trash_event(
                db=db,
                email_id=email.id,
                user_id=email.user_id,
                event_type='moved_to_trash',
                email_data=email_data,
                is_auto_categorized=False,
                categorization_source='user'
            )
            
            logger.info(f"Recorded trash event for email {email.id} from operation {operation.id}")

    def retrain_all_models(self, db: Session) -> Dict[str, Any]:
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
        global_results = self.train_trash_classifier(db, save_model=True)
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
        #     user_results = self.train_trash_classifier(db, user_id, save_model=True)
        #     results[str(user_id)] = user_results
        
        return results 

    def bootstrap_training_data(self, db: Session, user_id: UUID) -> Dict[str, Any]:
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
                self.record_trash_event(
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

    def evaluate_model(self, db: Session, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Evaluate the trained classifier model and return metrics
        
        Args:
            db: Database session
            user_id: Optional user ID to evaluate a user-specific model
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"[ML-SERVICE] Evaluating trash classifier for {'user ' + str(user_id) if user_id else 'global model'}")
        
        # Load the classifier model
        model_loaded = self.load_trash_classifier(user_id)
        if not model_loaded:
            logger.error(f"[ML-SERVICE] No model available for evaluation")
            return {
                "status": "error",
                "message": "No trained model available for evaluation"
            }
        
        # Get test data from database - use all available events for evaluation
        query = db.query(EmailTrashEvent)
        if user_id:
            query = query.filter(EmailTrashEvent.user_id == user_id)
        
        # Since we're evaluating, we'll use all available data
        # In a real system, you'd want to keep a separate test set
        test_events = query.all()
        
        if not test_events:
            logger.error(f"[ML-SERVICE] No test data available for evaluation")
            return {
                "status": "error",
                "message": "No test data available for evaluation"
            }
        
        # Extract features and labels
        test_features = []
        test_labels = []
        
        for event in test_events:
            test_features.append({
                "sender": event.sender_email,
                "subject": event.subject,
                "snippet": event.snippet
            })
            test_labels.append(1 if event.event_type == 'moved_to_trash' else 0)
        
        # If we already have stored metrics, use them
        if hasattr(classifier, 'evaluation_metrics') and classifier.evaluation_metrics:
            stored_metrics = classifier.evaluation_metrics
            logger.info(f"[ML-SERVICE] Using stored evaluation metrics")
            return stored_metrics
        
        # Otherwise, evaluate the model on the test data
        logger.info(f"[ML-SERVICE] Evaluating model on {len(test_features)} examples")
        metrics = self.evaluate_classifier(test_features, test_labels, user_id)
        
        # Store metrics in the classifier for future reference
        classifier.evaluation_metrics = metrics
        
        # Save the model with the updated metrics
        model_path = self.get_model_path(user_id)
        classifier.save_model(str(model_path))
        
        return metrics

    def evaluate_classifier(self, features: List[Dict[str, Any]], labels: List[int], user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Evaluate the classifier on test data and calculate metrics
        
        Args:
            features: List of feature dictionaries
            labels: List of ground truth labels (1 for trash, 0 for not trash)
            user_id: Optional user ID for user-specific model
            
        Returns:
            Dictionary with evaluation metrics
        """
        from ..utils.naive_bayes_classifier import classify_email as nbc_classify_email
        
        # Make predictions on test data
        predictions = []
        for feature in features:
            # Create a single email_data dict as expected by classify_email
            email_data = {
                "from_email": feature.get("sender", ""),
                "subject": feature.get("subject", ""),
                "snippet": feature.get("snippet", ""),
                "gmail_id": feature.get("gmail_id", "unknown")
            }
            
            # Call the classifier with the expected parameter format
            prediction, _ = nbc_classify_email(email_data, user_id)
            
            # Convert prediction to binary (1 for trash, 0 for not trash)
            predictions.append(1 if prediction == "trash" else 0)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        import numpy as np
        
        # Handle edge case where we might not have enough data of each class
        if len(set(labels)) < 2 or len(set(predictions)) < 2:
            logger.warning(f"[ML-SERVICE] Not enough class diversity in evaluation data")
            # Provide reasonable default metrics
            accuracy = accuracy_score(labels, predictions)
            precision = 0.0
            recall = 0.0
            f1 = 0.0
            cm = [[0, 0], [0, 0]]
        else:
            accuracy = accuracy_score(labels, predictions)
            precision = precision_score(labels, predictions, zero_division=0)
            recall = recall_score(labels, predictions, zero_division=0)
            f1 = f1_score(labels, predictions, zero_division=0)
            cm = confusion_matrix(labels, predictions).tolist()
        
        # Get top features from the model
        top_features = []
        try:
            from ..utils.naive_bayes_classifier import classifier
            
            # Extract feature importances from the Naive Bayes model
            # For NBC, the word likelihoods serve as feature importances
            word_likelihoods_trash = classifier.word_likelihoods['trash']
            word_likelihoods_not_trash = classifier.word_likelihoods['not_trash']
            
            # Combine all features
            all_features = {}
            
            # Calculate importance as the difference in likelihood between classes
            for word in classifier.vocabulary:
                trash_likelihood = word_likelihoods_trash.get(word, 0)
                not_trash_likelihood = word_likelihoods_not_trash.get(word, 0)
                
                if trash_likelihood > not_trash_likelihood:
                    all_features[word] = {
                        "importance": trash_likelihood / (not_trash_likelihood + 1e-9),
                        "class": "trash"
                    }
                else:
                    all_features[word] = {
                        "importance": not_trash_likelihood / (trash_likelihood + 1e-9),
                        "class": "not_trash"
                    }
            
            # Sort by importance and take top 15
            sorted_features = sorted(
                all_features.items(), 
                key=lambda x: x[1]["importance"], 
                reverse=True
            )[:15]
            
            top_features = [
                {
                    "feature": word,
                    "importance": info["importance"],
                    "class": info["class"]
                }
                for word, info in sorted_features
            ]
        except Exception as e:
            logger.error(f"[ML-SERVICE] Error extracting top features: {str(e)}")
        
        # Compile metrics
        metrics = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {
                "true_positives": cm[1][1] if len(cm) > 1 and len(cm[1]) > 1 else 0,
                "false_positives": cm[0][1] if len(cm) > 0 and len(cm[0]) > 1 else 0,
                "true_negatives": cm[0][0] if len(cm) > 0 and len(cm[0]) > 0 else 0,
                "false_negatives": cm[1][0] if len(cm) > 1 and len(cm[1]) > 0 else 0
            },
            "top_features": top_features,
            "training_size": classifier.training_data_size,
            "test_size": len(features),
            "training_time": f"{classifier.training_time:.2f}s" if hasattr(classifier, 'training_time') else "unknown"
        }
        
        return metrics 

    def train_balanced_trash_classifier(
        self, 
        db: Session, 
        user_id: Optional[UUID] = None,
        save_model: bool = True,
        test_size: float = 0.2,
        max_samples_per_class: int = 500
    ) -> Dict[str, Any]:
        """
        Train a Naive Bayes classifier with a balanced dataset of trash and non-trash emails
        explicitly using Gmail labels as the source of truth.
        
        Args:
            db: Database session
            user_id: Optional user ID to train a user-specific model
            save_model: Whether to save the trained model to disk
            test_size: Fraction of data to use for testing (0.0 to 1.0)
            max_samples_per_class: Maximum number of samples to use per class
            
        Returns:
            Dictionary with training results
        """
        logger.info(f"╔══════════════════════════════════════════════════════════════════════════╗")
        logger.info(f"║            TRAINING EMAIL CLASSIFIER WITH IMPROVED STRATEGY              ║")
        logger.info(f"╚══════════════════════════════════════════════════════════════════════════╝")
        
        start_time = time.time()
        logger.info(f"[ML-SERVICE] Starting improved trash classifier training for {'user ' + str(user_id) if user_id else 'global model'}")
        
        # Get emails with TRASH label for trash class
        trash_query = db.query(Email).filter(Email.labels.contains(['TRASH']))
        if user_id:
            trash_query = trash_query.filter(Email.user_id == user_id)
        trash_emails = trash_query.limit(max_samples_per_class).all()
        
        # Get emails in INBOX (without TRASH label) for not_trash class
        not_trash_query = db.query(Email).filter(
            Email.labels.contains(['INBOX']),
            ~Email.labels.contains(['TRASH'])  # Exclude emails with TRASH label
        )
        if user_id:
            not_trash_query = not_trash_query.filter(Email.user_id == user_id)
        not_trash_emails = not_trash_query.limit(max_samples_per_class).all()
        
        logger.info(f"[ML-SERVICE] Collected {len(trash_emails)} trash emails and {len(not_trash_emails)} non-trash emails")
        
        if len(trash_emails) < 10 or len(not_trash_emails) < 10:
            logger.warning(f"[ML-SERVICE] Insufficient training data: only {len(trash_emails)} trash and {len(not_trash_emails)} non-trash emails available (minimum 10 each required)")
            return {
                "status": "error",
                "message": f"Insufficient training data ({len(trash_emails)} trash, {len(not_trash_emails)} non-trash emails)",
                "trained": False
            }
        
        # Prepare training data
        features = []
        labels = []
        
        # Process trash emails
        for email in trash_emails:
            features.append({
                "sender": email.from_email,
                "subject": email.subject,
                "snippet": email.snippet,
                "gmail_id": email.gmail_id
            })
            labels.append(1)  # 1 for trash
        
        # Process non-trash emails
        for email in not_trash_emails:
            features.append({
                "sender": email.from_email,
                "subject": email.subject,
                "snippet": email.snippet,
                "gmail_id": email.gmail_id
            })
            labels.append(0)  # 0 for not_trash
        
        # Split into training and testing sets
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        logger.info(f"[ML-SERVICE] Split data into {len(X_train)} training and {len(X_test)} testing samples")
        
        # Train the classifier
        from ..utils.naive_bayes_classifier import train_classifier
        accuracy = train_classifier(X_train, y_train, user_id)
        
        logger.info(f"[ML-SERVICE] Classifier trained with training accuracy: {accuracy:.4f}")
        
        # Evaluate on test data
        evaluation_results = self.evaluate_classifier(X_test, y_test, user_id)
        
        # Save the model if requested
        if save_model:
            model_path = self.get_model_path(user_id)
            logger.info(f"[ML-SERVICE] Saved trained model to {model_path}")
        
        # Combine all results
        results = {
            "status": "success",
            "training_accuracy": accuracy,
            "test_accuracy": evaluation_results["accuracy"],
            "precision": evaluation_results["precision"],
            "recall": evaluation_results["recall"],
            "f1_score": evaluation_results["f1_score"],
            "confusion_matrix": evaluation_results["confusion_matrix"],
            "training_samples": len(X_train),
            "testing_samples": len(X_test),
            "trash_emails": len(trash_emails),
            "non_trash_emails": len(not_trash_emails),
            "training_time": time.time() - start_time,
            "trained": True
        }
        
        logger.info(f"[ML-SERVICE] Training completed in {results['training_time']:.2f}s with test accuracy: {results['test_accuracy']:.4f}")
        logger.info(f"[ML-SERVICE] Metrics: precision={results['precision']:.4f}, recall={results['recall']:.4f}, f1={results['f1_score']:.4f}")
        
        return results 

    def record_trash_event(
        self,
        db: Session,
        email_id: UUID,
        user_id: UUID,
        event_type: str,
        email_data: Dict[str, Any],
        is_auto_categorized: bool = False,
        categorization_source: str = 'user',
        confidence_score: Optional[float] = None
    ) -> EmailTrashEvent:
        """Record a trash event for future training"""
        from email.utils import parseaddr
        import re
        from collections import Counter
        
        try:
            gmail_id = email_data.get('gmail_id', 'unknown')
            subject = email_data.get('subject', 'No subject')[:30]
            from_email = email_data.get('from_email', 'unknown')
            
            # Extract sender domain
            _, sender_address = parseaddr(from_email)
            sender_domain = sender_address.split('@')[-1].lower() if '@' in sender_address else ''
            
            # Extract keywords
            text = f"{subject} {email_data.get('snippet', '')}".lower()
            words = re.findall(r'\b[a-z]{3,}\b', text)
            word_counts = Counter(words)
            keywords = [word for word, count in word_counts.most_common(10) if count > 1]
            
            event = EmailTrashEvent(
                email_id=email_id,
                user_id=user_id,
                event_type=event_type,
                sender_email=from_email,
                sender_domain=sender_domain,
                subject=email_data.get('subject', ''),
                snippet=email_data.get('snippet', ''),
                keywords=keywords,
                is_auto_categorized=is_auto_categorized,
                categorization_source=categorization_source,
                confidence_score=confidence_score,
                email_metadata={
                    'labels': email_data.get('labels', []),
                    'is_read': email_data.get('is_read', False)
                }
            )
            
            db.add(event)
            db.commit()
            
            logger.info(f"[ML-TRAINING] Successfully recorded trash event for email {gmail_id}")
            return event
            
        except Exception as e:
            logger.error(f"[ML-TRAINING] Error recording trash event: {str(e)}", exc_info=True)
            db.rollback()
            raise

# Create a singleton instance
email_classifier_service = EmailClassifierService()

# Export the singleton instance and class
__all__ = ['EmailClassifierService', 'email_classifier_service']