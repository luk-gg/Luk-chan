from datetime import datetime
from typing import Any, Literal, Self

from pydantic import BaseModel

from src.db._base import Database


class MonthlyLeaderboardEntry(BaseModel):
    message: int
    char: int
    rank_message: int
    rank_char: int


class _LeaderboardRankedEntry(BaseModel):
    user_id: str
    message: int
    char: int
    rank_message: int
    rank_char: int
    monthly: dict[str, MonthlyLeaderboardEntry]


class LeaderboardDatabase:
    __instance: Self | None = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self._db = Database("leaderboard")
        self._view = Database("leaderboard-ranked")

    async def update_user(
        self,
        user_id: str,
        message: str,
        date: datetime,
    ) -> None:
        await self._db.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "message": 1,
                    "char": len(message.strip()),
                    f"monthly.{date.strftime('%Y-%m')}.message": 1,
                    f"monthly.{date.strftime('%Y-%m')}.char": len(
                        message.strip(),
                    ),
                },
            },
            upsert=True,
        )

    async def set_leaderboard(self, leaderboard: list[dict[str, Any]]) -> None:
        await self._db.insert_many(leaderboard)

    async def get_user(self, user_id: str) -> _LeaderboardRankedEntry | None:
        if data := await self._view.find_one({"user_id": user_id}):
            return _LeaderboardRankedEntry(**data)
        return None

    async def get_top_users(
        self,
        limit: int = 10,
        _type: Literal["messages", "characters", "month"] = "messages",
    ) -> list[_LeaderboardRankedEntry]:
        sort_key = "rank_" + ("message" if _type == "messages" else "char")
        return [
            _LeaderboardRankedEntry(**entry)
            for entry in await self._view.find(
                {},
                sort=[(sort_key, 1)],
                limit=limit,
            )
        ]
