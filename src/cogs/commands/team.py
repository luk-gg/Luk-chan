from discord import (
    AllowedMentions,
    Embed,
    Interaction,
    Member,
    Message,
    app_commands,
)
from discord.ext import commands

from src._colors import LukColors
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

        self.team_list_ctx = app_commands.ContextMenu(
            name="List team",
            callback=self.team_list_command,
        )
        self.team_edit_ctx = app_commands.ContextMenu(
            name="Edit team",
            callback=self.team_edit_command,
        )
        self.team_delete_ctx = app_commands.ContextMenu(
            name="Close team",
            callback=self.team_delete_command,
        )

        self.bot.tree.add_command(self.team_list_ctx)
        # self.bot.tree.add_command(self.team_edit_ctx)
        self.bot.tree.add_command(self.team_delete_ctx)

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
    async def team_list_command(
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
            and not message.channel.permissions_for(interaction.user).administrator
        ):
            await interaction.followup.send(
                "You are not the owner of this group nor an administrator.",
            )
            return

        thread = message.thread or await message.fetch_thread()

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

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def team_edit_command(
        self,
        interaction: Interaction[commands.Bot],
        message: Message,
    ) -> None:
        pass

    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def team_delete_command(
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
            and not message.channel.permissions_for(interaction.user).administrator
        ):
            await interaction.followup.send(
                "You are not the owner of this group nor an administrator.",
            )
            return

        await message.edit(view=None)

        thread = message.thread or await message.fetch_thread()

        if not thread:
            await interaction.followup.send(
                "Could not find any thread from this message.",
            )
            return

        await thread.send(
            embed=Embed(
                description="This team has been closed and is no longer active.",
                colour=LukColors.primary_blue,
            ).set_author(
                name=interaction.user.name,
                icon_url=interaction.user.display_avatar.url,
            ),
        )

        await interaction.edit_original_response(
            content="Closed successfully.",
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TeamCog(bot))
