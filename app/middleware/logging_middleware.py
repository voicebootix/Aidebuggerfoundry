"""
Logging Middleware System
File: app/middleware/logging_middleware.py
"""

import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import Match
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import get_request_logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with comprehensive logging
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Skip logging for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Get operation name
        operation = self._get_operation_name(request)
        
        # Create request logger
        logger = get_request_logger(
            request_id=request_id,
            operation=operation
        )
        
        # Log request start
        start_time = time.time()
        
        # Get client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length")
            }
        )
        
        # Process request body for logging (if appropriate)
        request_body_log = await self._get_request_body_for_logging(request)
        if request_body_log:
            logger.debug("Request body", extra={"request_body": request_body_log})
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.url.path} -> {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "duration": round(duration, 3),
                    "response_size": response.headers.get("content-length")
                }
            )
            
            # Add timing header
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} -> {type(e).__name__}",
                extra={
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "duration": round(duration, 3)
                }
            )
            
            # Re-raise exception to be handled by error handler
            raise
    
    def _get_operation_name(self, request: Request) -> str:
        """
        Get operation name for the request
        """
        # Try to get route name from FastAPI route
        for route in request.app.routes:
            match, _ = route.matches({"type": "http", "path": request.url.path, "method": request.method})
            if match == Match.FULL:
                if hasattr(route, 'name') and route.name:
                    return route.name
                elif hasattr(route, 'endpoint') and route.endpoint:
                    return f"{route.endpoint.__module__}.{route.endpoint.__name__}"
        
        # Fallback to method and path
        return f"{request.method} {request.url.path}"
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get real client IP address
        """
        # Check for forwarded headers (common in production behind proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"
    
    async def _get_request_body_for_logging(self, request: Request) -> dict:
        """
        Get request body for logging (sanitized)
        """
        # Only log body for certain content types and methods
        if request.method not in ["POST", "PUT", "PATCH"]:
            return None
        
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return None
        
        try:
            # Read body
            body = await request.body()
            if not body:
                return None
            
            # Parse JSON
            json_body = json.loads(body)
            
            # Sanitize sensitive fields
            sanitized_body = self._sanitize_log_data(json_body)
            
            return sanitized_body
            
        except Exception:
            # If we can't parse, don't log body
            return None
    
    def _sanitize_log_data(self, data: dict) -> dict:
        """
        Remove sensitive information from log data
        """
        if not isinstance(data, dict):
            return data
        
        sensitive_keys = {
            "password", "token", "api_key", "secret", "authorization",
            "credit_card", "ssn", "social_security", "private_key"
        }
        
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_log_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_log_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring and alerts
    """
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 5.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request performance
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log slow requests
            if duration > self.slow_request_threshold:
                logger = get_request_logger(
                    request_id=getattr(request.state, 'request_id', 'unknown'),
                    operation=f"{request.method} {request.url.path}"
                )
                
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path}",
                    extra={
                        "duration": round(duration, 3),
                        "threshold": self.slow_request_threshold,
                        "status_code": response.status_code
                    }
                )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger = get_request_logger(
                request_id=getattr(request.state, 'request_id', 'unknown'),
                operation=f"{request.method} {request.url.path}"
            )
            
            logger.error(
                f"Request failed after {duration:.3f}s: {type(e).__name__}",
                extra={
                    "duration": round(duration, 3),
                    "exception_type": type(e).__name__
                }
            )
            
            raise
