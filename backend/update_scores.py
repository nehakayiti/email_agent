#!/usr/bin/env python3
"""
Quick script to update email attention scores using the enhanced scoring system.
This will apply our new algorithm to existing emails.
"""

import sys
import os
sys.path.append('.')

from app.db import get_db
from app.models.email import Email
from app.services.enhanced_attention_scoring import (
    update_email_attention_scores,
    get_scoring_performance_stats
)

def main():
    print("🚀 Updating email attention scores with enhanced algorithm...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get a sample of emails to update
        emails = db.query(Email).limit(100).all()
        
        if not emails:
            print("❌ No emails found in database")
            return
        
        print(f"📧 Found {len(emails)} emails to update")
        
        # Update scores using enhanced scoring
        result = update_email_attention_scores(emails, force_update=True)
        
        print(f"✅ Update complete:")
        print(f"   • Total emails: {result['total_emails']}")
        print(f"   • Updated: {result['updated_count']}")
        print(f"   • Errors: {result['error_count']}")
        print(f"   • Success rate: {result['success_rate']}%")
        print(f"   • Time: {result['total_time_seconds']:.2f}s")
        print(f"   • Speed: {result['emails_per_second']:.1f} emails/sec")
        
        # Commit the changes
        db.commit()
        print("💾 Changes committed to database")
        
        # Show performance stats
        stats = get_scoring_performance_stats()
        print(f"\n📊 Scoring system performance:")
        print(f"   • Cache hit rate: {stats.get('cache_hit_rate_percent', 0)}%")
        print(f"   • Calculations performed: {stats.get('calculations_performed', 0)}")
        
        # Show some sample scores
        updated_emails = db.query(Email).limit(10).all()
        print(f"\n🎯 Sample updated scores:")
        for email in updated_emails:
            bucket = "NOW" if email.attention_score >= 60 else "LATER" if email.attention_score >= 30 else "REFERENCE"
            print(f"   • {email.subject[:40]:<40} | {email.attention_score:5.1f} | {bucket}")
        
    except Exception as e:
        print(f"❌ Error updating scores: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()