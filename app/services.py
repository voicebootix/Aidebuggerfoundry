"""
Service Manager - Centralized Service Initialization
Handles all service initialization with proper error handling
Supports asyncpg database connections
"""

import os
import asyncio
from typing import Optional, Dict, Any
import openai
import anthropic
import asyncpg
from datetime import datetime

# Import all service classes
from app.utils.voice_processor import VoiceProcessor
from app.utils.voice_conversation_engine import VoiceConversationEngine
from app.utils.business_intelligence import BusinessIntelligence
from app.utils.dream_engine import DreamEngine
from app.utils.debug_engine import DebugEngine
from app.utils.contract_method import ContractMethod
from app.utils.smart_contract_system import SmartContractSystem
from app.utils.github_integration import GitHubIntegration
from app.utils.llm_provider import EnhancedLLMProvider
from app.utils.security_validator import SecurityValidator
from app.utils.project_manager import ProjectManager
from app.utils.deployment_manager import DeploymentManager
from app.utils.monaco_integration import MonacoIntegration
from app.utils.logger import get_logger

logger = get_logger("service_manager")

class ServiceManager:
    """Production-ready service manager with complete initialization"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            # Core AI services
            self.voice_processor: Optional[VoiceProcessor] = None
            self.conversation_engine: Optional[VoiceConversationEngine] = None
            self.business_intelligence: Optional[BusinessIntelligence] = None
            self.dream_engine: Optional[DreamEngine] = None
            self.debug_engine: Optional[DebugEngine] = None
            
            # Infrastructure services
            self.smart_contract_system: Optional[SmartContractSystem] = None
            self.github_integration: Optional[GitHubIntegration] = None
            self.monaco_integration: Optional[MonacoIntegration] = None
            self.project_manager: Optional[ProjectManager] = None
            self.deployment_manager: Optional[DeploymentManager] = None
            
            # Supporting services
            self.llm_provider: Optional[EnhancedLLMProvider] = None
            self.security_validator: Optional[SecurityValidator] = None
            self.contract_method: Optional[ContractMethod] = None
            
            # Database connection pool
            self.db_pool: Optional[asyncpg.Pool] = None
            
            # Service status tracking
            self.service_status: Dict[str, bool] = {}
            self.initialized = False
    
    async def initialize(self):
        """Initialize all services with comprehensive error handling"""
        logger.info("🚀 Starting service initialization...")
        
        try:
            # Load configuration from environment
            config = self._load_configuration()
            
            # Initialize database connection pool FIRST
            await self._initialize_database(config)
            
            # Initialize security validator (always needed)
            self.security_validator = SecurityValidator()
            self.service_status['security_validator'] = True
            logger.info("✅ Security Validator initialized")
            
            # Initialize LLM Provider (core dependency for many services)
            await self._initialize_llm_provider(config)
            
            # Initialize voice processing services
            await self._initialize_voice_services(config)
            
            # Initialize business intelligence
            await self._initialize_business_intelligence()
            
            # Initialize dream engine (code generation)
            await self._initialize_dream_engine()
            
            # Initialize debug engine
            await self._initialize_debug_engine()
            
            # Initialize GitHub integration
            await self._initialize_github_integration(config)
            
            # Initialize smart contract system
            await self._initialize_smart_contracts(config)
            
            # Initialize project and deployment managers
            await self._initialize_project_management()
            
            # Initialize Monaco editor integration
            await self._initialize_monaco_integration()
            
            self.initialized = True
            self._log_initialization_summary()
            
        except Exception as e:
            logger.error(f"❌ Critical error during service initialization: {e}")
            import traceback
            traceback.print_exc()
            # Still mark as initialized to prevent re-initialization attempts
            self.initialized = True
    
        def _load_configuration(self) -> Dict[str, Any]:
            """Load configuration with all necessary environment variables"""
            return {
            # Database
            'database_url': os.getenv('DATABASE_URL', 
                'postgresql://ai_debugger:secure_password@localhost:5432/ai_debugger_factory'),
            
            # LLM APIs
            'openai_api_key': os.getenv('OPENAI_API_KEY') or os.getenv('VOICE_API_KEY'),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            
            # Voice processing
            'elevenlabs_api_key': os.getenv('ELEVENLABS_API_KEY'),
            'voice_timeout': int(os.getenv('VOICE_TIMEOUT', '60')),
            
            # GitHub integration
            'github_token': os.getenv('GITHUB_TOKEN'),
            
            # Smart contracts
            'web3_provider_url': os.getenv('WEB3_PROVIDER_URL'),
            'smart_contract_address': os.getenv('SMART_CONTRACT_ADDRESS'),
            
            # Security
            'secret_key': os.getenv('SECRET_KEY'),
        }
        
        # Log configuration status (without exposing keys)
        logger.info("📋 Configuration loaded:")
        for key, value in config.items():
            if value and 'key' in key.lower():
                logger.info(f"  - {key}: {'✅ Set' if value else '❌ Not set'}")
            elif key == 'database_url':
                logger.info(f"  - {key}: {value.split('@')[1] if '@' in value else value}")
            else:
                logger.info(f"  - {key}: {value}")
        
        return config
    
    async def _initialize_database(self, config: Dict[str, Any]):
        """Initialize asyncpg connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                config['database_url'],
                min_size=10,
                max_size=20,
                command_timeout=60,
                max_queries=50000,
                max_cacheable_statement_size=1024
            )
            self.service_status['database'] = True
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.service_status['database'] = False
            raise
    
    async def _initialize_llm_provider(self, config: Dict[str, Any]):
        """Initialize LLM provider with fallback support"""
        try:
            self.llm_provider = EnhancedLLMProvider(api_keys={
                "openai": config['openai_api_key'],
                "anthropic": config['anthropic_api_key']
            })
            await self.llm_provider.initialize()
            self.service_status['llm_provider'] = True
            logger.info("✅ LLM Provider initialized with fallback support")
        except Exception as e:
            logger.error(f"❌ LLM Provider initialization failed: {e}")
            self.service_status['llm_provider'] = False
            # Don't raise - allow app to run with limited functionality
    
    async def _initialize_voice_services(self, config: Dict[str, Any]):
        """Initialize voice processing and conversation engine"""
        try:
            # Voice processor
            if config['openai_api_key']:
                self.voice_processor = VoiceProcessor(
                    openai_api_key=config['openai_api_key']
                )
                await self.voice_processor.initialize()
                self.service_status['voice_processor'] = True
                logger.info("✅ Voice Processor initialized")
                
                # Business Intelligence (needed for conversation engine)
                if not self.business_intelligence:
                    await self._initialize_business_intelligence()
                
                # Contract Method
                self.contract_method = ContractMethod(
                    llm_provider=self.llm_provider
                )
                self.service_status['contract_method'] = True
                logger.info("✅ Contract Method initialized")
                
                # Conversation Engine
                self.conversation_engine = VoiceConversationEngine(
                    openai_client=openai.AsyncOpenAI(api_key=config['openai_api_key']),
                    business_intelligence=self.business_intelligence,
                    contract_method=self.contract_method
                )
                self.service_status['conversation_engine'] = True
                logger.info("✅ Conversation Engine initialized")
            else:
                logger.warning("⚠️ Voice services skipped (no OpenAI API key)")
                self.service_status['voice_processor'] = False
                self.service_status['conversation_engine'] = False
                
        except Exception as e:
            logger.error(f"❌ Voice services initialization failed: {e}")
            self.service_status['voice_processor'] = False
            self.service_status['conversation_engine'] = False
    
    async def _initialize_business_intelligence(self):
        """Initialize business intelligence service"""
        try:
            if self.llm_provider:
                self.business_intelligence = BusinessIntelligence(
                    llm_provider=self.llm_provider
                )
                self.service_status['business_intelligence'] = True
                logger.info("✅ Business Intelligence initialized")
            else:
                logger.warning("⚠️ Business Intelligence skipped (no LLM provider)")
                self.service_status['business_intelligence'] = False
        except Exception as e:
            logger.error(f"❌ Business Intelligence initialization failed: {e}")
            self.service_status['business_intelligence'] = False
    
    async def _initialize_dream_engine(self):
        """Initialize dream engine for code generation"""
        try:
            if self.llm_provider:
                self.dream_engine = DreamEngine(
                    llm_provider=self.llm_provider,
                    business_intelligence=self.business_intelligence,
                    security_validator=self.security_validator
                )
                self.service_status['dream_engine'] = True
                logger.info("✅ Dream Engine initialized")
            else:
                logger.warning("⚠️ Dream Engine skipped (no LLM provider)")
                self.service_status['dream_engine'] = False
        except Exception as e:
            logger.error(f"❌ Dream Engine initialization failed: {e}")
            self.service_status['dream_engine'] = False
    
    async def _initialize_debug_engine(self):
        """Initialize debug engine"""
        try:
            if self.llm_provider:
                self.debug_engine = DebugEngine(
                    llm_provider=self.llm_provider,
                    github_integration=None  # Will be set after GitHub init
                )
                self.service_status['debug_engine'] = True
                logger.info("✅ Debug Engine initialized")
            else:
                logger.warning("⚠️ Debug Engine skipped (no LLM provider)")
                self.service_status['debug_engine'] = False
        except Exception as e:
            logger.error(f"❌ Debug Engine initialization failed: {e}")
            self.service_status['debug_engine'] = False
    
    async def _initialize_github_integration(self, config: Dict[str, Any]):
        """Initialize GitHub integration"""
        try:
            if config['github_token']:
                self.github_integration = GitHubIntegration(
                    github_token=config['github_token']
                )
                # Update debug engine with GitHub integration
                if self.debug_engine:
                    self.debug_engine.github_integration = self.github_integration
                self.service_status['github_integration'] = True
                logger.info("✅ GitHub Integration initialized")
            else:
                logger.warning("⚠️ GitHub Integration skipped (no token)")
                self.service_status['github_integration'] = False
        except Exception as e:
            logger.error(f"❌ GitHub Integration initialization failed: {e}")
            self.service_status['github_integration'] = False
    
    async def _initialize_smart_contracts(self, config: Dict[str, Any]):
        """Initialize smart contract system"""
        try:
            if config['web3_provider_url']:
                self.smart_contract_system = SmartContractSystem(
                    web3_provider_url=config['web3_provider_url'],
                    platform_wallet_address=config['smart_contract_address'] or "0x0000000000000000000000000000000000000000"
                )
                self.service_status['smart_contract_system'] = True
                logger.info("✅ Smart Contract System initialized")
            else:
                logger.warning("⚠️ Smart Contract System skipped (no Web3 provider)")
                self.service_status['smart_contract_system'] = False
        except Exception as e:
            logger.error(f"❌ Smart Contract System initialization failed: {e}")
            self.service_status['smart_contract_system'] = False
    
    async def _initialize_project_management(self):
        """Initialize project and deployment managers"""
        try:
            # Project Manager
            self.project_manager = ProjectManager(
                db_pool=self.db_pool,
                github_integration=self.github_integration
            )
            self.service_status['project_manager'] = True
            logger.info("✅ Project Manager initialized")
            
            # Deployment Manager
            self.deployment_manager = DeploymentManager(
                github_integration=self.github_integration,
                project_manager=self.project_manager
            )
            self.service_status['deployment_manager'] = True
            logger.info("✅ Deployment Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Project management initialization failed: {e}")
            self.service_status['project_manager'] = False
            self.service_status['deployment_manager'] = False
    
    async def _initialize_monaco_integration(self):
        """Initialize Monaco editor integration"""
        try:
            self.monaco_integration = MonacoIntegration(
                github_integration=self.github_integration,
                debug_engine=self.debug_engine
            )
            self.service_status['monaco_integration'] = True
            logger.info("✅ Monaco Integration initialized")
        except Exception as e:
            logger.error(f"❌ Monaco Integration initialization failed: {e}")
            self.service_status['monaco_integration'] = False
    
    def _log_initialization_summary(self):
        """Log summary of initialization results"""
        logger.info("\n" + "="*50)
        logger.info("🎯 SERVICE INITIALIZATION SUMMARY")
        logger.info("="*50)
        
        total_services = len(self.service_status)
        initialized_services = sum(1 for status in self.service_status.values() if status)
        
        for service, status in self.service_status.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {service.replace('_', ' ').title()}")
        
        logger.info("="*50)
        logger.info(f"📊 Total: {initialized_services}/{total_services} services initialized")
        
        if initialized_services == total_services:
            logger.info("🎉 All services initialized successfully!")
        elif initialized_services > 0:
            logger.info("⚠️ Running with partial functionality")
        else:
            logger.error("❌ No services initialized - check configuration!")
        logger.info("="*50 + "\n")
    
    async def get_db_connection(self) -> asyncpg.Connection:
        """Get a database connection from the pool"""
        if not self.db_pool:
            raise RuntimeError("Database pool not initialized")
        return await self.db_pool.acquire()
    
    def check_service(self, service_name: str) -> bool:
        """Check if a service is available"""
        return self.service_status.get(service_name, False)
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("🧹 Cleaning up services...")
        
        if self.db_pool:
            await self.db_pool.close()
            logger.info("✅ Database pool closed")
        
        # Add other cleanup as needed
        logger.info("✅ Cleanup complete")

# Create singleton instance
service_manager = ServiceManager()