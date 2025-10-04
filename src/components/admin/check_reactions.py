import asyncio
from typing import TypedDict

import discord
from discord import (
    ButtonStyle,
    Client,
    Emoji,
    Interaction,
    Member,
    Message,
    PartialEmoji,
    Role,
    SelectOption,
    ui,
)


class CheckReactionsView(ui.LayoutView):
    def __init__(self, message: Message) -> None:
        super().__init__(timeout=None)
        self.message = message
        self.role: Role | None = None
        self.emoji: Emoji | PartialEmoji | str | None = None

        self.add_item(SelectRoleContainer())
        self.add_item(SelectEmojiContainer(message))

    async def edit_self(self) -> None:
        if self.emoji and self.role:
            reacted = [
                member
                for reaction in self.message.reactions
                async for member in reaction.users()
                if isinstance(member, Member)
                and reaction.emoji == self.emoji
                and self.role in member.roles
            ]
            not_reacted = [
                member for member in self.role.members if member not in reacted
            ]
            self.add_item(
                OutputContainer(
                    role=self.role,
                    emoji=self.emoji,
                    reacted=reacted,
                    not_reacted=not_reacted,
                ),
            )


class SelectRoleContainer(ui.Container["CheckReactionsView"]):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(ui.TextDisplay("Select a role from the dropdown below:"))
        self.add_item(ui.ActionRow(RoleSelect()))


class RoleSelect(ui.RoleSelect["CheckReactionsView"]):
    def __init__(self) -> None:
        super().__init__(placeholder="Select a role", min_values=1, max_values=1)

    async def callback(self, interaction: Interaction[Client]) -> None:
        await interaction.response.defer()

        if not self.values:
            await interaction.response.send_message("No role selected.", ephemeral=True)
            return

        if not self.view:
            await interaction.response.send_message("View not found.", ephemeral=True)
            return

        self.view.role = self.values[0]
        await self.view.edit_self()

        await interaction.edit_original_response(view=self.view)


class SelectEmojiContainer(ui.Container["CheckReactionsView"]):
    def __init__(self, message: Message) -> None:
        super().__init__()
        self.add_item(ui.TextDisplay("Select an emoji from the dropdown below:"))
        self.add_item(ui.ActionRow(EmojiSelect(message)))


class EmojiSelect(ui.Select["CheckReactionsView"]):
    def __init__(self, message: Message) -> None:
        super().__init__(placeholder="Select an emoji", min_values=1, max_values=1)

        self.options = [
            SelectOption(
                label=f":{reaction.emoji.name}:"
                if isinstance(reaction.emoji, (PartialEmoji, Emoji))
                else reaction.emoji,
                value=str(reaction.emoji),
            )
            for reaction in message.reactions
        ][:25]

    async def callback(self, interaction: Interaction[Client]) -> None:
        await interaction.response.defer()

        if not self.values:
            await interaction.followup.send(
                "No emoji selected.",
                ephemeral=True,
            )
            return

        if not self.view:
            await interaction.followup.send("View not found.", ephemeral=True)
            return

        self.view.emoji = next(
            (
                reaction.emoji
                for reaction in self.view.message.reactions
                if str(reaction.emoji) == self.values[0]
                and not isinstance(reaction.emoji, str)
            ),
            None,
        )

        await self.view.edit_self()
        await interaction.edit_original_response(view=self.view)


class OutputContainer(ui.Container["CheckReactionsView"]):
    def __init__(
        self,
        role: Role,
        emoji: Emoji | PartialEmoji | str,
        reacted: list[Member],
        not_reacted: list[Member],
    ) -> None:
        super().__init__()
        self.reacted = reacted
        self.not_reacted = not_reacted
        separator = ui.Separator["CheckReactionsView"]()

        text = ui.TextDisplay["CheckReactionsView"](
            content=(
                f"{len(reacted)} member(s) with the role {role.mention} "
                f"reacted with {emoji}: \n"
                f"{', '.join(member.mention for member in reacted)}"
            ),
        )

        text_2 = ui.TextDisplay["CheckReactionsView"](
            content=(
                f"{len(not_reacted)} member(s) with the role {role.mention} "
                f"didn't react with {emoji}: \n"
                f"{', '.join(member.mention for member in not_reacted)}"
            ),
        )

        self.add_item(text)
        self.add_item(separator)
        self.add_item(text_2)
        self.add_item(ui.ActionRow(SendNotifyToWhoDidnt(not_reacted)))


class SendNotifyToWhoDidnt(ui.Button["CheckReactionsView"]):
    def __init__(self, members: list[Member]) -> None:
        super().__init__(
            label="Notify who didn't react",
            style=ButtonStyle.danger,
        )
        self.members = members

    async def callback(self, interaction: Interaction[Client]) -> None:
        await interaction.response.defer()

        if not self.view or not self.view.role or not self.view.emoji:
            await interaction.followup.send("View not found.", ephemeral=True)
            return

        class _TypedFailed(TypedDict):
            member: Member
            error: str

        failed: list[_TypedFailed] = []

        for member in self.members:
            try:
                await member.send(
                    view=_NotificationMessageView(self.view.message.jump_url, member),
                )
                if (self.members.index(member) + 1) % 5 == 0:
                    await asyncio.sleep(1)
            except discord.HTTPException as e:
                failed.append({"member": member, "error": e.text})

        await interaction.followup.send(
            content=(
                f"Notified {len(self.members) - len(failed)} member(s). \n"
                f"Failed to notify {len(failed)} member(s): \n"
                f"{'\n'.join(f'{f["member"].mention}: {f["error"]}' for f in failed)}"
            ),
            ephemeral=True,
        )


class _NotificationMessageView(ui.LayoutView):
    def __init__(self, message_url: str, member: Member) -> None:
        super().__init__()
        message = ui.TextDisplay["_NotificationMessageView"](
            content=(
                f"**Hey {member.name}! This is a reminder to check out "
                f"[__this message__]({message_url}) in LUK.GG!**"
            ),
        )

        container = ui.Container["_NotificationMessageView"](message)

        self.add_item(container)
