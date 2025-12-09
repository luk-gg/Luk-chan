from datetime import datetime
from urllib.parse import quote, unquote

from cachetools import TTLCache
from discord import Embed, Member, PartialEmoji, User
from discord.utils import format_dt
from pydantic import BaseModel

from src._colors import LukColors
from src._emojis import LukEmojis

_INTERNAL_CACHE: TTLCache[int, "GroupEmbedController"] = TTLCache(
    maxsize=1024,
    ttl=60 * 60 * 3,
)


class _GroupUser(BaseModel):
    id: int
    role: str
    help: bool = False
    airona: int | None = None
    tina: int | None = None


class _GroupOwner(BaseModel):
    id: int
    name: str
    icon_url: str


class _GroupData(BaseModel):
    name: str
    time: datetime
    desc: str | None

    dps_limit: float
    healer_limit: float
    tank_limit: float

    dps_members: list[_GroupUser] = []
    healer_members: list[_GroupUser] = []
    tank_members: list[_GroupUser] = []

    owner: _GroupOwner


IMAGINE_EMOJIS = {
    "airona": [
        LukEmojis.airona,
        LukEmojis.airona_angry,
        LukEmojis.airona3,
        LukEmojis.airona_grin,
        LukEmojis.airona_laugh,
        LukEmojis.airona_wauw,
    ],
    "tina": [
        LukEmojis.tina,
        LukEmojis.tina_smile,
        LukEmojis.tina_wink,
        LukEmojis.tina_grin,
        LukEmojis.tina_laugh,
        LukEmojis.tina_wauw,
    ],
}


