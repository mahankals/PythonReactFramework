from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://cloudpe:cloudpe@localhost:5432/cloudpe"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours

    # Email/SMTP Settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@example.com"
    smtp_from_name: str = "SampleApp"
    smtp_use_tls: bool = True

    # App Settings
    app_name: str = "SampleApp"
    app_url: str = "http://localhost:3000"
    environment: str = "development"  # development, staging, production
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Logging
    log_level: str = "INFO"
    json_logs: bool = False

    # Superadmin (created on first startup)
    superadmin_email: str = "admin@example.com"
    superadmin_password: str = "Admin@123"
    superadmin_first_name: str = "Super"
    superadmin_last_name: str = "Admin"

    # Password Reset
    password_reset_expire_minutes: int = 30
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
