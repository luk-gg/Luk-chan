from typing import Any

from dateutil.parser import parse
from discord import Interaction, Member, TextStyle, ui

from src._utils import TIMEZONES, datetime_now
from src.embeds.bpsr.group_controller import GroupEmbedController


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
            embed=GroupEmbedController(
                name=group_name,
                limit=limit,
                time=time,
                desc=description,
                author=leader if isinstance(leader, Member) else None,
            ).embed,
            view=GroupView(),
        )


class GroupView(ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

        self.add_item(DpsButton())
        self.add_item(HealerButton())
        self.add_item(TankButton())
        self.add_item(WaitingButton())

    async def button_callback(
        self,
        interaction: Interaction[Any],
        button: "_BaseButton",
    ) -> None:
        if not interaction.message or not interaction.message.embeds:
            return

        await interaction.response.defer()

        embed_controller = await GroupEmbedController.from_message(
            interaction.message.embeds[0],
        )

        await embed_controller.button_clicked(button.custom_id, interaction.user)  # pyright: ignore[reportArgumentType]

        await interaction.edit_original_response(
            embeds=[
                embed_controller.embed,
            ],
        )


class _BaseButton(ui.Button["GroupView"]):
    def __init__(self, label: str, custom_id: str) -> None:
        super().__init__(label=label, custom_id=custom_id)

    async def callback(self, interaction: Interaction[Any]) -> None:
        if not self.view:
            return

        await self.view.button_callback(interaction, self)


class DpsButton(_BaseButton):
    def __init__(self) -> None:
        super().__init__(label="Join as DPS", custom_id="dps")


class HealerButton(_BaseButton):
    def __init__(self) -> None:
        super().__init__(label="Join as Healer", custom_id="healer")


class TankButton(_BaseButton):
    def __init__(self) -> None:
        super().__init__(label="Join as Tank", custom_id="tank")


class WaitingButton(_BaseButton):
    def __init__(self) -> None:
        super().__init__(label="Join Waiting List", custom_id="waiting")
