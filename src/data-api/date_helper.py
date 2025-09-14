from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_upcoming_weekend():
    today = datetime.now(ZoneInfo("Europe/London"))
    weekday = today.weekday()
    days_until_friday = (4 - weekday) % 7
    friday = today + timedelta(days=days_until_friday)
    return [
        friday.strftime("%Y-%m-%d"),
        (friday + timedelta(days=1)).strftime("%Y-%m-%d"),
        (friday + timedelta(days=2)).strftime("%Y-%m-%d")
    ]
