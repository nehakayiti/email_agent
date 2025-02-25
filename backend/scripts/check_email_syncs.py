import sys
import os
import logging
from sqlalchemy import text

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_email_syncs():
    """Check the email_syncs table directly using SQL"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM email_syncs"))
        rows = result.fetchall()
        
        print("\n=== EMAIL SYNCS ===")
        if not rows:
            print("No records found in email_syncs table")
        else:
            for row in rows:
                print(f"ID: {row[0]}")
                print(f"User ID: {row[1]}")
                print(f"Last Fetched At: {row[2]}")
                print(f"Sync Cadence: {row[3]}")
                print(f"Created At: {row[4]}")
                print(f"Updated At: {row[5]}")
                print("-------------------")
        print("===================\n")

if __name__ == "__main__":
    check_email_syncs() 