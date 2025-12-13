from discord import (
    AllowedMentions,
    Interaction,
    Member,
    Message,
    TextChannel,
    app_commands,
)
from discord.ext import commands

from src._constants import TeamPreset
from src.components.team.create_group import (
    CreateGroupModal,
    GroupView,
)
from src.embeds.team.group_controller import GroupEmbedController


@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class TeamCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(GroupView())

        self.check_role_ctx = app_commands.ContextMenu(
            name="Team list",
            callback=self.message_list_group,
        )
        self.bot.tree.add_command(self.check_role_ctx)

    @app_commands.command(
        name="team",
        description="Create a team group",
    )
    async def create_team(
        self,
        interaction: Interaction,
        preset: TeamPreset = TeamPreset.BPSR5,
    ) -> None:
        await interaction.response.send_modal(CreateGroupModal(preset))

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def message_list_group(
        self,
        interaction: Interaction[commands.Bot],
        message: Message,
    ) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not isinstance(interaction.user, Member):
            await interaction.followup.send(
                "This command can only be used by members. (in a guild)",
            )
            return

        if not message.embeds:
            await interaction.followup.send("This message has no embeds.")
            return

        controller = GroupEmbedController.from_message(message.embeds[0], message.id)

        if (
            interaction.user.id != controller.data.owner.id
            and not interaction.channel.permissions_for(interaction.user).administrator
        ):
            await interaction.followup.send(
                "You are not the owner of this group nor an administrator.",
            )
            return

        thread = interaction.messsage.thread or await interaction.message.fetch_thread()

        if not thread:
            await interaction.followup.send(
                "Could not find any thread from this message.",
            )
            return

        msg = await thread.send(
            content=controller.generate_list(interaction.user),
            allowed_mentions=AllowedMentions.all(),
        )
        await interaction.edit_original_response(
            content=f"Sent team call. {msg.jump_url}",
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TeamCog(bot))
