import pytest
from backend.app.utils.email_categorizer import RuleBasedCategorizer
from backend.app.db import SessionLocal
from backend.app.models import *  # Ensure all models are registered
from backend.app.models.email_category import EmailCategory, CategoryKeyword
from backend.app.models.sender_rule import SenderRule

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# --- Modular Utility to Build Rules from the Real DB ---
def build_rules_from_db_data():
    """
    Query the real DB for all categories, keywords, and sender rules,
    and build the rules dict for RuleBasedCategorizer.
    """
    session = SessionLocal()
    try:
        # Fetch all categories
        categories = session.query(EmailCategory).all()
        # Build categories dict
        categories_dict = {
            str(cat.id): {"name": cat.name, "priority": cat.priority}
            for cat in categories
        }
        # Fetch all keywords
        keywords = session.query(CategoryKeyword).all()
        keywords_dict = {}
        for kw in keywords:
            cat_id = str(kw.category_id)
            if cat_id not in keywords_dict:
                keywords_dict[cat_id] = []
            keywords_dict[cat_id].append({
                "keyword": kw.keyword,
                "is_regex": kw.is_regex,
                "weight": kw.weight
            })
        # Fetch all sender rules
        sender_rules = session.query(SenderRule).all()
        senders_dict = {}
        for sr in sender_rules:
            cat_id = str(sr.category_id)
            if cat_id not in senders_dict:
                senders_dict[cat_id] = []
            senders_dict[cat_id].append({
                "pattern": sr.pattern,
                "is_domain": sr.is_domain,
                "weight": sr.weight
            })
        # Build rules dict
        rules = {
            "categories": categories_dict,
            "keywords": keywords_dict,
            "senders": senders_dict,
        }
        return rules
    finally:
        session.close()

# --- Helper for direct rules dict testing ---
class TestableRuleBasedCategorizer(RuleBasedCategorizer):
    def __init__(self, rules):
        self.rules = []
        # flatten keywords + sender rules from rules dict
        for cat_id, cat in rules.get("categories", {}).items():
            name     = cat.get("name")
            priority = cat.get("priority", 0)
            # keywords
            for kw in rules.get("keywords", {}).get(cat_id, []):
                self.rules.append({
                    "type":     "substring",
                    "value":    kw["keyword"],
                    "category": name,
                    "priority": priority,
                    "weight":   kw.get("weight", 1),
                    "reason":   f"keyword:{kw['keyword']}"
                })
            # sender rules
            for sr in rules.get("senders", {}).get(cat_id, []):
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
        self.rules.sort(key=lambda r: (r["priority"] - r["weight"]))

# --- Parameterized Test Using Real DB Rules ---
@pytest.mark.parametrize("email_data,expected_category", [
    ({
        "labels": [],
        "subject": "Top stories this week: Our most notable stories and conversation starters.",
        "from_email": "admin@twistedsifter.com"
    }, "newsletters"),
    ({
        "labels": [],
        "subject": "📣 LAST CHANCE! Extra 25% Off Plus Up To 50% Off Sitewide",
        "from_email": "luckybrand@cs.luckybrand.com"
    }, "promotions"),
    ({
        "labels": [],
        "subject": "2025-04-13 20:03:21 UPDATED: (M6.5) south of the Fiji Islands -26.1 -178.4 (96494)",
        "from_email": "ens@ens.usgs.gov"
    }, "important"),
    ({
        "labels": ["Inbox"],
        "subject": "Churches are selling for up to $55m",
        "from_email": "news@thehustle.co"
    }, "newsletters"),
])
def test_real_db_rules_categorization(email_data, expected_category, db_session):
    categorizer = RuleBasedCategorizer(db=db_session)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == expected_category
    assert confidence >= 0

def make_categorizer(rules):
    return TestableRuleBasedCategorizer(rules=rules)

