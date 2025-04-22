"""
Centralized logging configuration for the email agent application.

This module provides a consistent logging setup across all application components,
with daily log rotation and configurable log levels.
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

def configure_logging(
    log_dir="logs",
    log_level=None,
    log_file_name="email_agent.log",
    console_output=True
):
    """
    Configure application-wide logging with daily rotation.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO, can be set via LOG_LEVEL env)
        log_file_name: Name of the log file
        console_output: Whether to output logs to console
    
    Environment Variables:
        LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        LOGGING_ENABLED: Set to '0' or 'false' to disable logging
    """
    # Check if logging is disabled
    if os.environ.get("LOGGING_ENABLED", "1").lower() in ("0", "false", "no"):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        return root_logger

    # Allow log level override via env
    env_log_level = os.environ.get("LOG_LEVEL")
    if env_log_level:
        log_level = getattr(logging, env_log_level.upper(), logging.INFO)
    elif log_level is None:
        log_level = logging.INFO
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a formatter with timestamp, level, and module
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
                                 '%Y-%m-%d %H:%M:%S')
    
    # Create console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Create file handler with daily rotation
    log_file = os.path.join(log_dir, log_file_name)
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30  # Keep logs for 30 days
    )
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"  # Add date suffix to rotated files
    root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log that logging has been set up
    logging.getLogger(__name__).info(f"Logging configured. Log file: {log_file}")
    
    return root_logger 