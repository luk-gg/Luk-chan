from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("config",)


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TOKEN: str

    API_URL: str = "https://api.luk.gg"

    GUILD_ID: int = 862600196704829440
    BPSR_GROUP_CHANNEL_ID: int = 1447796900387491904


config = _Settings()  # pyright: ignore[reportCallIssue]
