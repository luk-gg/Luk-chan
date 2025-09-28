from discord import Member, User, ui

from src._colors import LukColors


class MemberNitroView(ui.LayoutView):
    def __init__(self, user: Member | User) -> None:
        super().__init__()

        header = ui.TextDisplay["MemberNitroView"](
            content="### Thank you for boosting LUK.GG!",
        )
        text = ui.TextDisplay["MemberNitroView"](
            content=(
                "We appreciate your support! As a booster, you help us maintain and "
                "grow our community. Enjoy your exclusive perks and features!"
            ),
        )

        user_icon = ui.Thumbnail["MemberNitroView"](media=user.display_avatar.url)

        self.add_item(
            ui.Container(
                ui.Section(header, text, accessory=user_icon),
                accent_color=LukColors.primary_blue,
            ),
        )
