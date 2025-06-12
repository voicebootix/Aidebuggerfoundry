import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # App settings
    APP_NAME: str = "AI Debugger Factory"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_debugger_factory")
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # LLM settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    
    # GitHub settings
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO: Optional[str] = os.getenv("GITHUB_REPO")
    
    # Voice API settings
    VOICE_API_KEY: Optional[str] = os.getenv("VOICE_API_KEY")
    VOICE_API_ENDPOINT: Optional[str] = os.getenv("VOICE_API_ENDPOINT")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Contract settings
    CONTRACT_FILE_PATH: str = os.getenv("CONTRACT_FILE_PATH", "../../meta/api-contracts.json")
    PROMPT_LOG_PATH: str = os.getenv("PROMPT_LOG_PATH", "../../meta/prompt_log.json")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
