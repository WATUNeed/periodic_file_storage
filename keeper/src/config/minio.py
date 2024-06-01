from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='MINIO_')

    host: str
    port: int

    access_key: str
    secret_key: str

    def endpoint(self) -> str:
        return f'{self.host}:{self.port}'


MINIO_CONFIG = MinioConfig()
