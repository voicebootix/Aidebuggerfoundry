"""
GitHub Integration API Router
Complete GitHub workflow integration endpoints
Seamless Layer 1 → GitHub → Layer 2 workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from app.utils.auth_utils import get_current_user, get_optional_current_user

from app.database.db import get_db
from app.database.models import *
from app.utils.github_integration import GitHubIntegration, GitHubRepository, GitHubDeployment
from app.utils.logger import get_logger
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["GitHub Integration"])
logger = get_logger("github_integration_api")

# Initialize GitHub integration
github_integration = None  # Will be initialized with token

@router.post("/create-repository", response_model=GitHubRepositoryResponse)
async def create_github_repository(
    request: CreateGitHubRepositoryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Create new GitHub repository for project
    Seamless repository creation with proper initialization
    """
    
    try:
        # Validate project access
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == (current_user.get("id") if current_user else "demo_user")
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Initialize GitHub integration if needed
        global github_integration
        if not github_integration:
            github_integration = GitHubIntegration(github_token=request.github_token)
        
        # Create repository
        github_repo = await github_integration.create_repository(
            repo_name=request.repository_name,
            description=f"AI-generated application: {project.project_name}",
            private=request.private
        )
        
        # Update project with GitHub info
        project.github_repo_url = github_repo.repo_url
        db.commit()
        
        logger.log_structured("info", "GitHub repository created", {
            "project_id": project.id,
            "user_id": current_user.id,
            "repo_url": github_repo.repo_url
        })
        
        return GitHubRepositoryResponse(
            repository_name=github_repo.repo_name,
            repository_url=github_repo.repo_url,
            clone_url=github_repo.clone_url,
            default_branch=github_repo.default_branch,
            private=github_repo.private,
            ready_for_upload=True
        )
        
    except Exception as e:
        logger.log_structured("error", "GitHub repository creation failed", {
            "project_id": request.project_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create GitHub repository: {str(e)}"
        )

@router.post("/upload-code/{project_id}")
async def upload_generated_code_to_github(
    project_id: str,
    request: UploadCodeToGitHubRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Upload AI-generated code to GitHub repository
    Complete project upload with all generated files
    """
    
    try:
        # Validate project and GitHub repo
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == (current_user.get("id") if current_user else "demo_user")
        ).first()
        
        if not project or not project.github_repo_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project not found or GitHub repository not configured"
            )
        
        # Get generated code
        dream_session = db.query(DreamSession).filter(
            DreamSession.project_id == project.id,
            DreamSession.status == "code_generated"
        ).first()
        
        if not dream_session or not dream_session.generated_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No generated code found for upload"
            )
        
        # Upload to GitHub
        repo_name = project.github_repo_url.split('/')[-1].replace('.git', '')
        
        upload_result = await github_integration.upload_generated_code(
            repo_name=repo_name,
            generated_files=dream_session.generated_files["files"],
            commit_message=request.commit_message or "Initial AI-generated application"
        )
        
        if upload_result["success"]:
            # Update project status
            project.status = "uploaded_to_github"
            db.commit()
            
            logger.log_structured("info", "Code uploaded to GitHub", {
                "project_id": project.id,
                "user_id": current_user.id,
                "files_uploaded": upload_result["files_uploaded"],
                "repo_url": upload_result["repository_url"]
            })
        
        return GitHubUploadResponse(
            success=upload_result["success"],
            repository_url=upload_result.get("repository_url"),
            files_uploaded=upload_result["files_uploaded"],
            upload_results=upload_result.get("upload_results", []),
            commit_message=request.commit_message or "Initial AI-generated application",
            ready_for_layer2_debug=True
        )
        
    except Exception as e:
        logger.log_structured("error", "GitHub upload failed", {
            "project_id": project_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload code to GitHub: {str(e)}"
        )

@router.post("/sync-debug-changes/{project_id}")
async def sync_debug_changes_to_github(
    project_id: str,
    request: SyncDebugChangesRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Sync Layer 2 debug changes back to GitHub
    Real-time synchronization of debugging improvements
    """
    
    try:
        # Validate project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == (current_user.get("id") if current_user else "demo_user")
        ).first()
        
        if not project or not project.github_repo_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project or GitHub repository not found"
            )
        
        # Sync changes
        repo_name = project.github_repo_url.split('/')[-1].replace('.git', '')
        
        sync_result = await github_integration.sync_project_changes(
            repo_name=repo_name,
            changed_files=request.changed_files
        )
        
        logger.log_structured("info", "Debug changes synced to GitHub", {
            "project_id": project.id,
            "user_id": current_user.id,
            "files_synced": sync_result.get("synced_files", 0)
        })
        
        return GitHubSyncResponse(
            success=sync_result["success"],
            synced_files=sync_result.get("synced_files", 0),
            sync_results=sync_result.get("sync_results", []),
            commit_message="AI Debug: Synchronized debugging improvements",
            last_sync=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.log_structured("error", "GitHub sync failed", {
            "project_id": project_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync changes to GitHub: {str(e)}"
        )

@router.get("/repository-status/{project_id}")
async def get_github_repository_status(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get GitHub repository status and recent activity"""
    
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == (current_user.get("id") if current_user else "demo_user")
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return GitHubRepositoryStatusResponse(
        project_id=project.id,
        repository_url=project.github_repo_url,
        has_repository=bool(project.github_repo_url),
        last_upload=None,  # Would be tracked in database
        files_in_repo=0,   # Would be fetched from GitHub API
        recent_commits=[],  # Would be fetched from GitHub API
        sync_status="up_to_date"
    )
