"""
AI Debugger Factory - Application Runner
Production-ready startup script with proper error handling
"""

import asyncio
import signal
import sys
import uvicorn
from app.main import app
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class GracefulShutdown:
    """Handle graceful shutdown on SIGTERM/SIGINT"""
    
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown = True

def print_startup_banner():
    """Print application startup banner"""
    banner = f"""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                     🚀 AI DEBUGGER FACTORY v1.0.0                          ║
    ║                 Revolutionary AI-Powered Development Platform                ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║                                                                              ║
    ║  ✨ REVOLUTIONARY FEATURES ACTIVE:                                          ║
    ║  🎤 VoiceBotics AI Cofounder         (Patent-worthy Innovation)             ║
    ║  🧠 Smart Business Intelligence      (Intelligent Validation)               ║
    ║  📋 Contract Method Compliance       (Patent-worthy AI Monitoring)          ║
    ║  💰 Smart Contract Revenue Sharing   (Patent-worthy Monetization)           ║
    ║  🔧 Professional Monaco Editor       (Professional Development)             ║
    ║  📤 Complete GitHub Workflow         (Seamless Integration)                 ║
    ║                                                                              ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║  🌍 Server: http://{settings.API_HOST}:{settings.API_PORT:<52} ║
    ║  📚 API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs{' ' * 47} ║
    ║  🔍 Health: http://{settings.API_HOST}:{settings.API_PORT}/health{' ' * 45} ║
    ║  📊 Status: http://{settings.API_HOST}:{settings.API_PORT}/status{' ' * 45} ║
    ║                                                                              ║
    ║  🎯 TRANSFORM FOUNDER CONVERSATIONS INTO PROFITABLE BUSINESSES! 🎯         ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_required_settings():
    """Validate that required settings are present"""
    required_settings = [
        'SECRET_KEY',
        'DATABASE_URL', 
        'JWT_SECRET_KEY',
        'API_KEY_SALT'
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        logger.error(f"Missing required settings: {', '.join(missing_settings)}")
        logger.error("Please check your .env file or environment variables")
        sys.exit(1)

def check_optional_features():
    """Check which optional features are enabled"""
    features = {
        "OpenAI Integration": bool(settings.OPENAI_API_KEY),
        "Anthropic Claude": bool(settings.ANTHROPIC_API_KEY),
        "GitHub Integration": bool(settings.GITHUB_TOKEN),
        "Voice Processing": bool(settings.VOICE_API_KEY),
        "ElevenLabs TTS": bool(settings.ELEVENLABS_API_KEY),
        "Smart Contracts": bool(settings.WEB3_PROVIDER_URL),
        "Business Intelligence": bool(settings.SERPAPI_KEY),
        "Error Monitoring": bool(settings.SENTRY_DSN)
    }
    
    enabled_features = [name for name, enabled in features.items() if enabled]
    disabled_features = [name for name, enabled in features.items() if not enabled]
    
    if enabled_features:
        logger.info(f"✅ Enabled features: {', '.join(enabled_features)}")
    
    if disabled_features:
        logger.warning(f"⚠️  Disabled features (missing API keys): {', '.join(disabled_features)}")

async def run_server():
    """Run the server with proper configuration"""
    try:
        # Validate settings
        validate_required_settings()
        check_optional_features()
        
        # Print startup banner
        print_startup_banner()
        
        # Setup graceful shutdown
        shutdown_handler = GracefulShutdown()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.RELOAD and settings.ENVIRONMENT == "development",
            workers=1 if settings.DEBUG else settings.API_WORKERS,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True,
            server_header=False,  # Security: Hide server header
            date_header=False     # Security: Hide date header
        )
        
        server = uvicorn.Server(config)
        
        # Start server
        logger.info("🚀 Starting AI Debugger Factory server...")
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}", exc_info=True)
        sys.exit(1)

def main():
    """Main entry point"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()