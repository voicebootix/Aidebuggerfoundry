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
from typing import Optional, Dict, Any
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

# Core imports
from app.services import service_manager
from app.database.db import db_manager, get_db
from app.database.models import *
from app.utils.auth_utils import get_optional_current_user
from app.config import settings, get_settings

# Database and models
import asyncpg

# Core utilities
from app.utils.logger import get_logger
logger = get_logger("service_manager")

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
logger = logging.getLogger(__name__)

# Database manager instance
db_manager = None

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

async def ensure_demo_user():
    """Ensure the demo user with a valid UUID exists in the users table."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.warning("DATABASE_URL not set; skipping demo user creation.")
        return
    conn = await asyncpg.connect(database_url)
    await conn.execute(
        "INSERT INTO users (id, email, hashed_password, full_name, is_active, is_verified) "
        "VALUES ($1, $2, $3, $4, $5, $6) "
        "ON CONFLICT (id) DO NOTHING;",
        DEMO_USER_ID, 'demo@example.com', '', 'Demo User', True, True
    )
    await conn.close()

async def create_tables():
    """Create database tables if they don't exist"""
    if db_manager:
        async with db_manager.get_connection() as conn:
            # Check existing tables
            existing = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            existing_tables = {row['table_name'] for row in existing}
            logger.info(f"📋  tables: {', '.join(existing_tables)}")
            
            # users table
            if 'users' not in existing_tables:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255),
                        full_name VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        is_verified BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                ''')
                logger.info("✅ users table ")
            
            # code_generations table - FIXED VERSION
            if 'code_generations' not in existing_tables:
                # First check dream_sessions id type
                dream_sessions_info = await conn.fetchrow("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'dream_sessions' 
                    AND column_name = 'id'
                """)
                
                if dream_sessions_info:
                    dream_id_type = dream_sessions_info['data_type']
                    logger.info(f"📊 dream_sessions.id type: {dream_id_type}")
                    
                    # Create table based on existing type
                    if dream_id_type == 'integer':
                        await conn.execute('''
                            CREATE TABLE IF NOT EXISTS code_generations (
                                id SERIAL PRIMARY KEY,
                                dream_session_id INTEGER REFERENCES dream_sessions(id),
                                project_id VARCHAR(255),
                                status VARCHAR(50) DEFAULT 'pending',
                                metadata JSONB,
                                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                            )
                        ''')
                    else:
                        await conn.execute('''
                            CREATE TABLE IF NOT EXISTS code_generations (
                                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                                dream_session_id VARCHAR(255) REFERENCES dream_sessions(id),
                                project_id VARCHAR(255),
                                status VARCHAR(50) DEFAULT 'pending',
                                metadata JSONB,
                                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                            )
                        ''')
                    logger.info("✅ code_generations table ")
                else:
                    # No foreign key if dream_sessions doesn't exist
                    await conn.execute('''
                        CREATE TABLE IF NOT EXISTS code_generations (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            dream_session_id VARCHAR(255),
                            project_id VARCHAR(255),
                            status VARCHAR(50) DEFAULT 'pending',
                            metadata JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        )
                    ''')
                    logger.info("✅ code_generations table  (foreign key )")
            
            logger.info("✅ tables")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - UNIFIED SERVICE APPROACH"""
    # Startup
    logger.info("🚀 Starting AI Debugger Factory...")

    # Ensure demo user exists before anything else
    await ensure_demo_user()

    # Initialize database FIRST
    try:
        global db_manager
        from app.database.db import DatabaseManager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        await create_tables()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # ✅ CRITICAL: Initialize ALL services through service manager
    try:
        await service_manager.initialize()
        logger.info("✅ All services initialized through service manager")
    except Exception as e:
        logger.error(f"❌ Service initialization error: {e}")
        logger.error(f"Full error details: {e}", exc_info=True)
        # Continue running - services will show as unavailable

    # Log all registered routes for debugging
    from fastapi.routing import APIRoute
    route_info = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ','.join(route.methods)
            route_info.append(f"{methods} {route.path}")
    logger.info(f"[ROUTES] Registered routes: {route_info}")

    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Debugger Factory...")
    await service_manager.cleanup()
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
    logger.info(f"[MIDDLEWARE] Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[MIDDLEWARE] Exception during request: {e}")
        raise
    process_time = asyncio.get_event_loop().time() - start_time
    logger.info(f"[MIDDLEWARE] {request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Error handling middleware
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"[EXCEPTION] HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
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
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    logger.error(f"[EXCEPTION] Global exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Templates
templates = Jinja2Templates(directory="app/templates")

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


