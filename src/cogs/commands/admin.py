import json
from io import BytesIO

from discord import File, Interaction, Message, Permissions, TextChannel, app_commands
from discord.ext import commands

from src._settings import config
from src.components.admin.check_reactions import CheckReactionsView
from src.db.leaderboard import LeaderboardDatabase


class AdminCog(commands.Cog):
    admin_group = app_commands.Group(
        name="admin",
        description="Admin-only commands.",
        guild_only=True,
        default_permissions=Permissions(administrator=True),
    )

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._leadeboard_db = LeaderboardDatabase()

        self.check_role_ctx = app_commands.ContextMenu(
            name="Roll call",
            callback=self.message_check,
        )
        self.bot.tree.add_command(self.check_role_ctx)

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def message_check(
        self,
        interaction: Interaction[commands.Bot],
        message: Message,
    ) -> None:
        if not message.reactions:
            await interaction.response.send_message(
                "This message has no reactions.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            view=CheckReactionsView(message),
            ephemeral=True,
        )

    @admin_group.command(name="leaderboard", description="Syncs the leaderboard.")
    async def sync_leaderboard(self, interaction: Interaction[commands.Bot]) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        guild = interaction.guild

        if not guild:
            await interaction.edit_original_response(
                content="This command can only be used in a guild.",
            )
            return

        table: dict[int, dict[int, int]] = {}

        for channel in await guild.fetch_channels():
            if isinstance(channel, (TextChannel)):
                table[channel.id] = {}

                async for message in channel.history(limit=None):
                    if message.author.bot or (
                        not message.content
                        or message.content.isspace()
                        or message.content.startswith(("!", "/", "?"))
                        or len(message.content) < config.MIN_MESSAGE_LENGTH
                    ):
                        continue

                    await self._leadeboard_db.update_user(
                        user_id=str(message.author.id),
                        message=message.content.strip(),
                    )
                    if message.author.id not in table[channel.id]:
                        table[channel.id][message.author.id] = 0

                    table[channel.id][message.author.id] += 1

        await interaction.followup.send(
            content=(
                "Leaderboard synced successfully.\n\n"
                f"Channels synced: {len(table)}\n"
                f"Users synced: {sum(len(users) for users in table.values())}"
            ),
            ephemeral=True,
            file=File(
                BytesIO(json.dumps(table, indent=4).encode()),
                filename="leaderboard.json",
            ),
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
