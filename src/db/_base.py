from typing import Any, Self

from pymongo import AsyncMongoClient

from src._settings import config


class Database:
    __instance: Self | None = None
    _client = AsyncMongoClient[Any](config.MONGO_URI)
    _db = _client[config.MONGO_DB_NAME]

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ANN401, ARG004
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self, collection: str) -> None:
        self._collection = self._db[collection]

    @classmethod
    async def connect(cls) -> None:
        await cls._client.aconnect()
        await cls._client.admin.command("ping")

    @classmethod
    async def disconnect(cls) -> None:
        await cls._client.aclose()

    async def find_one(
        self,
        query: dict[str, Any],
    ) -> dict[str, Any] | None:
        return await self._collection.find_one(query)

    async def insert_one(
        self,
        document: dict[str, Any],
    ) -> None:
        await self._collection.insert_one(document)

    async def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        *,
        upsert: bool = False,
    ) -> None:
        await self._collection.update_one(query, update, upsert=upsert)

    async def delete_one(
        self,
        query: dict[str, Any],
    ) -> None:
        await self._collection.delete_one(query)
