import asyncio
import logging

from config import BOT_SETTINGS
from twitchio import MultiSubscribePayload, authentication, eventsub, utils
from twitchio.ext import commands
from twitchio.web import StarletteAdapter

from shared import DatabaseClient, Token

LOGGER = logging.getLogger("Bot")


class MyStarletteAdapter(StarletteAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "domain" not in kwargs:
            self._domain = "http://localhost:4343"


adapter = MyStarletteAdapter(
    host="0.0.0.0",
    port=4343,
)


class Bot(commands.AutoBot):
    database: DatabaseClient

    def __init__(
        self, *, database: DatabaseClient, subs: list[eventsub.SubscriptionPayload]
    ) -> None:
        super().__init__(
            client_id=BOT_SETTINGS.CLIENT_ID,
            client_secret=BOT_SETTINGS.CLIENT_SECRET,
            bot_id=BOT_SETTINGS.BOT_ID,
            owner_id=BOT_SETTINGS.OWNER_ID,
            prefix="!",
            adapter=adapter,
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
        LOGGER.info("Loading tokens from the database...")
        tokens = await self.database.tokens.get()

        for token in tokens:
            await self.add_token(token.token, token.refresh)
        LOGGER.info("Loaded tokens")

    async def add_token(self, token: str, refresh: str) -> authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens internally and return us some data...
        LOGGER.info("Adding token for user with token: %s", token)
        resp: authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        LOGGER.info("Adding token for user: %s with login: %s", resp.user_id, resp.login)

        assert resp.user_id is not None, "User ID should not be None"
        assert resp.login is not None, "Login should not be None"

        LOGGER.info("Adding token for user: %s with login: %s", resp.user_id, resp.login)

        # Store our tokens in MongoDB when they are authorized...
        await self.database.tokens.save(
            Token(
                user_id=resp.user_id,
                login=resp.login,
                token=token,
                refresh=refresh,
            )
        )

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


async def setup_database(
    db: DatabaseClient,
) -> tuple[list[Token], list[eventsub.SubscriptionPayload]]:
    # Fetch any existing tokens...
    LOGGER.info("Fetching tokens from the database...")
    tokens = await db.tokens.get()

    subs: list[eventsub.SubscriptionPayload] = []

    for token in tokens:
        subs.append(
            eventsub.ChatMessageSubscription(
                broadcaster_user_id=token.user_id, user_id=BOT_SETTINGS.BOT_ID
            )
        )
        LOGGER.info("Found token for user %s with login %s", token.user_id, token.login)

    return tokens, subs


def main() -> None:
    utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with DatabaseClient(
            host=BOT_SETTINGS.MONGO__HOST,
            port=BOT_SETTINGS.MONGO__PORT,
            database_name=BOT_SETTINGS.MONGO__DB,
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
