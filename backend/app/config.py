from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Find the main project folder
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    APP_NAME: str = "LedgerLine API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"

    JWT_SECRET_KEY: str = "ledgerline-secret-key-replace-in-production"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Create one settings object for the application
settings = Settings()
