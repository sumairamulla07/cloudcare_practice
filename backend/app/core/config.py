from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"

    aws_profile: str | None = "cloudcare-bootstrap"
    aws_region: str = "ap-south-1"
    aws_role_arn: str
    aws_external_id: str

    execution_enabled: bool = False
    execution_mode: str = "simulation"


@lru_cache
def get_settings() -> Settings:
    return Settings()
