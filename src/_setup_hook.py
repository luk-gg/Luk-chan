from logging import getLogger
from pathlib import Path

from discord.ext import commands


async def load_cogs(bot: commands.Bot) -> None:
    _logger = getLogger("luk.extensions")

    async def path_loader(path: str = "./src/cogs") -> None:
        for file in Path(path).iterdir():
            if "__pycache__" in file.parts:
                continue

            if file.is_dir():
                _logger.debug("Loading extensions from %s", file)

                await path_loader(str(file))
                continue

            if file.is_file() and (file.suffix != ".py" or file.name == "__init__.py"):
                _logger.debug("Skipping non-Python file %s", file)
                continue

            cog_path = ".".join(file.parts).removesuffix(".py")
            cog_short_path = ".".join(cog_path.split(".")[2:])

            _logger.debug("Loading extension %s", cog_path)

            try:
                await bot.load_extension(cog_path)
            except commands.NoEntryPointError:
                _logger.warning(
                    "Extension %s has no setup function",
                    cog_short_path,
                )
                continue

            _logger.info("Loaded extension %s", cog_short_path)

    await path_loader()
