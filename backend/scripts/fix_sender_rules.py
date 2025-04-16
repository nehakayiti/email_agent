"""Script to fix incorrect sender rules."""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create DB connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/email_agent_db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Fix techmeme.com rules
    # First delete all existing techmeme.com rules
    session.execute(
        text("""
        DELETE FROM sender_rules 
        WHERE pattern IN ('techmeme.com>', 'techmeme.com') 
        AND is_domain = true
        """)
    )
    
    # Add single correct rule with high weight
    session.execute(
        text("""
        INSERT INTO sender_rules (category_id, pattern, is_domain, weight, user_id)
        SELECT ec.id, 'techmeme.com', true, 8, NULL
        FROM email_categories ec
        WHERE ec.name = 'newsletters'
        """)
    )
    
    # Fix barrons rules - remove the less specific one
    session.execute(
        text("DELETE FROM sender_rules WHERE pattern = 'barrons' AND is_domain = true")
    )
    
    # Update barrons.com to have high weight and make it a system rule
    session.execute(
        text("""
        UPDATE sender_rules 
        SET weight = 8, user_id = NULL 
        WHERE pattern = 'barrons.com' AND is_domain = true
        """)
    )
    
    # Update all major news source weights to be higher
    session.execute(
        text("""
        UPDATE sender_rules 
        SET weight = 8 
        WHERE pattern IN (
            'wsj.com', 'nytimes.com', 'bloomberg.com', 'reuters.com',
            'ft.com', 'economist.com', 'barrons.com', 'techmeme.com',
            'theinformation.com', 'hbr.org', 'substack.com'
        ) 
        AND is_domain = true 
        AND user_id IS NULL
        """)
    )
    
    session.commit()
    logger.info("Successfully fixed sender rules and updated weights")
    
except Exception as e:
    session.rollback()
    logger.error(f"Error fixing sender rules: {str(e)}")
finally:
    session.close() 