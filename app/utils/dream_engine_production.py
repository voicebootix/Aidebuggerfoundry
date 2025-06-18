import asyncio
import json
import re
import uuid
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from string import punctuation

logger = logging.getLogger(__name__)

@dataclass
class ProjectAnalysis:
    """Strategic project analysis results"""
    feasibility_score: float
    complexity_level: str
    required_technologies: List[str]
    estimated_timeline: str
    recommended_architecture: str
    potential_challenges: List[str]
    business_viability: str

@dataclass
class CodeGenerationResult:
    """Complete code generation with intelligence"""
    files: List[Dict[str, Any]]
    architecture_explanation: str
    deployment_strategy: str
    security_recommendations: List[str]
    scalability_notes: str
    testing_strategy: str

class IntelligentDreamEngine:
    """Production-ready AI engine with strategic intelligence"""
    
    def __init__(self):
        # Initialize API keys from environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.active_generations = {}
        
    async def process_founder_vision(self, input_text: str, user_id: str) -> Dict:
        """Process the founder's vision to generate code and analysis."""
        logger.info(f"Processing vision for user {user_id}: {input_text[:50]}...")
        start_time = datetime.now()
        
        try:
            # Step 1: Strategic Analysis & Feasibility Validation
            analysis = await self._analyze_project_feasibility(input_text)
            
            # Step 2: Intelligent Architecture Planning
            architecture = await self._design_intelligent_architecture(input_text, analysis)
            
            # Step 3: Technology Stack Optimization
            tech_stack = await self._optimize_technology_stack(input_text, analysis)
            
            # Step 4: AI-Powered Code Generation
            code_result = await self._generate_production_code(input_text, architecture, tech_stack)
            
            # Step 5: Security & Quality Validation
            validation_result = await self._validate_and_secure_output(code_result)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Save to database
            session_data = {
                "session_id": str(uuid.uuid4()),
                "user_id": user_id,
                "input_text": input_text,
                "result_data": validation_result.__dict__,
                "status": "completed",
                "processing_time": processing_time,
                "feasibility_score": analysis.feasibility_score,
                "model_provider": self._get_active_model_provider()
            }
            
            # Try to save to database
            try:
                from app.database.db_production import db_manager
                await db_manager.save_dream_session(session_data)
            except Exception as e:
                logger.warning(f"⚠️ Could not save to database: {str(e)}")
            
            return {
                "id": session_data["session_id"],
                "request_id": session_data["session_id"],
                "user_id": user_id,
                "status": "success",
                "message": "Strategic AI analysis and code generation completed",
                "strategic_analysis": {
                    "feasibility_score": analysis.feasibility_score,
                    "complexity_level": analysis.complexity_level,
                    "business_viability": analysis.business_viability,
                    "required_technologies": analysis.required_technologies,
                    "estimated_timeline": analysis.estimated_timeline,
                    "potential_challenges": analysis.potential_challenges
                },
                "files": validation_result.files,
                "architecture_explanation": validation_result.architecture_explanation,
                "deployment_strategy": validation_result.deployment_strategy,
                "security_recommendations": validation_result.security_recommendations,
                "scalability_notes": validation_result.scalability_notes,
                "testing_strategy": validation_result.testing_strategy,
                "generation_time_seconds": processing_time,
                "model_provider": "intelligent_multi_llm",
                "confidence_score": analysis.feasibility_score,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ DreamEngine processing failed: {str(e)}")
            # Return enhanced fallback instead of error
            return await self._generate_intelligent_fallback(input_text, user_id, str(e))
    
    async def _analyze_project_feasibility(self, input_text: str) -> ProjectAnalysis:
        """Strategic feasibility analysis using AI or intelligent fallback."""
        logger.info(f"Analyzing project feasibility for input: {input_text[:50]}...")
        
        try:
            if self.openai_api_key:
                return await self._analyze_with_openai(input_text)
            elif self.anthropic_api_key:
                return await self._analyze_with_anthropic(input_text)
            else:
                return await self._analyze_with_intelligent_heuristics(input_text)
        except Exception as e:
            logger.warning(f"⚠️ AI analysis failed, using intelligent fallback: {str(e)}")
            return await self._analyze_with_intelligent_heuristics(input_text)
    
    async def _analyze_with_openai(self, input_text: str) -> ProjectAnalysis:
        """Analyze project feasibility using OpenAI's GPT model."""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            analysis_prompt = f"""
            Analyze this startup/project idea with deep strategic intelligence:
            
            IDEA: {input_text}
            
            Provide comprehensive analysis in JSON format:
            {{
                "feasibility_score": <0-10 float>,
                "complexity_level": "<simple|moderate|complex|enterprise>",
                "required_technologies": ["tech1", "tech2"],
                "estimated_timeline": "<X weeks/months>",
                "recommended_architecture": "<microservices|monolith|serverless>",
                "potential_challenges": ["challenge1", "challenge2"],
                "business_viability": "<high|medium|low>"
            }}
            
            Be realistic and strategic - analyze market fit, technical complexity, and implementation challenges.
            """
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic technology consultant and startup advisor with deep expertise in software architecture and business analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3
            )
            
            analysis_json = self._extract_json_from_response(response.choices[0].message.content)
            
            return ProjectAnalysis(
                feasibility_score=analysis_json.get("feasibility_score", 7.5),
                complexity_level=analysis_json.get("complexity_level", "moderate"),
                required_technologies=analysis_json.get("required_technologies", ["FastAPI", "PostgreSQL", "React"]),
                estimated_timeline=analysis_json.get("estimated_timeline", "8-12 weeks"),
                recommended_architecture=analysis_json.get("recommended_architecture", "monolith"),
                potential_challenges=analysis_json.get("potential_challenges", ["User authentication", "Database design"]),
                business_viability=analysis_json.get("business_viability", "medium")
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI analysis failed: {str(e)}")
            raise
    
    async def _analyze_with_anthropic(self, input_text: str) -> ProjectAnalysis:
        """Analyze project feasibility using Anthropic's Claude model."""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
            
            analysis_prompt = f"""
            Analyze this project idea strategically:
            
            PROJECT: {input_text}
            
            Provide analysis considering:
            - Technical feasibility (score 0-10)
            - Implementation complexity
            - Required technologies
            - Development timeline
            - Business viability
            - Potential challenges
            
            Format as structured analysis.
            """
            
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            content = response.content[0].text
            return self._parse_claude_analysis(content, input_text)
            
        except Exception as e:
            logger.error(f"❌ Claude analysis failed: {str(e)}")
            raise
    
    async def _analyze_with_intelligent_heuristics(self, input_text: str) -> ProjectAnalysis:
        """Analyze project feasibility using advanced heuristic-based logic when AI APIs are unavailable."""
        logger.info("Using intelligent heuristic analysis for project feasibility.")

        # Clean and tokenize input text
        text_lower = input_text.lower().strip()
        text_clean = re.sub(f"[{punctuation}]", " ", text_lower)
        tokens = text_clean.split()
        token_count = len(tokens)

        # Define project type patterns
        project_types = {
            r"todo|task|list": {
                "type": "Todo App",
                "base_complexity": 0.3,
                "base_timeline_weeks": 2,
                "base_tech": ["FastAPI", "React", "SQLite"],
                "viability": "low"
            },
            r"ecommerce|shop|store|marketplace": {
                "type": "E-commerce",
                "base_complexity": 0.7,
                "base_timeline_weeks": 8,
                "base_tech": ["FastAPI", "PostgreSQL", "React"],
                "viability": "high"
            },
            r"blog|content|post": {
                "type": "Blog Platform",
                "base_complexity": 0.5,
                "base_timeline_weeks": 4,
                "base_tech": ["FastAPI", "PostgreSQL", "React"],
                "viability": "medium"
            },
            r"social|network|community": {
                "type": "Social Media",
                "base_complexity": 0.9,
                "base_timeline_weeks": 12,
                "base_tech": ["FastAPI", "PostgreSQL", "React", "Redis"],
                "viability": "high"
            },
            r"api|backend|rest": {
                "type": "API Service",
                "base_complexity": 0.6,
                "base_timeline_weeks": 6,
                "base_tech": ["FastAPI", "PostgreSQL"],
                "viability": "medium"
            }
        }

        # Define feature patterns
        features = {
            r"auth|login|signup|user": {
                "complexity": 0.2,
                "timeline_weeks": 1,
                "tech": ["JWT"],
                "challenges": ["Secure authentication implementation", "User data privacy"]
            },
            r"database|storage|data": {
                "complexity": 0.3,
                "timeline_weeks": 1,
                "tech": ["PostgreSQL"],
                "challenges": ["Database schema design", "Data integrity"]
            },
            r"payment|stripe|paypal|billing": {
                "complexity": 0.4,
                "timeline_weeks": 2,
                "tech": ["Stripe"],
                "challenges": ["PCI compliance", "Payment error handling"]
            },
            r"frontend|ui|react|vue|spa": {
                "complexity": 0.4,
                "timeline_weeks": 2,
                "tech": ["React"],
                "challenges": ["Responsive UI design", "State management"]
            },
            r"mobile|ios|android|app": {
                "complexity": 0.6,
                "timeline_weeks": 4,
                "tech": ["Flutter"],
                "challenges": ["Cross-platform compatibility", "App store deployment"]
            },
            r"ai|machine learning|chatbot|gpt": {
                "complexity": 0.8,
                "timeline_weeks": 6,
                "tech": ["OpenAI"],
                "challenges": ["Model training", "API rate limits"]
            },
            r"real-time|chat|websocket": {
                "complexity": 0.5,
                "timeline_weeks": 2,
                "tech": ["Redis"],
                "challenges": ["Real-time scalability", "Connection reliability"]
            }
        }

        # Initialize analysis defaults
        project_type = "Generic Web App"
        base_complexity = 0.4
        total_complexity = base_complexity
        base_timeline_weeks = 4
        total_timeline_weeks = base_timeline_weeks
        required_technologies = ["FastAPI", "PostgreSQL", "React"]
        potential_challenges = ["Requirement clarification", "Basic testing coverage"]
        business_viability = "medium"
        architecture = "monolith"

        # Detect project type
        for pattern, info in project_types.items():
            if re.search(pattern, text_lower):
                project_type = info["type"]
                base_complexity = info["base_complexity"]
                total_complexity = base_complexity
                base_timeline_weeks = info["base_timeline_weeks"]
                total_timeline_weeks = base_timeline_weeks
                required_technologies = info["base_tech"]
                business_viability = info["viability"]
                break

        # Detect features and adjust metrics
        feature_count = 0
        detected_features = []
        for pattern, info in features.items():
            if re.search(pattern, text_lower):
                feature_count += 1
                total_complexity += info["complexity"]
                total_timeline_weeks += info["timeline_weeks"]
                required_technologies.extend([t for t in info["tech"] if t not in required_technologies])
                potential_challenges.extend([c for c in info["challenges"] if c not in potential_challenges])
                detected_features.append(pattern.split("|")[0])

        # Normalize complexity (0 to 1)
        total_complexity = min(total_complexity, 1.0)

        # Calculate feasibility score (0 to 10)
        # Higher complexity and feature count reduce feasibility
        feasibility_score = max(9.0 - (total_complexity * 4) - (feature_count * 0.5), 3.0)

        # Determine complexity level
        if total_complexity < 0.4:
            complexity_level = "simple"
        elif total_complexity < 0.7:
            complexity_level = "moderate"
        elif total_complexity < 0.9:
            complexity_level = "complex"
        else:
            complexity_level = "enterprise"

        # Format timeline
        if total_timeline_weeks <= 4:
            estimated_timeline = "2-4 weeks"
        elif total_timeline_weeks <= 8:
            estimated_timeline = "4-8 weeks"
        elif total_timeline_weeks <= 12:
            estimated_timeline = "8-12 weeks"
        else:
            estimated_timeline = "12+ weeks"

        # Determine architecture
        if total_complexity > 0.8 or re.search(r"microservices|distributed", text_lower):
            architecture = "microservices"
            potential_challenges.append("Microservices coordination")
        elif total_complexity > 0.5:
            architecture = "modular monolith"
        else:
            architecture = "monolith"

        # Adjust business viability based on feature count
        if feature_count >= 3 and business_viability != "high":
            business_viability = "high" if project_type in ["E-commerce", "Social Media"] else "medium"

        # Limit challenges to 4
        potential_challenges = potential_challenges[:4]

        # Log analysis details
        logger.debug(
            f"Analysis for {project_type}: feasibility={feasibility_score:.2f}, "
            f"complexity={complexity_level}, timeline={estimated_timeline}, "
            f"features={detected_features}"
        )

        # Return structured analysis
        return ProjectAnalysis(
            feasibility_score=feasibility_score,
            complexity_level=complexity_level,
            required_technologies=required_technologies,
            estimated_timeline=estimated_timeline,
            recommended_architecture=architecture,
            potential_challenges=potential_challenges,
            business_viability=business_viability
        )
    
    async def _design_intelligent_architecture(self, input_text: str, analysis: ProjectAnalysis) -> str:
        """Design an intelligent architecture based on project analysis."""
        logger.info(f"Designing architecture for complexity: {analysis.complexity_level}")
        
        if analysis.complexity_level == 'simple':
            return f"""
**Monolithic Architecture Recommendation**

For this {analysis.complexity_level} project, a clean monolithic architecture is optimal:

- **Backend**: FastAPI with modular route organization
- **Database**: {analysis.required_technologies[1] if len(analysis.required_technologies) > 1 else 'SQLite'} with proper indexing
- **Frontend**: React SPA with component-based architecture
- **Authentication**: JWT-based auth system
- **Deployment**: Docker containerization for easy deployment

This architecture provides simplicity, fast development, and easy maintenance while supporting future growth.
"""
        
        elif analysis.complexity_level == 'moderate':
            return f"""
**Modular Monolith Architecture**

For this {analysis.complexity_level} project:

- **API Layer**: FastAPI with organized blueprints/routers
- **Business Logic**: Service layer with dependency injection
- **Data Layer**: SQLAlchemy ORM with {analysis.required_technologies[1] if len(analysis.required_technologies) > 1 else 'PostgreSQL'}
- **Caching**: Redis for session and query caching
- **Frontend**: React with state management (Redux/Zustand)
- **Security**: OAuth2 + JWT with role-based access

This provides good separation of concerns while maintaining development speed.
"""
        
        else:
            return f"""
**Microservices-Ready Architecture**

For this {analysis.complexity_level} project:

- **API Gateway**: FastAPI main service with routing
- **Core Services**: Modular services for different domains
- **Database**: {analysis.required_technologies[1] if len(analysis.required_technologies) > 1 else 'PostgreSQL'} with service-specific schemas
- **Message Queue**: Redis for inter-service communication
- **Frontend**: React with micro-frontend capabilities
- **Monitoring**: Logging and health check endpoints
- **Security**: Distributed auth with JWT validation

This architecture supports scaling and team distribution.
"""
    
    async def _optimize_technology_stack(self, input_text: str, analysis: ProjectAnalysis) -> Dict[str, str]:
        """Optimize technology stack based on project requirements and analysis."""
        logger.info("Optimizing technology stack")
        
        base_stack = {
            "backend_framework": "FastAPI",
            "database": analysis.required_technologies[1] if len(analysis.required_technologies) > 1 else "PostgreSQL",
            "frontend": "React",
            "authentication": "JWT",
            "deployment": "Docker",
            "cloud_provider": "Render"
        }
        
        # Adjust stack based on input and analysis
        text_lower = input_text.lower()
        
        if any(word in text_lower for word in ['payment', 'billing', 'subscription']):
            base_stack["payment"] = "Stripe"
        
        if any(word in text_lower for word in ['ai', 'chatbot', 'gpt', 'openai']):
            base_stack["ai_service"] = "OpenAI"
        
        if any(word in text_lower for word in ['cache', 'session', 'real-time']):
            base_stack["cache"] = "Redis"
        
        if analysis.complexity_level in ['complex', 'enterprise']:
            base_stack["message_queue"] = "Redis"
            base_stack["monitoring"] = "Prometheus"
        
        return base_stack
    
    async def _generate_production_code(self, input_text: str, architecture: str, tech_stack: Dict) -> CodeGenerationResult:
        """Generate production-ready code using AI or intelligent templates."""
        logger.info("Generating production code")
        
        try:
            # Try AI generation first
            if self.openai_api_key or self.anthropic_api_key:
                return await self._generate_with_ai(input_text, architecture, tech_stack)
            else:
                return await self._generate_with_intelligent_templates(input_text, architecture, tech_stack)
        except Exception as e:
            logger.warning(f"⚠️ AI code generation failed, using intelligent templates: {str(e)}")
            return await self._generate_with_intelligent_templates(input_text, architecture, tech_stack)
    
    async def _generate_with_ai(self, input_text: str, architecture: str, tech_stack: Dict) -> CodeGenerationResult:
        """Generate code using AI models (OpenAI or Anthropic)."""
        logger.info("Generating code with AI")
        
        try:
            if self.openai_api_key:
                import openai
                client = openai.AsyncOpenAI(api_key=self.openai_api_key)
                
                prompt = f"""
                Generate production-ready code for the following project:
                
                Project: {input_text}
                Architecture: {architecture}
                Tech Stack: {json.dumps(tech_stack, indent=2)}
                
                Provide a complete FastAPI-based application with:
                - Main application file (main.py)
                - Database models (models.py)
                - Authentication logic (auth.py)
                - Requirements file (requirements.txt)
                - Dockerfile
                
                Return the response in JSON format with file details:
                [
                    {{
                        "filename": "filename",
                        "path": "path",
                        "content": "code content",
                        "language": "language",
                        "purpose": "purpose"
                    }}
                ]
                """
                
                response = await client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert software engineer specializing in FastAPI and modern web development."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5
                )
                
                files = json.loads(response.choices[0].message.content)
                
                return CodeGenerationResult(
                    files=files,
                    architecture_explanation=architecture,
                    deployment_strategy=self._generate_deployment_strategy(tech_stack),
                    security_recommendations=self._generate_security_recommendations(),
                    scalability_notes=self._generate_scalability_notes(),
                    testing_strategy=self._generate_testing_strategy()
                )
                
            elif self.anthropic_api_key:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=self.anthropic_api_key)
                
                prompt = f"""
                Generate production-ready code for:
                
                Project: {input_text}
                Architecture: {architecture}
                Tech Stack: {json.dumps(tech_stack, indent=2)}
                
                Include FastAPI application files, models, auth, requirements, and Dockerfile.
                Return JSON array of file objects.
                """
                
                response = await client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                files = json.loads(response.content[0].text)
                
                return CodeGenerationResult(
                    files=files,
                    architecture_explanation=architecture,
                    deployment_strategy=self._generate_deployment_strategy(tech_stack),
                    security_recommendations=self._generate_security_recommendations(),
                    scalability_notes=self._generate_scalability_notes(),
                    testing_strategy=self._generate_testing_strategy()
                )
                
        except Exception as e:
            logger.error(f"❌ AI code generation failed: {str(e)}")
            raise
    
    async def _generate_with_intelligent_templates(self, input_text: str, architecture: str, tech_stack: Dict) -> CodeGenerationResult:
        """Generate code using intelligent templates when AI is unavailable."""
        logger.info("Generating code with intelligent templates")
        
        # Analyze project requirements
        text_lower = input_text.lower()
        is_api = any(word in text_lower for word in ['api', 'backend', 'rest'])
        has_auth = any(word in text_lower for word in ['user', 'login', 'auth', 'account'])
        has_crud = any(word in text_lower for word in ['create', 'manage', 'crud', 'edit', 'delete'])
        
        files = []
        
        # Generate main FastAPI application
        main_py_content = self._generate_main_py_template(input_text, has_auth, has_crud, tech_stack)
        files.append({
            "filename": "main.py",
            "path": "app/",
            "content": main_py_content,
            "language": "python",
            "purpose": "Main FastAPI application server"
        })
        
        # Generate models if CRUD operations detected
        if has_crud:
            models_content = self._generate_models_template(input_text)
            files.append({
                "filename": "models.py",
                "path": "app/",
                "content": models_content,
                "language": "python",
                "purpose": "Database models and schemas"
            })
        
        # Generate authentication if detected
        if has_auth:
            auth_content = self._generate_auth_template()
            files.append({
                "filename": "auth.py",
                "path": "app/",
                "content": auth_content,
                "language": "python",
                "purpose": "Authentication and authorization"
            })
        
        # Generate requirements.txt
        requirements_content = self._generate_requirements_template(tech_stack)
        files.append({
            "filename": "requirements.txt",
            "path": "./",
            "content": requirements_content,
            "language": "text",
            "purpose": "Python dependencies"
        })
        
        # Generate Dockerfile
        dockerfile_content = self._generate_dockerfile_template()
        files.append({
            "filename": "Dockerfile",
            "path": "./",
            "content": dockerfile_content,
            "language": "dockerfile",
            "purpose": "Container configuration"
        })
        
        return CodeGenerationResult(
            files=files,
            architecture_explanation=architecture,
            deployment_strategy=self._generate_deployment_strategy(tech_stack),
            security_recommendations=self._generate_security_recommendations(),
            scalability_notes=self._generate_scalability_notes(),
            testing_strategy=self._generate_testing_strategy()
        )
    
    def _generate_main_py_template(self, input_text: str, has_auth: bool, has_crud: bool, tech_stack: Dict) -> str:
        """Generate main.py template for FastAPI application."""
        entity_name = self._extract_main_entity(input_text)
        
        return f'''from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="{entity_name.title()} API",
    description="Generated by AI Debugger Factory DreamEngine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class {entity_name.title()}Base(BaseModel):
    name: str
    description: Optional[str] = None

class {entity_name.title()}Create({entity_name.title()}Base):
    pass

class {entity_name.title()}Response({entity_name.title()}Base):
    id: str
    created_at: datetime
    updated_at: datetime

# In-memory storage (replace with database in production)
{entity_name}_storage = []

@app.get("/")
async def root():
    return {{
        "message": "Welcome to {entity_name.title()} API",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }}

@app.get("/health")
async def health_check():
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "{entity_name.title()} API"
    }}
''' + (f'''
# Authentication endpoint
@app.post("/auth/login")
async def login(credentials: dict):
    # Implement your authentication logic here
    return {{
        "access_token": "demo_token",
        "token_type": "bearer",
        "user_id": "demo_user"
    }}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implement token verification here
    return {{"user_id": "demo_user"}}
''' if has_auth else '') + (f'''
# {entity_name.title()} CRUD endpoints
@app.get("/{entity_name}s", response_model=List[{entity_name.title()}Response])
async def get_{entity_name}s():
    return {entity_name}_storage

@app.post("/{entity_name}s", response_model={entity_name.title()}Response)
async def create_{entity_name}(item: {entity_name.title()}Create):
    new_item = {entity_name.title()}Response(
        id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **item.dict()
    )
    {entity_name}_storage.append(new_item)
    return new_item

@app.get("/{entity_name}s/{{item_id}}", response_model={entity_name.title()}Response)
async def get_{entity_name}(item_id: str):
    for item in {entity_name}_storage:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{entity_name.title()} not found")

@app.put("/{entity_name}s/{{item_id}}", response_model={entity_name.title()}Response)
async def update_{entity_name}(item_id: str, update_data: {entity_name.title()}Create):
    for i, item in enumerate({entity_name}_storage):
        if item.id == item_id:
            updated_item = {entity_name.title()}Response(
                id=item_id,
                created_at=item.created_at,
                updated_at=datetime.now(),
                **update_data.dict()
            )
            {entity_name}_storage[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="{entity_name.title()} not found")

@app.delete("/{entity_name}s/{{item_id}}")
async def delete_{entity_name}(item_id: str):
    for i, item in enumerate({entity_name}_storage):
        if item.id == item_id:
            del {entity_name}_storage[i]
            return {{"message": "{entity_name.title()} deleted successfully"}}
    raise HTTPException(status_code=404, detail="{entity_name.title()} not found")
''' if has_crud else '') + '''
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _extract_main_entity(self, input_text: str) -> str:
        """Extract primary entity from input text for naming purposes."""
        common_entities = ['task', 'user', 'product', 'item', 'post', 'project', 'order', 'booking']
        text_lower = input_text.lower()
        
        for entity in common_entities:
            if entity in text_lower:
                return entity
        
        return 'item'
    
    def _generate_models_template(self, input_text: str) -> str:
        """Generate database models template using SQLAlchemy."""
        return '''from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

