from sqlalchemy.orm import Session
from ..models.email_category import EmailCategory

def set_email_category_and_labels(email, new_category, db: Session = None):
    """
    Set the email's category and update labels accordingly.
    If db is provided, validate new_category against valid categories in the database.
    Raise ValueError if invalid.
    """
    if db is not None:
        valid_categories = {cat.name for cat in db.query(EmailCategory).all()}
        if new_category not in valid_categories:
            raise ValueError(f"Invalid category '{new_category}'. Must be one of: {', '.join(valid_categories)}")
    old_category = email.category
    email.category = new_category
    labels = set(email.labels or [])
    if new_category == 'trash':
        labels.add('TRASH')
        labels.discard('INBOX')
    elif new_category == 'archive':
        labels.discard('INBOX')
        labels.discard('TRASH')
    else:
        labels.add('INBOX')
        labels.discard('TRASH')
    email.labels = list(labels)
    return old_category != new_category 