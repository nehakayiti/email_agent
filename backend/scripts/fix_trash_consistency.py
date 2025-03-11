#!/usr/bin/env python
"""
Script to fix inconsistencies between 'trash' category and 'TRASH' label
This script finds all emails with category='trash' but missing TRASH label, or 
emails with TRASH label but not categorized as 'trash', and fixes them.
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the required modules, being careful with circular dependencies
from app.db import get_db
from app.models.email import Email
from app.models.user import User
from app.models.base import Base  # Import Base instead of specific models that might have circular references

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"trash_consistency_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger("trash_fix")

def fix_trash_consistency():
    """
    Find and fix any inconsistencies between 'trash' category and 'TRASH' label
    """
    # Get a database session directly instead of using dependency injection
    try:
        # Create the database engine and session directly
        # Get database URL from environment or use default
        database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/email_agent")
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Case 1: Emails with category='trash' but missing TRASH label
        category_trash_no_label = db.query(Email).filter(
            and_(
                Email.category == 'trash',
                ~Email.labels.contains(['TRASH'])
            )
        ).all()
        
        logger.info(f"Found {len(category_trash_no_label)} emails with 'trash' category but missing TRASH label")
        
        for email in category_trash_no_label:
            logger.info(f"Fixing email {email.id}: Adding TRASH label")
            current_labels = set(email.labels or [])
            current_labels.add('TRASH')
            
            # Remove INBOX label if present (it's contradictory to being in trash)
            if 'INBOX' in current_labels:
                logger.info(f"Removing contradictory INBOX label from email {email.id}")
                current_labels.remove('INBOX')
                
            email.labels = list(current_labels)
        
        # Case 2: Emails with TRASH label but not categorized as 'trash'
        label_trash_wrong_category = db.query(Email).filter(
            and_(
                Email.labels.contains(['TRASH']),
                Email.category != 'trash'
            )
        ).all()
        
        logger.info(f"Found {len(label_trash_wrong_category)} emails with TRASH label but wrong category")
        
        for email in label_trash_wrong_category:
            logger.info(f"Fixing email {email.id}: Setting category to 'trash' (was '{email.category}')")
            email.category = 'trash'
            
            # Remove INBOX label if present
            current_labels = set(email.labels or [])
            if 'INBOX' in current_labels:
                logger.info(f"Removing contradictory INBOX label from email {email.id}")
                current_labels.remove('INBOX')
                email.labels = list(current_labels)
        
        # Commit all changes
        total_fixed = len(category_trash_no_label) + len(label_trash_wrong_category)
        if total_fixed > 0:
            db.commit()
            logger.info(f"Successfully fixed {total_fixed} emails with trash inconsistencies")
        else:
            logger.info("No inconsistencies found, no changes needed")
            
        return total_fixed
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return 0
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    total_fixed = fix_trash_consistency()
    print(f"Fixed {total_fixed} emails with trash inconsistencies") 