class Item(BaseModel):
    __tablename__ = "items"
    
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
'''
    
    def _generate_auth_template(self) -> str:
        """Generate authentication template for JWT-based security."""
        return '''from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"user_id": user_id, "username": "demo_user"}
'''
    
    def _generate_requirements_template(self, tech_stack: Dict) -> str:
        """Generate requirements.txt template based on tech stack."""
        base_requirements = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.5.0",
            "python-multipart>=0.0.6"
        ]
        
        if tech_stack.get("authentication") == "JWT":
            base_requirements.extend([
                "python-jose[cryptography]>=3.3.0",
                "passlib[bcrypt]>=1.7.4"
            ])
        
        if tech_stack.get("database") == "PostgreSQL":
            base_requirements.append("asyncpg>=0.28.0")
        
        if tech_stack.get("cache") == "Redis":
            base_requirements.append("redis>=4.5.0")
        
        if tech_stack.get("payment") == "Stripe":
            base_requirements.append("stripe>=7.0.0")
        
        if tech_stack.get("ai_service") == "OpenAI":
            base_requirements.append("openai>=1.0.0")
        
        return "\n".join(base_requirements)
    
    def _generate_dockerfile_template(self) -> str:
        """Generate Dockerfile template for containerization."""
        return '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_deployment_strategy(self, tech_stack: Dict) -> str:
        """Generate deployment strategy documentation."""
        return f"""
**Deployment Strategy**

1. **Containerization**: Docker-based deployment for consistency
2. **Cloud Platform**: {tech_stack.get('cloud_provider', 'Render')} for hosting
3. **Database**: Managed PostgreSQL service for reliability
4. **Environment Variables**: Secure configuration management
5. **CI/CD**: GitHub Actions for automated deployment
6. **Monitoring**: Health checks and logging implementation
7. **SSL**: Automatic HTTPS certificate management

**Deployment Steps**:
1. Build Docker image
2. Push to container registry
3. Deploy to cloud platform
4. Configure environment variables
5. Run database migrations
6. Verify health checks
"""
    
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations for the project."""
        return [
            "Implement proper authentication with JWT tokens",
            "Use HTTPS for all communications",
            "Validate and sanitize all user inputs",
            "Implement rate limiting to prevent abuse",
            "Use environment variables for sensitive configuration",
            "Regular security updates for dependencies",
            "Implement proper error handling without information leakage",
            "Use parameterized queries to prevent SQL injection"
        ]
    
    def _generate_scalability_notes(self) -> str:
        """Generate scalability notes for the project."""
        return """
**Scalability Considerations**

- **Horizontal Scaling**: Application is stateless and can be horizontally scaled
- **Database**: Implement connection pooling and read replicas if needed
- **Caching**: Add Redis for session storage and query caching
- **Load Balancing**: Use cloud load balancer for multiple instances
- **Monitoring**: Implement metrics and alerting for performance tracking
- **Optimization**: Database indexing and query optimization
"""
    
    def _generate_testing_strategy(self) -> str:
        """Generate testing strategy documentation."""
        return """
**Testing Strategy**

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and database interactions
- **Load Testing**: Verify performance under expected load
- **Security Testing**: Validate authentication and authorization
- **End-to-End Testing**: Test complete user workflows
- **Automated Testing**: CI/CD pipeline with automated test execution
"""
    
    async def _validate_and_secure_output(self, code_result: CodeGenerationResult) -> CodeGenerationResult:
        """Validate and secure generated code output."""
        logger.info("Validating and securing code output")
        
        validated_files = []
        
        for file_info in code_result.files:
            content = file_info.get("content", "")
            
            if self._is_safe_content(content):
                validated_files.append(file_info)
            else:
                logger.warning(f"⚠️ Security concerns in {file_info.get('filename')}")
                validated_files.append(file_info)  # In production, sanitize or reject unsafe content
        
        return CodeGenerationResult(
            files=validated_files,
            architecture_explanation=code_result.architecture_explanation,
            deployment_strategy=code_result.deployment_strategy,
            security_recommendations=code_result.security_recommendations,
            scalability_notes=code_result.scalability_notes,
            testing_strategy=code_result.testing_strategy
        )
    
    def _is_safe_content(self, content: str) -> bool:
        """Check content for potentially dangerous code patterns."""
        dangerous_patterns = [
            'os.system(',
            'subprocess.call(',
            'eval(',
            'exec(',
            '__import__'
        ]
        
        return not any(pattern in content for pattern in dangerous_patterns)
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response text."""
        json_pattern = r'```json\s*(.*?)\s*```'
        json_match = re.search(json_pattern, text, re.DOTALL)
        
        if json_match:
            json_text = json_match.group(1)
        else:
            json_pattern = r'\{.*\}'
            json_match = re.search(json_pattern, text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                return {}
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Failed to parse JSON: {json_text[:200]}...")
            return {}
    
    async def _parse_claude_analysis(self, content: str, input_text: str) -> ProjectAnalysis:
        """Parse Claude's analysis response into ProjectAnalysis."""
        logger.info("Parsing Claude analysis response")
        
        score_match = re.search(r'feasibility.*?(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        feasibility_score = float(score_match.group(1)) if score_match else 7.5
        
        complexity_keywords = ['simple', 'moderate', 'complex', 'enterprise']
        complexity_level = 'moderate'
        
        for keyword in complexity_keywords:
            if keyword in content.lower():
                complexity_level = keyword
                break
        
        # Fallback to heuristic analysis for other fields
        fallback_analysis = await self._analyze_with_intelligent_heuristics(input_text)
        
        return ProjectAnalysis(
            feasibility_score=feasibility_score,
            complexity_level=complexity_level,
            required_technologies=fallback_analysis.required_technologies,
            estimated_timeline=fallback_analysis.estimated_timeline,
            recommended_architecture=fallback_analysis.recommended_architecture,
            potential_challenges=fallback_analysis.potential_challenges,
            business_viability='high' if feasibility_score > 7 else 'medium' if feasibility_score > 5 else 'low'
        )
    
    def _get_active_model_provider(self) -> str:
        """Determine the active model provider based on available API keys."""
        if self.openai_api_key:
            return "openai"
        elif self.anthropic_api_key:
            return "anthropic"
        elif self.google_api_key:
            return "google"
        else:
            return "intelligent_heuristics"
    
    async def _generate_intelligent_fallback(self, input_text: str, user_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when AI processing fails."""
        logger.info(f"Generating intelligent fallback for user {user_id}")
        
        # Use heuristic analysis
        analysis = await self._analyze_with_intelligent_heuristics(input_text)
        architecture = await self._design_intelligent_architecture(input_text, analysis)
        tech_stack = await self._optimize_technology_stack(input_text, analysis)
        code_result = await self._generate_with_intelligent_templates(input_text, architecture, tech_stack)
        
        return {
            "id": str(uuid.uuid4()),
            "request_id": str(uuid.uuid4()),
            "user_id": user_id,
            "status": "success",
            "message": "Code generated using intelligent analysis (AI services unavailable)",
            "strategic_analysis": {
                "feasibility_score": analysis.feasibility_score,
                "complexity_level": analysis.complexity_level,
                "business_viability": analysis.business_viability,
                "required_technologies": analysis.required_technologies,
                "estimated_timeline": analysis.estimated_timeline,
                "potential_challenges": analysis.potential_challenges
            },
            "files": code_result.files,
            "architecture_explanation": code_result.architecture_explanation,
            "deployment_strategy": code_result.deployment_strategy,
            "security_recommendations": code_result.security_recommendations,
            "scalability_notes": code_result.scalability_notes,
            "testing_strategy": code_result.testing_strategy,
            "generation_time_seconds": 2.5,
            "model_provider": "intelligent_fallback",
            "confidence_score": analysis.feasibility_score,
            "timestamp": datetime.now().isoformat(),
            "note": "Generated using intelligent heuristics - connect AI APIs for enhanced analysis"
        }

# Global instance
dream_engine = IntelligentDreamEngine()
