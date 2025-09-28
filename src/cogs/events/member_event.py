from typing import TYPE_CHECKING

from discord import Member, TextChannel, Thread
from discord.ext import commands

from src._channels import LukChannels
from src._emojis import LukEmojis
from src.components.member_join import MemberJoinView

if TYPE_CHECKING:
    from discord.abc import GuildChannel, PrivateChannel


class MemberJoinEvent(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._channel: GuildChannel | PrivateChannel | Thread | None = None

    @commands.Cog.listener("on_member_join")
    async def send_welcome(self, member: Member) -> None:
        if not self._channel:
            self._channel = self.bot.get_channel(LukChannels.welcome.id)

        if self._channel and isinstance(self._channel, TextChannel):
            msg = await self._channel.send(view=MemberJoinView(member))
            await msg.add_reaction(LukEmojis.wave)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemberJoinEvent(bot))
