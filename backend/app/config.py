from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache
from typing import Literal


# Supported database dialects (SQLAlchemy)
DatabaseDialect = Literal["postgresql", "mysql", "mariadb", "sqlite"]

# Default ports for each database
DEFAULT_PORTS: dict[str, int] = {
    "postgresql": 5432,
    "mysql": 3306,
    "mariadb": 3306,
    "sqlite": 0,  # SQLite doesn't use ports
}

# SQLAlchemy async dialect prefixes
# PostgreSQL: asyncpg, MySQL/MariaDB: aiomysql, SQLite: aiosqlite
ASYNC_DIALECT_PREFIXES: dict[str, str] = {
    "postgresql": "postgresql+asyncpg",
    "mysql": "mysql+aiomysql",
    "mariadb": "mariadb+aiomysql",
    "sqlite": "sqlite+aiosqlite",
}


class Settings(BaseSettings):
    # Database - supports PostgreSQL (default), MySQL, MariaDB, SQLite
    database_dialect: DatabaseDialect = "postgresql"
    database_user: str = "sampleapp"
    database_secret: str = "sampleapp"
    database_host: str = "localhost"
    database_port: int | None = None  # None = use default for dialect
    database_name: str = "sampleapp"  # For SQLite: file path (e.g., ./data.db)

    @property
    def database_url(self) -> str:
        """Build async database URL for SQLAlchemy."""
        dialect = self.database_dialect
        prefix = ASYNC_DIALECT_PREFIXES.get(dialect, f"{dialect}+asyncpg")

        # SQLite uses file path, not host/port
        if dialect == "sqlite":
            return f"{prefix}:///{self.database_name}"

        # Determine port (use default if not specified)
        port = self.database_port or DEFAULT_PORTS.get(dialect, 5432)

        return f"{prefix}://{self.database_user}:{self.database_secret}@{self.database_host}:{port}/{self.database_name}"
    
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
    log_dir: str = "logs"
    log_retention_days: int = 30  # Auto-delete logs older than this
    log_max_size_mb: int = 10  # Max size per log file before rotation
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
