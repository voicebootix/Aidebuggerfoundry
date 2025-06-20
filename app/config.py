"""
AI Debugger Factory - Configuration Management
Centralized settings for all application components
"""

import os
import sys
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Core Application
    APP_NAME: str = Field(default="AI Debugger Factory", description="Application name")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    SECRET_KEY: str = Field(..., description="Secret key for security")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, description="Database max overflow connections")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed hosts")
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] =  Field(default=None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, description="Anthropic API key")
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google API key")
    DEFAULT_LLM_PROVIDER: str = Field(default="auto", description="Default LLM provider")
    
    # OpenAI Specific
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI temperature")
    OPENAI_RATE_LIMIT_TPM: int = Field(default=100000, description="OpenAI rate limit tokens per minute")
    OPENAI_VOICE_MODEL: str = Field(default="whisper-1", description="OpenAI voice model")
    
    # Voice Processing
    VOICE_API_KEY: Optional[str] = Field(default=None, description="Voice API key")
    VOICE_LANGUAGE: str = Field(default="en", description="Voice processing language")
    VOICE_TIMEOUT: int = Field(default=60, description="Voice processing timeout")
    SUPPORTED_VOICE_FORMATS: str = Field(
        default="webm,mp4,mpeg,mpga,m4a,wav,flac,ogg", 
        description="Supported voice formats"
    )
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, description="ElevenLabs API key")
    
    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = Field(default=None, description="GitHub personal access token")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    
    # Smart Contracts
    WEB3_PROVIDER_URL: Optional[str] = Field(default=None, description="Web3 provider URL")
    SMART_CONTRACT_ADDRESS: Optional[str] = Field(default=None, description="Smart contract address")
    PRIVATE_KEY: Optional[str] = Field(default=None, description="Private key for contract deployment")
    PLATFORM_REVENUE_SHARE: float = Field(default=0.15, description="Platform revenue share (15%)")
    FOUNDER_REVENUE_SHARE: float = Field(default=0.85, description="Founder revenue share (85%)")
    
    # Business Intelligence
    SERPAPI_KEY: Optional[str] = Field(default=None, description="SerpAPI key for market research")
    RAPID_API_KEY: Optional[str] = Field(default=None, description="RapidAPI key")
    
    # DreamEngine Configuration  
    DREAMENGINE_DEFAULT_PROVIDER: str = Field(default="auto", description="Default LLM provider for DreamEngine")
    DREAMENGINE_MAX_TOKENS: int = Field(default=8192, description="Max tokens for code generation")
    DREAMENGINE_TEMPERATURE: float = Field(default=0.7, description="Temperature for code generation")
    DREAMENGINE_STREAMING_ENABLED: bool = Field(default=True, description="Enable streaming responses")
    DREAMENGINE_STREAMING_CHUNK_SIZE: int = Field(default=1024, description="Streaming chunk size")
    DREAMENGINE_STREAMING_MAX_CONNECTIONS: int = Field(default=10, description="Max streaming connections")
    DREAMENGINE_CACHE_ENABLED: bool = Field(default=False, description="Enable response caching")
    DREAMENGINE_CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    DREAMENGINE_RATE_LIMIT: int = Field(default=100, description="Rate limit per hour")
    DREAMENGINE_RATE_LIMIT_PERIOD: int = Field(default=3600, description="Rate limit period")
    DREAMENGINE_SECURITY_SCAN_ENABLED: bool = Field(default=True, description="Enable security scanning")
    DREAMENGINE_LOG_LEVEL: str = Field(default="INFO", description="Log level")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # Security
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT expiration in hours")
    API_KEY_SALT: str = Field(..., description="API key salt")
    HTTP_TIMEOUT: int = Field(default=60, description="HTTP timeout in seconds")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error monitoring")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: json or text")
    
    # Development
    RELOAD: bool = Field(default=True, description="Auto-reload on code changes")
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('Invalid log level')
        return v
    
    @validator('PLATFORM_REVENUE_SHARE', 'FOUNDER_REVENUE_SHARE')
    def validate_revenue_shares(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Revenue share must be between 0 and 1')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Add root directory to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import from root config (your existing excellent config)
#from config import Settings, get_settings, settings

# Re-export everything for app modules
#__all__ = ['Settings', 'get_settings', 'settings']

# Validation function (optional)
def validate_startup_requirements():
    """Validate that all required settings are present"""
    required = ['SECRET_KEY', 'DATABASE_URL', 'JWT_SECRET_KEY', 'API_KEY_SALT']
    missing = [key for key in required if not getattr(settings, key, None)]
    
    if missing:
        print(f"⚠️  Missing required environment variables: {', '.join(missing)}")
        print("📝 Please create a .env file with the required values")
        return False
    
    return True

# Global settings instance
settings = get_settings()