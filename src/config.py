from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from src.constants import Environment


class Settings(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: Environment = Environment.LOCAL
    authjwt_secret_key: str = "foo"


settings = Settings()
