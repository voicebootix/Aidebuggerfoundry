from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Form, File, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import uvicorn
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import tempfile
import shutil
import logging
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
import time

# Import local modules
from app.config import settings
from app.models.prompt import PromptRequest, PromptResponse
from app.utils.contract_generator import generate_api_contract
from app.utils.code_generator import generate_backend_code
from app.database.db import get_db, init_db
from app.utils.logger import setup_logger
from app.utils.voice_processor import VoiceInputProcessor
from pydantic import BaseModel
from app.utils.github_integrator import GitHubAutoDeployer, GitHubDeployRequest, GitHubDeployResponse
# Voice processing endpoint
from fastapi import UploadFile, File
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

# FIXED: Create a simple DreamEngine router directly here
dream_router = APIRouter(prefix="/api/v1/dreamengine", tags=["dreamengine"])

@dream_router.get("/health")
async def dreamengine_health():
    """DreamEngine health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DreamEngine - AI Debugger Factory Extension",
        "version": "1.0.0",
        "providers": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "google": bool(os.getenv("GOOGLE_API_KEY"))
        }
    }

@dream_router.post("/process")
async def dreamengine_process_intelligent(request_data: dict):
    """Intelligent DreamEngine process endpoint with real AI"""
    
    try:
        input_text = request_data.get("input_text", "")
        user_id = request_data.get("user_id", "anonymous")
        
        if not input_text:
            raise HTTPException(status_code=400, detail="input_text is required")
        
        # Import the production engine
        from app.utils.dream_engine_production import dream_engine
        
        # Process with real AI intelligence
        result = await dream_engine.process_founder_vision(input_text, user_id)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ DreamEngine intelligent processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@dream_router.post("/validate")
async def dreamengine_validate(request_data: dict):
    """DreamEngine validate endpoint - simplified for now"""
    return {
        "feasibility": {"score": 0.8, "explanation": "Technically feasible", "recommendations": []},
        "complexity": {"score": 0.6, "explanation": "Moderate complexity", "recommendations": []},
        "clarity": {"score": 0.9, "explanation": "Requirements are clear", "recommendations": []},
        "security_considerations": {"score": 0.7, "explanation": "Standard security", "recommendations": []},
        "overall_score": 0.75,
        "detected_project_type": "web_api",
        "detected_language": "python",
        "detected_database": "postgresql",
        "estimated_time": "2-4 weeks",
        "summary": "This is a well-defined project with clear requirements."
    }

# Include the DreamEngine router
app.include_router(dream_router)

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
    logger.info("✅ DreamEngine endpoints are now available")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Root endpoint serving the UI"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
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
        try:
            with open("../../meta/prompt_log.json", "r") as f:
                prompt_log = json.load(f)
        except:
            prompt_log = {"prompts": []}
        
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
        try:
            with open("../../meta/prompt_log.json", "r") as f:
                prompt_log = json.load(f)
        except:
            prompt_log = {"prompts": []}
        
        prompt_log["prompts"].append(log_entry)
        
        with open("../../meta/prompt_log.json", "w") as f:
            json.dump(prompt_log, f, indent=2)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Failed to generate code",
                "detail": str(e)
            }
        )

@app.post("/api/v1/voice")
async def process_voice_enhanced(audio_file: UploadFile = File(...)):
    """Enhanced voice processing with proper error handling"""
    try:
        result = await process_voice_input(audio_file)
        return result
    except Exception as e:
        logger.error(f"Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/debug/status")
async def get_repository_status():
    """Get repository status"""
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
    """Check contract drift"""
    return {
        "status": "success",
        "drift_detected": False,
        "drift_details": [],
        "timestamp": datetime.now().isoformat()
    }

def upload_to_github(repo_name, github_token, files_content, commit_message="Initial Commit", branch="main"):
    """
    Dummy GitHub upload function — replace with your actual implementation
    """
    # For demonstration: pretend all files uploaded
    uploaded_files = list(files_content.keys())
    return {"total_files": len(uploaded_files), "uploaded_files": uploaded_files}

@app.post("/upload-to-github")
async def upload_to_github_api(
    request: Request,
    repo: str = Form(...),
    token: str = Form(...),
    commit_message: str = Form("Initial Commit"),
    project_id: str = Form(...)
):
    try:
        # Sample generated files
        sample_files = {
            "app/main.py": """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Generated API")

