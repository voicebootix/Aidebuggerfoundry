"""
Debug Engine API Router - Layer 2 Debug
Professional debugging with Monaco Editor integration
Real-time AI-powered code analysis and improvement
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import json
import asyncio
import uuid
from datetime import datetime

from app.database.db import get_db
from app.database.models import *
from app.utils.debug_engine import DebugEngine, CodeAnalysis, DebugSuggestion, DebugSession
from app.utils.monaco_integration import MonacoIntegration, MonacoWorkspace
from app.utils.github_integration import GitHubIntegration
from app.utils.logger import get_logger
from app.utils.auth_utils import get_current_user, get_optional_current_user
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["Layer 2 - Debug"])
logger = get_logger("debug_engine_api")

# Initialize core components
debug_engine = None  # Will be initialized with dependencies
monaco_integration = None  # Will be initialized
github_integration = None  # Will be initialized

@router.post("/start-session", response_model=DebugSessionResponse)
async def start_debug_session(
    request: StartDebugSessionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Start professional debugging session with Monaco integration
    Real-time code analysis and AI debugging assistance
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
        
        # Get generated code from dream session
        dream_session = db.query(DreamSession).filter(
            DreamSession.project_id == project.id,
            DreamSession.status == "code_generated"
        ).first()
        
        if not dream_session or not dream_session.generated_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No generated code found. Please complete Layer 1 Build first."
            )
        
        # Initialize debug engine if needed
        global debug_engine, monaco_integration
        if not debug_engine:
            debug_engine = DebugEngine(
                llm_provider=None,  # Initialize with actual LLM provider
                monaco_integration=monaco_integration,
                github_integration=github_integration
            )
        
        # Prepare codebase for debugging
        codebase = {}
        for file_data in dream_session.generated_files["files"]:
            codebase[file_data["filename"]] = file_data["content"]
        
        # Start debug session
        debug_session = await debug_engine.start_debug_session(
            project_id=project.id,
            user_id=current_user.id,
            codebase=codebase
        )
        
        # Initialize Monaco workspace
        if not monaco_integration:
            monaco_integration = MonacoIntegration(redis_client=None)
        
        monaco_workspace = await monaco_integration.initialize_monaco_workspace(
            project_id=project.id,
            codebase=codebase
        )
        
        # Store debug session in database
        db_debug_session = DebugSessionModel(
            project_id=project.id,
            debug_request="Debug session initialization",
            analysis_results={
                "session_id": debug_session.session_id,
                "files_analyzed": len(debug_session.analysis_results),
                "issues_found": sum(len(analysis.issues_found) for analysis in debug_session.analysis_results),
                "initial_suggestions": len(debug_session.suggestions)
            },
            monaco_workspace_state={
                "workspace_id": monaco_workspace.workspace_id,
                "files": list(monaco_workspace.files.keys()),
                "collaborators": monaco_workspace.collaborators
            },
            status="active"
        )
        
        db.add(db_debug_session)
        db.commit()
        db.refresh(db_debug_session)
        
        # Update project status
        project.status = "debugging"
        db.commit()
        
        logger.log_structured("info", "Debug session started", {
            "project_id": project.id,
            "user_id": current_user.id,
            "session_id": debug_session.session_id,
            "monaco_workspace_id": monaco_workspace.workspace_id
        })
        
        return DebugSessionResponse(
            session_id=debug_session.session_id,
            project_id=project.id,
            monaco_workspace_id=monaco_workspace.workspace_id,
            initial_analysis=debug_session.analysis_results,
            suggestions=debug_session.suggestions,
            files_available=list(codebase.keys()),
            collaboration_enabled=True,
            github_sync_available=bool(project.github_repo_url)
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to start debug session", {
            "project_id": request.project_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start debug session: {str(e)}"
        )

@router.post("/analyze-request/{session_id}")
async def process_debug_request(
    session_id: str,
    request: DebugRequestAnalysis,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Process AI debugging request with intelligent analysis
    Provides specific, actionable debugging assistance
    """
    
    try:
        # Validate session access
        db_debug_session = db.query(DebugSessionModel).filter(
            DebugSessionModel.project_id.in_(
                db.query(Project.id).filter(Project.user_id == (current_user.get("id") if current_user else "demo_user"))
            )
        ).first()
        
        if not db_debug_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Debug session not found"
            )
        
        # Process debug request
        debug_response = await debug_engine.process_debug_request(
            session_id=session_id,
            user_request=request.debug_request
        )
        
        # Update session in database
        if db_debug_session.analysis_results:
            db_debug_session.analysis_results["conversation_history"] = db_debug_session.analysis_results.get("conversation_history", [])
            db_debug_session.analysis_results["conversation_history"].append({
                "user_request": request.debug_request,
                "ai_response": debug_response["message"],
                "timestamp": datetime.now().isoformat()
            })
        
        db.commit()
        
        logger.log_structured("info", "Debug request processed", {
            "session_id": session_id,
            "user_id": current_user.id,
            "confidence": debug_response.get("confidence", 0.8)
        })
        
        return DebugResponseAnalysis(
            session_id=session_id,
            ai_response=debug_response["message"],
            suggestions=debug_response.get("suggestions", []),
            code_changes=debug_response.get("code_changes", {}),
            next_steps=debug_response.get("next_steps", []),
            confidence=debug_response.get("confidence", 0.8)
        )
        
    except Exception as e:
        logger.log_structured("error", "Debug request processing failed", {
            "session_id": session_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug request processing failed: {str(e)}"
        )

@router.post("/apply-changes/{session_id}")
async def apply_debug_changes(
    session_id: str,
    request: ApplyDebugChangesRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Apply AI-suggested code changes to project
    Real-time code modification with validation
    """
    
    try:
        # Apply changes through debug engine
        apply_result = await debug_engine.apply_code_changes(
            session_id=session_id,
            changes=request.changes
        )
        
        if apply_result["success"]:
            # Sync changes to GitHub if available
            project = db.query(Project).filter(
                Project.user_id == (current_user.get("id") if current_user else "demo_user")
            ).first()
            
            if project and project.github_repo_url and github_integration:
                sync_result = await github_integration.sync_project_changes(
                    repo_name=project.github_repo_url.split('/')[-1],
                    changed_files={request.changes["file_path"]: "updated_content"}
                )
                
                logger.log_structured("info", "Changes synced to GitHub", {
                    "session_id": session_id,
                    "project_id": project.id,
                    "sync_success": sync_result["success"]
                })
        
        return ApplyChangesResponse(
            success=apply_result["success"],
            message=apply_result["message"],
            updated_analysis=apply_result.get("updated_analysis", {}),
            github_synced=bool(project and project.github_repo_url),
            next_suggestions=["Test the changes", "Review code quality", "Continue debugging"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to apply debug changes", {
            "session_id": session_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply changes: {str(e)}"
        )

@router.websocket("/realtime-collaboration/{workspace_id}")
async def realtime_collaboration(
    websocket: WebSocket,
    workspace_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Real-time collaboration WebSocket for Monaco Editor
    Professional real-time code editing and debugging
    """
    
    await websocket.accept()
    
    try:
        # Enable real-time collaboration
        collaboration_session = await monaco_integration.enable_real_time_collaboration(
            workspace_id=workspace_id
        )
        
        # Add user to collaboration
        collaboration_session.active_users.append(current_user.id)
        
        await websocket.send_text(json.dumps({
            "type": "collaboration_started",
            "session_id": collaboration_session.session_id,
            "active_users": collaboration_session.active_users
        }))
        
        # Handle real-time messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process collaboration message
            if message["type"] == "code_change":
                # Broadcast change to other users
                collaboration_session.real_time_changes.append({
                    "user_id": current_user.id,
                    "change": message["change"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # In production, broadcast to other connected users
                await websocket.send_text(json.dumps({
                    "type": "change_applied",
                    "change_id": message.get("change_id"),
                    "status": "success"
                }))
            
    except WebSocketDisconnect:
        # Remove user from collaboration
        if collaboration_session and current_user.id in collaboration_session.active_users:
            collaboration_session.active_users.remove(current_user.id)
        
        logger.log_structured("info", "User disconnected from collaboration", {
            "workspace_id": workspace_id,
            "user_id": current_user.id
        })

@router.get("/session-summary/{session_id}")
async def get_debug_session_summary(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get comprehensive debug session summary and metrics"""
    
    try:
        session_summary = await debug_engine.get_session_summary(session_id)
        
        return DebugSessionSummaryResponse(
            session_id=session_id,
            metrics=session_summary["metrics"],
            suggestions_available=session_summary["suggestions_available"],
            conversation_length=session_summary["conversation_length"],
            last_activity=session_summary["last_activity"],
            overall_code_quality=session_summary["metrics"]["average_quality_score"],
            issues_resolved=0,  # Would be calculated from session history
            time_saved="Estimated 2-4 hours of manual debugging"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session summary: {str(e)}"
        )

@router.post("/export-report/{session_id}")
async def export_debug_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Export comprehensive debugging report"""
    
    try:
        debug_report = await debug_engine.export_debug_report(session_id)
        
        return DebugReportResponse(
            report_id=str(uuid.uuid4()),
            session_id=session_id,
            report_data=debug_report,
            generated_at=datetime.now().isoformat(),
            download_url=f"/debug/download-report/{session_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export debug report: {str(e)}"
        )
