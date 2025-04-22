def set_email_category_and_labels(email, new_category):
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