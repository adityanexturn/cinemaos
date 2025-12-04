"""
Logger Configuration
--------------------
Sets up logging for the Cinema OS application using loguru.
This provides better debugging capabilities and error tracking across all modules.
Logs are written to both console and file for comprehensive monitoring.
"""

import sys
from loguru import logger
from pathlib import Path


def setup_logger():
    """
    Configure the application logger with appropriate format and output destinations.
    The logger writes to both console (for development) and a rotating log file (for production).
    Log files are stored in a 'logs' directory and rotate when they reach 10MB.
    """
    
    # Remove default logger to avoid duplicate logs
    logger.remove()
    
    # Create logs directory if it doesn't exist
    # This ensures log files have a dedicated location for easy access
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Add console logger for development - shows INFO level and above
    # Simple format without color markup
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="INFO"
    )
    
    # Add file logger for production - captures DEBUG level and above
    # Rotation ensures log files don't grow indefinitely (10MB max per file)
    # Retention keeps files for 7 days (instead of "10 files" which was invalid)
    logger.add(
        log_dir / "cinema_os_{time}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info("Cinema OS logger initialized successfully")
    return logger


# Initialize logger on module import
# This makes the logger available throughout the application
cinema_logger = setup_logger()
