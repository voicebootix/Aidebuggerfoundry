import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncpg
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ProjectContext:
    """Complete project context and memory"""
    project_id: str
    user_id: str
    original_prompt: str
    tech_stack: Dict
    files: Dict[str, str]
    conversation_history: List[Dict]
    decisions: List[Dict]
    features: List[Dict]
    created_at: datetime
    last_updated: datetime

@dataclass
class ConversationMemory:
    """Individual conversation memory unit"""
    id: str
    project_id: str
    timestamp: datetime
    user_input: str
    ai_response: str
    intent_detected: str
    changes_made: List[str]
    reasoning: str

class ProjectMemoryManager:
    """
    Manages persistent project memory and conversation context
    """
    
    def __init__(self):
        self.db_pool = None
        
    async def init_db(self):
        """Initialize database connection"""
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.db_pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
                await self._create_memory_tables()
        except Exception as e:
            logger.error(f"❌ Memory DB init failed: {str(e)}")
    
    async def _create_memory_tables(self):
        """Create memory storage tables"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS project_memory (
                    project_id UUID PRIMARY KEY,
                    user_id VARCHAR(255),
                    original_prompt TEXT,
                    tech_stack JSONB,
                    files JSONB,
                    conversation_history JSONB,
                    decisions JSONB,
                    features JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_updated TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    project_id UUID REFERENCES project_memory(project_id),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    user_input TEXT,
                    ai_response TEXT,
                    intent_detected VARCHAR(100),
                    changes_made JSONB,
                    reasoning TEXT
                )
            """)
    
    async def save_project_context(self, context: ProjectContext):
        """Save complete project context"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO project_memory 
                    (project_id, user_id, original_prompt, tech_stack, files, 
                     conversation_history, decisions, features, created_at, last_updated)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (project_id) DO UPDATE SET
                        files = EXCLUDED.files,
                        conversation_history = EXCLUDED.conversation_history,
                        decisions = EXCLUDED.decisions,
                        features = EXCLUDED.features,
                        last_updated = EXCLUDED.last_updated
                """, 
                    context.project_id,
                    context.user_id,
                    context.original_prompt,
                    json.dumps(context.tech_stack),
                    json.dumps(context.files),
                    json.dumps(context.conversation_history),
                    json.dumps(context.decisions),
                    json.dumps(context.features),
                    context.created_at,
                    context.last_updated
                )
        except Exception as e:
            logger.error(f"❌ Failed to save project context: {str(e)}")
    
    async def load_project(self, project_id: str) -> Optional[Dict]:
        """Load project context from memory"""
        if not self.db_pool:
            return None
            
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM project_memory WHERE project_id = $1",
                    project_id
                )
                
                if row:
                    return {
                        "project_id": row["project_id"],
                        "user_id": row["user_id"],
                        "original_prompt": row["original_prompt"],
                        "tech_stack": json.loads(row["tech_stack"]) if row["tech_stack"] else {},
                        "files": json.loads(row["files"]) if row["files"] else {},
                        "conversation_history": json.loads(row["conversation_history"]) if row["conversation_history"] else [],
                        "decisions": json.loads(row["decisions"]) if row["decisions"] else [],
                        "features": json.loads(row["features"]) if row["features"] else [],
                        "created_at": row["created_at"],
                        "last_updated": row["last_updated"]
                    }
                    
        except Exception as e:
            logger.error(f"❌ Failed to load project: {str(e)}")
            
        return None
    
    async def remember_conversation(self, memory: ConversationMemory):
        """Store individual conversation memory"""
        if not self.db_pool:
            return
            
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO conversation_memory 
                    (project_id, timestamp, user_input, ai_response, 
                     intent_detected, changes_made, reasoning)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    memory.project_id,
                    memory.timestamp,
                    memory.user_input,
                    memory.ai_response,
                    memory.intent_detected,
                    json.dumps(memory.changes_made),
                    memory.reasoning
                )
        except Exception as e:
            logger.error(f"❌ Failed to store conversation memory: {str(e)}")
    
    async def get_conversation_context(self, project_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        if not self.db_pool:
            return []
            
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM conversation_memory 
                    WHERE project_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                """, project_id, limit)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Failed to get conversation context: {str(e)}")
            return []
