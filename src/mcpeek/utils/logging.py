"""Logging configuration for MCPeek."""

import logging
import sys
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


class LoggingManager:
    """Centralized logging configuration."""

    def __init__(self):
        self.logger = logging.getLogger("mcpeek")
        self._configured = False

    def setup_logging(self, level: str, format_type: str = "structured") -> None:
        """Configure logging with specified level and format."""
        if self._configured:
            return

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Set logging level
        self.configure_log_level(level)

        # Create formatter
        if format_type == "structured":
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = logging.Formatter('%(levelname)s: %(message)s')

        # Create console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self._configured = True

    def configure_log_level(self, level: str) -> None:
        """Set logging level (DEBUG, INFO, WARNING, ERROR)."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
        }

        log_level = level_map.get(level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

    def create_structured_logs(self, context: Dict[str, Any]) -> None:
        """Create structured log entries with context."""
        # Add context to all subsequent log messages
        for key, value in context.items():
            self.logger = logging.LoggerAdapter(self.logger, {key: value})

    def handle_log_rotation(self, max_size: int, backup_count: int) -> None:
        """Configure log rotation if file logging is enabled."""
        # This would be used if we add file logging in the future
        pass

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger


# Global logging manager instance
logging_manager = LoggingManager()


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    return logging_manager.get_logger()