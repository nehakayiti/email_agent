from datetime import date, timedelta
from sqlalchemy import select, func, cast, Date
from app.models.email import Email
from sqlalchemy.orm import Session

def analyze_email_volume(db: Session, days: int = 30) -> dict:
    # First, determine the latest date on which an email was received.
    # We cast Email.received_at to a Date so that time is removed.
    max_date = db.scalar(select(func.max(cast(Email.received_at, Date))))
    # If there is no data, use today's date.
    if max_date is None:
        max_date = date.today()

    # Define the start of the range (inclusive)
    start_date = max_date - timedelta(days=days - 1)

    # Build a query to aggregate email counts by date for the relevant period.
    query = (
        select(
            cast(Email.received_at, Date).label("date"),
            func.count(Email.id).label("count")
        )
        .where(cast(Email.received_at, Date) >= start_date)
        .group_by(cast(Email.received_at, Date))
        .order_by(cast(Email.received_at, Date))
    )
    result = db.execute(query)
    rows = result.fetchall()
    
    # Build a dictionary: {date: count}
    counts_by_date = {row.date: row.count for row in rows}
    
    # Generate the complete date series ending with max_date.
    # For example, if max_date is Feb 17 and days=5, we generate Feb 13,14,15,16,17.
    all_dates = [max_date - timedelta(days=x) for x in reversed(range(days))]
    
    daily_volume = []
    total_emails = 0
    for d in all_dates:
        cnt = counts_by_date.get(d, 0)
        total_emails += cnt
        daily_volume.append({"date": d.isoformat(), "count": cnt})
    
    return {
        "daily_volume": daily_volume,
        "total_days": days,
        "total_emails": total_emails,
    }
