import logging

from pymongo import AsyncMongoClient

from shared.tokens import TokensDBFunctions

LOGGER = logging.getLogger(__name__)


class DatabaseClient(AsyncMongoClient):
    """
    Custom MongoDB client that extends AsyncMongoClient with app-specific queries.
    Works exactly like AsyncMongoClient but adds helper methods for our bot.
    """

    def __init__(self, *, host: str, port: int, database_name: str) -> None:
        super().__init__(host=host, port=port)
        self.database_name = database_name
        self.tokens = TokensDBFunctions(self)

    async def __aenter__(self) -> "DatabaseClient":
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await super().__aexit__(exc_type, exc_value, traceback)
