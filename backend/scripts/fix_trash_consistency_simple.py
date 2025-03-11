#!/usr/bin/env python
"""
Script to fix inconsistencies between 'trash' category and 'TRASH' label
This simpler version uses raw SQL to avoid import dependency issues.
"""

import os
import sys
import logging
import psycopg2
from datetime import datetime
from psycopg2.extras import RealDictCursor

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
    Find and fix any inconsistencies between 'trash' category and 'TRASH' label using direct SQL
    """
    # Get database connection info from environment or use default
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/email_agent")
    
    # Extract connection parameters from the URL
    # Format: postgresql://username:password@host:port/database
    if database_url.startswith('postgresql://'):
        parts = database_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else None
        host = host_db[0].split(':')[0]
        port = host_db[0].split(':')[1] if ':' in host_db[0] else '5432'
        database = host_db[1]
    else:
        # Use defaults if URL format is not recognized
        user = 'postgres'
        password = 'postgres'
        host = 'localhost'
        port = '5432'
        database = 'email_agent'
    
    conn = None
    category_trash_no_label_count = 0
    label_trash_wrong_category_count = 0
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        conn.autocommit = False
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Case 1: Find emails with category='trash' but missing TRASH label
        cursor.execute("""
            SELECT id, labels
            FROM emails
            WHERE category = 'trash' AND NOT labels @> '["TRASH"]'
        """)
        
        category_trash_no_label = cursor.fetchall()
        category_trash_no_label_count = len(category_trash_no_label)
        
        logger.info(f"Found {category_trash_no_label_count} emails with 'trash' category but missing TRASH label")
        
        # Update each email
        for email in category_trash_no_label:
            email_id = email['id']
            current_labels = email['labels'] or []
            
            # Add TRASH label
            if 'TRASH' not in current_labels:
                current_labels.append('TRASH')
            
            # Remove INBOX label if present
            if 'INBOX' in current_labels:
                current_labels.remove('INBOX')
                logger.info(f"Removing contradictory INBOX label from email {email_id}")
            
            # Update the database
            cursor.execute(
                "UPDATE emails SET labels = %s WHERE id = %s",
                (current_labels, email_id)
            )
            logger.info(f"Added TRASH label to email {email_id}")
        
        # Case 2: Find emails with TRASH label but not categorized as 'trash'
        cursor.execute("""
            SELECT id, category, labels
            FROM emails
            WHERE labels @> '["TRASH"]' AND category != 'trash'
        """)
        
        label_trash_wrong_category = cursor.fetchall()
        label_trash_wrong_category_count = len(label_trash_wrong_category)
        
        logger.info(f"Found {label_trash_wrong_category_count} emails with TRASH label but wrong category")
        
        # Update each email
        for email in label_trash_wrong_category:
            email_id = email['id']
            current_category = email['category']
            current_labels = email['labels'] or []
            
            # Remove INBOX label if present
            if 'INBOX' in current_labels:
                current_labels.remove('INBOX')
                cursor.execute(
                    "UPDATE emails SET labels = %s WHERE id = %s",
                    (current_labels, email_id)
                )
                logger.info(f"Removed contradictory INBOX label from email {email_id}")
            
            # Update category to 'trash'
            cursor.execute(
                "UPDATE emails SET category = 'trash' WHERE id = %s",
                (email_id,)
            )
            logger.info(f"Changed category from '{current_category}' to 'trash' for email {email_id}")
        
        # Commit changes if any
        total_fixed = category_trash_no_label_count + label_trash_wrong_category_count
        if total_fixed > 0:
            conn.commit()
            logger.info(f"Successfully fixed {total_fixed} emails with trash inconsistencies")
        else:
            logger.info("No inconsistencies found, no changes needed")
        
        return total_fixed
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if conn:
            conn.rollback()
        return 0
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    total_fixed = fix_trash_consistency()
    print(f"Fixed {total_fixed} emails with trash inconsistencies") 