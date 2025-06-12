import logging
import os
import sys
from typing import Optional

def setup_logger(name: str = "ai_debugger_factory", level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Add console handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
