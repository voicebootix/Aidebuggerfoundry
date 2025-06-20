"""
Enhanced Logger - Production-Ready Centralized Logging
Comprehensive logging with structured output and monitoring integration
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class EnhancedLogger:
    """Production-ready structured logging system"""
    
    def __init__(self, service_name: str = "ai_debugger_factory"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self._setup_logger()
        
    def info(self, message):
        return self.logger.info(message)
    
    def error(self, message):
        return self.logger.error(message)

    def warning(self, message):
        return self.logger.warning(message)

    def debug(self, message):
        return self.logger.debug(message)
    
    def _setup_logger(self):
        """Setup structured logging"""
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_structured(self, 
                      level: str,
                      message: str,
                      context: Dict[str, Any] = None):
        """Log structured message with context"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            "context": context or {}
        }
        
        log_message = json.dumps(log_entry)
        
        if level == "error":
            self.logger.error(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "info":
            self.logger.info(log_message)
        else:
            self.logger.debug(log_message)

def setup_logger(service_name: str = "ai_debugger_factory") -> EnhancedLogger:
    """Setup and return enhanced logger"""
    return EnhancedLogger(service_name)

def get_logger(service_name: str = "ai_debugger_factory") -> EnhancedLogger:
    """Get existing logger instance"""
    return EnhancedLogger(service_name)