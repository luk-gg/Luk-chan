from discord import Interaction, Message, app_commands
from discord.ext import commands

from src.components.admin.check_reactions import CheckReactionsView


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
