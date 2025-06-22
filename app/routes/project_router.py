"""
Project Management API Router
Cross-layer project lifecycle management
Enhanced project persistence and state management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.database.db import get_db
from app.database.models import *
from app.utils.project_manager import ProjectManager, ProjectMetadata, ProjectState, ProjectStatus
from app.utils.logger import get_logger
from app.utils.auth_utils import get_current_user, get_optional_current_user
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["Project Management"])
logger = get_logger("project_management_api")

# Initialize project manager
project_manager = None  # Will be initialized with database

@router.post("/create", response_model=ProjectCreateResponse)
async def create_new_project(
    request: CreateProjectRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Create new AI Debugger Factory project
    Initialize project lifecycle management
    """
    
    try:
        # Initialize project manager if needed
        global project_manager
        if not project_manager:
            project_manager = ProjectManager(database_manager=None)
        
        # Create project metadata
        project_metadata = await project_manager.create_project(
            project_name=request.project_name,
            description=request.description,
            founder_id=current_user.id
        )
        
        # Create project in database
        db_project = Project(
            id=project_metadata.project_id,
            project_name=project_metadata.project_name,
            user_id=current_user.id,
            technology_stack=request.technology_stack or ["FastAPI", "React", "PostgreSQL"],
            status=project_metadata.status.value
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        logger.log_structured("info", "New project created", {
            "project_id": project_metadata.project_id,
            "user_id": current_user.id,
            "project_name": project_metadata.project_name
        })
        
        return ProjectCreateResponse(
            project_id=project_metadata.project_id,
            project_name=project_metadata.project_name,
            description=project_metadata.description,
            status=project_metadata.status.value,
            created_at=project_metadata.created_at.isoformat(),
            next_steps=["Start AI cofounder conversation", "Define business requirements", "Begin Layer 1 Build"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Project creation failed", {
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/", response_model=List[ProjectSummaryResponse])
async def get_user_projects(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get all projects for current user with optional filtering"""
    
    query = db.query(Project).filter(Project.user_id == (current_user.get("id") if current_user else "demo_user"))
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()
    
    project_summaries = []
    for project in projects:
        # Get latest conversation session
        latest_conversation = db.query(VoiceConversation).filter(
            VoiceConversation.user_id == current_user.id
        ).order_by(VoiceConversation.created_at.desc()).first()
        
        # Get latest dream session
        latest_dream = db.query(DreamSession).filter(
            DreamSession.project_id == project.id
        ).order_by(DreamSession.created_at.desc()).first()
        
        # Get latest debug session  
        latest_debug = db.query(DebugSessionModel).filter(
            DebugSessionModel.project_id == project.id
        ).order_by(DebugSessionModel.created_at.desc()).first()
        
        project_summaries.append(ProjectSummaryResponse(
            project_id=project.id,
            project_name=project.project_name,
            status=project.status,
            technology_stack=project.technology_stack,
            created_at=project.created_at.isoformat(),
            last_modified=project.updated_at.isoformat() if project.updated_at else project.created_at.isoformat(),
            has_conversation=bool(latest_conversation),
            has_generated_code=bool(latest_dream and latest_dream.generated_files),
            has_github_repo=bool(project.github_repo_url),
            has_debug_session=bool(latest_debug),
            completion_percentage=_calculate_completion_percentage(project, latest_conversation, latest_dream, latest_debug)
        ))
    
    return project_summaries

def _calculate_completion_percentage(project, conversation, dream, debug) -> int:
    """Calculate project completion percentage"""
    completion = 0
    
    if conversation:
        completion += 25  # Conversation started
    if project.founder_ai_agreement:
        completion += 25  # Agreement created
    if dream and dream.generated_files:
        completion += 25  # Code generated
    if project.github_repo_url:
        completion += 15  # GitHub integration
    if debug:
        completion += 10  # Debug session started
    
    return min(completion, 100)

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_details(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get comprehensive project details and status"""
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == (current_user.get("id") if current_user else "demo_user")
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get related data
    conversation = db.query(VoiceConversation).filter(
        VoiceConversation.user_id == current_user.id,
        VoiceConversation.session_id == project.conversation_session_id
    ).first()
    
    dream_sessions = db.query(DreamSession).filter(
        DreamSession.project_id == project.id
    ).all()
    
    debug_sessions = db.query(DebugSessionModel).filter(
        DebugSessionModel.project_id == project.id
    ).all()
    
    revenue_sharing = db.query(RevenueSharing).filter(
        RevenueSharing.project_id == project.id
    ).first()
    
    return ProjectDetailResponse(
        project_id=project.id,
        project_name=project.project_name,
        description=project.project_name,  # Would store description separately
        status=project.status,
        technology_stack=project.technology_stack,
        created_at=project.created_at.isoformat(),
        founder_ai_agreement=project.founder_ai_agreement,
        conversation_history=conversation.conversation_history if conversation else [],
        github_repo_url=project.github_repo_url,
        deployment_url=project.deployment_url,
        smart_contract_address=project.smart_contract_address,
        layer_1_status="completed" if dream_sessions else "pending",
        layer_2_status="active" if debug_sessions else "pending",
        revenue_generated=revenue_sharing.revenue_tracked if revenue_sharing else 0.0,
        completion_percentage=_calculate_completion_percentage(project, conversation, dream_sessions, debug_sessions)
    )

@router.put("/{project_id}/status")
async def update_project_status(
    project_id: str,
    request: UpdateProjectStatusRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Update project status and metadata"""
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == (current_user.get("id") if current_user else "demo_user")
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project
    project.status = request.status
    if request.deployment_url:
        project.deployment_url = request.deployment_url
    if request.notes:
        # Would store notes in a separate field
        pass
    
    project.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Project status updated successfully", "new_status": request.status}
