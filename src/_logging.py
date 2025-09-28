import logging

from discord.utils import (
    _ColourFormatter,  # pyright: ignore[reportPrivateUsage]
    stream_supports_colour,
)


def setup_logging() -> None:
    """Setup logging."""

    handler = logging.StreamHandler()

    if stream_supports_colour(handler.stream):
        formatter = _ColourFormatter()
    else:
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )

    handler.setFormatter(formatter)
    logger = logging.getLogger("luk")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.debug("Logging setup complete")