@pytest.mark.parametrize("rules,email_data,expected_category", [
    # Techmeme Newsletter
    ({
        "categories": {"1": {"name": "newsletter", "priority": 10}, "2": {"name": "inbox", "priority": 20}},
        "keywords": {},
        "senders": {"1": [{"pattern": "techmeme.com", "is_domain": True, "weight": 1}]},
    },
    {"labels": [], "subject": "US tech tariff exemptions said to be temporary; Mac-tethered Vision Pro in the works", "from_email": "newsletter@techmeme.com"},
    "newsletter"),
    # Lucky Brand Promotion
    ({
        "categories": {"1": {"name": "promotions", "priority": 10}, "2": {"name": "inbox", "priority": 20}},
        "keywords": {"1": [
            {"keyword": "off", "is_regex": False, "weight": 1},
            {"keyword": "sale", "is_regex": False, "weight": 1},
            {"keyword": "discount", "is_regex": False, "weight": 1},
        ]},
        "senders": {"1": [{"pattern": "luckybrand.com", "is_domain": True, "weight": 1}]},
    },
    {"labels": [], "subject": "📣 LAST CHANCE! Extra 25% Off Plus Up To 50% Off Sitewide", "from_email": "luckybrand@cs.luckybrand.com"},
    "promotions"),
    # USGS ENS Important Alert
    ({
        "categories": {"1": {"name": "important", "priority": 5}, "2": {"name": "inbox", "priority": 20}},
        "keywords": {"1": [
            {"keyword": "earthquake", "is_regex": False, "weight": 2},
            {"keyword": "updated", "is_regex": False, "weight": 1},
        ]},
        "senders": {"1": [{"pattern": "usgs.gov", "is_domain": True, "weight": 2}]},
    },
    {"labels": [], "subject": "2025-04-13 20:03:21 UPDATED: (M6.5) south of the Fiji Islands -26.1 -178.4 (96494)", "from_email": "ens@ens.usgs.gov"},
    "important"),
    # The Hustle Newsletter
    ({
        "categories": {"1": {"name": "newsletter", "priority": 10}, "2": {"name": "inbox", "priority": 20}},
        "keywords": {"1": [
            {"keyword": "hustle", "is_regex": False, "weight": 1},
        ]},
        "senders": {"1": [{"pattern": "thehustle.co", "is_domain": True, "weight": 1}]},
    },
    {"labels": [], "subject": "Churches are selling for up to $55m", "from_email": "news@thehustle.co"},
    "newsletter"),
])
def test_sender_based_categorizer(rules, email_data, expected_category):
    categorizer = make_categorizer(rules)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == expected_category
    assert confidence > 0

# 5. TwistedSifter Newsletter
def test_sender_based_categorizer_twistedsifter_newsletter():
    rules = {
        "categories": {
            "1": {"name": "newsletter", "priority": 10},
            "2": {"name": "inbox", "priority": 20},
        },
        "keywords": {
            "1": [
                {"keyword": "top stories", "is_regex": False, "weight": 1},
            ]
        },
        "senders": {
            "1": [
                {"pattern": "twistedsifter.com", "is_domain": True, "weight": 1}
            ]
        },
    }
    email_data = {
        "labels": [],
        "subject": "Neighbor Started Building His Driveway On Their Property, So They Had A Friend Block The Path For The Construction Crew",
        "from_email": "admin@twistedsifter.com"
    }
    categorizer = TestableRuleBasedCategorizer(rules=rules)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == "newsletter"
    assert confidence > 0

# 6. MarketWatch Newsletter
def test_sender_based_categorizer_marketwatch_newsletter():
    rules = {
        "categories": {
            "1": {"name": "newsletter", "priority": 10},
            "2": {"name": "inbox", "priority": 20},
        },
        "keywords": {
            "1": [
                {"keyword": "marketwatch", "is_regex": False, "weight": 1},
            ]
        },
        "senders": {
            "1": [
                {"pattern": "marketwatchmail.com", "is_domain": True, "weight": 1}
            ]
        },
    }
    email_data = {
        "labels": [],
        "subject": "Need to Know: As tariff angst lingers, this wealth manager has just upgraded U.S. stocks",
        "from_email": "reports@marketwatchmail.com"
    }
    categorizer = TestableRuleBasedCategorizer(rules=rules)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == "newsletter"
    assert confidence > 0

# 7. Patient Gateway Important
def test_sender_based_categorizer_patientgateway_important():
    rules = {
        "categories": {
            "1": {"name": "important", "priority": 5},
            "2": {"name": "inbox", "priority": 20},
        },
        "keywords": {
            "1": [
                {"keyword": "patient gateway", "is_regex": False, "weight": 2},
                {"keyword": "new message", "is_regex": False, "weight": 2},
            ]
        },
        "senders": {
            "1": [
                {"pattern": "partners.org", "is_domain": True, "weight": 2}
            ]
        },
    }
    email_data = {
        "labels": [],
        "subject": "You have received a new message in Patient Gateway. Please click here to log in and read it.",
        "from_email": "PatientGateway@partners.org"
    }
    categorizer = TestableRuleBasedCategorizer(rules=rules)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == "important"
    assert confidence > 0

# Test: Display name in from_email should match domain sender rule
def test_sender_rule_domain_with_display_name():
    rules = {
        "categories": {"1": {"name": "newsletter", "priority": 10}},
        "keywords": {},
        "senders": {"1": [{"pattern": "techmeme.com", "is_domain": True, "weight": 1}]},
    }
    email_data = {
        "labels": [],
        "subject": "Nintendo Switch 2 pricing leak",
        "from_email": "Techmeme <newsletter@techmeme.com>"
    }
    categorizer = TestableRuleBasedCategorizer(rules)
    category, confidence, reason = categorizer.categorize(email_data)
    assert category == "newsletter"
    assert confidence > 0 