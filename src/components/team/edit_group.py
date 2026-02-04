from dateutil.parser import parse
from discord import (
    Interaction,
    Message,
    TextStyle,
    ui,
)

from src._utils import TIMEZONES, datetime_now
from src.embeds.team.group_controller import GroupEmbedController


class EditGroupModal(ui.Modal):
    def __init__(self, controller: GroupEmbedController, message: Message) -> None:
        super().__init__(
            title="Edit a Team",
            timeout=300,
        )
        self.controller = controller
        self.message = message

        self.group_name = ui.TextInput["EditGroupModal"](
            label="Name or Objective",
            style=TextStyle.short,
            placeholder="Enter the name or objective of your group",
            max_length=50,
            default=controller.data.name,
        )

        self.description = ui.TextInput["EditGroupModal"](
            label="Description",
            style=TextStyle.paragraph,
            placeholder="Enter a brief description of your group",
            max_length=1000,
            required=False,
            default=controller.data.desc,
        )

        self.time = ui.TextInput["EditGroupModal"](
            label="Preferred Meeting Time (future only)",
            style=TextStyle.short,
            placeholder="e.g., '2024-12-31 20:00 BRT' or 'Dec 31 8pm EST'",
            default=controller.data.time.strftime("%Y-%m-%d %H:%M %Z"),
            required=True,
        )

        self.fields = ui.TextInput["EditGroupModal"](
            label="Fields and Limits",
            style=TextStyle.short,
            placeholder=("e.g., 'DPS:3 Sup:1 Tank:1' for 3 DPS, 1 Sup, 1 Tank"),
            required=False,
            default=self._limits_to_text_input(controller),
        )

        self.add_item(self.group_name)
        self.add_item(self.description)
        self.add_item(self.time)
        self.add_item(self.fields)

    def _limits_to_text_input(self, controller: GroupEmbedController) -> str:
        def _format_limit(value: float, role: str) -> str:
            if value == float("inf"):
                return role
            if value.is_integer():
                return f"{role}:{int(value)}"
            return f"{role}:{value}"

        return (
            f"{_format_limit(controller.data.dps_limit, 'DPS')} "
            f"{_format_limit(controller.data.healer_limit, 'Sup')} "
            f"{_format_limit(controller.data.tank_limit, 'Tank')}"
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
                elif role.lower() == "sup":
                    healers = count_int
                elif role.lower() == "tank":
                    tanks = count_int
        except ValueError:
            return dps, healers, tanks
        else:
            return dps, healers, tanks

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        group_name = self.group_name.value
        description = self.description.value
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

        self.controller.data.name = group_name
        self.controller.data.desc = description
        self.controller.data.dps_limit = dps_limit
        self.controller.data.healer_limit = healer_limit
        self.controller.data.tank_limit = tank_limit
        self.controller.data.time = time

        await self.message.edit(embed=self.controller.embed)
        await interaction.edit_original_response(content="Updated successfully.")
