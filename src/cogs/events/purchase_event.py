from logging import getLogger
from typing import TYPE_CHECKING

from discord import HTTPException, MessageType
from discord.ext import commands

from src._emojis import LukEmojis
from src._settings import config

if TYPE_CHECKING:
    from discord import Message


class PurchaseEvent(commands.Cog):
    @commands.Cog.listener("on_message")
    async def react_to_purchase(self, message: "Message") -> None:
        if (
            message.type is not MessageType.purchase_notification
            or message.guild is None
            or message.guild.id != config.GUILD_ID
            or message.channel != message.guild.system_channel
        ):
            return

        try:
            await message.add_reaction(LukEmojis.lukchan_point)
        except HTTPException:
            getLogger("luk.purchase").exception(
                "Failed to react to purchase message %s in channel %s",
                message.id,
                message.channel.id,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PurchaseEvent())
