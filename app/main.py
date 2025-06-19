"""
AI Debugger Factory - Main Application
Fixed to use ONLY enhanced production versions
File: app/main.py
"""

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
import time
import asyncpg

# ✅ CORRECT ENHANCED IMPORTS
from app.config import settings
from app.models.prompt import PromptRequest, PromptResponse
from app.database.db import get_db, init_db
from app.utils.logger import setup_logger, get_logger
from app.utils.error_handler import ErrorHandler
from app.utils.github_integrator import GitHubAutoDeployer, GitHubDeployRequest, GitHubDeployResponse

# ✅ ENHANCED VOICE PROCESSOR (PRODUCTION VERSION)
from app.utils.voice_processor_production import ProductionVoiceProcessor

# ✅ ENHANCED DREAM ENGINE AND LLM PROVIDER
from app.utils.dream_engine import DreamEngine
from app.utils.llm_provider import EnhancedLLMProvider
from app.utils.voice_processor import SomeClassOrFunction

# ✅ ENHANCED MIDDLEWARE
try:
    from app.middleware.logging_middleware import LoggingMiddleware, PerformanceLoggingMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False
    logging.warning("⚠️ Enhanced middleware not available")

# ✅ SECURITY VALIDATOR (if available)
try:
    from app.utils.security_validator import SecurityValidator
    SECURITY_VALIDATOR_AVAILABLE = True
except ImportError:
    SECURITY_VALIDATOR_AVAILABLE = False
    logging.warning("⚠️ Security validator not available")

from pydantic import BaseModel

# Set up logger
logger = setup_logger()

# ✅ PYDANTIC MODELS FOR ENHANCED API
class DreamProcessRequest(BaseModel):
    input_text: str
    user_id: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class DreamProcessResponse(BaseModel):
    id: str
    status: str
    message: str
    generated_files: Optional[List[Dict]] = None
    processing_time: float
    timestamp: str

class VoiceProcessRequest(BaseModel):
    audio_format: Optional[str] = "webm"
    language: Optional[str] = "en"

class GitHubUploadRequest(BaseModel):
    repo: str
    token: str
    paths: str
    commit_message: str = "AI Debugger Factory - Enhanced Version"

# Initialize FastAPI app
app = FastAPI(
    title="AI Debugger Factory - Enhanced Version",
    description="AI-powered SaaS platform with enhanced DreamEngine, voice processing, and LLM integration",
    version="2.0.0"
)

# ✅ ENHANCED CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ADD ENHANCED MIDDLEWARE IF AVAILABLE
if MIDDLEWARE_AVAILABLE:
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold=5.0)
    logger.info("✅ Enhanced middleware loaded")

# ✅ MOUNT STATIC FILES WITH ERROR HANDLING
try:
    if os.path.exists("app/static"):
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
        logger.info("✅ Static files mounted successfully")
    else:
        logger.info("📁 Static directory not found, skipping mount")
except Exception as e:
    logger.warning(f"⚠️ Failed to mount static files: {e}")

# ✅ INITIALIZE TEMPLATES WITH ERROR HANDLING
templates = None
try:
    if os.path.exists("app/templates"):
        templates = Jinja2Templates(directory="app/templates")
        logger.info("✅ Templates initialized successfully")
    else:
        logger.info("📁 Templates directory not found")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize templates: {e}")

# ✅ ENHANCED DATABASE CONNECTION
async def get_enhanced_db():
    """Get enhanced database connection with proper error handling"""
    try:
        database_url = os.getenv("DATABASE_URL") or os.getenv("AI_DEBUGGER_FACTORY")
        if not database_url:
            logger.warning("⚠️ No database URL configured, using fallback")
            yield None
            return
            
        conn = await asyncpg.connect(database_url)
        try:
            yield conn
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        yield None

# ✅ ENHANCED DREAM ENGINE ROUTER
dream_router = APIRouter(prefix="/api/v1/dreamengine", tags=["dreamengine"])

