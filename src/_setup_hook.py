from logging import getLogger

from discord.ext import commands

from src.cogs import EXTENSIONS


async def load_cogs(bot: commands.Bot) -> None:
    _logger = getLogger("luk.extensions")

    for extension in EXTENSIONS:
        _logger.debug("Loading extension %s", extension)

        try:
            await bot.load_extension(extension)
        except commands.NoEntryPointError:
            _logger.warning(
                "Extension %s has no setup function",
                extension,
            )
            continue

        _logger.info("Loaded extension %s", extension.split(".", 2)[-1])
