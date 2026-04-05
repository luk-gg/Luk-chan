from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("config",)


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    TOKEN: str

    API_URL: str = "https://api.luk.gg"

    GUILD_ID: int = 862600196704829440
    BPSR_GROUP_CHANNEL_ID: int = 1447796900387491904

    MONGO_URI: str
    MONGO_DB_NAME: str = "luk-chan"

    MIN_MESSAGE_LENGTH: int = 5


config = _Settings()  # pyright: ignore[reportCallIssue]
