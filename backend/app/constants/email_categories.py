"""
Email categorization constants and keyword sets.

This module contains the keywords and patterns used for email categorization.
These can be dynamically updated over time based on user behavior and preferences.
"""
from typing import Dict, Set, List

# Map of category name to a set of keywords found in subject lines
# Using sets for O(1) lookup performance
CATEGORY_KEYWORDS: Dict[str, Set[str]] = {
    "promotional": {
        "offer", "discount", "sale", "promo", "deal", "save", "subscription", 
        "limited time", "hurry", "expires", "coupon", "% off", "promotion",
        "special", "clearance", "membership", "renew", "trial", "upgrade",
        "buy now", "new arrival", "exclusive", "free shipping"
    },
    "social": {
        "invitation", "invite", "join", "connection", "follow", "friend", "like",
        "network", "social", "connect", "group", "community", "shared", "comment",
        "birthday", "anniversary", "celebrate", "event", "party", "meetup"
    },
    "updates": {
        "update", "notification", "alert", "status", "confirm", "confirmation",
        "receipt", "statement", "bill", "invoice", "purchase", "shipping", "tracking",
        "delivery", "payment", "security", "verification", "verify", "confirm"
    },
    "forums": {
        "forum", "thread", "topic", "discussion", "post", "reply", "digest", "community",
        "newsletter", "bulletin", "board", "mailing list", "subscribe", "unsubscribe"
    },
    "important": {
        "urgent", "important", "attention", "priority", "critical", "required",
        "action", "deadline", "expiration", "immediate", "asap", "now", "approval",
        "password", "security", "alert", "warning", "notice", "tax", "legal"
    },
    "personal": {
        "hello", "hey", "hi", "private", "confidential", "personal", "family", 
        "friend", "fyi", "introduction", "meeting", "appointment", "coffee", 
        "lunch", "dinner", "call"
    },
    "newsletters": {
        "newsletter", "digest", "weekly", "daily", "monthly", "edition", "issue",
        "bulletin", "report", "roundup", "update", "news", "briefing", "summary",
        "today's", "this week", "this month", "breaking", "latest", "trending",
        "insights", "analysis", "exclusive", "featuring", "spotlight"
    }
}

# Case-insensitive sender domains for category matching
SENDER_DOMAINS: Dict[str, str] = {
    # Social networks
    "facebook.com": "social",
    "twitter.com": "social", 
    "instagram.com": "social",
    "linkedin.com": "social",
    "pinterest.com": "social",
    
    # Common promotional senders
    "marketing": "promotional",
    "newsletter": "promotional",
    "noreply": "promotional",
    "promotions": "promotional",
    "info": "promotional",
    
    # Update services
    "accounts": "updates",
    "notifications": "updates",
    "no-reply": "updates", 
    "donotreply": "updates",
    "alerts": "updates",
    
    # Newsletter & News domains
    "nytimes.com": "newsletters",
    "barrons.com": "newsletters",
    "wsj.com": "newsletters",
    "theinformation.com": "newsletters",
    "hbr.org": "newsletters",
    "marketwatch.com": "newsletters",
    "economist.com": "newsletters",
    "bloomberg.com": "newsletters",
    "morningbrew.com": "newsletters",
    "substack.com": "newsletters",
    "medium.com": "newsletters",
    "wired.com": "newsletters",
    "techcrunch.com": "newsletters",
    "washingtonpost.com": "newsletters",
    "ft.com": "newsletters",
    "cnn.com": "newsletters",
    "forbes.com": "newsletters",
    "reuters.com": "newsletters"
}

# Category priority for when multiple categories match
# Lower number = higher priority
CATEGORY_PRIORITY: Dict[str, int] = {
    "important": 1,
    "personal": 2,
    "primary": 3,
    "newsletters": 4,  # Higher priority than general updates
    "updates": 5,
    "forums": 6,
    "social": 7,
    "promotional": 8,
    "trash": 9,
    "archive": 10
} 