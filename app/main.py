from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Form, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.utils.github_uploader import upload_to_github
import tempfile
import shutil

# Import local modules
from app.config import settings
from app.models.prompt import PromptRequest, PromptResponse
from app.utils.contract_generator import generate_api_contract
from app.utils.code_generator import generate_backend_code
from app.database.db import get_db, init_db
from app.utils.logger import setup_logger
from app.utils.voice_processor import process_voice_input, parse_prompt, enhance_prompt

from pydantic import BaseModel

class GitHubUploadRequest(BaseModel):
    repo: str
    token: str
    paths: str
    commit_message: str = "Initial Commit"

# Initialize FastAPI app
app = FastAPI(
    title="AI Debugger Factory",
    description="An AI-powered SaaS platform for generating, debugging, and evolving codebases",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if directory exists
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates if directory exists
templates = None
if os.path.exists("app/templates"):
    templates = Jinja2Templates(directory="app/templates")

# Set up logger
logger = setup_logger()

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    logger.info("Starting AI Debugger Factory BuildBot service")
    await init_db()
    
    # Ensure meta directory exists for prompt logs
    os.makedirs("../../meta", exist_ok=True)
    
    # Initialize prompt log if it doesn't exist
    if not os.path.exists("../../meta/prompt_log.json"):
        with open("../../meta/prompt_log.json", "w") as f:
            json.dump({"prompts": []}, f)
    
    logger.info("BuildBot service initialized successfully")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the UI"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return {
            "status": "online",
            "service": "AI Debugger Factory - BuildBot (Layer 1)",
            "version": "1.0.0"
        }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "AI Debugger Factory - BuildBot (Layer 1)"
    }

@app.post("/api/v1/build", response_model=PromptResponse)
async def build_from_prompt(
    prompt_request: PromptRequest,
    db=Depends(get_db)
):
    """
    Generate backend code from a structured product prompt
    
    This endpoint takes a structured product prompt and generates:
    - FastAPI backend code
    - Database schema
    - Environment configuration
    - API contract
    - Unit tests
    """
    logger.info(f"Received build request: {prompt_request.title}")
    
    try:
        # Generate API contract from prompt
        contract = generate_api_contract(prompt_request.prompt)
        
        # Generate backend code based on the contract
        code_result = generate_backend_code(
            prompt_request.prompt,
            contract,
            prompt_request.options
        )
        
        # Log the prompt and result
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_id": str(prompt_request.id),
            "title": prompt_request.title,
            "prompt": prompt_request.prompt,
            "contract_generated": contract["endpoints"],
            "success": True
        }
        
        # Update prompt log
        with open("../../meta/prompt_log.json", "r") as f:
            prompt_log = json.load(f)
        
        prompt_log["prompts"].append(log_entry)
        
        with open("../../meta/prompt_log.json", "w") as f:
            json.dump(prompt_log, f, indent=2)
        
        # Save contract to file
        with open("../../meta/api-contracts.json", "w") as f:
            json.dump(contract, f, indent=2)

        try:
            # Return response with generated code info
            return PromptResponse(
                id=prompt_request.id,
                title=prompt_request.title,
                status="success",
                contract=contract,
                files_generated=code_result["files_generated"],
                message="Backend code generated successfully",
                timestamp=datetime.now().isoformat()
            )
        except TypeError as e:
            # Log serialization error
            logger.error(f"Error serializing generated code: {str(e)}")

            # Create a serializable version of the response
            serializable_contract = json.loads(json.dumps(contract, default=str))

            return PromptResponse(
                id=prompt_request.id,
                title=prompt_request.title,
                status="success",
                contract=serializable_contract,
                files_generated=code_result["files_generated"],
                message="Backend code generated successfully",
                timestamp=datetime.now().isoformat()
            )

        
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        
        # Log the error
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_id": str(prompt_request.id),
            "title": prompt_request.title,
            "prompt": prompt_request.prompt,
            "error": str(e),
            "success": False
        }
        
        # Update prompt log with error
        with open("../../meta/prompt_log.json", "r") as f:
            prompt_log = json.load(f)
        
        prompt_log["prompts"].append(log_entry)
        
        with open("../../meta/prompt_log.json", "w") as f:
            json.dump(prompt_log, f, indent=2)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code: {str(e)}"
        )

