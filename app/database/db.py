import asyncpg
import logging
from typing import AsyncGenerator, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_debugger_factory")

# Connection pool
pool = None

async def get_db():
    """
    Get database connection from pool
    
    Yields:
        Connection: Database connection
    """
    global pool
    if pool is None:
        # This is a simplified implementation for testing
        # In production, we would use a proper connection pool
        logger.info("Creating database connection pool")
        try:
            # For testing purposes, we'll just return None
            # In production, this would be a real connection
            conn = None
            yield conn
        except Exception as e:
            logger.error(f"Error getting database connection: {str(e)}")
            raise
    else:
        try:
            async with pool.acquire() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Error getting database connection: {str(e)}")
            raise

async def init_db():
    """
    Initialize database
    
    This function is called on application startup
    """
    global pool
    try:
        # For testing purposes, we'll just log a message
        # In production, this would create a real connection pool
        logger.info("Initializing database")
        
        # Simulate successful initialization
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
