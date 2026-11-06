from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Find the main project folder
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Create one settings object for the application
settings = Settings()