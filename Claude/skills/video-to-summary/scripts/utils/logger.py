"""
Logging utilities for Video to Summary
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "video-to-summary", level: str = "INFO") -> logging.Logger:
    """
    Set up a logger with consistent formatting.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Add success method
    def success(message):
        logger.info(f"✓ {message}")

    logger.success = success

    return logger


class ProgressHandler:
    """Simple progress tracking"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.current_step = 0
        self.total_steps = 0

    def set_total(self, total: int):
        """Set total number of steps"""
        self.total_steps = total
        self.current_step = 0

    def next_step(self, step_name: str):
        """Move to next step"""
        self.current_step += 1
        self.logger.info(f"[{self.current_step}/{self.total_steps}] {step_name}")

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def success(self, message: str):
        """Log success message"""
        print(f"✓ {message}")
