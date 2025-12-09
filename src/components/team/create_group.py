from datetime import timedelta
from typing import TypedDict

from dateutil.parser import parse
from discord import (
    ButtonStyle,
    Interaction,
    Member,
    Message,
    PartialEmoji,
    SelectOption,
    TextChannel,
    TextStyle,
    User,
    ui,
)
from discord.utils import format_dt

from src._constants import PRESETS, TeamPreset
from src._emojis import LukEmojis
from src._settings import config
from src._utils import TIMEZONES, datetime_now
from src.embeds.team.group_controller import IMAGINE_EMOJIS, GroupEmbedController


class CreateGroupModal(ui.Modal):
    def __init__(self, preset: TeamPreset) -> None:
        super().__init__(
            title="Create a Team",
            timeout=300,
        )

        self.preset = preset

        self.group_name = ui.TextInput["CreateGroupModal"](
            label="Name or Objective",
            style=TextStyle.short,
            placeholder="Enter the name or objective of your group",
            max_length=50,
        )

        self.description = ui.TextInput["CreateGroupModal"](
            label="Description",
            style=TextStyle.paragraph,
            placeholder="Enter a brief description of your group",
            max_length=1000,
            required=False,
        )

        self.time = ui.TextInput["CreateGroupModal"](
            label="Preferred Meeting Time (future only)",
            style=TextStyle.short,
            placeholder="e.g., '2024-12-31 20:00 BRT' or 'Dec 31 8pm EST'",
            default=(datetime_now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M %Z"),
            required=True,
        )

        self.fields = ui.TextInput["CreateGroupModal"](
            label="Fields and Limits",
            style=TextStyle.short,
            placeholder=("e.g., 'DPS:3 Healer:1 Tank:1' for 3 DPS, 1 Healer, 1 Tank"),
            required=False,
            default=self._get_preset(preset),
        )

        self.add_item(self.group_name)
        self.add_item(self.description)
        self.add_item(self.time)
        self.add_item(self.fields)

    def _get_preset(self, preset: TeamPreset) -> str:
        return " ".join(
            f"{field['name']}:{field['default_limit']}"
            for field in PRESETS.get(preset, PRESETS[TeamPreset.BPSR5])
        )

    def parse_limit(
        self,
    ) -> tuple[float, float, float]:
        dps, healers, tanks = 3, 1, 1
        if not self.fields.value:
            return dps, healers, tanks

        try:
            parts = self.fields.value.split()
            for part in parts:
                role_part = part.split(":")
                if len(role_part) != 2:  # noqa: PLR2004
                    role = role_part[0]
                    count = float("inf")
                else:
                    role, count = role_part

                count_int = float(count)
                if role.lower() == "dps":
                    dps = count_int
                elif role.lower() == "healer":
                    healers = count_int
                elif role.lower() == "tank":
                    tanks = count_int
        except ValueError:
            return dps, healers, tanks
        else:
            return dps, healers, tanks

    async def on_submit(self, interaction: Interaction) -> None:
        group_name = self.group_name.value
        description = self.description.value
        leader = interaction.user
        dps_limit, healer_limit, tank_limit = self.parse_limit()
        time = parse(
            self.time.value,
            tzinfos=TIMEZONES,
        )

        if not time:
            msg = f"Invalid date format. {self.time.value!r} could not be parsed."
            raise ValueError(msg)

        if datetime_now().timestamp() > time.timestamp():
            msg = "The specified time is in the past. Please provide a future time."
            raise ValueError(msg)

        controller = GroupEmbedController(
            name=group_name,
            dps_limit=dps_limit,
            healer_limit=healer_limit,
            tank_limit=tank_limit,
            time=time,
            desc=description,
            owner=leader,
        )

        await interaction.response.send_message(
            embed=controller.embed,
            ephemeral=True,
            view=_ConfirmGroupCreateView(controller),
        )


class _ConfirmGroupCreateView(ui.View):
    def __init__(self, controller: GroupEmbedController) -> None:
        super().__init__(timeout=300)
        self.controller = controller

    @ui.button(
        label="Confirm",
        style=ButtonStyle.success,
        custom_id="confirm_create_group:confirm",
    )
    async def confirm_button(
        self,
        interaction: Interaction,
        _: ui.Button["_ConfirmGroupCreateView"],
    ) -> None:
        await interaction.response.defer()
        await interaction.followup.send(embed=self.controller.embed, view=GroupView())
        return

        if not interaction.guild:
            await interaction.followup.send(
                content="Error: This interaction must be used in a guild.",
                ephemeral=True,
            )
            return

        channel = interaction.guild.get_channel(config.BPSR_GROUP_CHANNEL_ID)

        if not channel or not isinstance(channel, (TextChannel)):
            await interaction.followup.send(
                content="Error: Could not find the designated group channel.",
                ephemeral=True,
            )
            return

        msg = await channel.send(embed=self.controller.embed, view=GroupView())
        await msg.create_thread(name=self.controller.data.name)

        await interaction.followup.send(
            content=f"Group creation confirmed! {msg.jump_url}",
            ephemeral=True,
        )


class GroupView(ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.controller: GroupEmbedController | None = None

    @ui.button(
        label="Join Group",
        style=ButtonStyle.primary,
        custom_id="group_view:join_group",
    )
    async def join_button(
        self,
        interaction: Interaction,
        _: ui.Button["GroupView"],
    ) -> None:
        if not interaction.message:
            await interaction.response.send_message(
                content="Error: No message found.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        await interaction.followup.send(
            content="Choose your role to join the group.",
            ephemeral=True,
            view=JoinGroupView(interaction.message),
        )

    @ui.button(
        label="Leave Group",
        style=ButtonStyle.danger,
        custom_id="group_view:leave_group",
    )
    async def leave_button(
        self,
        interaction: Interaction,
        _: ui.Button["GroupView"],
    ) -> None:
        if not interaction.message or not interaction.message.embeds:
            await interaction.response.send_message(
                content="Error: No message found.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        controller = GroupEmbedController.from_message(
            interaction.message.embeds[0],
            message_id=interaction.message.id,
        )
        controller.remove_member(interaction.user)

        await interaction.edit_original_response(embed=controller.embed)

        await interaction.followup.send(
            content=(
                f"You have left {controller.data.owner.name}'s "
                f'group "{controller.data.name}" at '
                f"{format_dt(controller.data.time, 'F')}."
            ),
            ephemeral=True,
        )


class _RoleMapping(TypedDict):
    id: str
    name: str
    role: str
    emoji: PartialEmoji


_role_mapping: dict[str, _RoleMapping] = {
    # Classes
    # DPS
    "sb": {
        "id": "sb",
        "name": "Stormblade",
        "role": "dps",
        "emoji": LukEmojis.sb,
    },
    "fm": {
        "id": "fm",
        "name": "Frost Mage",
        "role": "dps",
        "emoji": LukEmojis.fm,
    },
    "wk": {
        "id": "wk",
        "name": "Wind Knight",
        "role": "dps",
        "emoji": LukEmojis.wk,
    },
    "mm": {
        "id": "mm",
        "name": "Marksman",
        "role": "dps",
        "emoji": LukEmojis.mm,
    },
    # Healer
    "vo": {
        "id": "vo",
        "name": "Verdant Oracle",
        "role": "healer",
        "emoji": LukEmojis.vo,
    },
    "bp": {
        "id": "bp",
        "name": "Beat Performer",
        "role": "healer",
        "emoji": LukEmojis.bp,
    },
    # Tank
    "sk": {
        "id": "sk",
        "name": "Shield Knight",
        "role": "tank",
        "emoji": LukEmojis.sk,
    },
    "hg": {
        "id": "hg",
        "name": "Heavy Guardian",
        "role": "tank",
        "emoji": LukEmojis.hg,
    },
}

_role_map = {
    "dps": "Damage",
    "healer": "Support",
    "tank": "Tank",
}


class JoinGroupView(ui.View):
    def __init__(self, message: Message) -> None:
        super().__init__(timeout=300)
        self.message = message

    def get_response_message(
        self,
        controller: GroupEmbedController,
        member: Member | User,
    ) -> str:
        user = controller.find_member(member)
        if user:
            user_role = user.role.split(":")[1]
            airona = (
                ""
                if (user.airona is None)
                else (
                    f"Airona A{
                        IMAGINE_EMOJIS['airona'][user.airona].name.rsplit('A', 1)[1]
                    }"
                )
            )

            tina = (
                ""
                if (user.tina is None)
                else (
                    f"Tina A{IMAGINE_EMOJIS['tina'][user.tina].name.rsplit('A', 1)[1]}"
                )
            )

            return (
                f"You have joined {controller.data.owner.name}'s group "
                f'"{controller.data.name}" at {format_dt(controller.data.time, "F")} '
                f"as {_role_mapping[user_role]['name']}{
                    ('' if not user.airona and not user.tina else ' with ')
                }"
                f"{airona}{(' and ' if airona and tina else '')}{tina}."
                f"{' You are also helping!' if user.help else ''}"
            )

        return "Missing user in group data."

    @ui.select(
        placeholder="Select your role to join the group",
        min_values=1,
        max_values=1,
        options=[
            SelectOption(
                label=role["name"],
                emoji=role["emoji"],
                value=id_,
            )
            for id_, role in _role_mapping.items()
        ],
        custom_id="join_group_view:select_role",
    )
    async def select_role(
        self,
        interaction: Interaction,
        select: ui.Select["JoinGroupView"],
    ) -> None:
        await interaction.response.defer()

        selected_role = _role_mapping[select.values[0]]
        controller = GroupEmbedController.from_message(
            self.message.embeds[0],
            message_id=self.message.id,
        )
        controller.add_member(
            member=interaction.user,
            role=selected_role["role"],
            emoji=selected_role["emoji"],
        )

        await self.message.edit(embed=controller.embed)
        self.message.embeds[0] = controller.embed

        await interaction.edit_original_response(
            content=self.get_response_message(controller, interaction.user),
        )

    @ui.select(
        placeholder="Select your human imagines",
        min_values=0,
        max_values=2,
        options=[
            SelectOption(
                label=f"{name.title()} A{index}",
                emoji=emoji,
                value=f"{name}_{index}",
            )
            for name, emojis in IMAGINE_EMOJIS.items()
            for index, emoji in enumerate(emojis)
        ],
        custom_id="join_group_view:select_imagine",
    )
    async def select_imagine(
        self,
        interaction: Interaction,
        select: ui.Select["JoinGroupView"],
    ) -> None:
        await interaction.response.defer()

        tina: int | None = None
        airona: int | None = None

        for value in select.values:
            name, index_str = value.rsplit("_", 1)
            index = int(index_str)
            if name == "tina":
                tina = index
            elif name == "airona":
                airona = index

        controller = GroupEmbedController.from_message(
            self.message.embeds[0],
            message_id=self.message.id,
        )
        controller.set_imagine(member=interaction.user, tina=tina, airona=airona)

        await self.message.edit(embed=controller.embed)
        self.message.embeds[0] = controller.embed

        await interaction.edit_original_response(
            content=self.get_response_message(controller, interaction.user),
        )

    @ui.button(
        label="Helping",
        style=ButtonStyle.success,
        custom_id="join_group_view:help_button",
        emoji=LukEmojis.lukchan_wow,
    )
    async def help_button(
        self,
        interaction: Interaction,
        _: ui.Button["JoinGroupView"],
    ) -> None:
        await interaction.response.defer()

        controller = GroupEmbedController.from_message(
            self.message.embeds[0],
            message_id=self.message.id,
        )
        controller.toggle_help(member=interaction.user)

        await self.message.edit(embed=controller.embed)
        self.message.embeds[0] = controller.embed

        await interaction.edit_original_response(
            content=self.get_response_message(controller, interaction.user),
        )
