#!/usr/bin/env python
"""
Script to manually train the email classifier.

This script can be used to initialize the classifier with existing data
or to retrain it after collecting more training data.

Usage:
    python -m app.scripts.train_classifier [--user USER_ID]
"""
import sys
import os
import logging
from pathlib import Path
import argparse

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import after path setup
from app.db import SessionLocal
from app.services.email_classifier_service import train_trash_classifier, ensure_models_directory
from app.core.logging_config import configure_logging

# Configure logging
configure_logging(log_file_name="classifier_training.log")
logger = logging.getLogger(__name__)

def main():
    """Main function to train the classifier"""
    parser = argparse.ArgumentParser(description="Train the email classifier")
    parser.add_argument("--user", help="User ID to train a user-specific model (optional)")
    args = parser.parse_args()
    
    # Ensure models directory exists
    if not ensure_models_directory():
        logger.error("Failed to create models directory")
        return 1
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Train the classifier
        user_id = args.user
        logger.info(f"Training classifier for {'user ' + user_id if user_id else 'global model'}")
        
        result = train_trash_classifier(db, user_id=user_id if user_id else None)
        
        if result["status"] == "success":
            logger.info(f"Training successful: {result['message']}")
            logger.info(f"Trained with {result['events_count']} events")
            logger.info(f"Accuracy: {result.get('accuracy', 'N/A')}")
            logger.info(f"Training time: {result.get('training_time', 'N/A')}")
            return 0
        else:
            logger.error(f"Training failed: {result['message']}")
            return 1
    except Exception as e:
        logger.error(f"Error training classifier: {str(e)}", exc_info=True)
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main()) 