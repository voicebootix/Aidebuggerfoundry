"""
Production PostgreSQL Database Manager
Real connection pooling with async operations
Enhanced with performance optimization and monitoring
"""

import asyncpg
import asyncio
import logging
import os
from typing import AsyncGenerator, Optional, Dict, Any
from contextlib import asynccontextmanager
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Production-ready PostgreSQL database manager with connection resilience"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.database_url = os.getenv(
            'DATABASE_URL', 
            'postgresql://ai_debugger_factory_user:Nz7YsUqQdmYSU62GghoWcV4xaeW3OXqc@dpg-d15csb6uk2gs73c2ubng-a/ai_debugger_factory'
        )
        self.min_connections = int(os.getenv('DB_MIN_CONNECTIONS', '5'))
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', '20'))
        self._initialization_lock = asyncio.Lock()
        self._initialized = False
        
    async def initialize(self, max_retries: int = 3, retry_delay: float = 2.0):
        """Initialize database connection pool with retry logic"""
        async with self._initialization_lock:
            if self._initialized and self.pool:
                return
                
            for attempt in range(max_retries):
                try:
                    logger.info(f"🔄 Database connection attempt {attempt + 1}/{max_retries}")
                    
                    self.pool = await asyncpg.create_pool(
                        self.database_url,
                        min_size=self.min_connections,
                        max_size=self.max_connections,
                        command_timeout=60,
                        server_settings={
                            'jit': 'off',  # Disable JIT for faster startup
                            'timezone': 'UTC'
                        }
                    )
                    
                    # Test connection and log database info
                    async with self.pool.acquire() as conn:
                        result = await conn.fetchval('SELECT version()')
                        db_name = await conn.fetchval('SELECT current_database()')
                        logger.info(f"✅ Connected to PostgreSQL: {db_name}")
                        logger.info(f"📊 Database version: {result}")
                        logger.info(f"🔗 Connection pool: {self.min_connections}-{self.max_connections} connections")
                        
                        # Verify AI Debugger Factory tables exist
                        tables = await conn.fetch("""
                            SELECT table_name FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            ORDER BY table_name
                        """)
                        
                        if tables:
                            table_names = [table['table_name'] for table in tables]
                            logger.info(f"📋 Existing tables: {', '.join(table_names)}")
                        else:
                            logger.warning("⚠️ No tables found - run migrations to create schema")
                    
                    self._initialized = True
                    return
                    
                except Exception as e:
                    logger.error(f"❌ Database connection attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        raise ConnectionError(f"Failed to connect to database after {max_retries} attempts: {e}")
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self._initialized = False
            logger.info("🔒 Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection from pool with automatic cleanup"""
        if not self.pool or not self._initialized:
            await self.initialize()
        
        if not self.pool:
            raise ConnectionError("Database pool is not initialized")
            
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                await connection.execute("ROLLBACK")  # Rollback any pending transaction
                raise
    
    async def execute_query(self, query: str, *args) -> None:
        """Execute a query without returning results"""
        async with self.get_connection() as conn:
            await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[dict]:
        """Fetch single row as dictionary"""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> list:
        """Fetch all rows as list of dictionaries"""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def health_check(self) -> dict:
        """Perform database health check"""
        try:
            async with self.get_connection() as conn:
                # Test basic connectivity
                result = await conn.fetchval('SELECT 1')
                
                # Check connection pool status
                pool_stats = {
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "available_connections": self.pool.get_idle_size() if self.pool else 0,
                    "min_connections": self.min_connections,
                    "max_connections": self.max_connections
                }
                
                # Check database size and performance
                db_stats = await conn.fetchrow("""
                    SELECT 
                        pg_database_size(current_database()) as db_size_bytes,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections
                """)
                
                return {
                    "status": "healthy",
                    "connected": bool(result),
                    "timestamp": datetime.now().isoformat(),
                    "pool_stats": pool_stats,
                    "database_size_mb": round(db_stats['db_size_bytes'] / 1024 / 1024, 2) if db_stats else 0,
                    "active_connections": db_stats['active_connections'] if db_stats else 0
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            async with self.get_connection() as conn:
                # Database size stats
                size_stats = await conn.fetchrow("""
                    SELECT 
                        pg_database_size(current_database()) as db_size,
                        pg_size_pretty(pg_database_size(current_database())) as db_size_pretty
                """)
                
                # Table statistics
                table_stats = await conn.fetch("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                        n_live_tup as row_count
                    FROM pg_stat_user_tables
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 10
                """)
                
                # Connection stats
                conn_stats = await conn.fetchrow("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)
                
                return {
                    "database_size": size_stats['db_size_pretty'] if size_stats else "0 MB",
                    "database_size_bytes": size_stats['db_size'] if size_stats else 0,
                    "tables": [
                        {
                            "name": f"{t['schemaname']}.{t['tablename']}",
                            "size": t['size'],
                            "rows": t['row_count']
                        }
                        for t in table_stats
                    ] if table_stats else [],
                    "connections": {
                        "total": conn_stats['total_connections'] if conn_stats else 0,
                        "active": conn_stats['active_connections'] if conn_stats else 0,
                        "idle": conn_stats['idle_connections'] if conn_stats else 0
                    },
                    "pool": {
                        "size": self.pool.get_size() if self.pool else 0,
                        "available": self.pool.get_idle_size() if self.pool else 0
                    }
                }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {
                "error": str(e),
                "database_size": "Unknown",
                "tables": [],
                "connections": {"total": 0, "active": 0, "idle": 0},
                "pool": {"size": 0, "available": 0}
            }

    async def run_migrations(self):
        """Run database migrations"""
        try:
            async with self.pool.acquire() as conn:
                # Check if tables exist and create them if needed
                tables = await conn.fetch("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_names = [row['table_name'] for row in tables]
                logger.info(f"📋 Existing tables: {', '.join(table_names)}")
                
                # Run init_db to create missing tables
                await init_db()
                
                logger.info("✅ Database migrations completed")
                return True
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise        

# Global database manager instance
db_manager = DatabaseManager()

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for database connections"""
    # Ensure database is initialized
    if not db_manager.pool:
        await db_manager.initialize()
    async with db_manager.get_connection() as conn:
        yield conn

async def init_db():
    """Initialize database with complete schema"""
    async with db_manager.get_connection() as conn:
        
        # Enable UUID extension
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Users table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Voice conversations table (Revolutionary VoiceBotics)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS voice_conversations (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                conversation_history JSONB NOT NULL DEFAULT '[]',
                founder_type_detected VARCHAR(50),
                business_validation_requested BOOLEAN DEFAULT FALSE,
                strategy_validated BOOLEAN DEFAULT FALSE,
                founder_ai_agreement JSONB,
                conversation_state VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Projects table (Core entity)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_name VARCHAR(255) NOT NULL,
                user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                conversation_session_id UUID REFERENCES voice_conversations(id),
                founder_ai_agreement JSONB,
                github_repo_url VARCHAR(500),
                deployment_url VARCHAR(500),
                smart_contract_address VARCHAR(255),
                technology_stack JSONB DEFAULT '["FastAPI", "React", "PostgreSQL"]',
                status VARCHAR(50) DEFAULT 'planning',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Dream sessions table (Layer 1 - Build)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS dream_sessions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                user_input TEXT NOT NULL,
                strategic_analysis JSONB,
                generated_files JSONB,
                generation_quality_score DECIMAL(3,2),
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Debug sessions table (Layer 2 - Debug)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS debug_sessions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                debug_request TEXT NOT NULL,
                analysis_results JSONB,
                suggestions JSONB,
                code_modifications JSONB,
                monaco_workspace_state JSONB,
                collaboration_users JSONB DEFAULT '[]',
                github_sync_history JSONB DEFAULT '[]',
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Business validations table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS business_validations (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                conversation_id VARCHAR(255) NOT NULL,
                market_analysis JSONB,
                competitor_research JSONB,
                business_model_validation JSONB,
                strategy_recommendations JSONB,
                validation_score DECIMAL(3,2),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Contract compliance table (Patent-worthy)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS contract_compliance (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                founder_contract JSONB NOT NULL,
                compliance_monitoring JSONB DEFAULT '[]',
                deviation_alerts JSONB DEFAULT '[]',
                compliance_score DECIMAL(3,2) DEFAULT 1.0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Revenue sharing table (Patent-worthy)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS revenue_sharing (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
                smart_contract_address VARCHAR(255),
                revenue_tracked DECIMAL(15,2) DEFAULT 0.00,
                platform_share DECIMAL(15,2) DEFAULT 0.00,
                digital_fingerprint VARCHAR(500),
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')
        
        # Create indexes for performance
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_voice_conversations_user_id ON voice_conversations(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_dream_sessions_project_id ON dream_sessions(project_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_debug_sessions_project_id ON debug_sessions(project_id)')
        
        logger.info("✅ Database schema initialized successfully")
        
