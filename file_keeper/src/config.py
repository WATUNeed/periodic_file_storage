from typing import List

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    broker_url: str
    factories: List[str]


config = Config()
