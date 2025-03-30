"""
Script to update the email categories to only use the following 4 categories:
1. Important
2. Newsletters
3. Social
4. Promotions

This script will:
1. Ensure these 4 categories exist as system categories
2. Map existing categories to the new structure
3. Transfer emails, keywords, and sender rules to the new categories
4. Remove old categories (except special ones like 'trash' and 'archive')

Usage:
python -m backend.scripts.update_categories
"""
import os
import sys
import logging
from datetime import datetime
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, JSON

# Define the base model
Base = declarative_base()

# Define email category model matching the one in the app
class EmailCategory(Base):
    __tablename__ = "email_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Integer, default=50)
    is_system = Column(Boolean, default=False)
    created_at = Column(JSON, nullable=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create DB connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL not found in environment variables")
    sys.exit(1)

logger.info(f"Connecting to database: {DATABASE_URL.split('@')[-1]}")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Time tracking
start_time = datetime.now()
logger.info(f"Category migration started at {start_time}")

try:
    # 1. Ensure all target categories exist as system categories
    # Define the desired categories with their properties
    required_categories = [
        {
            "name": "important", 
            "display_name": "Important", 
            "description": "High-priority and time-sensitive emails",
            "priority": 1
        },
        {
            "name": "newsletters", 
            "display_name": "Newsletters", 
            "description": "News, periodicals, and subscription digests",
            "priority": 2
        },
        {
            "name": "social", 
            "display_name": "Social", 
            "description": "Emails related to social networks and communications",
            "priority": 3
        },
        {
            "name": "promotions", 
            "display_name": "Promotions", 
            "description": "Marketing, deals, and promotional content",
            "priority": 4
        }
    ]
    
    # Make sure each required category exists
    for category_data in required_categories:
        existing = session.execute(
            text("SELECT id, display_name, description, priority FROM email_categories WHERE name = :name AND is_system = true"),
            {"name": category_data["name"]}
        ).fetchone()
        
        if not existing:
            # Create if doesn't exist using the ORM model
            logger.info(f"Creating system category: {category_data['name']}")
            new_category = EmailCategory(
                name=category_data["name"],
                display_name=category_data["display_name"],
                description=category_data["description"],
                priority=category_data["priority"],
                is_system=True,
                created_at={"timestamp": datetime.utcnow().isoformat()}
            )
            session.add(new_category)
            session.flush()
        else:
            # Update existing category if needed
            logger.info(f"Updating system category: {category_data['name']}")
            session.execute(
                text("""
                UPDATE email_categories 
                SET display_name = :display_name, description = :description, priority = :priority
                WHERE name = :name AND is_system = true
                """),
                {
                    "name": category_data["name"],
                    "display_name": category_data["display_name"],
                    "description": category_data["description"],
                    "priority": category_data["priority"]
                }
            )
    
    # 2. Define mapping of old categories to new ones
    category_mapping = {
        "personal": "important",
        "primary": "important",
        "updates": "newsletters",
        "forums": "newsletters",
        "promotional": "promotions"
    }
    
    # Check which categories actually exist in the database before proceeding
    existing_categories = session.execute(
        text("SELECT name FROM email_categories WHERE name IN :names"),
        {"names": tuple(category_mapping.keys())}
    ).fetchall()
    existing_category_names = [cat[0] for cat in existing_categories]
    
    logger.info(f"Found existing categories to migrate: {existing_category_names}")
    
    # 3. Transfer emails to new categories
    for old_cat, new_cat in category_mapping.items():
        if old_cat not in existing_category_names:
            logger.info(f"Skipping migration for non-existent category: {old_cat}")
            continue
            
        count = session.execute(
            text("UPDATE emails SET category = :new_cat WHERE category = :old_cat"),
            {"old_cat": old_cat, "new_cat": new_cat}
        ).rowcount
        logger.info(f"Moved {count} emails from '{old_cat}' to '{new_cat}'")
    
    # 4. Transfer keywords and sender rules to new categories
    for old_cat, new_cat in category_mapping.items():
        if old_cat not in existing_category_names:
            continue
            
        # Get IDs of categories
        old_id = session.execute(
            text("SELECT id FROM email_categories WHERE name = :name"),
            {"name": old_cat}
        ).fetchone()
        
        new_id = session.execute(
            text("SELECT id FROM email_categories WHERE name = :name"),
            {"name": new_cat}
        ).fetchone()
        
        if old_id and new_id:
            old_id = old_id[0]
            new_id = new_id[0]
            
            # Move keywords
            count = session.execute(
                text("UPDATE category_keywords SET category_id = :new_id WHERE category_id = :old_id"),
                {"old_id": old_id, "new_id": new_id}
            ).rowcount
            logger.info(f"Moved {count} keywords from '{old_cat}' to '{new_cat}'")
            
            # Move sender rules
            count = session.execute(
                text("UPDATE sender_rules SET category_id = :new_id WHERE category_id = :old_id"),
                {"old_id": old_id, "new_id": new_id}
            ).rowcount
            logger.info(f"Moved {count} sender rules from '{old_cat}' to '{new_cat}'")
    
    # 5. Remove old system categories (except trash and archive which have special functions)
    categories_to_preserve = ["important", "newsletters", "social", "promotions", "trash", "archive"]
    
    # First, count how many categories will be removed
    to_remove = session.execute(
        text("""
        SELECT name FROM email_categories 
        WHERE is_system = true AND name NOT IN :preserve_names
        """),
        {"preserve_names": tuple(categories_to_preserve)}
    ).fetchall()
    
    to_remove_names = [cat[0] for cat in to_remove]
    logger.info(f"Found {len(to_remove_names)} categories to remove: {to_remove_names}")
    
    # Now delete them
    if to_remove_names:
        count = session.execute(
            text("""
            DELETE FROM email_categories 
            WHERE is_system = true AND name IN :names
            """),
            {"names": tuple(to_remove_names)}
        ).rowcount
        logger.info(f"Removed {count} categories")
    
    # Commit all changes
    session.commit()
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Migration completed successfully in {duration:.2f} seconds!")
    
except Exception as e:
    # Roll back on error
    session.rollback()
    logger.error(f"Error during migration: {str(e)}")
    raise
finally:
    session.close() 