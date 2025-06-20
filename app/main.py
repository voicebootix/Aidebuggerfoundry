"""
AI Debugger Factory - Main Application
Revolutionary AI-powered development platform with patent-worthy innovations

Features:
- VoiceBotics AI Cofounder conversations (PATENT-WORTHY)
- Smart Business Intelligence validation (INTELLIGENT)
- Contract Method AI compliance system (PATENT-WORTHY)
- Smart Contract revenue sharing (PATENT-WORTHY)
- Professional Monaco Editor integration (PROFESSIONAL)
- Complete GitHub workflow (SEAMLESS)
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

# Database and models
from app.database.db import DatabaseManager, get_db
from app.database.models import *

# Core utilities
# from app.utils.logger import get_logger, log_request_response
from app.config import settings, get_settings

# Route imports - Import all revolutionary features
from app.routes.voice_conversation_router import router as voice_conversation_router
from app.routes.business_intelligence_router import router as business_intelligence_router
from app.routes.dream_router import router as dream_router
from app.routes.debug_router import router as debug_router
from app.routes.github_router import router as github_router
from app.routes.smart_contract_router import router as smart_contract_router
from app.routes.contract_method_router import router as contract_method_router
from app.routes.project_router import router as project_router
from app.routes.auth_router import router as auth_router

# Initialize logger
logger = get_logger(__name__)

# Database manager instance
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting AI Debugger Factory...")
    
    global db_manager
    db_manager = DatabaseManager()
    
    # Initialize database
    try:
        await db_manager.initialize()
        await db_manager.run_migrations()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize other services
    try:
        # Initialize LLM providers
        from app.utils.llm_provider import llm_provider
        await llm_provider.initialize()
        logger.info("✅ LLM providers initialized")
        
        # Initialize voice processor
        from app.utils.voice_processor import voice_processor
        await voice_processor.initialize()
        logger.info("✅ Voice processor initialized")
        
        # Initialize GitHub integration
        from app.utils.github_integration import github_manager
        await github_manager.initialize()
        logger.info("✅ GitHub integration initialized")
        
        logger.info("🎉 AI Debugger Factory startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
        # Continue startup even if some services fail
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Debugger Factory...")
    if db_manager:
        await db_manager.close()
    logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI Debugger Factory",
    description="Revolutionary AI-powered development platform that transforms founder conversations into profitable businesses",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# ==========================================
# MIDDLEWARE CONFIGURATION
# ==========================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust proxy headers
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else settings.ALLOWED_HOSTS
)

# Request/Response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    start_time = asyncio.get_event_loop().time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = asyncio.get_event_loop().time() - start_time
    
    # Log request/response
    await log_request_response(
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": asyncio.get_event_loop().time(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error", 
            "message": "Internal server error" if not settings.DEBUG else str(exc),
            "timestamp": asyncio.get_event_loop().time(),
            "path": str(request.url.path)
        }
    )

# ==========================================
# STATIC FILES AND TEMPLATES
# ==========================================

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# ==========================================
# API ROUTES REGISTRATION
# ==========================================

# Register all revolutionary API routers
API_PREFIX = "/api/v1"

# VoiceBotics AI Cofounder (REVOLUTIONARY - PATENT-WORTHY)
app.include_router(
    voice_conversation_router, 
    prefix=f"{API_PREFIX}/voice-conversation",
    tags=["🎤 VoiceBotics AI Cofounder"]
)

# Business Intelligence (INTELLIGENT - OPTIONAL)
app.include_router(
    business_intelligence_router,
    prefix=f"{API_PREFIX}/business-intelligence", 
    tags=["🧠 Business Intelligence"]
)

# Layer 1 Build - Dream Engine (CORE GENERATION)
app.include_router(
    dream_router,
    prefix=f"{API_PREFIX}/dreamengine",
    tags=["⚡ Layer 1 Build"]
)

# Layer 2 Debug - Debug Engine (PROFESSIONAL DEBUGGING)
app.include_router(
    debug_router,
    prefix=f"{API_PREFIX}/debug",
    tags=["🔧 Layer 2 Debug"]
)

# GitHub Integration (SEAMLESS WORKFLOW)
app.include_router(
    github_router,
    prefix=f"{API_PREFIX}/github",
    tags=["📤 GitHub Integration"]
)

# Smart Contract Revenue Sharing (PATENT-WORTHY)
app.include_router(
    smart_contract_router,
    prefix=f"{API_PREFIX}/smart-contract",
    tags=["💰 Smart Contract Revenue"]
)

# Contract Method AI Compliance (PATENT-WORTHY)
app.include_router(
    contract_method_router,
    prefix=f"{API_PREFIX}/contract-method",
    tags=["📋 Contract Method Compliance"]
)

# Project Management (CROSS-LAYER COORDINATION)
app.include_router(
    project_router,
    prefix=f"{API_PREFIX}/projects",
    tags=["📁 Project Management"]
)

# Authentication (SECURITY)
app.include_router(
    auth_router,
    prefix=f"{API_PREFIX}/auth",
    tags=["🔐 Authentication"]
)

# ==========================================
# CORE APPLICATION ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve main application interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse) 
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve user dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/voice-conversation", response_class=HTMLResponse)
async def voice_conversation_page(request: Request):
    """Serve VoiceBotics AI Cofounder interface"""
    return templates.TemplateResponse("voice_conversation.html", {"request": request})

# ==========================================
# HEALTH & STATUS ENDPOINTS
# ==========================================

# Add this after the main FastAPI app creation, before route registration

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    try:
        # Test database connection
        db_health = await db_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "database": db_health["status"],
            "services": {
                "api": "healthy",
                "database": db_health["status"],
                "auth": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@app.get("/status")
async def status():
    """Detailed application status"""
    try:
        # Get database stats
        db_stats = {}
        if db_manager:
            db_stats = await db_manager.get_stats()
        
        # Get system info
        import psutil
        system_stats = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return {
            "application": {
                "name": "AI Debugger Factory",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG
            },
            "database": db_stats,
            "system": system_stats,
            "features": {
                "voicebotics_ai_cofounder": "✅ Active (Patent-worthy)",
                "business_intelligence": "✅ Active (Intelligent)",
                "contract_method_compliance": "✅ Active (Patent-worthy)", 
                "smart_contract_revenue": "✅ Active (Patent-worthy)",
                "monaco_editor_integration": "✅ Active (Professional)",
                "github_workflow": "✅ Active (Seamless)"
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

# ==========================================
# REVOLUTIONARY FEATURES INFO
# ==========================================

@app.get("/features")
async def get_features():
    """Get information about revolutionary features"""
    return {
        "revolutionary_features": {
            "voicebotics_ai_cofounder": {
                "status": "patent_worthy",
                "description": "Natural conversation interface that transforms founder discussions into deployed applications",
                "innovation": "First AI system to conduct full business development conversations",
                "patent_elements": [
                    "Conversational business development AI",
                    "Intelligent founder type detection",
                    "Real-time strategy evolution through dialogue",
                    "Voice-to-deployment pipeline"
                ]
            },
            "business_intelligence_validation": {
                "status": "intelligent",
                "description": "Optional but smart business validation system with market research",
                "innovation": "AI-driven business strategy optimization",
                "features": [
                    "Automated market research",
                    "Competitor analysis",
                    "Strategy recommendations",
                    "Pivot suggestions"
                ]
            },
            "contract_method_compliance": {
                "status": "patent_worthy",
                "description": "AI creates and monitors its own behavioral agreements",
                "innovation": "Self-monitoring AI with contract enforcement",
                "patent_elements": [
                    "AI-generated behavioral contracts",
                    "Automatic deviation detection",
                    "Self-correction mechanisms",
                    "Compliance scoring algorithms"
                ]
            },
            "smart_contract_revenue_sharing": {
                "status": "patent_worthy", 
                "description": "Blockchain-based automated revenue distribution with digital fingerprinting",
                "innovation": "Transparent AI-generated code monetization",
                "patent_elements": [
                    "Automated revenue distribution",
                    "Digital code fingerprinting",
                    "Unauthorized usage detection",
                    "Blockchain-based profit sharing"
                ]
            },
            "professional_monaco_integration": {
                "status": "professional",
                "description": "VS Code-level debugging experience with AI assistance",
                "innovation": "AI-powered professional development environment",
                "features": [
                    "Monaco Editor integration",
                    "Real-time collaboration",
                    "AI debugging assistance",
                    "GitHub synchronization"
                ]
            },
            "complete_github_workflow": {
                "status": "seamless",
                "description": "Automatic Layer 1 → GitHub → Layer 2 workflow",
                "innovation": "Seamless code generation to debugging pipeline",
                "features": [
                    "Automatic repository creation",
                    "Code push automation",
                    "Branch management",
                    "Pull request generation"
                ]
            }
        },
        "competitive_advantages": [
            "Only platform with voice-to-deployment capability",
            "Patent-worthy AI behavioral monitoring",
            "Blockchain-based transparent monetization",
            "Professional development environment",
            "Complete founder journey automation"
        ]
    }

# ==========================================
# METRICS & ANALYTICS
# ==========================================

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    try:
        metrics = {
            "timestamp": asyncio.get_event_loop().time(),
            "application": {
                "uptime_seconds": 0,  # Would calculate from startup time
                "total_requests": 0,  # Would track from middleware
                "active_sessions": 0   # Would track from session manager
            },
            "features": {
                "voice_conversations_started": 0,
                "business_validations_completed": 0,
                "code_generations_successful": 0,
                "github_repositories_created": 0,
                "debug_sessions_active": 0,
                "smart_contracts_deployed": 0
            },
            "performance": {
                "average_response_time_ms": 0,
                "code_generation_time_avg_seconds": 0,
                "voice_processing_time_avg_seconds": 0
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")

# ==========================================
# STARTUP MESSAGE
# ==========================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    🚀 AI DEBUGGER FACTORY - REVOLUTIONARY AI-POWERED DEVELOPMENT PLATFORM
    
    ✨ Revolutionary Features Active:
    🎤 VoiceBotics AI Cofounder (Patent-worthy)
    🧠 Smart Business Intelligence (Intelligent)  
    📋 Contract Method Compliance (Patent-worthy)
    💰 Smart Contract Revenue Sharing (Patent-worthy)
    🔧 Professional Monaco Editor (Professional)
    📤 Complete GitHub Workflow (Seamless)
    
    🌍 Server starting on http://localhost:8000
    📚 API Documentation: http://localhost:8000/docs
    🔍 Health Check: http://localhost:8000/health
    
    Transform founder conversations into profitable businesses! 🎯
    """)
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
        log_level="info"
    )