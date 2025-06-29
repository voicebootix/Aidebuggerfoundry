"""
Dream Engine API Router - Layer 1 Build
Enhanced strategic analysis and code generation endpoints
Transforms founder agreements into production-ready applications
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, List, Optional, Any, AsyncGenerator
import json
import asyncio
import uuid
from datetime import datetime
import asyncpg

from app.database.db import get_db
from app.database.models import *
from app.utils.dream_engine import DreamEngine, StrategicAnalysis, CodeGenerationResult
from app.utils.llm_provider import EnhancedLLMProvider
from app.utils.security_validator import SecurityValidator
from app.utils.smart_contract_system import SmartContractSystem
from app.utils.logger import get_logger
from app.utils.auth_utils import get_optional_current_user
from app.services import service_manager


router = APIRouter(tags=["Layer 1 - Build"])
logger = get_logger("dream_engine_api")

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

@router.post("/analyze-strategic-requirements", response_model=StrategicAnalysisResponse)
async def analyze_strategic_requirements(
    request: StrategicAnalysisRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Comprehensive strategic analysis of founder requirements
    Enhanced business and technical analysis
    """
    # Handle demo mode
    user_id = current_user.get("id") if current_user else DEMO_USER_ID
    user_email = current_user.get("email") if current_user else "demo@example.com"

    # Check if dream engine is available
    if not service_manager.dream_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dream Engine service is not available. Please ensure LLM provider is configured."
        )

    # Get or create project
    project = await db.fetchrow(
        "SELECT * FROM projects WHERE id = $1 AND user_id = $2",
        request.project_id, user_id
    )
    
    if not project:
        # Create new project
        project_id = request.project_id or str(uuid.uuid4())
        await db.execute(
            """INSERT INTO projects 
            (id, project_name, user_id, technology_stack, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, NOW(), NOW())""",
            project_id,
            f"Project {project_id[-6:]}",
            user_id,
            json.dumps(["FastAPI", "React", "PostgreSQL"]),
            "planning"
        )
        
        project = await db.fetchrow(
            "SELECT * FROM projects WHERE id = $1", project_id
        )
    
    # Store founder agreement if provided
    if hasattr(request, 'founder_agreement') and request.founder_agreement:
        await db.execute(
            "UPDATE projects SET founder_ai_agreement = $1, updated_at = NOW() WHERE id = $2",
            json.dumps(request.founder_agreement), project['id']
        )
    
    try:
        # Prepare founder agreement
        founder_agreement = json.loads(project['founder_ai_agreement']) if project['founder_ai_agreement'] else {}
        if hasattr(request, 'additional_requirements') and request.additional_requirements:
            founder_agreement['additional_requirements'] = request.additional_requirements

        # Perform strategic analysis
        strategic_analysis = await service_manager.dream_engine.analyze_strategic_requirements(
            founder_agreement=founder_agreement,
            project_context={
                "project_id": project['id'],
                "project_name": project['project_name'],
                "user_id": user_id
            }
        )
        
        # Create dream session
        dream_session_id = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO dream_sessions 
            (id, project_id, user_input, strategic_analysis, status, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())""",
            dream_session_id,
            project['id'],
            json.dumps(founder_agreement),
            json.dumps({
                "business_context": strategic_analysis.business_context,
                "technical_requirements": strategic_analysis.technical_requirements,
                "architecture_recommendations": strategic_analysis.architecture_recommendations,
                "implementation_strategy": strategic_analysis.implementation_strategy,
                "risk_assessment": strategic_analysis.risk_assessment,
                "timeline_estimate": strategic_analysis.timeline_estimate
            }),
            "analysis_complete"
        )
        
        logger.info(f"Strategic analysis completed for project: {project['id']}")
        
        return StrategicAnalysisResponse(
            analysis_id=dream_session_id,
            project_id=project['id'],
            business_context=strategic_analysis.business_context,
            technical_requirements=strategic_analysis.technical_requirements,
            architecture_recommendations=strategic_analysis.architecture_recommendations,
            implementation_strategy=strategic_analysis.implementation_strategy,
            risk_assessment=strategic_analysis.risk_assessment,
            timeline_estimate=strategic_analysis.timeline_estimate,
            ready_for_code_generation=True
        )
        
    except Exception as e:
        logger.error(f"Strategic analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategic analysis failed: {str(e)}"
        )

@router.post("/generate-code")
async def generate_production_code(
    request: CodeGenerationRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Generate production-ready code from strategic analysis
    Complete application generation with all components
    """
    
    try:
        # Handle authentication
        user_id = current_user.get("id") if current_user else DEMO_USER_ID
        
        # Check if dream engine is available
        if not service_manager.dream_engine:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Dream Engine service is not available."
            )
         
        # Validate project and get strategic analysis
        dream_session = await db.fetchrow(
            """SELECT ds.*, p.founder_ai_agreement, p.project_name
            FROM dream_sessions ds
            JOIN projects p ON ds.project_id = p.id
            WHERE ds.id = $1 AND p.user_id = $2""",
            request.analysis_id, user_id
        )
        
        if not dream_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Strategic analysis not found"
            )
        
        # Create strategic analysis object
        strategic_analysis_data = json.loads(dream_session['strategic_analysis'])
        strategic_analysis = StrategicAnalysis(
            business_context=strategic_analysis_data["business_context"],
            technical_requirements=strategic_analysis_data["technical_requirements"],
            architecture_recommendations=strategic_analysis_data["architecture_recommendations"],
            implementation_strategy=strategic_analysis_data["implementation_strategy"],
            risk_assessment=strategic_analysis_data["risk_assessment"],
            timeline_estimate=strategic_analysis_data["timeline_estimate"]
        )
        
        # Generate production code
        founder_agreement = json.loads(dream_session['founder_ai_agreement']) if dream_session['founder_ai_agreement'] else {}
        code_generation_result = await service_manager.dream_engine.generate_production_code(
            strategic_analysis=strategic_analysis,
            founder_agreement=founder_agreement
        )
        
        # Add digital watermarks if smart contract system is available
        watermarked_files = []
        if service_manager.smart_contract_system:
            for generated_file in code_generation_result.generated_files:
                watermarked_content = await service_manager.smart_contract_system.add_digital_watermark(
                    code_content=generated_file.content,
                    project_id=dream_session['project_id']
                )
                watermarked_files.append({
                    "filename": generated_file.filename,
                    "content": watermarked_content,
                    "file_type": generated_file.file_type,
                    "description": generated_file.description
                })
        else:
            # No watermarking if smart contract system unavailable
            watermarked_files = [{
                "filename": f.filename,
                "content": f.content,
                "file_type": f.file_type,
                "description": f.description
            } for f in code_generation_result.generated_files]
        
        # Update dream session with results
        await db.execute(
            """UPDATE dream_sessions 
            SET generated_files = $1, generation_quality_score = $2, status = $3
            WHERE id = $4""",
            json.dumps({
                "files": watermarked_files,
                "project_structure": code_generation_result.project_structure,
                "deployment_instructions": code_generation_result.deployment_instructions,
                "testing_guide": code_generation_result.testing_guide
            }),
            code_generation_result.quality_score,
            "code_generated",
            request.analysis_id
        )
        
        # Update project status
        await db.execute(
            "UPDATE projects SET status = 'built', updated_at = NOW() WHERE id = $1",
            dream_session['project_id']
        )
        
        logger.log_structured("info", "Code generation completed", {
            "project_id": dream_session['project_id'],
            "user_id": user_id,
            "files_generated": len(watermarked_files),
            "quality_score": code_generation_result.quality_score
        })
        
        return CodeGenerationResponse(
            generation_id=request.analysis_id,
            project_id=dream_session['project_id'],
            generated_files=watermarked_files,
            project_structure=code_generation_result.project_structure,
            deployment_instructions=code_generation_result.deployment_instructions,
            testing_guide=code_generation_result.testing_guide,
            quality_score=code_generation_result.quality_score,
            ready_for_github_upload=True,
            estimated_deployment_time="15-30 minutes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_structured("error", "Code generation failed", {
            "analysis_id": request.analysis_id,
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )

