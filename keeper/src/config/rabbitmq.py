from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='RABBITMQ_')

    host: str
    port: int
    user: str
    password: str
    driver: str

    def connection_url(self, vhost: str = '') -> str:
        return f'{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{vhost}'


RABBITMQ_CONFIG = RabbitMQConfig()
