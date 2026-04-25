from datetime import datetime
from zoneinfo import ZoneInfo

from src._constants import TIMEZONES


def get_timezone(tz_abbreviation: str) -> ZoneInfo:
    """Get the ZoneInfo object for a given timezone abbreviation.

    Args:
        tz_abbreviation (str): The timezone abbreviation (e.g., "BRT", "EST").

    Returns:
        ZoneInfo: The corresponding ZoneInfo object, or the UTC ZoneInfo if not found.
    """
    return TIMEZONES.get(tz_abbreviation.upper(), TIMEZONES["UTC"])


def datetime_now() -> datetime:
    """Get the current datetime in UTC.

    Returns:
        datetime: The current datetime with UTC timezone.
    """
    return datetime.now(tz=ZoneInfo("UTC"))


def datetime_to_relative_past_string(dt: datetime) -> str:
    """Calculate the relative time difference from a given datetime to now.

    Args:
        dt (datetime): The datetime to compare with the current time.

    Returns:
        str: A string representing the relative time difference.
    """
    delta = datetime_now() - dt
    total_seconds = int(delta.total_seconds())

    intervals = (
        ("year", 365 * 24 * 60 * 60),
        ("month", 30 * 24 * 60 * 60),
        ("day", 24 * 60 * 60),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    )

    for name, seconds in intervals:
        value = total_seconds // seconds
        if value > 0:
            return f"{value} {name}{'s' if value > 1 else ''} ago"

    return "just now"
