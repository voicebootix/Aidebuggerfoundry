import asyncio
import asyncpg
import logging
import json
import os
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from app.config import settings

logger = logging.getLogger(__name__)

class ProductionDatabaseManager:
    """Production database manager with real PostgreSQL connection"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.fallback_enabled = True
        
    async def initialize_pool(self):
        """Initialize PostgreSQL connection pool"""
        
        try:
            # Try PostgreSQL connection
            self.pool = await asyncpg.create_pool(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
                database=settings.DATABASE_NAME,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Test connection
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            logger.info("PostgreSQL pool initialized successfully")
            
            # Create tables if they don't exist
            await self._create_tables()
            
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {str(e)}")
            logger.info("Falling back to file-based storage")
            self.pool = None
            self._ensure_fallback_directories()
    
    async def _create_tables(self):
        """Create necessary tables"""
        
        if not self.pool:
            return
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS dream_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id UUID UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    input_text TEXT NOT NULL,
                    result_data JSONB,
                    status VARCHAR(50) DEFAULT 'processing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    processing_time FLOAT
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS generated_files (
                    id SERIAL PRIMARY KEY,
                    session_id UUID REFERENCES dream_sessions(session_id),
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500),
                    content TEXT,
                    language VARCHAR(50),
                    purpose TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_dream_sessions_user_id ON dream_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_dream_sessions_status ON dream_sessions(status);
                CREATE INDEX IF NOT EXISTS idx_generated_files_session_id ON generated_files(session_id);
            ''')
    
    def _ensure_fallback_directories(self):
        """Ensure fallback directories exist"""
        os.makedirs("data/sessions", exist_ok=True)
        os.makedirs("data/files", exist_ok=True)
    
    async def save_dream_session(self, session_data: Dict[str, Any]) -> str:
        """Save dream session to database or fallback"""
        
        if self.pool:
            return await self._save_session_postgres(session_data)
        else:
            return await self._save_session_fallback(session_data)
    
    async def _save_session_postgres(self, session_data: Dict[str, Any]) -> str:
        """Save session to PostgreSQL"""
        
        async with self.pool.acquire() as conn:
            session_id = await conn.fetchval('''
                INSERT INTO dream_sessions (session_id, user_id, input_text, result_data, status, processing_time)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING session_id
            ''', 
            session_data["session_id"],
            session_data["user_id"], 
            session_data["input_text"],
            json.dumps(session_data.get("result_data", {})),
            session_data.get("status", "completed"),
            session_data.get("processing_time", 0.0)
            )
            
            # Save generated files
            for file_info in session_data.get("files", []):
                await conn.execute('''
                    INSERT INTO generated_files (session_id, filename, file_path, content, language, purpose)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''',
                session_id,
                file_info.get("filename"),
                file_info.get("path", ""),
                file_info.get("content"),
                file_info.get("language"),
                file_info.get("purpose")
                )
            
            return str(session_id)
    
    async def _save_session_fallback(self, session_data: Dict[str, Any]) -> str:
        """Save session to file fallback"""
        
        session_id = str(session_data["session_id"])
        session_file = f"data/sessions/{session_id}.json"
        
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2, default=str)
        
        return session_id
    
    async def get_dream_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get dream session by ID"""
        
        if self.pool:
            return await self._get_session_postgres(session_id)
        else:
            return await self._get_session_fallback(session_id)
    
    async def _get_session_postgres(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from PostgreSQL"""
        
        async with self.pool.acquire() as conn:
            session_row = await conn.fetchrow('''
                SELECT * FROM dream_sessions WHERE session_id = $1
            ''', session_id)
            
            if not session_row:
                return None
            
            files = await conn.fetch('''
                SELECT * FROM generated_files WHERE session_id = $1
            ''', session_id)
            
            return {
                "session_id": str(session_row["session_id"]),
                "user_id": session_row["user_id"],
                "input_text": session_row["input_text"],
                "result_data": session_row["result_data"],
                "status": session_row["status"],
                "created_at": session_row["created_at"].isoformat(),
                "processing_time": session_row["processing_time"],
                "files": [dict(file) for file in files]
            }
    
    async def _get_session_fallback(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from file fallback"""
        
        session_file = f"data/sessions/{session_id}.json"
        
        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()

# Global instance
db_manager = ProductionDatabaseManager()

@asynccontextmanager
async def get_db_connection():
    """Database connection context manager"""
    if db_manager.pool:
        async with db_manager.pool.acquire() as conn:
            yield conn
    else:
        # For fallback, yield a mock connection object
        yield None
