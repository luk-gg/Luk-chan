from discord import Interaction, app_commands
from discord.ext import commands

from src.components.bpsr.create_group import CreateGroupModal


class BpsrCog(commands.GroupCog, group_name="bpsr", group_description="BPSR commands"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    group_commands = app_commands.Group(name="group", description="BPSR group commands")

    @group_commands.command(name="create", description="Create a BPSR group")
    async def create_bpsr_group(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(CreateGroupModal())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BpsrCog(bot))
