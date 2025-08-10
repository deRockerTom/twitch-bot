import logging
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from shared.db import DatabaseClient

LOGGER = logging.getLogger(__name__)


class Message(BaseModel):
    """
    Represents a message sent to the bot to display on an overlay.
    """

    user_id: str
    login: str
    message: str
    timestamp: datetime  # ISO 8601 format

    def __str__(self) -> str:
        return f"{self.login}: {self.message} at {self.timestamp}"


class MessagesDBFunctions:
    """
    Encapsulates all message-related database operations.
    Accessed via `mongo_client.messages`.
    """

    def __init__(self, client: "DatabaseClient") -> None:
        self._client = client
        self._collection = client[self._client.database_name]["messages"]

    async def save(self, message: Message) -> None:
        """Insert a new message into the database."""
        await self._collection.insert_one(message.model_dump())
        LOGGER.info("Saved message from user %s (%s)", message.user_id, message.login)