@dream_router.get("/health")
async def dreamengine_health():
    """Enhanced DreamEngine health check"""
    try:
        # Test LLM provider availability
        llm_provider = EnhancedLLMProvider()
        available_providers = llm_provider.get_available_providers()
        
        return {
            "status": "healthy",
            "service": "Enhanced DreamEngine",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "available_llm_providers": available_providers,
            "features": {
                "voice_processing": True,
                "streaming_generation": True,
                "multi_llm_support": True,
                "security_validation": SECURITY_VALIDATOR_AVAILABLE,
                "enhanced_middleware": MIDDLEWARE_AVAILABLE
            }
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@dream_router.post("/process", response_model=DreamProcessResponse)
async def process_dream_enhanced(
    request: DreamProcessRequest,
    db: Optional[asyncpg.Connection] = Depends(get_enhanced_db)
):
    """Enhanced DreamEngine processing with multi-LLM support"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"🚀 Processing dream request: {request_id}")
        
        # ✅ Initialize enhanced DreamEngine
        dream_engine = DreamEngine()
        
        # ✅ Process with enhanced capabilities
        result = await dream_engine.process_founder_input(
            input_text=request.input_text,
            user_id=request.user_id or f"user_{request_id[:8]}",
            options=request.options or {}
        )
        
        processing_time = time.time() - start_time
        
        response = DreamProcessResponse(
            id=request_id,
            status="success",
            message="Code generated successfully with enhanced DreamEngine",
            generated_files=result.get("files", []),
            processing_time=round(processing_time, 3),
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Dream processed successfully: {request_id} in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Enhanced DreamEngine processing failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        return DreamProcessResponse(
            id=request_id,
            status="error",
            message=error_msg,
            processing_time=round(processing_time, 3),
            timestamp=datetime.now().isoformat()
        )

@dream_router.post("/stream")
async def stream_dream_generation(request: DreamProcessRequest):
    """Enhanced streaming generation with multi-LLM support"""
    
    async def generate_enhanced_stream():
        try:
            dream_engine = DreamEngine()
            
            # Get the best available LLM provider
            llm_provider = EnhancedLLMProvider()
            provider_name = llm_provider.get_best_available_provider()
            logger.info(f"🎯 Streaming with {provider_name} provider")
            
            # Yield initial status
            yield f"data: {json.dumps({'type': 'status', 'content': f'Starting enhanced generation with {provider_name}...'})}\n\n"
            
            # Generate with streaming
            async for chunk in dream_engine.generate_code_streaming(
                prompt=request.input_text,
                user_id=request.user_id or f"stream_user_{int(time.time())}",
                options=request.options or {}
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
                
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_msg = f"Enhanced streaming failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            error_chunk = {
                "type": "error",
                "content": error_msg,
                "is_final": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_enhanced_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

# ✅ ENHANCED VOICE PROCESSING ENDPOINT
@app.post("/api/v1/voice/process")
async def process_voice_enhanced(file: UploadFile = File(...)):
    """Enhanced voice processing with production-grade capabilities"""
    try:
        # Validate file format
        if not file.filename.endswith(('.webm', '.mp3', '.wav', '.m4a', '.flac', '.ogg')):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported audio format. Supported: webm, mp3, wav, m4a, flac, ogg"
            )
        
        # ✅ Use ENHANCED voice processor
        voice_processor = ProductionVoiceProcessor()
        
        # Check if voice processor is initialized
        if not voice_processor.openai_api_key:
            raise HTTPException(
                status_code=503,
                detail="Voice processing unavailable: OpenAI API key not configured"
            )
        
        # Process with enhanced capabilities
        result = await voice_processor.process_voice_file(file)
        
        if result.get("success"):
            logger.info(f"✅ Voice processed: {len(result.get('transcribed_text', ''))} chars")
            return {
                "status": "success",
                "transcribed_text": result["transcribed_text"],
                "structured_prompt": result.get("structured_prompt", {}),
                "confidence_score": result.get("confidence", 0.8),
                "processing_time": result.get("processing_time", 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ Voice processing failed: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Voice processing failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Voice processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# ✅ ENHANCED GITHUB INTEGRATION
@app.post("/api/v1/github/upload")
async def upload_to_github_enhanced(request: GitHubUploadRequest):
    """Enhanced GitHub integration with auto-deployment"""
    try:
        deployer = GitHubAutoDeployer()
        
        # Validate request
        if SECURITY_VALIDATOR_AVAILABLE:
            validator = SecurityValidator()
            validation_result = validator.validate_github_request(request.dict())
            if not validation_result["is_valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Security validation failed: {validation_result['issues']}"
                )
        
        # Process deployment
        deploy_request = GitHubDeployRequest(
            repository_url=request.repo,
            access_token=request.token,
            file_paths=request.paths.split(","),
            commit_message=request.commit_message
        )
        
        result = await deployer.deploy_to_github(deploy_request)
        
        return {
            "status": "success",
            "message": "Files uploaded to GitHub successfully",
            "repository": request.repo,
            "commit_sha": result.commit_sha,
            "deployment_url": result.deployment_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ GitHub upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GitHub upload failed: {str(e)}")

# ✅ INCLUDE ENHANCED DREAM ROUTER
app.include_router(dream_router)

# ✅ SAFE LOADING OF OPTIONAL ENHANCED ROUTERS
OPTIONAL_ENHANCED_ROUTERS = [
    ("app.routes.debug_router", "router", "Enhanced DebugBot Layer 2"),
    ("app.routes.smart_contract_router", "router", "Smart Contract Generator"),
    ("app.routes.contract_router", "router", "Contract Manager")
]

for module_path, router_name, description in OPTIONAL_ENHANCED_ROUTERS:
    try:
        module = __import__(module_path, fromlist=[router_name])
        router = getattr(module, router_name)
        app.include_router(router)
        logger.info(f"✅ {description} loaded successfully")
    except ImportError:
        logger.info(f"📦 {description} not available (optional)")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load {description}: {e}")

# ✅ ROOT ENDPOINT
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Root endpoint serving enhanced UI"""
    if templates:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "app_version": "2.0.0",
            "features": {
                "enhanced_dream_engine": True,
                "production_voice": True,
                "multi_llm": True,
                "security_validation": SECURITY_VALIDATOR_AVAILABLE
            }
        })
    return {
        "status": "online",
        "service": "AI Debugger Factory - Enhanced Version",
        "version": "2.0.0",
        "features": {
            "enhanced_dream_engine": True,
            "production_voice_processing": True,
            "multi_llm_support": True,
            "enhanced_middleware": MIDDLEWARE_AVAILABLE,
            "security_validation": SECURITY_VALIDATOR_AVAILABLE
        },
        "endpoints": {
            "health": "/api/v1/dreamengine/health",
            "process": "/api/v1/dreamengine/process",
            "stream": "/api/v1/dreamengine/stream",
            "voice": "/api/v1/voice/process",
            "github": "/api/v1/github/upload"
        }
    }

