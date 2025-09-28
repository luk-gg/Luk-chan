from pydantic_settings import BaseSettings

__all__ = ("config",)


class _Settings(BaseSettings):
    TOKEN: str

    API_URL: str = "https://api.luk.gg"

    GUILD_ID: int = 862600196704829440


config = _Settings()  # pyright: ignore[reportCallIssue]
