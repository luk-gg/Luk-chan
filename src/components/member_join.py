from discord import ButtonStyle, Member, User, ui

from src._channels import LukChannels
from src._colors import LukColors
from src._emojis import LukEmojis


class MemberJoinView(ui.LayoutView):
    def __init__(self, user: Member | User) -> None:
        super().__init__()

        header = ui.TextDisplay["MemberJoinView"](
            content=f"### Welcome {user.name}!",
        )

        text = ui.TextDisplay["MemberJoinView"](
            content=(
                "We're a growing community of theorycrafters, guide makers, "
                "and video game enthusiasts! We welcome players of all skill levels "
                "and play styles. Guides and resources can be found throughout this "
                "server and on the website."
            ),
        )

        user_icon = ui.Thumbnail["MemberJoinView"](media=user.display_avatar.url)

        action_row = ui.ActionRow(
            ui.Button["MemberJoinView"](
                label="LUK.GG",
                emoji=LukEmojis.luk_logo_rounded,
                style=ButtonStyle.link,
                url="https://luk.gg",
            ),
            ui.Button["MemberJoinView"](
                label="Info & Rules",
                emoji=LukEmojis.lukchan_noted,
                style=ButtonStyle.link,
                url=LukChannels.rules.url,
            ),
        )

        self.add_item(
            ui.Container(
                ui.Section(header, text, accessory=user_icon),
                action_row,
                accent_color=LukColors.primary_blue,
            ),
        )
