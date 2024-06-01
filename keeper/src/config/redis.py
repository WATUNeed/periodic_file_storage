from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='REDIS_')

    host: str
    port: int
    driver: str
    user: str = 'default'
    password: str

    def get_connection_url(self, index: int = 0) -> str:
        return f'{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}//{index}'


REDIS_CONFIG = RedisConfig()
