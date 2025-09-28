from discord import ButtonStyle, SeparatorSpacing, ui

from src._colors import LukColors
from src._emojis import LukEmojis


class WelcomeLayoutView(ui.LayoutView):
    def __init__(self) -> None:
        super().__init__()

        self.add_item(_Container())


class _Container(ui.Container["WelcomeLayoutView"]):
    def __init__(self) -> None:
        welcome = ui.TextDisplay["WelcomeLayoutView"](content="### Welcome to LUK.GG!")
        theory = ui.TextDisplay["WelcomeLayoutView"](
            content=(
                "We're a growing community of theorycrafters, guide makers, "
                "and video game enthusiasts! We welcome players of all skill levels "
                "and play styles. Guides and resources can be found throughout this "
                "server and on the website."
            ),
        )

        website_button = ui.Button["WelcomeLayoutView"](
            label="LUK.GG",
            emoji=LukEmojis.luk_logo_rounded,
            style=ButtonStyle.url,
            url="https://luk.gg",
        )

        action_row = ui.ActionRow["WelcomeLayoutView"](website_button)

        separator = ui.Separator["WelcomeLayoutView"](spacing=SeparatorSpacing.large)

        section_1: list[ui.Item[WelcomeLayoutView]] = [
            welcome,
            theory,
            action_row,
        ]

        rules = ui.TextDisplay["WelcomeLayoutView"](content="### Rules")
        rules_list = ui.TextDisplay["WelcomeLayoutView"](
            content="```1️⃣ Don't be overly weird or an asshole.```",
        )

        section_2: list[ui.Item[WelcomeLayoutView]] = [
            rules,
            rules_list,
        ]

        customization = ui.TextDisplay["WelcomeLayoutView"](
            content="### Customization & Bot Commands",
        )
        customization_list = ui.TextDisplay["WelcomeLayoutView"](
            content=(
                "Visit <id:customize> to assign yourself roles and add channels for "
                "your favorite games. You can view my commands by typing `/` in the "
                "chat and clicking on my icon!"
            ),
        )

        section_3: list[ui.Item[WelcomeLayoutView]] = [
            customization,
            customization_list,
        ]

        roles = ui.TextDisplay["WelcomeLayoutView"](content="### Roles")
        roles_list = ui.TextDisplay["WelcomeLayoutView"](
            content=(
                f"Members of our guild, {LukEmojis.bapharia_emblem} **Bapharia**, will "
                f"be granted the {LukEmojis.initiate}, {LukEmojis.ascendant}, and "
                f"{LukEmojis.vip} roles based on their lifetime activity. Non-members "
                f"can participate in guild channels with the {LukEmojis.guest} role."
                f"\n\n{LukEmojis.staff}, {LukEmojis.legend}, and {LukEmojis.null} are "
                "reserved for moderators, server boosters, and bots!"
            ),
        )
        section_4: list[ui.Item[WelcomeLayoutView]] = [
            roles,
            roles_list,
        ]

        super().__init__(
            *section_1,
            separator,
            *section_2,
            separator,
            *section_3,
            separator,
            *section_4,
            accent_color=LukColors.primary_blue,
        )