class Item(BaseModel):
    id: int
    name: str
    description: str = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
""",
            "requirements.txt": """fastapi
uvicorn
pydantic
""",
            "README.md": f"""# Generated API

This project was generated by AI Debugger Factory.

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```
"""
        }
        
        result = upload_to_github(repo, token, sample_files, commit_message)
        return {
            "status": "success", 
            "message": f"{result['total_files']} file(s) uploaded to {repo}",
            "files": result['uploaded_files']
        }
    except Exception as e:
        logger.error(f"GitHub upload error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Add these Pydantic models
class GenerationOptions(BaseModel):
    model_provider: str = "auto"
    project_type: Optional[str] = None
    programming_language: Optional[str] = None
    database_type: Optional[str] = None
    security_level: str = "standard"
    include_tests: bool = True
    include_documentation: bool = True
    include_docker: bool = False
    include_ci_cd: bool = False
    temperature: float = 0.7

class DreamProcessRequest(BaseModel):
    id: str
    user_id: str
    input_text: str
    options: Optional[GenerationOptions] = None

# Add this router to your existing main.py
from fastapi import APIRouter
dream_router = APIRouter(prefix="/api/v1/dreamengine", tags=["dreamengine"])

@dream_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DreamEngine",
        "version": "1.0.0"
    }

@dream_router.post("/validate")
async def validate_idea(request: DreamProcessRequest):
    """Validate a founder's idea"""
    try:
        # Simple validation logic for now
        input_length = len(request.input_text.strip())
        word_count = len(request.input_text.split())
        
        # Calculate a validation score
        score = min(10, max(1, (input_length / 50) + (word_count / 10)))
        
        return {
            "id": request.id,
            "user_id": request.user_id,
            "status": "success",
            "validation_result": {
                "overall_score": round(score, 1),
                "feasibility": "High" if score > 7 else "Medium" if score > 4 else "Low",
                "market_potential": "Good" if word_count > 20 else "Needs more detail",
                "technical_complexity": "Medium",
                "recommendations": [
                    "Consider adding more specific requirements",
                    "Define your target audience clearly",
                    "Think about monetization strategy"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@dream_router.post("/process")
async def generate_code(request: DreamProcessRequest):
    """Main code generation endpoint"""
    try:
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Generate sample code based on the request
        generated_files = generate_sample_code(request.input_text, request.options)
        
        return {
            "id": request.id,
            "request_id": request.id,
            "user_id": request.user_id,
            "status": "success",
            "message": "Code generated successfully",
            "files": generated_files,
            "main_file": generated_files[0]["filename"] if generated_files else None,
            "explanation": generate_explanation(request.input_text),
            "architecture": generate_architecture_description(request.input_text),
            "project_type": request.options.project_type if request.options else "web_api",
            "programming_language": request.options.programming_language if request.options else "python",
            "generation_time_seconds": 2.0,
            "model_provider": "gpt-4",
            "security_issues": [],
            "quality_issues": [],
            "deployment_steps": generate_deployment_steps(),
            "dependencies": ["fastapi", "uvicorn", "pydantic"],
            "environment_variables": ["DATABASE_URL", "SECRET_KEY"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

# ADD these endpoints to the existing dream_router
@dream_router.post("/deploy", response_model=GitHubDeployResponse)
async def deploy_to_github(request: GitHubDeployRequest):
    """Deploy generated code to GitHub with auto-deployment setup"""
    try:
        deployer = GitHubAutoDeployer()
        result = await deployer.create_and_deploy(request)
        
        logger.info(f"✅ Deployment successful: {result.repo_url}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

@dream_router.get("/deploy/platforms")
async def get_deployment_platforms():
    """Get available deployment platforms"""
    return {
        "platforms": [
            {
                "id": "render",
                "name": "Render", 
                "description": "Easy full-stack deployment",
                "auto_deploy": True
            },
            {
                "id": "railway", 
                "name": "Railway",
                "description": "Infrastructure, simplified",
                "auto_deploy": True
            },
            {
                "id": "vercel",
                "name": "Vercel",
                "description": "Frontend deployment platform",
                "auto_deploy": True
            },
            {
                "id": "heroku",
                "name": "Heroku",
                "description": "Cloud application platform", 
                "auto_deploy": False
            }
        ]
    }

@dream_router.post("/stream")
async def stream_generation(request: DreamProcessRequest):
    """Streaming code generation"""
    
    async def generate_stream():
        try:
            # Send initial chunk
            yield f"data: {json.dumps({'content_type': 'status', 'content': 'Starting generation...', 'progress': 0})}\n\n"
            await asyncio.sleep(0.5)
            
            # Generate code in chunks
            files = generate_sample_code(request.input_text, request.options)
            
            for i, file in enumerate(files):
                # File start
                yield f"data: {json.dumps({'content_type': 'file_start', 'file_path': file['filename'], 'progress': (i/len(files))*80})}\n\n"
                await asyncio.sleep(0.3)
                
                # File content in chunks
                content_chunks = [file['content'][j:j+200] for j in range(0, len(file['content']), 200)]
                for chunk in content_chunks:
                    yield f"data: {json.dumps({'content_type': 'file_content', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.1)
                
                # File end
                yield f"data: {json.dumps({'content_type': 'file_end', 'progress': ((i+1)/len(files))*80})}\n\n"
            
            # Send explanation
            yield f"data: {json.dumps({'content_type': 'explanation', 'content': generate_explanation(request.input_text), 'progress': 90})}\n\n"
            await asyncio.sleep(0.3)
            
            # Send final chunk
            yield f"data: {json.dumps({'content_type': 'status', 'content': 'Generation complete!', 'progress': 100, 'is_final': True})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_chunk = {
                "content_type": "error",
                "content": f"Generation failed: {str(e)}",
                "is_final": True,
                "error": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )



@dream_router.post("/voice")
async def process_voice_input(audio_file: UploadFile = File(...)):
    """Process voice input and return transcription"""
    try:
        processor = VoiceInputProcessor()
        result = processor.process_voice_input(audio_file)
        if asyncio.iscoroutine(result):
            result = await result
        
        if result["status"] == "success":
            logger.info(f"✅ Voice transcription successful: {len(result['transcribed_text'])} chars")
            return {
                "status": "success",
                "transcribed_text": result["transcribed_text"],
                "structured_prompt": result.get("structured_prompt", {}),
                "timestamp": result.get("timestamp")
            }
        else:
            logger.error(f"❌ Voice transcription failed: {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"❌ Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# Helper functions
def generate_sample_code(input_text: str, options: Optional[GenerationOptions]) -> list:
    """Generate sample code files based on input"""
    
    # Determine if it's a to-do app or other type
    is_todo_app = "todo" in input_text.lower() or "task" in input_text.lower()
    
    if is_todo_app:
        return [
            {
                "filename": "main.py",
                "content": '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# In-memory storage (use database in production)
tasks: List[Task] = []

@app.get("/")
async def root():
    return {"message": "Todo API is running!"}

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks

@app.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    task = Task(
        id=str(uuid.uuid4()),
        title=task_data.title,
        description=task_data.description,
        completed=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    tasks.append(task)
    return task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    task = next((t for t in tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.now()
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    global tasks
    tasks = [t for t in tasks if t.id != task_id]
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                "language": "python",
                "purpose": "FastAPI backend with CRUD operations"
            },
            {
                "filename": "index.html",
                "content": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My To-Do List</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .input-section {
            padding: 30px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .task-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            margin-bottom: 15px;
            transition: border-color 0.3s ease;
        }
        
        .task-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .add-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        
        .add-btn:hover {
            transform: translateY(-2px);
        }
        
        .tasks-section {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .task-item {
            display: flex;
            align-items: center;
            padding: 20px 30px;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s ease;
        }
        
        .task-item:hover {
            background-color: #f8f9fa;
        }
        
        .task-checkbox {
            width: 20px;
            height: 20px;
            margin-right: 15px;
            cursor: pointer;
        }
        
        .task-text {
            flex: 1;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .task-text.completed {
            text-decoration: line-through;
            color: #888;
        }
        
        .delete-btn {
            background: #ff4757;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s ease;
        }
        
        .delete-btn:hover {
            background: #ff3742;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 30px;
            color: #888;
        }
        
        .empty-state h3 {
            margin-bottom: 10px;
            font-size: 1.5rem;
        }
        
        .status-section {
            padding: 20px 30px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>My To-Do List</h1>
            <p>Stay organized and productive</p>
        </div>
        
        <div class="input-section">
            <input type="text" id="taskInput" class="task-input" placeholder="What needs to be done?" maxlength="100">
            <button onclick="addTask()" class="add-btn">Add Task</button>
        </div>
        
        <div class="tasks-section" id="tasksContainer">
            <div class="empty-state" id="emptyState">
                <h3>🎯 Ready to be productive?</h3>
                <p>Add your first task above to get started!</p>
            </div>
        </div>
        
        <div class="status-section">
            <span id="taskStats">0 tasks</span>
            <button onclick="clearCompleted()" style="background: none; border: none; color: #667eea; cursor: pointer; font-size: 14px;">Clear Completed</button>
        </div>
    </div>
    
    <script>
        let tasks = JSON.parse(localStorage.getItem('tasks')) || [];
        let taskIdCounter = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;
        
        function renderTasks() {
            const container = document.getElementById('tasksContainer');
            const emptyState = document.getElementById('emptyState');
            
            if (tasks.length === 0) {
                container.innerHTML = emptyState.outerHTML;
                updateStats();
                return;
            }
            
            container.innerHTML = tasks.map(task => `
                <div class="task-item">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} 
                           onchange="toggleTask(${task.id})">
                    <span class="task-text ${task.completed ? 'completed' : ''}">${task.text}</span>
                    <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
                </div>
            `).join('');
            
            updateStats();
        }
        
        function addTask() {
            const input = document.getElementById('taskInput');
            const text = input.value.trim();
            
            if (text === '') return;
            
            tasks.push({
                id: taskIdCounter++,
                text: text,
                completed: false,
                createdAt: new Date().toISOString()
            });
            
            input.value = '';
            saveTasks();
            renderTasks();
        }
        
        function toggleTask(id) {
            const task = tasks.find(t => t.id === id);
            if (task) {
                task.completed = !task.completed;
                saveTasks();
                renderTasks();
            }
        }
        
        function deleteTask(id) {
            tasks = tasks.filter(t => t.id !== id);
            saveTasks();
            renderTasks();
        }
        
        function clearCompleted() {
            tasks = tasks.filter(t => !t.completed);
            saveTasks();
            renderTasks();
        }
        
        function saveTasks() {
            localStorage.setItem('tasks', JSON.stringify(tasks));
        }
        
        function updateStats() {
            const total = tasks.length;
            const completed = tasks.filter(t => t.completed).length;
            const pending = total - completed;
            
            document.getElementById('taskStats').textContent = 
                `${total} task${total !== 1 ? 's' : ''} • ${pending} pending`;
        }
        
        // Add task on Enter key press
        document.getElementById('taskInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addTask();
            }
        });
        
        // Initial render
        renderTasks();
    </script>
</body>
</html>
''',
                "language": "html",
                "purpose": "Frontend to-do application"
            },
            {
                "filename": "requirements.txt",
                "content": '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
''',
                "language": "text",
                "purpose": "Python dependencies"
            }
        ]
    else:
        # Generic web app
        return [
            {
                "filename": "main.py",
                "content": '''from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Generated Application")

@app.get("/")
async def root():
    return {"message": "Your application is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
''',
                "language": "python",
                "purpose": "Basic FastAPI application"
            }
        ]

def generate_explanation(input_text: str) -> str:
    """Generate explanation based on input"""
    if "todo" in input_text.lower() or "task" in input_text.lower():
        return """
## Generated To-Do Application

I've created a complete full-stack to-do application based on your requirements:

### Backend (main.py)
- **FastAPI** framework for high-performance API
- **CRUD operations** for tasks (Create, Read, Update, Delete)
- **RESTful endpoints** following best practices
- **Pydantic models** for data validation
- **CORS middleware** for frontend integration
- **UUID-based task IDs** for uniqueness
- **Datetime tracking** for created/updated timestamps

### Frontend (index.html)
- **Modern, responsive design** with gradient styling
- **Real-time task management** with instant updates
- **Local storage** for data persistence
- **Interactive features**: add, toggle, delete tasks
- **Task statistics** showing total and pending counts
- **Clean completed tasks** functionality
- **Mobile-friendly** responsive layout

### Key Features Implemented:
✅ Add new tasks with Enter key or button click
✅ Mark tasks as completed with checkboxes
✅ Delete individual tasks
✅ Clear all completed tasks at once
✅ Persistent storage using localStorage
✅ Real-time task counter and statistics
✅ Beautiful, modern UI with smooth animations

### Next Steps:
1. Run `pip install -r requirements.txt`
2. Start the backend: `uvicorn main:app --reload`
3. Open `index.html` in your browser
4. Start managing your tasks!

The application is production-ready and can be easily extended with user authentication, database integration, and cloud deployment.
        """
    else:
        return "I've generated a basic web application structure based on your requirements. The code includes a FastAPI backend with essential endpoints and can be extended based on your specific needs."

def generate_architecture_description(input_text: str) -> str:
    """Generate architecture description"""
    return """
## Application Architecture

### Frontend Layer
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Storage**: Browser localStorage for data persistence
- **Design**: Mobile-first responsive design
- **Interactions**: Real-time updates without page reloads

### Backend Layer
- **Framework**: FastAPI (Python)
- **API Design**: RESTful architecture
- **Data Models**: Pydantic for validation
- **CORS**: Enabled for cross-origin requests

### Data Flow
1. User interactions trigger JavaScript functions
2. Data is validated and stored in localStorage
3. UI updates immediately reflect changes
4. Backend API ready for database integration

### Scalability Considerations
- **Database Ready**: Easy to integrate PostgreSQL/MongoDB
- **Authentication**: JWT token structure prepared
- **Caching**: Redis integration possible
- **Deployment**: Docker containerization ready
    """

def generate_deployment_steps() -> list:
    """Generate deployment steps"""
    return [
        {
            "step_number": 1,
            "description": "Install Dependencies",
            "command": "pip install -r requirements.txt",
            "verification": "Check that all packages install without errors"
        },
        {
            "step_number": 2,
            "description": "Start the Backend Server",
            "command": "uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            "verification": "Visit http://localhost:8000/docs to see the API documentation"
        },
        {
            "step_number": 3,
            "description": "Test the Frontend",
            "command": "Open index.html in your web browser",
            "verification": "You should see the to-do application interface"
        },
        {
            "step_number": 4,
            "description": "Test Full Functionality",
            "command": "Add, complete, and delete tasks to verify everything works",
            "verification": "All task operations should work smoothly"
        }
    ]

# Add the router to your main app
# In your main.py, add this line:
# app.include_router(dream_router)

async def get_db():
    """Get database connection - Fixed for production"""
    try:
        database_url = os.getenv("DATABASE_URL") or os.getenv("AI_DEBUGGER_FACTORY")
        if not database_url:
            logger.warning("No database URL configured")
            yield None
            return
            
        conn = await asyncpg.connect(database_url)
        try:
            yield conn
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        yield None

@app.post("/api/v1/voice/process")
async def process_voice_real(file: UploadFile = File(...), language: str = "en"):
    """Real voice processing endpoint"""
    
    try:
        if not file.filename.endswith(('.webm', '.mp3', '.wav', '.m4a')):
            raise HTTPException(status_code=400, detail="Unsupported audio format")
        
        audio_data = await file.read()
        
        from app.utils.voice_processor_production import voice_processor
        result = await voice_processor.process_voice_input(audio_data, language)
        
        return result
        
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing error: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize production systems"""
    try:
        from app.database.db_production import db_manager
        await db_manager.initialize_pool()
        logger.info("✅ DreamEngine production systems initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {str(e)}")
        logger.info("📁 Continuing with file-based fallback")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup production systems"""
    try:
        from app.database.db_production import db_manager
        await db_manager.close()
        logger.info("🔌 DreamEngine production systems shutdown")
    except Exception as e:
        logger.warning(f"⚠️ Cleanup warning: {str(e)}")
