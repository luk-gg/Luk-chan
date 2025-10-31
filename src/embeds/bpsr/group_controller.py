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
        limit: tuple[int, int, int],
        time: datetime,
        desc: str | None = None,
        author: Member | None = None,
    ) -> None:
        self.name = name
        self.time = time
        self.desc = desc
        self.author = author
        self.dps_limit, self.healer_limit, self.tank_limit = limit

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

        embed.add_field(
            name=f"DPS ({len(self.dps_members)}/{self.dps_limit})",
            value="\u200b",
        )
        embed.add_field(
            name=f"Healer ({len(self.healer_members)}/{self.healer_limit})",
            value="\u200b",
        )
        embed.add_field(
            name=f"Tank ({len(self.tank_members)}/{self.tank_limit})",
            value="\u200b",
        )

        embed.add_field(name="Waiting", value="\u200b", inline=False)

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

        dps_limit = int(dps_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]
        healer_limit = int(healer_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]
        tank_limit = int(tank_field.name.rsplit("/", 1)[1].rstrip(")"))  # pyright: ignore[reportOptionalMemberAccess]

        controller = GroupEmbedController(
            name=title,
            limit=(dps_limit, healer_limit, tank_limit),
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

        params: list[tuple[list[str], float, str]] = [
            (self.dps_members, self.dps_limit, "dps"),
            (self.healer_members, self.healer_limit, "healer"),
            (self.tank_members, self.tank_limit, "tank"),
            (self.waiting_members, float("inf"), "waiting"),
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
            if btn_id == button_id and len(lst) < limit and mention not in lst:
                lst.append(mention)
                self.update_embed()
                return

    def update_embed(self) -> None:
        self.embed.set_field_at(
            0,
            name=f"DPS ({len(self.dps_members)}/{self.dps_limit})",
            value="\n".join(self.dps_members) if self.dps_members else "\u200b",
        )
        self.embed.set_field_at(
            1,
            name=f"Healer ({len(self.healer_members)}/{self.healer_limit})",
            value="\n".join(self.healer_members) if self.healer_members else "\u200b",
        )
        self.embed.set_field_at(
            2,
            name=f"Tank ({len(self.tank_members)}/{self.tank_limit})",
            value="\n".join(self.tank_members) if self.tank_members else "\u200b",
        )
        self.embed.set_field_at(
            3,
            name="Waiting",
            value="\n".join(self.waiting_members) if self.waiting_members else "\u200b",
        )
