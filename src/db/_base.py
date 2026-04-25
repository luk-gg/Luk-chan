from typing import Any

from pymongo import AsyncMongoClient

from src._settings import config


class Database:
    _client = AsyncMongoClient[Any](config.MONGO_URI)
    _db = _client[config.MONGO_DB_NAME]

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

    async def find(
        self,
        query: dict[str, Any],
        sort: list[tuple[str, int]] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self._collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if limit is not None:
            cursor = cursor.limit(limit)

        return await cursor.to_list(length=limit)

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

    async def insert_many(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        await self._collection.insert_many(documents)
