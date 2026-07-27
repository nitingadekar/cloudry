"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cloudry application settings.

    Values are loaded from environment variables, with .env file as fallback.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: str = "development"

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Cloudflare Turnstile
    turnstile_secret_key: str = ""
    turnstile_enabled: bool = False

    # Rate limiting
    rate_limit_per_minute: int = 20

    # File limits
    max_file_size_mb: int = 20

    # Logging
    log_level: str = "info"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB limit to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
