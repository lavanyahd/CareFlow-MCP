from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIRECTORY / ".env"


class Settings(BaseSettings):
    app_name: str = "CareFlow-MCP"
    environment: str = "development"
    database_url: str = "sqlite:///./careflow.db"
    frontend_url: str = "http://localhost:5173"
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()