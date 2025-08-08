import logging
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel
from pymongo import ASCENDING

if TYPE_CHECKING:
    from shared.db import DatabaseClient

LOGGER = logging.getLogger(__name__)


class Token(BaseModel):
    user_id: str
    login: str
    token: str
    refresh: str


class TokensDBFunctions:
    """
    Encapsulates all token-related database operations.
    Accessed via `mongo_client.tokens`.
    """

    def __init__(self, client: "DatabaseClient") -> None:
        self._client = client
        self._collection = client[self._client.database_name]["tokens"]

    async def get(
        self,
        length: Optional[int] = None,
    ) -> list[Token]:
        """Fetch all stored tokens."""
        rows = await self._collection.find({}, sort=[("login", ASCENDING)]).to_list(length=length)
        LOGGER.debug("Fetched %d tokens from DB", len(rows))
        return [Token(**row) for row in rows]

    async def save(self, token: Token) -> None:
        """Insert or update a token for a given user."""
        await self._collection.update_one(
            {"user_id": token.user_id},
            {
                "$set": {
                    "token": token.token,
                    "refresh": token.refresh,
                    "user_id": token.user_id,
                    "login": token.login,
                }
            },
            upsert=True,
        )
        LOGGER.info("Saved token for user %s (%s)", token.user_id, token.login)

    async def find_by_user(self, user_id: str) -> Optional[Token]:
        """Find a token for a specific user."""
        data = await self._collection.find_one({"user_id": user_id})
        return Token(**data) if data else None
