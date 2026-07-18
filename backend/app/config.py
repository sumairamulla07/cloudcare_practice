from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central app config, loaded from environment variables / .env.
    See .env.example for the full list of placeholders you need to fill in.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    # MongoDB — PLACEHOLDER until you create a real Atlas cluster
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "cloudcare"

    # Auth — PLACEHOLDER, replace with a real secret before shipping
    jwt_secret: str = "dev-only-insecure-secret-change-me"
    jwt_expire_minutes: int = 60

    # AWS — PLACEHOLDER, only needed once a real sandbox account is connected
    aws_region: str = "ap-south-1"
    aws_profile: str = "cloudcare-bootstrap"
    aws_read_role_arn: str = ""
    aws_external_id: str = ""

    # LLM — PLACEHOLDER, only needed once Decision/Supervisor call a real LLM
    openrouter_api_key: str = ""
    llm_model: str = "anthropic/claude-3.5-sonnet"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
