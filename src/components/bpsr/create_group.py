from datetime import datetime
from typing import Any, TypedDict

from dateutil.parser import parse
from discord import Interaction, Member, TextStyle, User, ui
from discord.utils import format_dt

from src._utils import TIMEZONES, datetime_now


class TextMapping(TypedDict):
    text: ui.TextDisplay["GroupLayoutView"]
    limit: int | None


class CreateGroupModal(ui.Modal):
    def __init__(self) -> None:
        super().__init__(
            title="Create BPSR Group",
            timeout=300,
        )

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
            max_length=200,
            required=False,
        )

        self.time = ui.TextInput["CreateGroupModal"](
            label="Preferred Meeting Time (future only)",
            style=TextStyle.short,
            placeholder="e.g., '2024-12-31 20:00 BRT' or 'Dec 31 8pm EST'",
            required=True,
        )

        self.limit = ui.TextInput["CreateGroupModal"](
            label="Member Limit",
            style=TextStyle.short,
            placeholder="e.g., '3 1 1' for 3 DPS, 1 Healer, 1 Tank",
            required=False,
            default="3 1 1",
        )

        self.add_item(self.group_name)
        self.add_item(self.description)
        self.add_item(self.time)
        self.add_item(self.limit)

    def parse_limit(self) -> tuple[int, int, int]:
        if not self.limit.value:
            return 3, 1, 1  # Default values

        try:
            dps, healers, tanks = map(int, self.limit.value.split())
        except ValueError:
            return 3, 1, 1  # Fallback to default on error
        else:
            return dps, healers, tanks

    async def on_submit(self, interaction: Interaction) -> None:
        group_name = self.group_name.value
        description = self.description.value
        leader = interaction.user
        limit = self.parse_limit()
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

        await interaction.response.send_message(
            view=GroupLayoutView(
                group_name=group_name,
                group_time=time,
                group_leader=leader,
                group_limit=limit,
                group_description=description,
            ),
        )


class GroupLayoutView(ui.LayoutView):
    def __init__(
        self,
        group_name: str,
        group_time: datetime,
        group_leader: User | Member,
        group_limit: tuple[int, int, int],
        group_description: str | None = None,
    ) -> None:
        super().__init__(timeout=None)
        self.group_name = group_name
        self.group_time = group_time
        self.group_description = group_description
        self.group_leader = group_leader
        self.limit_dps, self.limit_healers, self.limit_tanks = group_limit

        header_name = ui.TextDisplay["GroupLayoutView"](f"## {self.group_name}")
        header_time = ui.TextDisplay["GroupLayoutView"](
            f"**Time:** {format_dt(self.group_time, style='R')}",
        )
        header_leader = ui.TextDisplay["GroupLayoutView"](
            f"**Leader:** {self.group_leader.mention}",
        )
        header_description = ui.TextDisplay["GroupLayoutView"](
            self.group_description or "",
        )

        self.header_section = ui.Container["GroupLayoutView"](
            header_name,
            header_time,
            header_leader,
        )
        if self.group_description:
            self.header_section.add_item(header_description)

        self.dps_text = ui.TextDisplay["GroupLayoutView"](
            f"**DPS** (0/{self.limit_dps})",
        )
        self.healer_text = ui.TextDisplay["GroupLayoutView"](
            f"**Healers** (0/{self.limit_healers})",
        )
        self.tank_text = ui.TextDisplay["GroupLayoutView"](
            f"**Tanks** (0/{self.limit_tanks})",
        )
        self.waiting_text = ui.TextDisplay["GroupLayoutView"]("**Waiting List** (0)")

        self.dps_container = ui.Container["GroupLayoutView"](self.dps_text)
        self.healer_container = ui.Container["GroupLayoutView"](self.healer_text)
        self.tank_container = ui.Container["GroupLayoutView"](self.tank_text)
        self.waiting_container = ui.Container["GroupLayoutView"](self.waiting_text)

        self.add_item(self.header_section)
        self.add_item(self.dps_container)
        self.add_item(self.healer_container)
        self.add_item(self.tank_container)
        self.add_item(self.waiting_container)

        self.add_item(
            ui.ActionRow["GroupLayoutView"](
                DpsButton(),
                HealerButton(),
                TankButton(),
                WaitingButton(),
            ),
        )

        self._mapping: dict[str, TextMapping] = {
            "dps": {"text": self.dps_text, "limit": self.limit_dps},
            "healer": {"text": self.healer_text, "limit": self.limit_healers},
            "tank": {"text": self.tank_text, "limit": self.limit_tanks},
            "waiting": {"text": self.waiting_text, "limit": None},
        }

    async def button_callback(
        self,
        interaction: Interaction[Any],
        button: ui.Button["GroupLayoutView"],
    ) -> None:
        if button.custom_id not in self._mapping:
            return

        await interaction.response.defer()

        group_limit = self._mapping[button.custom_id]["limit"]
        text_display = self._mapping[button.custom_id]["text"]

        header, users = self.get_section(button.custom_id)

        if (
            group_limit is not None
            and len(users) >= group_limit
            and interaction.user.mention not in users
        ):
            await interaction.followup.send(
                content=(
                    f"The {button.custom_id.title()} section is full. "
                    "Please choose another role or join the waiting list."
                ),
                ephemeral=True,
            )
            return

        if interaction.user.mention not in users:
            users.append(interaction.user.mention)

        else:
            users.remove(interaction.user.mention)

        text_display.content = (
            f"{header} ({len(users)}"
            f"{f'/{group_limit}' if group_limit is not None else ''})\n"
        ) + "\n".join(
            users,
        )

        await interaction.edit_original_response(view=self)

    def get_section(self, section: str) -> tuple[str, list[str]]:
        if section not in self._mapping:
            return "", []

        text_display = self._mapping[section]["text"]
        text_lines = text_display.content.splitlines()

        return text_lines[0].rsplit(" ", 1)[0], [
            user.strip() for user in text_lines[1:] if user.strip()
        ]


class DpsButton(ui.Button["GroupLayoutView"]):
    def __init__(self) -> None:
        super().__init__(label="Join as DPS", custom_id="dps")

    async def callback(self, interaction: Interaction[Any]) -> None:
        if not self.view:
            return

        await self.view.button_callback(interaction, self)


class HealerButton(ui.Button["GroupLayoutView"]):
    def __init__(self) -> None:
        super().__init__(label="Join as Healer", custom_id="healer")

    async def callback(self, interaction: Interaction[Any]) -> None:
        if not self.view:
            return

        await self.view.button_callback(interaction, self)


class TankButton(ui.Button["GroupLayoutView"]):
    def __init__(self) -> None:
        super().__init__(label="Join as Tank", custom_id="tank")

    async def callback(self, interaction: Interaction[Any]) -> None:
        if not self.view:
            return

        await self.view.button_callback(interaction, self)


class WaitingButton(ui.Button["GroupLayoutView"]):
    def __init__(self) -> None:
        super().__init__(label="Join Waiting List", custom_id="waiting")

    async def callback(self, interaction: Interaction[Any]) -> None:
        if not self.view:
            return

        await self.view.button_callback(interaction, self)
