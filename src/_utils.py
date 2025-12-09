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
