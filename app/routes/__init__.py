"""
AI Debugger Factory - API Routes Module Initialization
Revolutionary API endpoints for all platform features
"""

from .voice_conversation_router import router as voice_conversation_router
from .business_intelligence_router import router as business_intelligence_router
from .dream_router import router as dream_router
from .debug_router import router as debug_router
from .github_router import router as github_router
from .smart_contract_router import router as smart_contract_router
from .contract_method_router import router as contract_method_router
from .project_router import router as project_router
from .auth_router import router as auth_router

__all__ = [
    "voice_conversation_router",
    "business_intelligence_router", 
    "dream_router",
    "debug_router",
    "github_router",
    "smart_contract_router",
    "contract_method_router",
    "project_router",
    "auth_router"
]

# API Router descriptions
ROUTER_DESCRIPTIONS = {
    "voice_conversation": "Revolutionary VoiceBotics AI Cofounder conversations (PATENT-WORTHY)",
    "business_intelligence": "Smart business validation and strategy analysis (INTELLIGENT)",
    "dream": "Layer 1 Build - Strategic analysis and code generation",
    "debug": "Layer 2 Debug - Professional debugging with Monaco Editor",
    "github": "Complete GitHub workflow integration",
    "smart_contract": "Smart contract revenue sharing system (PATENT-WORTHY)",
    "contract_method": "AI agent compliance and monitoring (PATENT-WORTHY)",
    "project": "Cross-layer project lifecycle management",
    "auth": "Production-ready authentication and authorization"
}

print("🚀 AI Debugger Factory API Routes Loaded")
print("✅ Revolutionary APIs:", list(ROUTER_DESCRIPTIONS.keys()))