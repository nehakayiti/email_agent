"""
Email categorization constants and keyword sets.

This module contains the keywords and patterns used for email categorization.
These can be dynamically updated over time based on user behavior and preferences.
"""
from typing import Dict, Set, List

# Map of category name to a set of keywords found in subject lines
# Using sets for O(1) lookup performance
CATEGORY_KEYWORDS: Dict[str, Set[str]] = {
    "promotions": {
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
    "important": {
        # Original important keywords
        "urgent", "important", "attention", "priority", "critical", "required",
        "action", "deadline", "expiration", "immediate", "asap", "now", "approval",
        "password", "security", "alert", "warning", "notice", "tax", "legal",
        # Added from personal
        "hello", "hey", "hi", "private", "confidential", "personal", "family", 
        "friend", "fyi", "introduction", "meeting", "appointment", "coffee", 
        "lunch", "dinner", "call",
        # Added high-priority update terms
        "confirm", "confirmation", "receipt", "payment", "verification", "verify"
    },
    "newsletters": {
        # Original newsletter keywords
        "newsletter", "digest", "weekly", "daily", "monthly", "edition", "issue",
        "bulletin", "report", "roundup", "update", "news", "briefing", "summary",
        "today's", "this week", "this month", "breaking", "latest", "trending",
        "insights", "analysis", "exclusive", "featuring", "spotlight",
        # Added from updates
        "notification", "alert", "status", "statement", "bill", "invoice", 
        "purchase", "shipping", "tracking", "delivery",
        # Added from forums
        "forum", "thread", "topic", "discussion", "post", "reply", "digest", "community",
        "bulletin", "board", "mailing list", "subscribe", "unsubscribe"
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
    "tiktok.com": "social",
    "snapchat.com": "social",
    "youtube.com": "social",
    "reddit.com": "social",
    "discord.com": "social",
    "slack.com": "social",
    
    # Common promotional senders
    "marketing": "promotions",
    "newsletter": "promotions",
    "noreply": "promotions",
    "promotions": "promotions",
    "info": "promotions",
    "offers": "promotions",
    "deals": "promotions",
    "sales": "promotions",
    
    # Update services - now in newsletters
    "accounts": "newsletters",
    "notifications": "newsletters",
    "no-reply": "newsletters", 
    "donotreply": "newsletters",
    "alerts": "newsletters",
    "updates": "newsletters",
    
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
    "newsletters": 2,
    "social": 3,
    "promotions": 4,
    "trash": 5,      # Keeping trash and archive
    "archive": 6
} 