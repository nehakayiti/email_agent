#!/usr/bin/env python3
"""
Script to initialize the ML model directory structure.
Run this script once when setting up the application to ensure
the model directory exists with proper permissions.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Path to the models directory
MODELS_DIR = Path("backend/models")

def initialize_model_directory():
    """Create the models directory with appropriate permissions."""
    try:
        # Create the models directory if it doesn't exist
        os.makedirs(MODELS_DIR, exist_ok=True)
        logger.info(f"Created models directory at {MODELS_DIR}")
        
        # Create a .gitkeep file to ensure the directory is included in git
        gitkeep_file = MODELS_DIR / ".gitkeep"
        if not gitkeep_file.exists():
            with open(gitkeep_file, 'w') as f:
                f.write("# This file ensures the models directory is included in git\n")
            logger.info(f"Created {gitkeep_file} file")
        
        # Set directory permissions
        try:
            # Try to set permissions on Unix-like systems
            os.chmod(MODELS_DIR, 0o755)  # rwxr-xr-x
            logger.info(f"Set directory permissions to 755")
        except Exception as e:
            # On Windows or if permissions can't be set
            logger.warning(f"Could not set directory permissions: {str(e)}")
            logger.warning("Please ensure the directory is writable by the application")
            
        # Create a README file with information
        readme_file = MODELS_DIR / "README.md"
        if not readme_file.exists():
            with open(readme_file, 'w') as f:
                f.write("""# Machine Learning Models Directory

This directory stores trained machine learning models for the email classification system.

## Files

- `trash_classifier_global.pkl`: Global trash email classifier model
- `trash_classifier_<user_id>.pkl`: User-specific trash email classifier models

These models are automatically created and updated through the application UI.
Do not manually modify these files.
""")
            logger.info(f"Created {readme_file} file with usage information")
            
        return True
    except Exception as e:
        logger.error(f"Error initializing model directory: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Initializing ML model directory...")
    success = initialize_model_directory()
    
    if success:
        logger.info("✅ Model directory initialized successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Failed to initialize model directory")
        sys.exit(1) 