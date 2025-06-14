import asyncpg
import logging
from typing import Dict, List, Optional, Any
import os
import json
from datetime import datetime

from app.config import settings

# Set up logger
logger = logging.getLogger(__name__)

# Database connection pool
pool = None

async def init_db():
    """Initialize database connection pool and create tables if they don't exist"""
    global pool
    
    try:
        # Create connection pool
        logger.info(f"Connecting to database: {settings.DATABASE_URL}")
        pool = await asyncpg.create_pool(settings.DATABASE_URL)
        
        # Create tables
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    id SERIAL PRIMARY KEY,
                    prompt_id INTEGER REFERENCES prompts(id),
                    contract JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS generated_code (
                    id SERIAL PRIMARY KEY,
                    prompt_id INTEGER REFERENCES prompts(id),
                    contract_id INTEGER REFERENCES contracts(id),
                    files JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS build_logs (
                    id SERIAL PRIMARY KEY,
                    prompt_id INTEGER REFERENCES prompts(id),
                    status TEXT NOT NULL,
                    message TEXT,
                    details JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS prompt_lineage (
                    id SERIAL PRIMARY KEY,
                    parent_prompt_id INTEGER REFERENCES prompts(id),
                    child_prompt_id INTEGER REFERENCES prompts(id),
                    relationship_type TEXT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
        logger.info("Database initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        
        # Create a fallback file-based storage if database connection fails
        os.makedirs("../../meta/db_fallback", exist_ok=True)
        
        # Initialize fallback files if they don't exist
        for table in ["prompts", "contracts", "generated_code", "build_logs", "prompt_lineage"]:
            if not os.path.exists(f"../../meta/db_fallback/{table}.json"):
                with open(f"../../meta/db_fallback/{table}.json", "w") as f:
                    json.dump({"records": []}, f)
        
        logger.info("Initialized fallback file-based storage")
        return False

async def get_db():
    """Get database connection from pool"""
    global pool
    
    if pool is None:
        success = await init_db()
        if not success:
            # Return a fallback file-based DB handler
            yield FallbackDBHandler()
    
    try:
        # Return a connection from the pool
        conn = await pool.acquire()
        try:
            yield DBHandler(conn)
        finally:
            await pool.release(conn)
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        # Return a fallback file-based DB handler
        yield FallbackDBHandler()

class DBHandler:
    """Database handler for PostgreSQL operations"""
    
    def __init__(self, conn):
        self.conn = conn
    
    async def save_prompt(self, title: str, prompt: str) -> int:
        """Save a prompt to the database and return its ID"""
        query = """
            INSERT INTO prompts (title, prompt)
            VALUES ($1, $2)
            RETURNING id
        """
        prompt_id = await self.conn.fetchval(query, title, prompt)
        return prompt_id
    
    async def save_contract(self, prompt_id: int, contract: Dict) -> int:
        """Save an API contract to the database and return its ID"""
        query = """
            INSERT INTO contracts (prompt_id, contract)
            VALUES ($1, $2)
            RETURNING id
        """
        contract_id = await self.conn.fetchval(query, prompt_id, json.dumps(contract))
        return contract_id
    
    async def save_generated_code(self, prompt_id: int, contract_id: int, files: Dict) -> int:
        """Save generated code files to the database and return its ID"""
        query = """
            INSERT INTO generated_code (prompt_id, contract_id, files)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        code_id = await self.conn.fetchval(query, prompt_id, contract_id, json.dumps(files))
        return code_id
    
    async def save_build_log(self, prompt_id: int, status: str, message: str, details: Dict = None) -> int:
        """Save a build log to the database and return its ID"""
        query = """
            INSERT INTO build_logs (prompt_id, status, message, details)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        log_id = await self.conn.fetchval(query, prompt_id, status, message, json.dumps(details) if details else None)
        return log_id
    
    async def save_prompt_lineage(self, parent_prompt_id: int, child_prompt_id: int, relationship_type: str) -> int:
        """Save a prompt lineage relationship to the database and return its ID"""
        query = """
            INSERT INTO prompt_lineage (parent_prompt_id, child_prompt_id, relationship_type)
            VALUES ($1, $2, $3)
            RETURNING id
        """
        lineage_id = await self.conn.fetchval(query, parent_prompt_id, child_prompt_id, relationship_type)
        return lineage_id
    
    async def get_prompt_by_id(self, prompt_id: int) -> Dict:
        """Get a prompt by its ID"""
        query = """
            SELECT id, title, prompt, created_at
            FROM prompts
            WHERE id = $1
        """
        row = await self.conn.fetchrow(query, prompt_id)
        if row:
            return dict(row)
        return None
    
    async def get_contract_by_prompt_id(self, prompt_id: int) -> Dict:
        """Get an API contract by prompt ID"""
        query = """
            SELECT id, prompt_id, contract, created_at
            FROM contracts
            WHERE prompt_id = $1
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await self.conn.fetchrow(query, prompt_id)
        if row:
            result = dict(row)
            result["contract"] = json.loads(result["contract"])
            return result
        return None
    
    async def get_generated_code_by_prompt_id(self, prompt_id: int) -> Dict:
        """Get generated code by prompt ID"""
        query = """
            SELECT id, prompt_id, contract_id, files, created_at
            FROM generated_code
            WHERE prompt_id = $1
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await self.conn.fetchrow(query, prompt_id)
        if row:
            result = dict(row)
            result["files"] = json.loads(result["files"])
            return result
        return None

class FallbackDBHandler:
    """Fallback file-based database handler when PostgreSQL is unavailable"""
    
    def __init__(self):
        self.base_path = "../../meta/db_fallback"
        os.makedirs(self.base_path, exist_ok=True)
    
    async def save_prompt(self, title: str, prompt: str) -> int:
        """Save a prompt to the fallback storage and return its ID"""
        file_path = f"{self.base_path}/prompts.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"records": []}
        
        # Generate a new ID
        prompt_id = len(data["records"]) + 1
        
        # Add the new prompt
        data["records"].append({
            "id": prompt_id,
            "title": title,
            "prompt": prompt,
            "created_at": datetime.now().isoformat()
        })
        
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return prompt_id
    
    async def save_contract(self, prompt_id: int, contract: Dict) -> int:
        """Save an API contract to the fallback storage and return its ID"""
        file_path = f"{self.base_path}/contracts.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"records": []}
        
        # Generate a new ID
        contract_id = len(data["records"]) + 1
        
        # Add the new contract
        data["records"].append({
            "id": contract_id,
            "prompt_id": prompt_id,
            "contract": contract,
            "created_at": datetime.now().isoformat()
        })
        
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return contract_id
    
    async def save_generated_code(self, prompt_id: int, contract_id: int, files: Dict) -> int:
        """Save generated code files to the fallback storage and return its ID"""
        file_path = f"{self.base_path}/generated_code.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"records": []}
        
        # Generate a new ID
        code_id = len(data["records"]) + 1
        
        # Add the new generated code
        data["records"].append({
            "id": code_id,
            "prompt_id": prompt_id,
            "contract_id": contract_id,
            "files": files,
            "created_at": datetime.now().isoformat()
        })
        
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return code_id
    
    async def save_build_log(self, prompt_id: int, status: str, message: str, details: Dict = None) -> int:
        """Save a build log to the fallback storage and return its ID"""
        file_path = f"{self.base_path}/build_logs.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"records": []}
        
        # Generate a new ID
        log_id = len(data["records"]) + 1
        
        # Add the new build log
        data["records"].append({
            "id": log_id,
            "prompt_id": prompt_id,
            "status": status,
            "message": message,
            "details": details,
            "created_at": datetime.now().isoformat()
        })
        
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return log_id
    
    async def save_prompt_lineage(self, parent_prompt_id: int, child_prompt_id: int, relationship_type: str) -> int:
        """Save a prompt lineage relationship to the fallback storage and return its ID"""
        file_path = f"{self.base_path}/prompt_lineage.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"records": []}
        
        # Generate a new ID
        lineage_id = len(data["records"]) + 1
        
        # Add the new lineage
        data["records"].append({
            "id": lineage_id,
            "parent_prompt_id": parent_prompt_id,
            "child_prompt_id": child_prompt_id,
            "relationship_type": relationship_type,
            "created_at": datetime.now().isoformat()
        })
        
        # Save the updated data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return lineage_id
    
    async def get_prompt_by_id(self, prompt_id: int) -> Dict:
        """Get a prompt by its ID from fallback storage"""
        file_path = f"{self.base_path}/prompts.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            for record in data["records"]:
                if record["id"] == prompt_id:
                    return record
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return None
    
    async def get_contract_by_prompt_id(self, prompt_id: int) -> Dict:
        """Get an API contract by prompt ID from fallback storage"""
        file_path = f"{self.base_path}/contracts.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Find the most recent contract for the prompt
            matching_contracts = [
                record for record in data["records"]
                if record["prompt_id"] == prompt_id
            ]
            
            if matching_contracts:
                # Sort by created_at in descending order
                matching_contracts.sort(
                    key=lambda x: x["created_at"],
                    reverse=True
                )
                return matching_contracts[0]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return None
    
    async def get_generated_code_by_prompt_id(self, prompt_id: int) -> Dict:
        """Get generated code by prompt ID from fallback storage"""
        file_path = f"{self.base_path}/generated_code.json"
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Find the most recent generated code for the prompt
            matching_code = [
                record for record in data["records"]
                if record["prompt_id"] == prompt_id
            ]
            
            if matching_code:
                # Sort by created_at in descending order
                matching_code.sort(
                    key=lambda x: x["created_at"],
                    reverse=True
                )
                return matching_code[0]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        return None

async def test_db_connection():
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1")
            return result == 1
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False


