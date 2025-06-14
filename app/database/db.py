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

async def get_db() -> AsyncGenerator:
    """
    Get database connection from pool
    
    Yields:
        Connection: Database connection
    """
    global pool
    if pool is None:
        logger.info("Initializing database connection pool")
        try:
            # Initialize pool if not exists
            await init_db()
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            # Yield None for fallback handling
            yield None
            return
    
    try:
        # Get connection from pool
        async with pool.acquire() as conn:
            yield conn
    except Exception as e:
        logger.error(f"Error getting database connection: {str(e)}")
        # Yield None for fallback handling
        yield None

async def init_db():
    """
    Initialize database connection pool
    
    This function is called on application startup
    """
    global pool
    try:
        logger.info("Creating database connection pool")
        
        # Create connection pool
        pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        
        # Test the connection
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        
        logger.info("Database connection pool created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        # Set pool to None to trigger fallback
        pool = None
        return False

async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Database connection pool closed")
