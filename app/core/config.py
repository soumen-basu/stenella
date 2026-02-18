from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Stenella"
    DATABASE_URL: str = "postgresql+psycopg://spinner:longirostris@localhost:5432/stenella"
    SECRET_KEY: str = "changethis" # TODO: Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # For the JWT lifespan itself (short)
    SESSION_EXPIRE_DAYS: int = 7 # For the session record

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings():
    return Settings()
