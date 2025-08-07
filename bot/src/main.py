import asyncio
import logging

from config import BOT_SETTINGS
from pymongo import AsyncMongoClient
from twitchio import MultiSubscribePayload, authentication, eventsub, utils
from twitchio.ext import commands

LOGGER = logging.getLogger("Bot")


class Bot(commands.AutoBot):
    database: AsyncMongoClient

    def __init__(
        self, *, database: AsyncMongoClient, subs: list[eventsub.SubscriptionPayload]
    ) -> None:
        super().__init__(
            client_id=BOT_SETTINGS.CLIENT_ID,
            client_secret=BOT_SETTINGS.CLIENT_SECRET,
            bot_id=BOT_SETTINGS.BOT_ID,
            owner_id=BOT_SETTINGS.OWNER_ID,
            prefix="!",
        )
        self.database = database
        self.subs = subs

    async def setup_hook(self) -> None:
        await self.load_module("components.commands")

    async def event_oauth_authorized(self, payload: authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=payload.user_id, user_id=self.bot_id
            ),
        ]

        resp: MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

    async def load_tokens(self) -> None:
        tokens_collection = self.database[BOT_SETTINGS.MONGO__DB]["tokens"]
        rows = await tokens_collection.find({}).to_list(length=None)

        if not rows:
            return

        for row in rows:
            token = row.get("token")
            refresh = row.get("refresh")
            if token and refresh:
                await self.add_token(token, refresh)
            else:
                LOGGER.warning("Token or refresh missing for user: %s", row.get("user_id"))

    async def add_token(self, token: str, refresh: str) -> authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens internally and return us some data...
        resp: authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in MongoDB when they are authorized...
        tokens_collection = self.database[BOT_SETTINGS.MONGO__DB]["tokens"]

        LOGGER.info("Adding token for user: %s with login: %s", resp.user_id, resp.login)

        # Use upsert to insert or update the token for the user
        await tokens_collection.update_one(
            {"user_id": resp.user_id},
            {
                "$set": {
                    "token": token,
                    "refresh": refresh,
                    "user_id": resp.user_id,
                    "login": resp.login,
                }
            },
            upsert=True,
        )

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


async def setup_database(
    db: AsyncMongoClient,
) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    # Create our token table, if it doesn't exist..
    # You should add the created files to .gitignore or potentially store them somewhere safer
    # This is just for example purposes...

    # Ensure the tokens collection exists (MongoDB creates collections automatically on insert)
    tokens_collection = db[BOT_SETTINGS.MONGO__DB]["tokens"]

    # Fetch any existing tokens...
    rows = await tokens_collection.find({}).to_list(length=None)

    tokens: list[tuple[str, str]] = []
    subs: list[eventsub.SubscriptionPayload] = []

    for row in rows:
        tokens.append((row["token"], row["refresh"]))
        subs.append(
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=row["user_id"], user_id=BOT_SETTINGS.BOT_ID
            )
        )
        LOGGER.info("Found token for user %s with login %s", row["user_id"], row["login"])

    return tokens, subs


def main() -> None:
    utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with AsyncMongoClient(
            host=BOT_SETTINGS.MONGO__HOST,
            port=BOT_SETTINGS.MONGO__PORT,
        ) as mongo_client:
            tokens, subs = await setup_database(mongo_client)
            LOGGER.info("Database setup complete with %d tokens", len(tokens))
            LOGGER.info("Setting up bot with %d subscriptions", len(subs))
            async with Bot(database=mongo_client, subs=subs) as bot:
                await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt...")


if __name__ == "__main__":
    main()
