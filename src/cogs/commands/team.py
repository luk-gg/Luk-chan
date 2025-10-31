from discord import Interaction, Message, app_commands
from discord.ext import commands

from src.components.team.create_group import (
    CreateGroupModal,
    GroupView,
)


class BpsrCog(commands.GroupCog, group_name="team", group_description="Team commands"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(GroupView())

        self.check_role_ctx = app_commands.ContextMenu(
            name="Team list",
            callback=self.message_list_group,
        )
        self.bot.tree.add_command(self.check_role_ctx)

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    @app_commands.command(name="create", description="Creates a team")
    async def create_bpsr_group(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(CreateGroupModal())

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def message_list_group(
        self,
        interaction: Interaction[commands.Bot],
        message: Message,
    ) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not message.embeds:
            await interaction.followup.send("This message has no embeds.")
            return

        members = {
            str(field.name).rsplit(" ", 1)[0]: str(field.value).splitlines()
            for field in message.embeds[0].fields
        }

        response = "\n\n".join(
            f"**{role}**:\n"
            + "\n".join(f"- {member}" for member in member_list if member != "\u200b")
            for role, member_list in members.items()
            if member_list and member_list != ["\u200b"]
        )

        await interaction.edit_original_response(content=response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BpsrCog(bot))
