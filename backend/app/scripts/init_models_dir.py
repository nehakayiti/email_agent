#!/usr/bin/env python
"""
Script to initialize the models directory.

This script ensures the models directory exists and is writable.
It's useful for setting up the environment before starting the application.

Usage:
    python -m app.scripts.init_models_dir
"""
import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import after path setup
from app.services.email_classifier_service import ensure_models_directory, MODELS_DIR
from app.core.logging_config import configure_logging

# Configure logging
configure_logging(log_file_name="models_init.log")
logger = logging.getLogger(__name__)

def main():
    """Main function to initialize the models directory"""
    logger.info(f"Initializing models directory at {MODELS_DIR}")
    
    if ensure_models_directory():
        logger.info(f"Models directory successfully created/verified at {MODELS_DIR}")
        logger.info(f"Absolute path: {MODELS_DIR.absolute()}")
        return 0
    else:
        logger.error(f"Failed to create/verify models directory at {MODELS_DIR}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 