"""
Email categorization utilities with a simple, one-pass rule engine.

This module fetches categorization rules from the database, flattens
them into an ordered list, and assigns the first matching category.
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID
from sqlalchemy.orm import Session
from ..services.category_service import get_categorization_rules
from email.utils import parseaddr

logger = logging.getLogger(__name__)

class RuleBasedCategorizer:
    """
    One-pass engine: flatten all DB rules + hard-coded labels,
    sort by (priority – weight), then return on first match.
    """
    def __init__(self, db: Session = None, user_id: Optional[UUID] = None):
        self.db = db
        self.user_id = user_id
        raw = get_categorization_rules(db, user_id)

        # start with hard‑coded trash labels
        self.rules: List[Dict[str, Any]] = [
            {"type": "label", "value": "TRASH", "category": "trash", "priority": 0, "weight": 0, "reason": "label:TRASH"},
            {"type": "label", "value": "SPAM",  "category": "trash", "priority": 0, "weight": 0, "reason": "label:SPAM"},
        ]

        # flatten keywords + sender rules from DB
        for cat_id, cat in raw.get("categories", {}).items():
            name     = cat.get("name")
            priority = cat.get("priority", 0)
            # keywords
            for kw in raw.get("keywords", {}).get(cat_id, []):
                self.rules.append({
                    "type":     "substring",
                    "value":    kw["keyword"],
                    "category": name,
                    "priority": priority,
                    "weight":   kw.get("weight", 1),
                    "reason":   f"keyword:{kw['keyword']}"
                })
            # sender rules
            for sr in raw.get("senders", {}).get(cat_id, []):
                typ = "domain" if sr.get("is_domain", True) else "substring"
                self.rules.append({
                    "type":     typ,
                    "value":    sr["pattern"],
                    "category": name,
                    "priority": priority,
                    "weight":   sr.get("weight", 1),
                    "reason":   f"sender:{sr['pattern']}"
                })

        # sort so highest‑priority (smallest priority–weight) comes first
        def rule_sort_key(r):
            # Prefer label > domain > substring for same (priority-weight)
            type_order = {"label": 0, "domain": 1, "substring": 2}
            return (r["priority"] - r["weight"], type_order.get(r["type"], 99))
        self.rules.sort(key=rule_sort_key)

    def categorize(self, email_data: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Categorize an email based on the first matching rule.

        Returns:
            category_name, confidence (always 1.0), reason
        """
        labels     = email_data.get("labels", []) or []
        subject    = (email_data.get("subject") or "").lower()
        from_email_raw = (email_data.get("from_email") or "").lower()
        # Extract just the email address for matching
        _, from_email = parseaddr(from_email_raw)
        from_email = from_email.lower()

        # Normalize labels to uppercase for fallback logic
        labels_upper = [label.upper() for label in labels]

        # one‑pass through rules
        for r in self.rules:
            if r["type"] == "label":
                if r["value"] in labels:
                    return r["category"], 1.0, r["reason"]
            elif r["type"] == "domain":
                # Match if the email ends with the domain (e.g., usgs.gov), allowing subdomains
                if from_email.endswith(r["value"].lower()):
                    return r["category"], 1.0, r["reason"]
            else:  # substring
                if r["value"].lower() in from_email:
                    return r["category"], 1.0, r["reason"]
                if r["value"].lower() in subject:
                    return r["category"], 1.0, r["reason"]

        # fallback: archive if removed from inbox, else important
        if "INBOX" not in labels_upper:
            return "archive", 1.0, "fallback:archive"
        return "important", 1.0, "fallback:important"


def categorize_email(
    email_data: Dict[str, Any],
    db: Session,
    user_id: Optional[UUID] = None
) -> str:
    """
    Helper function to categorize an email from a data dictionary.

    Returns:
        Category string.
    """
    try:
        logger.info("[EMAIL_CAT] Starting categorization")
        categorizer = RuleBasedCategorizer(db, user_id)
        category, _, _ = categorizer.categorize(email_data)
        logger.info(f"[EMAIL_CAT] Result: {category}")
        return category
    except Exception as e:
        logger.error(f"[EMAIL_CAT] Error: {e}", exc_info=True)
        return "primary"


def determine_category(
    gmail_labels: List[str],
    subject: str,
    from_email: str,
    db: Session,
    user_id: Optional[UUID] = None
) -> str:
    """
    Determine email category based on Gmail labels, subject, and sender.
    Maintained for backward compatibility.
    """
    try:
        email_data = {
            "labels": gmail_labels,
            "subject": subject,
            "from_email": from_email,
            "gmail_id": "unknown"
        }
        categorizer = RuleBasedCategorizer(db, user_id)
        category, _, _ = categorizer.categorize(email_data)
        return category
    except Exception:
        return "primary"


def categorize_email_from_labels(
    labels: List[str],
    db: Session,
    user_id: Optional[UUID] = None
) -> str:
    """
    Categorize an email based only on Gmail labels.
    """
    try:
        email_data = {
            "labels": labels,
            "subject": "",
            "from_email": "",
            "gmail_id": "unknown_from_labels"
        }
        categorizer = RuleBasedCategorizer(db, user_id)
        category, _, _ = categorizer.categorize(email_data)
        return category
    except Exception:
        return "primary"