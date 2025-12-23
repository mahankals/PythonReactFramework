import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AppConfig(Base):
    """Database-driven application configuration."""
    __tablename__ = "app_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    value_type = Column(String(20), default="string")  # string, int, bool, json
    category = Column(String(50), default="general")  # general, email, security, etc.
    is_secret = Column(Boolean, default=False)  # If true, value should be masked in UI
    is_editable = Column(Boolean, default=True)  # If false, cannot be edited via API
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_typed_value(self):
        """Return the value converted to its proper type."""
        if self.value is None:
            return None

        if self.value_type == "int":
            return int(self.value)
        elif self.value_type == "bool":
            return self.value.lower() in ("true", "1", "yes")
        elif self.value_type == "json":
            import json
            return json.loads(self.value)
        else:
            return self.value

    def set_typed_value(self, value):
        """Set the value, converting from typed value to string."""
        if value is None:
            self.value = None
        elif self.value_type == "json":
            import json
            self.value = json.dumps(value)
        elif self.value_type == "bool":
            self.value = "true" if value else "false"
        else:
            self.value = str(value)


# Default configuration values to seed
DEFAULT_CONFIG = [
    # General
    {"key": "app_name", "value": "SampleApp", "description": "Application name", "category": "general", "value_type": "string"},
    {"key": "app_url", "value": "http://localhost:3000", "description": "Frontend application URL", "category": "general", "value_type": "string"},
    {"key": "support_email", "value": "support@example.com", "description": "Support email address", "category": "general", "value_type": "string"},
    {"key": "environment", "value": "development", "description": "Environment (development, staging, production)", "category": "general", "value_type": "string"},
    {"key": "debug", "value": "true", "description": "Enable debug mode (disable in production)", "category": "general", "value_type": "bool"},
    {"key": "log_level", "value": "INFO", "description": "Logging level (DEBUG, INFO, WARNING, ERROR)", "category": "general", "value_type": "string"},
    {"key": "json_logs", "value": "false", "description": "Output logs in JSON format", "category": "general", "value_type": "bool"},

    # Email/SMTP
    {"key": "smtp_host", "value": "smtp.gmail.com", "description": "SMTP server hostname", "category": "email", "value_type": "string"},
    {"key": "smtp_port", "value": "587", "description": "SMTP server port", "category": "email", "value_type": "int"},
    {"key": "smtp_user", "value": "", "description": "SMTP username", "category": "email", "value_type": "string", "is_secret": True},
    {"key": "smtp_password", "value": "", "description": "SMTP password", "category": "email", "value_type": "string", "is_secret": True},
    {"key": "smtp_from_email", "value": "noreply@example.com", "description": "From email address", "category": "email", "value_type": "string"},
    {"key": "smtp_from_name", "value": "SampleApp", "description": "From name", "category": "email", "value_type": "string"},
    {"key": "smtp_use_tls", "value": "true", "description": "Use TLS for SMTP", "category": "email", "value_type": "bool"},

    # Security
    {"key": "password_reset_expire_minutes", "value": "30", "description": "Password reset token expiry in minutes", "category": "security", "value_type": "int"},
    {"key": "require_email_verification", "value": "false", "description": "Require email verification for new users", "category": "security", "value_type": "bool"},
    {"key": "allow_registration", "value": "true", "description": "Allow new user registration", "category": "security", "value_type": "bool"},

    # Features
    {"key": "maintenance_mode", "value": "false", "description": "Enable maintenance mode", "category": "features", "value_type": "bool"},
    {"key": "maintenance_message", "value": "We are currently performing maintenance. Please check back later.", "description": "Maintenance mode message", "category": "features", "value_type": "string"},
]
