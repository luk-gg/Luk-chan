from pydantic_settings import BaseSettings

__all__ = ("config",)


class _Settings(BaseSettings):
    TOKEN: str

    API_URL: str = "https://api.luk.gg"


config = _Settings()  # pyright: ignore[reportCallIssue]