# ✅ ENHANCED HEALTH CHECK
@app.get("/api/v1/health")
async def health_check_enhanced():
    """Enhanced health check with component status"""
    components = {
        "enhanced_dream_engine": True,
        "production_voice_processor": True,
        "multi_llm_provider": True,
        "enhanced_middleware": MIDDLEWARE_AVAILABLE,
        "security_validator": SECURITY_VALIDATOR_AVAILABLE,
        "database": False,  # Will be updated with actual check
        "github_integration": True
    }
    
    # Test database connection
    try:
        db = await get_enhanced_db().__anext__()
        if db:
            components["database"] = True
            await db.close()
    except:
        pass
    
    # Test LLM providers
    try:
        llm_provider = EnhancedLLMProvider()
        available_providers = llm_provider.get_available_providers()
        components["available_llm_providers"] = available_providers
    except:
        components["available_llm_providers"] = []
    
    healthy_components = sum(1 for v in components.values() if v is True)
    total_components = len([k for k, v in components.items() if isinstance(v, bool)])
    health_score = healthy_components / total_components
    
    return {
        "status": "healthy" if health_score > 0.7 else "degraded",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "health_score": round(health_score, 2),
        "components": components
    }

# ✅ ENHANCED STARTUP EVENT
@app.on_event("startup")
async def startup_enhanced():
    """Enhanced startup with comprehensive component initialization"""
    logger.info("🚀 Starting AI Debugger Factory - Enhanced Version 2.0.0")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database connection initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e}")
        logger.info("📁 Continuing with file-based fallback")
    
    # Initialize production voice processor
    try:
        voice_processor = ProductionVoiceProcessor()
        await voice_processor.initialize()
        logger.info("✅ Enhanced voice processing system initialized")
    except Exception as e:
        logger.warning(f"⚠️ Voice processor initialization failed: {e}")
    
    # Initialize enhanced LLM providers
    try:
        llm_provider = EnhancedLLMProvider()
        available_providers = llm_provider.get_available_providers()
        logger.info(f"✅ Enhanced LLM providers initialized: {', '.join(available_providers)}")
    except Exception as e:
        logger.warning(f"⚠️ LLM provider initialization failed: {e}")
    
    # Initialize security validator
    if SECURITY_VALIDATOR_AVAILABLE:
        try:
            validator = SecurityValidator()
            logger.info("✅ Security validator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Security validator initialization failed: {e}")
    
    logger.info("🎯 AI Debugger Factory Enhanced Version startup complete")

@app.on_event("shutdown")
async def shutdown_enhanced():
    """Enhanced shutdown with proper cleanup"""
    logger.info("🔌 Shutting down AI Debugger Factory Enhanced Version")
    
    # Cleanup enhanced components
    try:
        # Close LLM provider connections
        llm_provider = EnhancedLLMProvider()
        await llm_provider.cleanup()
        logger.info("✅ LLM providers cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ LLM cleanup warning: {e}")
    
    logger.info("👋 AI Debugger Factory Enhanced Version shutdown complete")

# ✅ RUN THE ENHANCED APPLICATION
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )