from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional
import json
import asyncio
import uuid

from app.utils.debug_engine import DebugEngine, DebugRequest, DebugResponse
from app.utils.project_memory import ProjectMemoryManager
from app.utils.logger import setup_logger
from app.database.db import get_db
from typing import Dict, List, Any, Optional

logger = setup_logger()
router = APIRouter(prefix="/api/v1/debug", tags=["debug"])

# Initialize debug engine
debug_engine = DebugEngine()

@router.on_event("startup")
async def startup_debug():
    """Initialize debug system"""
    await debug_engine.memory_manager.init_db()
    logger.info("✅ DebugBot Layer 2 initialized")

@router.post("/session/start")
async def start_debug_session(
    project_id: str,
    user_id: str = "anonymous"
):
    """Start a new debugging session"""
    try:
        session_id = await debug_engine.start_debug_session(project_id, user_id)
        return {
            "status": "session_started",
            "session_id": session_id,
            "message": "Debug session initialized"
        }
    except Exception as e:
        logger.error(f"❌ Failed to start session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=DebugResponse)
async def analyze_code_issue(request: DebugRequest):
    """Main debugging analysis endpoint"""
    try:
        response = await debug_engine.process_debug_request(request)
        return response
    except Exception as e:
        logger.error(f"❌ Debug analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_debug_analysis(request: DebugRequest):
    """Streaming debug analysis"""
    
    async def debug_stream():
        try:
            yield f"data: {json.dumps({'type': 'status', 'content': 'Analyzing code...', 'progress': 10})}\n\n"
            
            # Start analysis
            response = await debug_engine.process_debug_request(request)
            
            # Stream analysis results
            yield f"data: {json.dumps({'type': 'analysis', 'content': response.analysis, 'progress': 50})}\n\n"
            await asyncio.sleep(0.5)
            
            # Stream suggested changes
            for i, change in enumerate(response.suggested_changes):
                progress = 60 + (i / len(response.suggested_changes)) * 30
                yield f"data: {json.dumps({'type': 'change_suggestion', 'content': change, 'progress': progress})}\n\n"
                await asyncio.sleep(0.2)
            
            # Stream explanation
            yield f"data: {json.dumps({'type': 'explanation', 'content': response.explanation, 'progress': 95})}\n\n"
            await asyncio.sleep(0.3)
            
            # Complete
            yield f"data: {json.dumps({'type': 'complete', 'response': response.dict(), 'progress': 100})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        debug_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.post("/apply-changes")
async def apply_suggested_changes(
    session_id: str,
    change_ids: List[str]
):
    """Apply approved changes to codebase"""
    try:
        result = await debug_engine.apply_suggested_changes(session_id, change_ids)
        return result
    except Exception as e:
        logger.error(f"❌ Failed to apply changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memory/{project_id}")
async def get_project_memory(project_id: str):
    """Get project memory and conversation history"""
    try:
        memory = await debug_engine.memory_manager.load_project(project_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Project not found")
        return memory
    except Exception as e:
        logger.error(f"❌ Failed to get memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def debug_health_check():
    """Debug system health check"""
    return {
        "status": "healthy",
        "service": "DebugBot Layer 2",
        "version": "2.0.0",
        "features": [
            "Code Analysis",
            "Bug Detection", 
            "Feature Integration",
            "Project Memory",
            "Precision Updates",
            "Conversation AI"
        ]
    }
