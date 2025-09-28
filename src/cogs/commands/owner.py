from discord.ext import commands

from src.components.member_join import MemberJoinView


class OwnerCog(commands.Cog):
    """Commands for the bot owner."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="cv2")
    async def test_cv2_view(self, ctx: commands.Context[commands.Bot]) -> None:
        await ctx.send(view=MemberJoinView(ctx.author))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OwnerCog(bot))
