from src._settings import config


class _LukChannel:
    def __init__(self, id_: int) -> None:
        self.id = id_
        self.url = f"https://discord.com/channels/{config.GUILD_ID}/{id_}"

    @staticmethod
    def from_url(url: str) -> "_LukChannel":
        channel_id = int(url.split("/")[-1])
        return _LukChannel(channel_id)


class LukChannels:
    rules = _LukChannel(862607056132112394)
    welcome = _LukChannel(862600196704829443)
