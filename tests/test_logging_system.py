"""
Comprehensive Logging System Tests
File: tests/test_logging_system.py
"""

import pytest
import logging
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.utils.logger import setup_logger, get_logger, get_request_logger, LoggerAdapter
from app.utils.error_handler import (
    ErrorHandler, APIError, ValidationAPIError, ResourceNotFoundAPIError,
    handle_errors, raise_validation_error, raise_not_found_error
)
from app.middleware.logging_middleware import LoggingMiddleware, PerformanceLoggingMiddleware

class TestLoggerSetup:
    """Test logger setup and configuration"""
    
    def test_setup_logger_default(self):
        """Test default logger setup"""
        logger = setup_logger()
        assert logger.name == "ai_debugger_factory"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_setup_logger_custom_level(self):
        """Test logger with custom level"""
        logger = setup_logger("test_logger", "DEBUG")
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
    
    def test_get_logger_existing(self):
        """Test getting existing logger"""
        logger1 = setup_logger("test_existing")
        logger2 = get_logger("test_existing")
        assert logger1 is logger2
    
    def test_get_logger_new(self):
        """Test getting new logger"""
        logger = get_logger("test_new")
        assert logger.name == "test_new"
        assert len(logger.handlers) > 0
    
    def test_request_logger_context(self):
        """Test request logger with context"""
        logger = get_request_logger(
            request_id="test-123",
            user_id="user-456",
            operation="test_operation"
        )
        assert isinstance(logger, LoggerAdapter)
        assert logger.extra["request_id"] == "test-123"
        assert logger.extra["user_id"] == "user-456"
        assert logger.extra["operation"] == "test_operation"
    
    def test_logger_adapter_with_context(self):
        """Test logger adapter context addition"""
        base_logger = get_logger("test_adapter")
        adapter = LoggerAdapter(base_logger, {"key1": "value1"})
        new_adapter = adapter.with_context(key2="value2")
        
        assert new_adapter.extra["key1"] == "value1"
        assert new_adapter.extra["key2"] == "value2"

