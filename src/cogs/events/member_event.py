from typing import TYPE_CHECKING

from discord import Member, TextChannel, Thread
from discord.ext import commands

from src.components.welcome import WelcomeLayoutView

if TYPE_CHECKING:
    from discord.abc import GuildChannel, PrivateChannel


class MemberEvent(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self._channel_id = 862600196704829443
        self._channel: GuildChannel | PrivateChannel | Thread | None = None

    @commands.Cog.listener("on_member_join")
    async def send_welcome(self, _: Member) -> None:
        self._channel = self.bot.get_channel(self._channel_id)

        if self._channel and isinstance(self._channel, TextChannel):
            await self._channel.send(view=WelcomeLayoutView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberEvent(bot))