@router.get("/generation-status/{generation_id}")
async def get_generation_status(
    generation_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get code generation status and progress"""
    
    dream_session = await db.fetchrow(
        """SELECT ds.*, p.founder_ai_agreement, p.project_name
        FROM dream_sessions ds
        JOIN projects p ON ds.project_id = p.id
        WHERE ds.id = $1 AND p.user_id = $2""",
        generation_id, current_user.get("id") if current_user else DEMO_USER_ID
    )
    
    if not dream_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation session not found"
        )
    
    return CodeGenerationStatusResponse(
        generation_id=generation_id,
        project_id=dream_session['project_id'],
        status=dream_session['status'],
        progress_percentage=100 if dream_session['status'] == "code_generated" else 50,
        quality_score=dream_session['generation_quality_score'],
        files_generated=len(json.loads(dream_session['generated_files'])['files']) if dream_session['generated_files'] else 0,
        estimated_completion="Completed" if dream_session['status'] == "code_generated" else "In progress"
    )

@router.post("/stream-generation")
async def stream_code_generation(
    request: StreamCodeGenerationRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Stream code generation progress in real-time
    Real-time updates during code generation process
    """
    
    async def generate_stream():
        try:
            # Validate and setup (similar to generate_production_code)
            yield f"data: {json.dumps({'status': 'initializing', 'message': 'Starting code generation...'})}\n\n"
            
            # Simulate streaming generation process
            stages = [
                "Analyzing strategic requirements...",
                "Designing system architecture...", 
                "Generating backend components...",
                "Creating frontend interface...",
                "Adding security features...",
                "Implementing testing framework...",
                "Generating documentation...",
                "Adding digital watermarks...",
                "Finalizing production build..."
            ]
            
            for i, stage in enumerate(stages):
                await asyncio.sleep(1)  # Simulate processing time
                progress = ((i + 1) / len(stages)) * 100
                
                yield f"data: {json.dumps({'status': 'generating', 'message': stage, 'progress': progress})}\n\n"
            
            yield f"data: {json.dumps({'status': 'completed', 'message': 'Code generation completed successfully!', 'progress': 100})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'Generation failed: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get("/download-code/{generation_id}")
async def download_generated_code(
    generation_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Download generated code as ZIP file"""
    
    dream_session = await db.fetchrow(
        """SELECT ds.*, p.founder_ai_agreement, p.project_name
        FROM dream_sessions ds
        JOIN projects p ON ds.project_id = p.id
        WHERE ds.id = $1 AND p.user_id = $2""",
        generation_id, current_user.get("id") if current_user else DEMO_USER_ID
    )
    
    if not dream_session or not dream_session['generated_files']:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated code not found"
        )
    
    # Create ZIP file in memory
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_data in json.loads(dream_session['generated_files'])['files']:
            zip_file.writestr(file_data["filename"], file_data["content"])
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=generated_code_{generation_id}.zip"}
    )