@app.post("/api/v1/voice")
async def process_voice(audio_file: UploadFile = File(...), options: Optional[str] = Form(None)):
    """
    Process voice input
    
    Args:
        audio_file: Audio file with prompt (sent as form field `audio_file`)
        options: JSON string with options
        
    Returns:
        Dictionary containing processing results
    """
    try:
        # Save audio file temporarily
        temp_file_path = f"/tmp/{audio_file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
        
        # Parse options
        options_dict = {}
        if options:
            try:
                options_dict = json.loads(options)
            except json.JSONDecodeError:
                logger.warning("Invalid options JSON, using default options")
        
        # Initialize voice processor with API key from environment
        from app.utils.voice_processor import VoiceInputProcessor
        voice_processor = VoiceInputProcessor()
        
        # Process voice input using the real implementation
        processing_result = voice_processor.process_voice_input(temp_file_path)
        
        if processing_result["status"] != "success":
            logger.error(f"Voice processing failed: {processing_result.get('message', 'Unknown error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Voice processing failed: {processing_result.get('message', 'Unknown error')}"
            )
        # Use the processing result
        result = processing_result
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        # Add serialization safety net
        try:
            # Return result with real transcription and processing
            return {
                "id": str(uuid.uuid4()),
                "transcribed_text": processing_result.get("transcribed_text", ""),
                "structured_prompt": processing_result.get("structured_prompt", {}),
                "status": "success",
                "message": "Voice prompt processed successfully",
                "timestamp": datetime.now().isoformat()
            }
        except TypeError as e:
            # Log serialization error
            logger.error(f"Error serializing voice processing result: {str(e)}")
            
            # Create a serializable version of the response
            serializable_result = json.loads(json.dumps(processing_result, default=str))
            
            return {
                "id": str(uuid.uuid4()),
                "transcribed_text": serializable_result.get("transcribed_text", ""),
                "structured_prompt": serializable_result.get("structured_prompt", {}),
                "status": "success",
                "message": "Voice prompt processed successfully",
                "timestamp": datetime.now().isoformat()
            }
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        logger.error(f"Error processing voice input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing voice input: {str(e)}"
        )


@app.get("/api/v1/debug/status")
async def get_repository_status():
    """
    Get repository status
    
    Returns:
        Dictionary containing repository status
    """
    # This would be implemented with actual GitHub API calls in a real implementation
    return {
        "status": "success",
        "repository": {
            "name": "ai-debugger-factory",
            "full_name": "user/ai-debugger-factory",
            "description": "AI-powered SaaS platform for generating, debugging, and evolving codebases",
            "url": "https://github.com/user/ai-debugger-factory",
            "default_branch": "main",
            "stars": 10,
            "forks": 5,
            "open_issues": 3
        },
        "issues": {
            "count": 2,
            "items": []
        },
        "pull_requests": {
            "count": 1,
            "items": []
        },
        "workflows": {
            "count": 5,
            "items": []
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/debug/contract-drift")
async def check_contract_drift():
    """
    Check contract drift
    
    Returns:
        Dictionary containing drift information
    """
    # This would be implemented with actual contract comparison in a real implementation
    return {
        "status": "success",
        "drift_detected": False,
        "drift_details": [],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    
@app.post("/upload-to-github")
async def upload_to_github_api(
    request: Request,
    repo: str = Form(...),
    token: str = Form(...),
    paths: str = Form(...),  # Comma-separated paths
    commit_message: str = Form("Initial Commit")
):
    try:
        file_paths = [path.strip() for path in paths.split(",")]
        upload_to_github(repo, token, file_paths, commit_message)
        return {"status": "success", "message": f"Uploaded {len(file_paths)} file(s) to {repo}."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from app.utils.dream_engine import router as dream_router
app.include_router(dream_router)

with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
    temp_file_path = temp_file.name
    await audio_file.seek(0)
    shutil.copyfileobj(audio_file.file, temp_file)
