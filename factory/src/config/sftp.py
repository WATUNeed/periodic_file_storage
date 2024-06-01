from pydantic_settings import BaseSettings, SettingsConfigDict


class SFTPConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='SFTP_')

    host: str
    port: int
    user: str
    password: str
    rsa_key_path: str


SFTP_CONFIG = SFTPConfig()
