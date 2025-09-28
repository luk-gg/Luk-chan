from typing import TYPE_CHECKING

from discord import TextChannel
from discord.ext import commands

from src._channels import LukChannels
from src.components.welcome import WelcomeLayoutView

if TYPE_CHECKING:
    from discord import Member, Thread
    from discord.abc import GuildChannel, PrivateChannel


class MemberNitroEvent(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._channel: GuildChannel | PrivateChannel | Thread | None = None

    @commands.Cog.listener("on_member_update")
    async def user_boosted_guild(self, _: "Member", after: "Member") -> None:
        if not after.premium_since:
            return

        if not self._channel:
            self._channel = self.bot.get_channel(LukChannels.welcome.id)

        if self._channel and isinstance(self._channel, TextChannel):
            await self._channel.send(view=WelcomeLayoutView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberNitroEvent(bot))
