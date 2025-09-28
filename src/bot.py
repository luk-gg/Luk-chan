from logging import getLogger

from discord import Intents
from discord.ext import commands

from src._logging import setup_logging
from src._settings import config
from src._setup_hook import load_cogs

_INTENTS = Intents.default()
_INTENTS.members = True
_INTENTS.message_content = True


class LukChan(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=_INTENTS, help_command=None)

    async def on_ready(self) -> None:
        logger = getLogger("luk.client")
        logger.info("Logged in as %s | %sms", self.user, round(self.latency * 1000, 1))

    async def setup_hook(self) -> None:
        setup_logging()

        await load_cogs(self)

    def init(self) -> None:
        self.run(token=config.TOKEN)
