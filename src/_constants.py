from enum import StrEnum
from typing import Literal, TypedDict
from zoneinfo import ZoneInfo


class TeamPreset(StrEnum):
    BPSR5 = "bpsr-5"
    BPSR10 = "bpsr-10"
    BPSR15 = "bpsr-15"
    BPSR20 = "bpsr-20"


class _Field(TypedDict):
    name: str
    default_limit: float


PRESETS: dict[TeamPreset, list[_Field]] = {
    TeamPreset.BPSR5: [
        {"name": "DPS", "default_limit": 3},
        {"name": "Sup", "default_limit": 1},
        {"name": "Tank", "default_limit": 1},
    ],
    TeamPreset.BPSR10: [
        {"name": "DPS", "default_limit": 6},
        {"name": "Sup", "default_limit": 2},
        {"name": "Tank", "default_limit": 2},
    ],
    TeamPreset.BPSR15: [
        {"name": "DPS", "default_limit": 9},
        {"name": "Sup", "default_limit": 3},
        {"name": "Tank", "default_limit": 3},
    ],
    TeamPreset.BPSR20: [
        {"name": "DPS", "default_limit": 12},
        {"name": "Sup", "default_limit": 4},
        {"name": "Tank", "default_limit": 4},
    ],
}

Timezones = Literal[
    "BRT",
    "ART",
    "CLT",
    "PYT",
    "UYT",
    "GFT",
    "AMT",
    "BOT",
    "EST",
    "CST",
    "MST",
    "PST",
    "PDT",
    "AKST",
    "HST",
    "GMT",
    "UTC",
    "BST",
    "CET",
    "EET",
    "MSK",
    "IST",
    "CST(China)",
    "JST",
    "KST",
    "SGT",
    "HKT",
    "AEST",
    "NZST",
]

TIMEZONES: dict[Timezones | str, ZoneInfo] = {
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
    "PDT": ZoneInfo("America/Los_Angeles"),  # Pacific Standard Time (UTC-8)
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