class GroupEmbedController:
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        time: datetime,
        desc: str | None,
        dps_limit: float,
        healer_limit: float,
        tank_limit: float,
        owner: Member | User | _GroupOwner,
    ) -> None:
        self.data: _GroupData = _GroupData(
            name=name,
            time=time,
            desc=desc,
            dps_limit=dps_limit,
            healer_limit=healer_limit,
            tank_limit=tank_limit,
            owner=_GroupOwner(
                id=owner.id,
                name=owner.name,
                icon_url=owner.display_avatar.url
                if isinstance(owner, (Member, User))
                else owner.icon_url,
            ),
        )
        self._embed: Embed | None = None

    @property
    def embed(self) -> Embed:
        if self._embed is None:
            self._embed = self._create_embed()

        return self._embed

    def _create_embed(self) -> Embed:
        embed = Embed(
            title=self.data.name,
            description=(
                f"**Time:** {format_dt(self.data.time, 'f')} "
                f"({format_dt(self.data.time, 'R')})\n\n"
            ),
            colour=LukColors.primary_blue,
        )

        if self.data.desc and embed.description:
            embed.description += self.data.desc

        dps_limit = (
            int(self.data.dps_limit) if self.data.dps_limit != float("inf") else None
        )
        embed.add_field(
            name=(
                f"{LukEmojis.dps} Damage ({len(self.data.dps_members)}"
                f"{f'/{dps_limit}' if dps_limit is not None else ''})"
            ),
            value=self.update_members(self.data.dps_members, limit=dps_limit),
            inline=False,
        )

        healer_limit = (
            int(self.data.healer_limit)
            if self.data.healer_limit != float("inf")
            else None
        )
        embed.add_field(
            name=(
                f"{LukEmojis.sup} Support ({len(self.data.healer_members)}"
                f"{f'/{healer_limit}' if healer_limit is not None else ''})"
            ),
            value=self.update_members(self.data.healer_members, limit=healer_limit),
            inline=False,
        )

        tank_limit = (
            int(self.data.tank_limit) if self.data.tank_limit != float("inf") else None
        )
        embed.add_field(
            name=(
                f"{LukEmojis.tank} Tank ({len(self.data.tank_members)}"
                f"{f'/{tank_limit}' if tank_limit is not None else ''})"
            ),
            value=self.update_members(self.data.tank_members, limit=tank_limit),
            inline=False,
        )

        embed.set_author(
            name=self.data.owner.name,
            icon_url=self.data.owner.icon_url,
            url=f"https://luk.gg/bpsr?data={quote(self.data.model_dump_json())}",
        )

        return embed

    def update_members(self, members: list[_GroupUser], limit: float | None) -> str:
        if not members:
            return "\u200b"

        members.sort(key=lambda m: m.help)

        return "\n".join(
            (
                f"{member.role} <@{member.id}> "
                f"{'' if (member.airona is None) else IMAGINE_EMOJIS['airona'][member.airona]} "  # noqa: E501
                f"{'' if (member.tina is None) else IMAGINE_EMOJIS['tina'][member.tina]} "  # noqa: E501
                f"{LukEmojis.lukchan_wow if member.help else ''} "
                f"{
                    (
                        LukEmojis.alert
                        if index >= (limit or float('inf')) and not member.help
                        else ''
                    )
                }"
            )
            for index, member in enumerate(members)
        )

    @classmethod
    def from_message(cls, embed: Embed, message_id: int) -> "GroupEmbedController":
        if message_id in _INTERNAL_CACHE:
            return _INTERNAL_CACHE[message_id]

        if not embed.author:
            raise ValueError("Embed does not have an author.")

        url_decoded = unquote(str(embed.author.url))

        _data = _GroupData.model_validate_json(
            url_decoded.split("data=")[1],
        )
        controller = cls(
            name=_data.name,
            time=_data.time,
            desc=_data.desc,
            dps_limit=_data.dps_limit,
            healer_limit=_data.healer_limit,
            tank_limit=_data.tank_limit,
            owner=_GroupOwner(
                id=_data.owner.id,
                name=_data.owner.name,
                icon_url=_data.owner.icon_url,
            ),
        )
        controller.data = _data

        _INTERNAL_CACHE[message_id] = controller

        return controller

    def add_member(self, member: Member | User, role: str, emoji: PartialEmoji) -> None:
        user_data = self.pop_member(member) or _GroupUser(
            id=member.id,
            role=str(emoji),
        )

        user_data.role = str(emoji)

        if role == "dps":
            self.data.dps_members.append(user_data)
        elif role == "healer":
            self.data.healer_members.append(user_data)
        elif role == "tank":
            self.data.tank_members.append(user_data)

        self._embed = None

    def pop_member(self, member: Member | User) -> _GroupUser | None:
        for user_list in [
            self.data.dps_members,
            self.data.healer_members,
            self.data.tank_members,
        ]:
            for index, user in enumerate(user_list):
                if user.id == member.id:
                    user_list.pop(index)
                    return user.model_copy(deep=True)
        return None

    def find_member(self, member: Member | User) -> _GroupUser | None:
        for user_list in [
            self.data.dps_members,
            self.data.healer_members,
            self.data.tank_members,
        ]:
            for user in user_list:
                if user.id == member.id:
                    return user
        return None

    def remove_member(self, member: Member | User) -> None:
        for user_list in [
            self.data.dps_members,
            self.data.healer_members,
            self.data.tank_members,
        ]:
            for index, user in enumerate(user_list):
                if user.id == member.id:
                    user_list.pop(index)
                    self._embed = None
                    return

    def toggle_help(self, member: Member | User) -> bool | None:
        for user in (
            self.data.dps_members + self.data.healer_members + self.data.tank_members
        ):
            if user.id == member.id:
                user.help = not user.help
                self._embed = None
                return user.help
        return None

    def set_imagine(
        self,
        member: Member | User,
        airona: int | None = None,
        tina: int | None = None,
    ) -> None:
        for users_list in [
            self.data.dps_members,
            self.data.healer_members,
            self.data.tank_members,
        ]:
            for user in users_list:
                if user.id == member.id:
                    user.airona = airona
                    user.tina = tina
                    self._embed = None
                    return
