"""
Project Manager - Cross-Layer Project Persistence
Manages project state across Layer 1 (Build) and Layer 2 (Debug)
Enhanced with comprehensive project lifecycle management
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ProjectStatus(Enum):
    PLANNING = "planning"
    BUILDING = "building"
    DEBUGGING = "debugging"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    MAINTENANCE = "maintenance"

@dataclass
class ProjectMetadata:
    project_id: str
    project_name: str
    description: str
    founder_id: str
    status: ProjectStatus
    created_at: datetime
    last_modified: datetime

@dataclass
class ProjectState:
    layer_1_data: Optional[Dict]  # Build data
    layer_2_data: Optional[Dict]  # Debug data
    github_integration: Optional[Dict]
    deployment_info: Optional[Dict]
    smart_contract_info: Optional[Dict]

class ProjectManager:
    """Comprehensive project lifecycle management"""
    
    def __init__(self, database_manager):
        self.db = database_manager
        self.active_projects: Dict[str, ProjectMetadata] = {}
        self.project_states: Dict[str, ProjectState] = {}
        
    async def create_project(self, 
                           project_name: str,
                           description: str,
                           founder_id: str) -> ProjectMetadata:
        """Create new project"""
        
        project_id = str(uuid.uuid4())
        
        metadata = ProjectMetadata(
            project_id=project_id,
            project_name=project_name,
            description=description,
            founder_id=founder_id,
            status=ProjectStatus.PLANNING,
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        
        state = ProjectState(
            layer_1_data=None,
            layer_2_data=None,
            github_integration=None,
            deployment_info=None,
            smart_contract_info=None
        )
        
        # Store in database
        await self._persist_project(metadata, state)
        
        self.active_projects[project_id] = metadata
        self.project_states[project_id] = state
        
        return metadata
    
    async def _persist_project(self, metadata: ProjectMetadata, state: ProjectState):
        """Persist project to database"""
        
        async with self.db.get_connection() as conn:
            await conn.execute("""
                INSERT INTO projects (
                    id, project_name, description, founder_id, status,
                    layer_1_data, layer_2_data, github_integration,
                    deployment_info, smart_contract_info, created_at, last_modified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
            metadata.project_id, metadata.project_name, metadata.description,
            metadata.founder_id, metadata.status.value,
            json.dumps(state.layer_1_data), json.dumps(state.layer_2_data),
            json.dumps(state.github_integration), json.dumps(state.deployment_info),
            json.dumps(state.smart_contract_info), metadata.created_at, metadata.last_modified)