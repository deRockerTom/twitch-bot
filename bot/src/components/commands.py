from datetime import datetime
from typing import TYPE_CHECKING

import twitchio
from main import LOGGER
from twitchio.ext import commands

from shared import Message

if TYPE_CHECKING:
    from main import Bot


class MyComponent(commands.Component):
    def __init__(self, bot: "Bot") -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot

    @commands.command(aliases=["hello", "howdy", "hey"])
    async def hi(self, ctx: commands.Context) -> None:
        """Simple command that says hello!

        !hi, !hello, !howdy, !hey
        """
        await ctx.reply(f"Hello {ctx.chatter.mention}!")

    @commands.command(aliases=["repeat"])
    @commands.is_moderator()
    async def say(self, ctx: commands.Context, *, content: str) -> None:
        """Moderator only command which repeats back what you say.

        !say hello world, !repeat I am cool LUL
        """
        await ctx.send(content)

    @commands.command()
    @commands.is_moderator()
    async def overlay(self, ctx: commands.Context, *, message: str) -> None:
        """Sends a message to the overlay.

        !overlay This is a test message
        """

        if not ctx.message:
            await ctx.reply("Something went wrong, try again later")
            LOGGER.error("Failed to send overlay message: %s", message)
            return

        if not ctx.channel:
            await ctx.reply("Something went wrong, try again later")
            LOGGER.error("Failed to send overlay message: %s", message)
            return

        await self.bot.database.messages.save(
            Message(
                user_id=ctx.chatter.id,
                login=ctx.channel.display_name if ctx.channel.display_name else "unknown",
                message=message,
                timestamp=ctx.message.timestamp if ctx.message.timestamp else datetime.now(),
            )
        )

        await ctx.reply(f"Overlay message sent: {message}")

    @commands.Component.listener()
    async def event_stream_online(self, payload: twitchio.StreamOnline) -> None:
        # Event dispatched when a user goes live from the subscription we made above...

        # Keep in mind we are assuming this is for ourselves
        # others may not want your bot randomly sending messages...
        await payload.broadcaster.send_message(
            sender=self.bot.bot_id,
            message=f"Hi... {payload.broadcaster}! You are live!!!",
        )


# This is our entry point for the module.
async def setup(bot: "Bot") -> None:
    await bot.add_component(MyComponent(bot))
