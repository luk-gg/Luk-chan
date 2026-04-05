from typing import Self

from src.db._base import Database


class LeaderboardDatabase:
    __instance: Self | None = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self) -> None:
        self._db = Database("leaderboard")

    async def update_user(
        self,
        user_id: str,
        message: str,
    ) -> None:
        await self._db.update_one(
            {"user_id": user_id},
            {"$inc": {"message": 1, "char": len(message)}},
            upsert=True,
        )
