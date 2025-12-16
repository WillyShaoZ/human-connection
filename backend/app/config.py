from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:234377@localhost:5432/card_game"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
