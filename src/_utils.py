from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONES = {
    # América do Sul
    "BRT": ZoneInfo("America/Sao_Paulo"),  # Brasília Time (UTC-3)
    "ART": ZoneInfo("America/Argentina/Buenos_Aires"),  # Argentina (UTC-3)
    "CLT": ZoneInfo("America/Santiago"),  # Chile Standard Time (UTC-4)
    "PYT": ZoneInfo("America/Asuncion"),  # Paraguay Time (UTC-4)
    "UYT": ZoneInfo("America/Montevideo"),  # Uruguay Time (UTC-3)
    "GFT": ZoneInfo("America/Cayenne"),  # French Guiana (UTC-3)
    "AMT": ZoneInfo("America/Manaus"),  # Amazon Time (UTC-4)
    "BOT": ZoneInfo("America/La_Paz"),  # Bolivia Time (UTC-4)
    # América do Norte
    "EST": ZoneInfo("America/New_York"),  # Eastern Standard Time (UTC-5)
    "CST": ZoneInfo("America/Chicago"),  # Central Standard Time (UTC-6)
    "MST": ZoneInfo("America/Denver"),  # Mountain Standard Time (UTC-7)
    "PST": ZoneInfo("America/Los_Angeles"),  # Pacific Standard Time (UTC-8)
    "AKST": ZoneInfo("America/Anchorage"),  # Alaska (UTC-9)
    "HST": ZoneInfo("Pacific/Honolulu"),  # Hawaii (UTC-10)
    # Europa
    "GMT": ZoneInfo("Etc/GMT"),  # Greenwich Mean Time (UTC+0)
    "UTC": ZoneInfo("UTC"),  # Coordinated Universal Time
    "BST": ZoneInfo("Europe/London"),  # British Summer Time (UTC+1)
    "CET": ZoneInfo("Europe/Paris"),  # Central European Time (UTC+1)
    "EET": ZoneInfo("Europe/Athens"),  # Eastern European Time (UTC+2)
    "MSK": ZoneInfo("Europe/Moscow"),  # Moscow Time (UTC+3)
    # Ásia
    "IST": ZoneInfo("Asia/Kolkata"),  # India Standard Time (UTC+5:30)
    "CST(China)": ZoneInfo("Asia/Shanghai"),  # China Standard Time (UTC+8)
    "JST": ZoneInfo("Asia/Tokyo"),  # Japan Standard Time (UTC+9)
    "KST": ZoneInfo("Asia/Seoul"),  # Korea Standard Time (UTC+9)
    "SGT": ZoneInfo("Asia/Singapore"),  # Singapore Time (UTC+8)
    "HKT": ZoneInfo("Asia/Hong_Kong"),  # Hong Kong Time (UTC+8)
    # Oceania
    "AEST": ZoneInfo("Australia/Sydney"),  # Australian Eastern Standard Time (UTC+10)
    "NZST": ZoneInfo("Pacific/Auckland"),  # New Zealand Standard Time (UTC+12)
}


def get_timezone(tz_abbreviation: str) -> ZoneInfo | None:
    """Get the ZoneInfo object for a given timezone abbreviation.

    Args:
        tz_abbreviation (str): The timezone abbreviation (e.g., "BRT", "EST").

    Returns:
        ZoneInfo | None: The corresponding ZoneInfo object, or None if not found.
    """
    return TIMEZONES.get(tz_abbreviation.upper())


def datetime_now() -> datetime:
    """Get the current datetime in UTC.

    Returns:
        datetime: The current datetime with UTC timezone.
    """
    return datetime.now(tz=ZoneInfo("UTC"))