class TestErrorHandler:
    """Test error handling functionality"""
    
    def test_api_error_creation(self):
        """Test APIError creation"""
        error = APIError("Test error", 400, "TEST_ERROR", {"detail": "test"})
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"detail": "test"}
    
    def test_validation_api_error(self):
        """Test ValidationAPIError"""
        error = ValidationAPIError("Invalid input")
        assert error.status_code == 400
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundAPIError"""
        error = ResourceNotFoundAPIError("User", "123")
        assert error.status_code == 404
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert "User not found: 123" in error.message
    
    def test_create_error_response_api_error(self):
        """Test error response creation for APIError"""
        error = ValidationAPIError("Test validation error", {"field": "required"})
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/test"
        
        response = ErrorHandler.create_error_response(error, "test-123", request)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        
        # Parse response content
        content = json.loads(response.body.decode())
        assert content["error"]["code"] == "VALIDATION_ERROR"
        assert content["error"]["message"] == "Test validation error"
        assert content["error"]["request_id"] == "test-123"
        assert "details" in content["error"]
    
    def test_create_error_response_unhandled_exception(self):
        """Test error response for unhandled exception"""
        error = RuntimeError("Unexpected error")
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        
        response = ErrorHandler.create_error_response(error, "test-456", request)
        
        assert response.status_code == 500
        content = json.loads(response.body.decode())
        assert content["error"]["code"] == "INTERNAL_ERROR"
        assert content["error"]["message"] == "An unexpected error occurred"
        assert "details" not in content["error"]  # No details for 5xx errors
    
    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""
        def test_func(x, y):
            return x + y
        
        result = ErrorHandler.safe_execute(test_func, 2, 3)
        assert result == 5
    
    def test_safe_execute_failure(self):
        """Test safe_execute with failing function"""
        def failing_func():
            raise ValueError("Test error")
        
        result = ErrorHandler.safe_execute(
            failing_func, 
            fallback_result="fallback",
            error_message="Custom error message"
        )
        assert result == "fallback"
    
    @pytest.mark.asyncio
    async def test_safe_execute_async_success(self):
        """Test safe_execute_async with successful function"""
        async def test_func(x, y):
            return x * y
        
        result = await ErrorHandler.safe_execute_async(test_func, 3, 4)
        assert result == 12
    
    @pytest.mark.asyncio
    async def test_safe_execute_async_failure(self):
        """Test safe_execute_async with failing function"""
        async def failing_func():
            raise ValueError("Async test error")
        
        result = await ErrorHandler.safe_execute_async(
            failing_func,
            fallback_result="async_fallback"
        )
        assert result == "async_fallback"

class TestErrorDecorator:
    """Test error handling decorator"""
    
    def test_handle_errors_decorator_sync(self):
        """Test error handling decorator for sync functions"""
        @handle_errors("test_operation")
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()
    
    @pytest.mark.asyncio
    async def test_handle_errors_decorator_async(self):
        """Test error handling decorator for async functions"""
        @handle_errors("async_test_operation")
        async def async_test_function():
            raise RuntimeError("Async test error")
        
        with pytest.raises(RuntimeError):
            await async_test_function()

class TestConvenienceFunctions:
    """Test convenience error raising functions"""
    
    def test_raise_validation_error(self):
        """Test raise_validation_error function"""
        with pytest.raises(ValidationAPIError) as exc_info:
            raise_validation_error("Invalid data", {"field": "required"})
        
        assert exc_info.value.message == "Invalid data"
        assert exc_info.value.details == {"field": "required"}
    
    def test_raise_not_found_error(self):
        """Test raise_not_found_error function"""
        with pytest.raises(ResourceNotFoundAPIError) as exc_info:
            raise_not_found_error("Document", "doc-123")
        
        assert "Document not found: doc-123" in exc_info.value.message

class TestLoggingMiddleware:
    """Test logging middleware functionality"""
    
    def setup_method(self):
        """Set up test app with middleware"""
        self.app = FastAPI()
        self.app.add_middleware(LoggingMiddleware)
        
        @self.app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @self.app.post("/test-error")
        async def error_endpoint():
            raise ValueError("Test error")
        
        self.client = TestClient(self.app)
    
    def test_successful_request_logging(self):
        """Test logging for successful requests"""
        with patch('app.middleware.logging_middleware.get_request_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            response = self.client.get("/test")
            
            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            assert "X-Processing-Time" in response.headers
            
            # Verify logging calls
            mock_logger_instance.info.assert_called()
    
    def test_error_request_logging(self):
        """Test logging for error requests"""
        with patch('app.middleware.logging_middleware.get_request_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            with pytest.raises(ValueError):
                self.client.post("/test-error")
            
            # Verify error logging
            mock_logger_instance.error.assert_called()
    
    def test_excluded_paths(self):
        """Test that excluded paths are not logged"""
        self.app.add_middleware(LoggingMiddleware)
        
        @self.app.get("/health")
        async def health():
            return {"status": "ok"}
        
        with patch('app.middleware.logging_middleware.get_request_logger') as mock_logger:
            response = self.client.get("/health")
            assert response.status_code == 200
            
            # Should not create logger for excluded paths
            mock_logger.assert_not_called()

class TestPerformanceLoggingMiddleware:
    """Test performance logging middleware"""
    
    def setup_method(self):
        """Set up test app with performance middleware"""
        self.app = FastAPI()
        self.app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold=0.1)
        
        @self.app.get("/fast")
        async def fast_endpoint():
            return {"message": "fast"}
        
        @self.app.get("/slow")
        async def slow_endpoint():
            await asyncio.sleep(0.2)  # Simulate slow operation
            return {"message": "slow"}
        
        self.client = TestClient(self.app)
    
    def test_fast_request_no_warning(self):
        """Test that fast requests don't trigger warnings"""
        with patch('app.middleware.logging_middleware.get_request_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            response = self.client.get("/fast")
            assert response.status_code == 200
            
            # Should not log warning for fast requests
            mock_logger_instance.warning.assert_not_called()
    
    def test_slow_request_warning(self):
        """Test that slow requests trigger warnings"""
        with patch('app.middleware.logging_middleware.get_request_logger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            response = self.client.get("/slow")
            assert response.status_code == 200
            
            # Should log warning for slow requests
            mock_logger_instance.warning.assert_called()

class TestIntegration:
    """Integration tests for the complete logging system"""
    
    @pytest.mark.asyncio
    async def test_complete_error_flow(self):
        """Test complete error handling flow"""
        # Create a mock request
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        request.state.request_id = "integration-test-123"
        
        # Create an API error
        error = ValidationAPIError("Integration test error")
        
        # Process error
        response = ErrorHandler.create_error_response(error, "integration-test-123", request)
        
        # Verify response
        assert response.status_code == 400
        content = json.loads(response.body.decode())
        assert content["error"]["code"] == "VALIDATION_ERROR"
        assert content["error"]["request_id"] == "integration-test-123"
    
    def test_logger_production_mode(self):
        """Test logger in production mode"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            logger = setup_logger("prod_test")
            
            # Should have JSON formatter in production
            handler = logger.handlers[0]
            assert hasattr(handler.formatter, 'format')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
