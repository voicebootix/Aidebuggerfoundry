"""
DreamEngine - Enhanced Strategic Analysis and Code Generation
Converts founder conversations into production-ready applications
Enhanced with business intelligence integration
"""

import asyncio
import json
import uuid
import os
import tempfile
import zipfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import openai
from dataclasses import dataclass
import re

@dataclass
class StrategicAnalysis:
    business_context: Dict
    technical_requirements: Dict
    architecture_recommendations: Dict
    implementation_strategy: Dict
    risk_assessment: Dict
    timeline_estimate: str

@dataclass
class GeneratedFile:
    filename: str
    content: str
    file_type: str
    description: str

@dataclass
class CodeGenerationResult:
    project_structure: Dict
    generated_files: List[GeneratedFile]
    deployment_instructions: str
    testing_guide: str
    quality_score: float

class DreamEngine:
    """Enhanced strategic analysis and code generation engine"""
    
    def __init__(self, llm_provider, business_intelligence, security_validator):
        self.llm_provider = llm_provider
        self.business_intelligence = business_intelligence
        self.security_validator = security_validator
        self.generation_templates = self._load_generation_templates()
        
    async def analyze_strategic_requirements(self, founder_agreement: Dict) -> StrategicAnalysis:
        """Comprehensive strategic analysis of founder requirements"""
        
        business_spec = founder_agreement.get("business_specification", {})
        ai_commitments = founder_agreement.get("ai_commitments", {})
        
        # Extract key information
        problem = business_spec.get("problem_statement", "")
        solution = business_spec.get("solution_description", "")
        target_market = business_spec.get("target_market", "")
        tech_stack = business_spec.get("technology_requirements", [])
        
        # Generate strategic analysis
        strategic_prompt = f"""
        Conduct comprehensive strategic analysis for this application:
        
        Business Context:
        - Problem: {problem}
        - Solution: {solution}
        - Target Market: {target_market}
        - Technology Stack: {tech_stack}
        
        Provide detailed analysis covering:
        1. Business context and market positioning
        2. Technical requirements and constraints
        3. Architecture recommendations
        4. Implementation strategy and phases
        5. Risk assessment and mitigation
        6. Timeline estimation with milestones
        
        Return JSON format:
        {{
            "business_context": {{
                "market_position": "How this positions in market",
                "value_proposition": "Core value delivered",
                "success_factors": ["factor1", "factor2"],
                "business_model": "Revenue and operational model"
            }},
            "technical_requirements": {{
                "core_functionality": ["requirement1", "requirement2"],
                "performance_requirements": ["requirement1", "requirement2"],
                "security_requirements": ["requirement1", "requirement2"],
                "integration_requirements": ["requirement1", "requirement2"],
                "scalability_requirements": ["requirement1", "requirement2"]
            }},
            "architecture_recommendations": {{
                "backend_architecture": "Recommended backend approach",
                "frontend_architecture": "Recommended frontend approach",
                "database_design": "Database architecture recommendations",
                "api_design": "API design principles",
                "deployment_architecture": "Deployment and hosting recommendations"
            }},
            "implementation_strategy": {{
                "development_phases": [
                    {{"phase": "Phase 1", "duration": "4 weeks", "deliverables": ["deliverable1"]}},
                    {{"phase": "Phase 2", "duration": "3 weeks", "deliverables": ["deliverable2"]}}
                ],
                "technology_choices": {{"backend": "FastAPI", "frontend": "React", "database": "PostgreSQL"}},
                "testing_strategy": "Comprehensive testing approach",
                "deployment_strategy": "Deployment and CI/CD approach"
            }},
            "risk_assessment": {{
                "technical_risks": [
                    {{"risk": "Risk description", "impact": "High/Medium/Low", "mitigation": "Mitigation strategy"}}
                ],
                "business_risks": [
                    {{"risk": "Risk description", "impact": "High/Medium/Low", "mitigation": "Mitigation strategy"}}
                ],
                "timeline_risks": [
                    {{"risk": "Risk description", "impact": "High/Medium/Low", "mitigation": "Mitigation strategy"}}
                ]
            }},
            "timeline_estimate": "12-16 weeks from requirements to production"
        }}
        """
        
        try:
            response = await self.llm_provider.generate_completion(
                prompt=strategic_prompt,
                model="gpt-4",
                temperature=0.2
            )
            
            analysis_data = json.loads(response)
            
            return StrategicAnalysis(
                business_context=analysis_data["business_context"],
                technical_requirements=analysis_data["technical_requirements"],
                architecture_recommendations=analysis_data["architecture_recommendations"],
                implementation_strategy=analysis_data["implementation_strategy"],
                risk_assessment=analysis_data["risk_assessment"],
                timeline_estimate=analysis_data["timeline_estimate"]
            )
            
        except Exception as e:
            # Fallback strategic analysis
            return StrategicAnalysis(
                business_context={
                    "market_position": "Technology-forward solution in target market",
                    "value_proposition": "Efficient, scalable solution for identified problem",
                    "success_factors": ["User experience", "Performance", "Reliability"],
                    "business_model": "Sustainable revenue through core product value"
                },
                technical_requirements={
                    "core_functionality": ["User management", "Core business logic", "Data persistence"],
                    "performance_requirements": ["Sub-2s response times", "99.9% uptime"],
                    "security_requirements": ["Authentication", "Data encryption", "Input validation"],
                    "integration_requirements": ["Payment processing", "Email notifications"],
                    "scalability_requirements": ["Horizontal scaling", "Database optimization"]
                },
                architecture_recommendations={
                    "backend_architecture": "RESTful API with FastAPI framework",
                    "frontend_architecture": "React single-page application",
                    "database_design": "PostgreSQL with optimized schema",
                    "api_design": "RESTful endpoints with comprehensive documentation",
                    "deployment_architecture": "Docker containers with cloud deployment"
                },
                implementation_strategy={
                    "development_phases": [
                        {"phase": "Core Backend", "duration": "3 weeks", "deliverables": ["API endpoints", "Database schema"]},
                        {"phase": "Frontend Development", "duration": "3 weeks", "deliverables": ["User interface", "API integration"]},
                        {"phase": "Integration & Testing", "duration": "2 weeks", "deliverables": ["Testing suite", "Integration testing"]}
                    ],
                    "technology_choices": {"backend": "FastAPI", "frontend": "React", "database": "PostgreSQL"},
                    "testing_strategy": "Unit, integration, and end-to-end testing",
                    "deployment_strategy": "Containerized deployment with CI/CD pipeline"
                },
                risk_assessment={
                    "technical_risks": [
                        {"risk": "Integration complexity", "impact": "Medium", "mitigation": "Incremental integration approach"}
                    ],
                    "business_risks": [
                        {"risk": "Market validation", "impact": "High", "mitigation": "MVP approach with user feedback"}
                    ],
                    "timeline_risks": [
                        {"risk": "Scope creep", "impact": "Medium", "mitigation": "Clear requirements documentation"}
                    ]
                },
                timeline_estimate="8-12 weeks from requirements to production"
            )
    
    async def generate_production_code(self, 
                                     strategic_analysis: StrategicAnalysis,
                                     founder_agreement: Dict) -> CodeGenerationResult:
        """Generate production-ready code based on strategic analysis"""
        
        business_spec = founder_agreement.get("business_specification", {})
        tech_choices = strategic_analysis.implementation_strategy.get("technology_choices", {})
        
        # Determine project type and complexity
        project_type = await self._determine_project_type(business_spec)
        
        generated_files = []
        
        # Generate backend files
        backend_files = await self._generate_backend_files(strategic_analysis, business_spec, tech_choices)
        generated_files.extend(backend_files)
        
        # Generate frontend files
        frontend_files = await self._generate_frontend_files(strategic_analysis, business_spec, tech_choices)
        generated_files.extend(frontend_files)
        
        # Generate configuration files
        config_files = await self._generate_configuration_files(strategic_analysis, tech_choices)
        generated_files.extend(config_files)
        
        # Generate documentation
        doc_files = await self._generate_documentation_files(strategic_analysis, founder_agreement)
        generated_files.extend(doc_files)
        
        # Create project structure
        project_structure = await self._create_project_structure(generated_files)
        
        # Generate deployment instructions
        deployment_instructions = await self._generate_deployment_instructions(strategic_analysis, tech_choices)
        
        # Generate testing guide
        testing_guide = await self._generate_testing_guide(strategic_analysis)
        
        # Calculate quality score
        quality_score = await self._calculate_quality_score(generated_files, strategic_analysis)
        
        return CodeGenerationResult(
            project_structure=project_structure,
            generated_files=generated_files,
            deployment_instructions=deployment_instructions,
            testing_guide=testing_guide,
            quality_score=quality_score
        )
    
    async def _determine_project_type(self, business_spec: Dict) -> str:
        """Determine project type from business specification"""
        
        solution = business_spec.get("solution_description", "").lower()
        
        if any(keyword in solution for keyword in ["marketplace", "booking", "reservation"]):
            return "marketplace"
        elif any(keyword in solution for keyword in ["e-commerce", "shop", "store", "product"]):
            return "ecommerce"
        elif any(keyword in solution for keyword in ["social", "community", "chat", "messaging"]):
            return "social"
        elif any(keyword in solution for keyword in ["analytics", "dashboard", "reporting"]):
            return "analytics"
        elif any(keyword in solution for keyword in ["api", "integration", "webhook"]):
            return "api_service"
        else:
            return "web_application"
    
    async def _generate_backend_files(self, 
                                    strategic_analysis: StrategicAnalysis,
                                    business_spec: Dict,
                                    tech_choices: Dict) -> List[GeneratedFile]:
        """Generate backend application files"""
        
        backend_files = []
        
        # Main application file
        main_app_content = await self._generate_main_app_file(strategic_analysis, business_spec)
        backend_files.append(GeneratedFile(
            filename="main.py",
            content=main_app_content,
            file_type="python",
            description="FastAPI main application file"
        ))
        
        # Database models
        models_content = await self._generate_database_models(strategic_analysis, business_spec)
        backend_files.append(GeneratedFile(
            filename="models.py",
            content=models_content,
            file_type="python",
            description="Database models and schemas"
        ))
        
        # API routes
        routes_content = await self._generate_api_routes(strategic_analysis, business_spec)
        backend_files.append(GeneratedFile(
            filename="routes.py",
            content=routes_content,
            file_type="python",
            description="API endpoint routes"
        ))
        
        # Database configuration
        database_content = await self._generate_database_config(strategic_analysis)
        backend_files.append(GeneratedFile(
            filename="database.py",
            content=database_content,
            file_type="python",
            description="Database configuration and connection"
        ))
        
        # Authentication system
        auth_content = await self._generate_auth_system(strategic_analysis)
        backend_files.append(GeneratedFile(
            filename="auth.py",
            content=auth_content,
            file_type="python",
            description="Authentication and authorization"
        ))
        
        # Business logic services
        services_content = await self._generate_business_services(strategic_analysis, business_spec)
        backend_files.append(GeneratedFile(
            filename="services.py",
            content=services_content,
            file_type="python",
            description="Business logic and services"
        ))
        
        return backend_files
    
    async def _generate_frontend_files(self,
                                     strategic_analysis: StrategicAnalysis,
                                     business_spec: Dict,
                                     tech_choices: Dict) -> List[GeneratedFile]:
        """Generate frontend application files"""
        
        frontend_files = []
        
        # Main React App component
        app_component = await self._generate_app_component(strategic_analysis, business_spec)
        frontend_files.append(GeneratedFile(
            filename="src/App.js",
            content=app_component,
            file_type="javascript",
            description="Main React application component"
        ))
        
        # Homepage component
        homepage_component = await self._generate_homepage_component(business_spec)
        frontend_files.append(GeneratedFile(
            filename="src/components/Homepage.js",
            content=homepage_component,
            file_type="javascript",
            description="Homepage component"
        ))
        
        # Authentication components
        auth_components = await self._generate_auth_components()
        for component_name, content in auth_components.items():
            frontend_files.append(GeneratedFile(
                filename=f"src/components/{component_name}.js",
                content=content,
                file_type="javascript",
                description=f"{component_name} authentication component"
            ))
        
        # API service layer
        api_service = await self._generate_api_service(strategic_analysis)
        frontend_files.append(GeneratedFile(
            filename="src/services/api.js",
            content=api_service,
            file_type="javascript", 
            description="API service layer for backend communication"
        ))
        
        # CSS styles
        main_styles = await self._generate_main_styles(business_spec)
        frontend_files.append(GeneratedFile(
            filename="src/styles/main.css",
            content=main_styles,
            file_type="css",
            description="Main application styles"
        ))
        
        # Package.json
        package_json = await self._generate_package_json(strategic_analysis)
        frontend_files.append(GeneratedFile(
            filename="package.json",
            content=package_json,
            file_type="json",
            description="Frontend dependencies and scripts"
        ))
        
        return frontend_files
    
    async def _generate_main_app_file(self, strategic_analysis: StrategicAnalysis, business_spec: Dict) -> str:
        """Generate FastAPI main application file"""
        
        problem = business_spec.get("problem_statement", "business problem")
        solution = business_spec.get("solution_description", "business solution")
        
        return f'''"""
{solution} - Main Application
Generated by AI Debugger Factory DreamEngine

Solves: {problem}
Architecture: {strategic_analysis.architecture_recommendations.get("backend_architecture", "FastAPI RESTful API")}
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from datetime import datetime

from app.database.db import get_db, init_db
from app.database.models import *
from app.routes import router
from app.routes.auth_router import get_current_user, create_access_token
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting {solution} application...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title="{solution}",
    description="{problem}",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {{
        "message": "Welcome to {solution}",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "{solution}"
    }}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
'''
    
    async def _generate_database_models(self, strategic_analysis: StrategicAnalysis, business_spec: Dict) -> str:
        """Generate SQLAlchemy database models"""
        
        solution = business_spec.get("solution_description", "application")
        
        return f'''"""
Database Models for {solution}
Generated by AI Debugger Factory DreamEngine
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add relationship to main business entity
    items = relationship("Item", back_populates="owner")

class Item(Base):
    """Main business entity model"""
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Decimal(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key to user
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")

# Pydantic schemas for API
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: Optional[str] = None

class ItemResponse(ItemBase):
    id: str
    is_active: bool
    created_at: datetime
    owner_id: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
'''
    
    async def _generate_api_routes(self, strategic_analysis: StrategicAnalysis, business_spec: Dict) -> str:
        """Generate FastAPI routes"""
        
        solution = business_spec.get("solution_description", "application")
        
        return f'''"""
API Routes for {solution}
Generated by AI Debugger Factory DreamEngine
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_db
from app.database.models import *
from app.routes.auth_router import get_current_user, create_access_token, verify_password, get_password_hash
from app import services

router = APIRouter()

# Authentication routes
@router.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/auth/login", response_model=Token)
async def login_user(form_data: dict, db: Session = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.email == form_data["email"]).first()
    
    if not user or not verify_password(form_data["password"], user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={{"WWW-Authenticate": "Bearer"}},
        )
    
    access_token = create_access_token(data={{"sub": user.email}})
    return {{"access_token": access_token, "token_type": "bearer"}}

# Core business routes
@router.get("/items/", response_model=List[ItemResponse])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get items"""
    items = db.query(Item).filter(Item.is_active == True).offset(skip).limit(limit).all()
    return items

@router.post("/items/", response_model=ItemResponse)
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new item"""
    db_item = Item(**item.dict(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

@router.get("/items/{{item_id}}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific item"""
    item = db.query(Item).filter(Item.id == item_id, Item.is_active == True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@router.put("/items/{{item_id}}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update item"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/items/{{item_id}}")
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete item (soft delete)"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.is_active = False
    db.commit()
    
    return {{"message": "Item deleted successfully"}}

# User profile routes
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user_profile(
    user_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    for field, value in user_update.items():
        if hasattr(current_user, field) and field != "id":
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

# Analytics routes
@router.get("/analytics/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics summary"""
    total_items = db.query(Item).filter(Item.owner_id == current_user.id, Item.is_active == True).count()
    
    return {{
        "total_items": total_items,
        "user_since": current_user.created_at,
        "last_login": current_user.updated_at
    }}
'''

    async def _load_generation_templates(self) -> Dict:
        """Load code generation templates"""
        return {
            "fastapi_main": "FastAPI main application template",
            "react_app": "React application template",
            "database_models": "SQLAlchemy models template",
            "api_routes": "FastAPI routes template",
            "auth_system": "Authentication system template"
        }
    
    # Additional methods for generating other file types...
    # (Continuing with remaining backend generation methods)
    
    async def _generate_database_config(self, strategic_analysis: StrategicAnalysis) -> str:
        """Generate database configuration"""
        return '''"""
Database Configuration
Generated by AI Debugger Factory DreamEngine
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
'''
    
    async def _generate_auth_system(self, strategic_analysis: StrategicAnalysis) -> str:
        """Generate authentication system"""
        return '''"""
Authentication System
Generated by AI Debugger Factory DreamEngine
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user
'''

    async def _generate_business_services(self, strategic_analysis: StrategicAnalysis, business_spec: Dict) -> str:
        """Generate business logic services"""
        
        solution = business_spec.get("solution_description", "application")
        
        return f'''"""
Business Services for {solution}
Generated by AI Debugger Factory DreamEngine
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.models import *
import logging

logger = logging.getLogger(__name__)

class ItemService:
    """Business logic for items"""
    
    @staticmethod
    def get_items(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get user items with pagination"""
        return db.query(Item).filter(
            Item.owner_id == user_id,
            Item.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_item(db: Session, item_data: ItemCreate, user_id: str) -> Item:
        """Create new item"""
        try:
            db_item = Item(**item_data.dict(), owner_id=user_id)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            
            logger.info(f"Created item {{db_item.id}} for user {{user_id}}")
            return db_item
        
        except Exception as e:
            logger.error(f"Failed to create item: {{e}}")
            db.rollback()
            raise
    
    @staticmethod
    def update_item(db: Session, item_id: str, item_data: ItemUpdate, user_id: str) -> Optional[Item]:
        """Update existing item"""
        try:
            item = db.query(Item).filter(
                Item.id == item_id,
                Item.owner_id == user_id,
                Item.is_active == True
            ).first()
            
            if not item:
                return None
            
            for field, value in item_data.dict(exclude_unset=True).items():
                setattr(item, field, value)
            
            db.commit()
            db.refresh(item)
            
            logger.info(f"Updated item {{item_id}}")
            return item
        
        except Exception as e:
            logger.error(f"Failed to update item {{item_id}}: {{e}}")
            db.rollback()
            raise
    
    @staticmethod
    def delete_item(db: Session, item_id: str, user_id: str) -> bool:
        """Soft delete item"""
        try:
            item = db.query(Item).filter(
                Item.id == item_id,
                Item.owner_id == user_id
            ).first()
            
            if not item:
                return False
            
            item.is_active = False
            db.commit()
            
            logger.info(f"Deleted item {{item_id}}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete item {{item_id}}: {{e}}")
            db.rollback()
            raise

class UserService:
    """Business logic for users"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Create new user
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Created user {{db_user.id}}")
            return db_user
        
        except Exception as e:
            logger.error(f"Failed to create user: {{e}}")
            db.rollback()
            raise
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> dict:
        """Get user statistics"""
        total_items = db.query(Item).filter(
            Item.owner_id == user_id,
            Item.is_active == True
        ).count()
        
        return {{
            "total_items": total_items,
            "active_items": total_items,  # All items are active in this query
        }}
'''