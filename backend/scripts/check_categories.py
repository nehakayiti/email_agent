"""
Script to check the current state of email categories after migration.
Shows current categories and email distribution.

Usage:
python -m backend.scripts.check_categories
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

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

try:
    # Get all categories
    categories = session.execute(
        text("""
        SELECT id, name, display_name, priority, is_system 
        FROM email_categories 
        ORDER BY priority
        """)
    ).fetchall()
    
    # Display categories
    print("\n=== CURRENT CATEGORIES ===")
    print(f"{'ID':<5} | {'NAME':<15} | {'DISPLAY NAME':<15} | {'PRIORITY':<8} | {'SYSTEM'}")
    print("-" * 70)
    for cat in categories:
        print(f"{cat[0]:<5} | {cat[1]:<15} | {cat[2]:<15} | {cat[3]:<8} | {cat[4]}")
    
    # Get count of emails per category
    email_counts = session.execute(
        text("""
        SELECT category, COUNT(*) 
        FROM emails 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
        """)
    ).fetchall()
    
    # Display email counts
    print("\n=== EMAIL COUNTS BY CATEGORY ===")
    print(f"{'CATEGORY':<15} | {'COUNT'}")
    print("-" * 25)
    for cat_count in email_counts:
        print(f"{cat_count[0]:<15} | {cat_count[1]}")
    
    # Get keyword counts
    keyword_counts = session.execute(
        text("""
        SELECT ec.name, COUNT(ck.id), ec.priority
        FROM email_categories ec
        LEFT JOIN category_keywords ck ON ec.id = ck.category_id
        GROUP BY ec.name, ec.priority
        ORDER BY ec.priority
        """)
    ).fetchall()
    
    # Display keyword counts
    print("\n=== KEYWORDS BY CATEGORY ===")
    print(f"{'CATEGORY':<15} | {'COUNT'}")
    print("-" * 25)
    for kw_count in keyword_counts:
        print(f"{kw_count[0]:<15} | {kw_count[1]}")
    
    # Get sender rule counts
    rule_counts = session.execute(
        text("""
        SELECT ec.name, COUNT(sr.id), ec.priority
        FROM email_categories ec
        LEFT JOIN sender_rules sr ON ec.id = sr.category_id
        GROUP BY ec.name, ec.priority
        ORDER BY ec.priority
        """)
    ).fetchall()
    
    # Display sender rule counts
    print("\n=== SENDER RULES BY CATEGORY ===")
    print(f"{'CATEGORY':<15} | {'COUNT'}")
    print("-" * 25)
    for rule_count in rule_counts:
        print(f"{rule_count[0]:<15} | {rule_count[1]}")
    
except Exception as e:
    logger.error(f"Error checking categories: {str(e)}")
    raise
finally:
    session.close() 