from pydantic_settings import BaseSettings


class KeeperConfig(BaseSettings):
    period_sec: float = 60.0
    retry_countdown: int = 60 * 5


KEEPER_CONFIG = KeeperConfig()
