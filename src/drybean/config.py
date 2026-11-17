"""Environment-based application settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from DRYBEAN_-prefixed environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="DRYBEAN_",
        env_file=".env",
        extra="ignore",
    )

    env: Literal["local", "ci", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    model_path: Path = Path("models/champion.pkl")
    params_path: Path = Path("configs/params.yaml")
    mlflow_tracking_uri: str = "http://localhost:5000"
    s3_endpoint_url: str | None = None
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    api_key: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
