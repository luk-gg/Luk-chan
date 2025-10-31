from datetime import datetime
from zoneinfo import ZoneInfo

import regex
from discord import Embed, Member, User
from discord.utils import format_dt

from src._colors import LukColors


class GroupEmbedController:
    def __init__(
        self,
        name: str,
        limit: tuple[float, float, float, float],
        time: datetime,
        desc: str | None = None,
        author: Member | None = None,
    ) -> None:
        self.name = name
        self.time = time
        self.desc = desc
        self.author = author
        self.dps_limit, self.healer_limit, self.tank_limit, self.waitlist_limit = limit

        self.dps_members: list[str] = []
        self.healer_members: list[str] = []
        self.tank_members: list[str] = []
        self.waiting_members: list[str] = []

        self._embed: Embed | None = None

    def _create_embed(self) -> Embed:
        embed = Embed(
            title=self.name,
            description=(
                f"**Time:** {format_dt(self.time, 'f')} ({format_dt(self.time, 'R')})\n"
            ),
            colour=LukColors.primary_blue,
        )

        if self.desc and embed.description:
            embed.description += self.desc

        if self.author:
            embed.set_author(
                name=self.author.name,
                icon_url=self.author.display_avatar.url,
            )

        dps_limit = int(self.dps_limit) if self.dps_limit != float("inf") else None
        embed.add_field(
            name=(
                f"DPS ({len(self.dps_members)}"
                f"{f'/{dps_limit}' if dps_limit is not None else ''})"
            ),
            value="\u200b",
        )

        healer_limit = (
            int(self.healer_limit) if self.healer_limit != float("inf") else None
        )
        embed.add_field(
            name=(
                f"Healer ({len(self.healer_members)}"
                f"{f'/{healer_limit}' if healer_limit is not None else ''})"
            ),
            value="\u200b",
        )

        tank_limit = int(self.tank_limit) if self.tank_limit != float("inf") else None
        embed.add_field(
            name=(
                f"Tank ({len(self.tank_members)}"
                f"{f'/{tank_limit}' if tank_limit is not None else ''})"
            ),
            value="\u200b",
        )

        waitlist_limit = (
            int(self.waitlist_limit) if self.waitlist_limit != float("inf") else None
        )
        embed.add_field(
            name=(
                f"Waiting ({len(self.waiting_members)}"
                f"{f'/{waitlist_limit}' if waitlist_limit is not None else ''})"
            ),
            value="\u200b",
            inline=False,
        )

        return embed

    @property
    def embed(self) -> Embed:
        if self._embed is None:
            self._embed = self._create_embed()

        return self._embed

    @staticmethod
    async def from_message(embed: Embed) -> "GroupEmbedController":
        title = embed.title or "Unnamed Group"
        description_lines = embed.description.split("\n") if embed.description else []
        time_line = description_lines[0] if description_lines else ""
        desc = "\n".join(description_lines[1:]) if len(description_lines) > 1 else None

        time_str = regex.search(r"<t:(\d+):R>", time_line)
        if not time_str:
            raise ValueError("Could not find time in embed description.")

        time = datetime.fromtimestamp(int(time_str.group(1)), tz=ZoneInfo("UTC"))

        dps_field = embed.fields[0]
        healer_field = embed.fields[1]
        tank_field = embed.fields[2]
        waiting_field = embed.fields[3]

        dps_limit = float("inf")
        healer_limit = float("inf")
        tank_limit = float("inf")
        waitlist_limit = float("inf")

        if "/" in dps_field.name:  # pyright: ignore[reportOperatorIssue]
            dps_limit = float(dps_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]

        if "/" in healer_field.name:  # pyright: ignore[reportOperatorIssue]
            healer_limit = float(healer_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]

        if "/" in tank_field.name:  # pyright: ignore[reportOperatorIssue]
            tank_limit = float(tank_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]

        if "/" in waiting_field.name:  # pyright: ignore[reportOperatorIssue]
            waitlist_limit = float(
                str(waiting_field.name).rsplit("/", 1)[1].rstrip(")"),
            )

        controller = GroupEmbedController(
            name=title,
            limit=(dps_limit, healer_limit, tank_limit, waitlist_limit),
            time=time,
            desc=desc,
        )

        controller._create_embed()

        controller.dps_members = [
            mention
            for mention in dps_field.value.splitlines()  # pyright: ignore[reportOptionalMemberAccess]
            if mention.strip() and mention != "\u200b"
        ]

        controller.healer_members = [
            mention
            for mention in healer_field.value.splitlines()  # pyright: ignore[reportOptionalMemberAccess]
            if mention.strip() and mention != "\u200b"
        ]

        controller.tank_members = [
            mention
            for mention in tank_field.value.splitlines()  # pyright: ignore[reportOptionalMemberAccess]
            if mention.strip() and mention != "\u200b"
        ]

        controller.waiting_members = [
            mention
            for mention in waiting_field.value.splitlines()  # pyright: ignore[reportOptionalMemberAccess]
            if mention.strip() and mention != "\u200b"
        ]

        return controller

    async def button_clicked(self, button_id: str, member: Member | User) -> None:
        mention = member.mention

        params: list[tuple[list[str], float | None, str]] = [
            (self.dps_members, self.dps_limit, "dps"),
            (self.healer_members, self.healer_limit, "healer"),
            (self.tank_members, self.tank_limit, "tank"),
            (self.waiting_members, self.waitlist_limit, "waiting"),
        ]

        for lst, _, btn_id in params:
            if mention in lst and btn_id == button_id:
                lst.remove(mention)
                self.update_embed()
                return

            if mention in lst and btn_id != button_id:
                self.update_embed()
                return

        for lst, limit, btn_id in params:
            if btn_id == button_id and mention not in lst:
                if limit is not None and len(lst) >= limit:
                    return
                lst.append(mention)
                self.update_embed()
                return

    def update_embed(self) -> None:
        dps_limit = int(self.dps_limit) if self.dps_limit != float("inf") else None
        self.embed.set_field_at(
            0,
            name=(
                f"DPS ({len(self.dps_members)}"
                f"{f'/{dps_limit}' if dps_limit is not None else ''})"
            ),
            value="\n".join(self.dps_members) if self.dps_members else "\u200b",
        )

        healer_limit = (
            int(self.healer_limit) if self.healer_limit != float("inf") else None
        )
        self.embed.set_field_at(
            1,
            name=(
                f"Healer ({len(self.healer_members)}"
                f"{f'/{healer_limit}' if healer_limit is not None else ''})"
            ),
            value="\n".join(self.healer_members) if self.healer_members else "\u200b",
        )

        tank_limit = int(self.tank_limit) if self.tank_limit != float("inf") else None
        self.embed.set_field_at(
            2,
            name=(
                f"Tank ({len(self.tank_members)}"
                f"{f'/{tank_limit}' if tank_limit is not None else ''})"
            ),
            value="\n".join(self.tank_members) if self.tank_members else "\u200b",
        )

        waitlist_limit = (
            int(self.waitlist_limit) if self.waitlist_limit != float("inf") else None
        )
        self.embed.set_field_at(
            3,
            name=(
                f"Waiting ({len(self.waiting_members)}"
                f"{f'/{waitlist_limit}' if waitlist_limit is not None else ''})"
            ),
            value="\n".join(self.waiting_members) if self.waiting_members else "\u200b",
        )
