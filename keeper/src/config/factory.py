from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FactoryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='factory_')

    hosts: str

    @computed_field()
    def names(self) -> List[str]:
        return [i for i in self.hosts.split(',') if i != '']


FACTORY_CONFIG = FactoryConfig()
