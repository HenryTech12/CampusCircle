from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://campuscircle:campuscircle@localhost:5432/campuscircle"
    app_env: str = "development"
    frontend_origin: str = "http://localhost:5173"
    session_secret: str
    brevo_api_key: str | None = None
    brevo_sender_email: str | None = None
    brevo_sender_name: str = "CampusCircle"
    groq_api_key: str | None = None
    groq_model: str | None = None
    bmoni_api_key: str | None = None
    bmoni_base_url: str | None = None
    otp_expiry_seconds: int = 600
    otp_max_attempts: int = 5
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
