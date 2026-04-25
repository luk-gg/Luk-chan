from typing import Literal

from discord import (
    AllowedMentions,
    Embed,
    Interaction,
    Message,
    User,
    app_commands,
    utils,
)
from discord.ext import commands

from src._colors import LukColors
from src._settings import config
from src._utils import datetime_now, datetime_to_relative_past_string
from src.db.leaderboard import LeaderboardDatabase, MonthlyLeaderboardEntry


class LeaderboardCog(commands.Cog):
    leaderboard_group = app_commands.Group(
        name="leaderboard",
        description="Commands related to leaderboard.",
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.leaderboard_db = LeaderboardDatabase()

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> None:
        if message.author.bot or (
            not message.content
            or message.content.isspace()
            or message.content.startswith(("!", "/", "?"))
            or len(message.content) < config.MIN_MESSAGE_LENGTH
        ):
            return

        await self.leaderboard_db.update_user(
            user_id=str(message.author.id),
            message=utils.remove_markdown(message.clean_content).strip(),
            date=message.created_at,
        )

    @leaderboard_group.command(
        name="user",
        description="Shows a user's position in the message leaderboard.",
    )
    @app_commands.describe(member="The member to check the leaderboard position for.")
    async def leaderboard_user(
        self,
        interaction: Interaction,
        member: User | None = None,
    ) -> None:
        user = member or interaction.user

        if user.bot:
            await interaction.response.send_message(
                "Bots are not included in the leaderboard.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        user_data = await self.leaderboard_db.get_user(str(user.id))

        if not user_data:
            await interaction.edit_original_response(
                content=f"{user} has no messages.",
            )
            return

        current_month = datetime_now().strftime("%Y-%m")
        activity_points = user_data.monthly.get(
            current_month,
            MonthlyLeaderboardEntry(message=0, char=0, rank_message=0, rank_char=0),
        )

        embed = Embed(
            description=(
                f"### {user.mention}'s stats\n"
                f"- {datetime_now().strftime('%B %Y')} activity points: "
                f"{activity_points.message:,} (#{activity_points.rank_message:,})\n"
                f"- Total messages sent: {user_data.message:,} "
                f"(#{user_data.rank_message:,})\n"
                f"- Total characters sent: {user_data.char:,} "
                f"(#{user_data.rank_char:,})\n"
                f"- Server join date: {user.joined_at.strftime('%B %d, %Y') if not isinstance(user, User) and user.joined_at else 'Unknown'}\n"  # noqa: E501
                f"- Discord account age: "
                f"{datetime_to_relative_past_string(user.created_at)}\n"
            ),
            colour=LukColors.primary_blue,
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.edit_original_response(
            embed=embed,
            allowed_mentions=AllowedMentions.none(),
        )

    @leaderboard_group.command(
        name="top",
        description="Shows the top users in the message leaderboard.",
    )
    @app_commands.describe(
        _type="The type of leaderboard to show (messages or characters).",
    )
    @app_commands.rename(_type="type")
    async def leaderboard_top(
        self,
        interaction: Interaction,
        _type: Literal["messages", "characters"] = "messages",
    ) -> None:
        await interaction.response.defer()

        top_users = await self.leaderboard_db.get_top_users(limit=10, _type=_type)

        if not top_users:
            await interaction.edit_original_response(
                content="No data available for the leaderboard.",
            )
            return

        embed = Embed(
            title=f"Top 10 users by {_type}",
            colour=LukColors.primary_blue,
        )

        embed.description = ""

        strings: list[str] = []

        for idx, user_data in enumerate(top_users, start=1):
            stat_value = getattr(
                user_data,
                "message" if _type == "messages" else "char",
            )
            strings.append(
                f"**{idx}.** <@{user_data.user_id}> - {stat_value:,} {_type}",
            )

        embed.description = "\n".join(strings)
        await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LeaderboardCog(bot=bot))
