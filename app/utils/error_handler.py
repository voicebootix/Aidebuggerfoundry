
"""
Centralized Error Handler System
File: app/utils/error_handler.py
"""

import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import asyncio

from app.utils.logger import get_logger, get_request_logger

logger = get_logger()

class APIError(Exception):
    """Base API error class"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = None,
        details: Dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(message)

class ValidationAPIError(APIError):
    """Validation error"""
    
    def __init__(self, message: str, details: Dict = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationAPIError(APIError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationAPIError(APIError):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )

class ResourceNotFoundAPIError(APIError):
    """Resource not found error"""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND"
        )

class RateLimitAPIError(APIError):
    """Rate limit exceeded error"""
    
    def __init__(self, retry_after: int = None):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after} if retry_after else {}
        )

class ExternalServiceError(APIError):
    """External service error"""
    
    def __init__(self, service: str, message: str = None):
        super().__init__(
            message=message or f"External service error: {service}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def create_error_response(
        error: Exception,
        request_id: str = None,
        request: Request = None
    ) -> JSONResponse:
        """
        Create standardized error response
        
        Args:
            error: Exception that occurred
            request_id: Request identifier
            request: FastAPI request object
            
        Returns:
            JSON error response
        """
        
        # Generate request ID if not provided
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Get request context for logging
        request_logger = get_request_logger(
            request_id=request_id,
            operation=f"{request.method} {request.url.path}" if request else "unknown"
        )
        
        # Handle different error types
        if isinstance(error, APIError):
            status_code = error.status_code
            error_code = error.error_code
            message = error.message
            details = error.details
            
            if status_code >= 500:
                request_logger.error(f"API Error: {message}", extra={"details": details})
            else:
                request_logger.warning(f"Client Error: {message}", extra={"details": details})
                
        elif isinstance(error, HTTPException):
            status_code = error.status_code
            error_code = "HTTP_EXCEPTION"
            message = error.detail
            details = {}
            
            if status_code >= 500:
                request_logger.error(f"HTTP Exception: {message}")
            else:
                request_logger.warning(f"HTTP Exception: {message}")
                
        elif isinstance(error, ValidationError):
            status_code = 422
            error_code = "VALIDATION_ERROR"
            message = "Validation failed"
            details = {"validation_errors": error.errors()}
            
            request_logger.warning(f"Validation Error: {message}", extra={"details": details})
            
        elif isinstance(error, ValueError):
            status_code = 400
            error_code = "VALUE_ERROR"
            message = str(error)
            details = {}
            
            request_logger.warning(f"Value Error: {message}")
            
        elif isinstance(error, FileNotFoundError):
            status_code = 404
            error_code = "FILE_NOT_FOUND"
            message = "Requested file not found"
            details = {}
            
            request_logger.warning(f"File Not Found: {message}")
            
        elif isinstance(error, PermissionError):
            status_code = 403
            error_code = "PERMISSION_ERROR"
            message = "Permission denied"
            details = {}
            
            request_logger.warning(f"Permission Error: {message}")
            
        elif isinstance(error, TimeoutError) or isinstance(error, asyncio.TimeoutError):
            status_code = 504
            error_code = "TIMEOUT_ERROR"
            message = "Request timeout"
            details = {}
            
            request_logger.error(f"Timeout Error: {message}")
            
        else:
            # Unhandled exception
            status_code = 500
            error_code = "INTERNAL_ERROR"
            message = "An unexpected error occurred"
            details = {}
            
            # Log full traceback for debugging
            request_logger.error(
                f"Unhandled Exception: {type(error).__name__}: {str(error)}",
                extra={
                    "exception_type": type(error).__name__,
                    "exception_str": str(error),
                    "traceback": traceback.format_exc()
                }
            )
        
        # Create response body
        response_body = {
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Add details for client errors (4xx) but not server errors (5xx)
        if 400 <= status_code < 500 and details:
            response_body["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=response_body
        )
    
    @staticmethod
    def safe_execute(func, *args, fallback_result=None, error_message="Operation failed", **kwargs):
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Function arguments
            fallback_result: Result to return on error
            error_message: Error message for logging
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback_result
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            return fallback_result
    
    @staticmethod
    async def safe_execute_async(func, *args, fallback_result=None, error_message="Async operation failed", **kwargs):
        """
        Safely execute an async function with error handling
        
        Args:
            func: Async function to execute
            *args: Function arguments
            fallback_result: Result to return on error
            error_message: Error message for logging
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback_result
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            return fallback_result

def handle_errors(operation: str = None):
    """
    Decorator for automatic error handling
    
    Args:
        operation: Description of the operation for logging
        
    Returns:
        Decorator function
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    operation_name = operation or f"{func.__module__}.{func.__name__}"
                    logger.error(f"Error in {operation_name}: {str(e)}")
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    operation_name = operation or f"{func.__module__}.{func.__name__}"
                    logger.error(f"Error in {operation_name}: {str(e)}")
                    raise
            return sync_wrapper
    return decorator

# Convenience functions
def raise_validation_error(message: str, details: Dict = None):
    """Raise validation error"""
    raise ValidationAPIError(message, details)

def raise_not_found_error(resource: str, identifier: str = None):
    """Raise not found error"""
    raise ResourceNotFoundAPIError(resource, identifier)

def raise_auth_error(message: str = None):
    """Raise authentication error"""
    raise AuthenticationAPIError(message)

def raise_access_error(message: str = None):
    """Raise authorization error"""
    raise AuthorizationAPIError(message)

def raise_rate_limit_error(retry_after: int = None):
    """Raise rate limit error"""
    raise RateLimitAPIError(retry_after)

def raise_external_service_error(service: str, message: str = None):
    """Raise external service error"""
    raise ExternalServiceError(service, message)
