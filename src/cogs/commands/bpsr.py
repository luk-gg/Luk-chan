from discord import app_commands
from discord.ext import commands


class BpsrCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.GROUP = app_commands.Group(name="bpsr", description="BPSR commands")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BpsrCog(bot))
