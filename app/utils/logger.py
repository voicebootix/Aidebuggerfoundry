"""
Enhanced Production Logger System
File: app/utils/logger.py
"""

import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": "ai_debugger_factory"
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logger(name: str = "ai_debugger_factory", level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure production-ready logger with structured output
    
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
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Determine if we're in production (Render/Railway) or development
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    if is_production:
        # Production: JSON structured logging to stdout
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter()
    else:
        # Development: Human-readable logging
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    handler.setLevel(numeric_level)
    logger.addHandler(handler)
    
    # Add file handler for local development
    if not is_production:
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / "ai_debugger_factory.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(numeric_level)
            logger.addHandler(file_handler)
        except Exception:
            # Silently fail if can't create file handler
            pass
    
    # Prevent log propagation to avoid duplicates
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get existing logger or create new one
    
    Args:
        name: Logger name (optional)
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "ai_debugger_factory"
    
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger

class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter for adding context to logs
    """
    
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
    
    def process(self, msg, kwargs):
        # Add extra fields to the log record
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        return msg, kwargs
    
    def with_context(self, **context):
        """Create new adapter with additional context"""
        new_extra = self.extra.copy()
        new_extra.update(context)
        return LoggerAdapter(self.logger, new_extra)

def get_request_logger(request_id: str = None, user_id: str = None, operation: str = None) -> LoggerAdapter:
    """
    Get logger with request context
    
    Args:
        request_id: Unique request identifier
        user_id: User identifier
        operation: Operation being performed
        
    Returns:
        Logger adapter with context
    """
    base_logger = get_logger()
    context = {}
    
    if request_id:
        context['request_id'] = request_id
    if user_id:
        context['user_id'] = user_id
    if operation:
        context['operation'] = operation
        
    return LoggerAdapter(base_logger, context)

# Initialize the default logger immediately
default_logger = setup_logger()
