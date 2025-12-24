"""
Application logging with daily rotation and auto-cleanup.

Log files:
- logs/app-YYYY-MM-DD.log: All logs (INFO, DEBUG, WARNING, ERROR)
- logs/error-YYYY-MM-DD.log: Error logs only (ERROR, CRITICAL)
"""

import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.config import settings


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """Custom handler that includes date in filename and auto-deletes old logs."""

    def __init__(
        self,
        log_dir: str,
        prefix: str,
        retention_days: int = 30,
        level: int = logging.DEBUG,
    ):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.retention_days = retention_days

        # Current log file with date
        log_file = self.log_dir / f"{prefix}-{datetime.now().strftime('%Y-%m-%d')}.log"

        super().__init__(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=retention_days,
            encoding="utf-8",
        )
        self.setLevel(level)
        self.namer = self._namer
        self.rotator = self._rotator

        # Clean up old logs on init
        self._cleanup_old_logs()

    def _namer(self, default_name: str) -> str:
        """Generate filename with date suffix."""
        # Extract date from the default name and create proper filename
        dir_name = os.path.dirname(default_name)
        date_suffix = default_name.split(".")[-1]
        return os.path.join(dir_name, f"{self.prefix}-{date_suffix}.log")

    def _rotator(self, source: str, dest: str) -> None:
        """Rotate the log file."""
        if os.path.exists(source):
            # On rotation, rename source to dest
            if os.path.exists(dest):
                os.remove(dest)
            os.rename(source, dest)

    def doRollover(self) -> None:
        """Perform rollover and cleanup old logs."""
        super().doRollover()
        # Update base filename to new date
        new_file = self.log_dir / f"{self.prefix}-{datetime.now().strftime('%Y-%m-%d')}.log"
        self.baseFilename = str(new_file)
        self._cleanup_old_logs()

    def _cleanup_old_logs(self) -> None:
        """Delete log files older than retention_days."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob(f"{self.prefix}-*.log"):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace(f"{self.prefix}-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    log_file.unlink()
            except (ValueError, OSError):
                # Skip files that don't match the date pattern
                pass


class AppLogger:
    """Singleton logger with file rotation and console output."""

    _instance: logging.Logger | None = None

    @classmethod
    def get_logger(cls, name: str = "app") -> logging.Logger:
        """Get or create the application logger."""
        if cls._instance is not None:
            return cls._instance

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Formatter
        if settings.json_logs:
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # App log file handler (all levels)
        app_handler = DailyRotatingFileHandler(
            log_dir=settings.log_dir,
            prefix="app",
            retention_days=settings.log_retention_days,
            level=logging.DEBUG,
        )
        app_handler.setFormatter(formatter)
        logger.addHandler(app_handler)

        # Error log file handler (ERROR and above only)
        error_handler = DailyRotatingFileHandler(
            log_dir=settings.log_dir,
            prefix="error",
            retention_days=settings.log_retention_days,
            level=logging.ERROR,
        )
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        cls._instance = logger
        return logger


# Convenience function
def get_logger(name: str = "app") -> logging.Logger:
    """Get the application logger."""
    return AppLogger.get_logger(name)


# Pre-configured logger instance
logger = get_logger()
