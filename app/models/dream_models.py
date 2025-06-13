"""
DreamEngine - Pydantic Models
Models for the DreamEngine module that integrates with AI Debugger Factory
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import uuid


class ModelProvider(str, Enum):
    """Supported LLM providers for code generation"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AUTO = "auto"  # Automatically select best provider based on request


class ProjectType(str, Enum):
    """Types of projects that can be generated"""
    WEB_API = "web_api"
    WEB_APP = "web_app"
    CLI_TOOL = "cli_tool"
    MOBILE_APP = "mobile_app"
    DATA_PIPELINE = "data_pipeline"
    MACHINE_LEARNING = "machine_learning"
    BLOCKCHAIN = "blockchain"
    IOT = "iot"
    GAME = "game"
    DESKTOP_APP = "desktop_app"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    SERVERLESS = "serverless"
    DEVOPS = "devops"
    OTHER = "other"


class ProgrammingLanguage(str, Enum):
    """Supported programming languages for code generation"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    CPP = "cpp"
    OTHER = "other"


class DatabaseType(str, Enum):
    """Supported database types for code generation"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    REDIS = "redis"
    DYNAMODB = "dynamodb"
    FIRESTORE = "firestore"
    COSMOSDB = "cosmosdb"
    NONE = "none"
    OTHER = "other"


class DeploymentTarget(str, Enum):
    """Supported deployment targets for generated code"""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS_LAMBDA = "aws_lambda"
    HEROKU = "heroku"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    AZURE = "azure"
    GCP = "gcp"
    LOCAL = "local"
    OTHER = "other"


class SecurityLevel(str, Enum):
    """Security levels for code generation"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    ENTERPRISE = "enterprise"


class GenerationOptions(BaseModel):
    """Options for code generation"""
    model_provider: ModelProvider = Field(
        default=ModelProvider.AUTO,
        description="LLM provider to use for code generation"
    )
    project_type: Optional[ProjectType] = Field(
        default=None,
        description="Type of project to generate"
    )
    programming_language: Optional[ProgrammingLanguage] = Field(
        default=None,
        description="Programming language to use"
    )
    database_type: Optional[DatabaseType] = Field(
        default=None,
        description="Database type to use"
    )
    deployment_target: Optional[DeploymentTarget] = Field(
        default=None,
        description="Deployment target for generated code"
    )
    security_level: SecurityLevel = Field(
        default=SecurityLevel.STANDARD,
        description="Security level for generated code"
    )
    include_tests: bool = Field(
        default=True,
        description="Whether to include tests in generated code"
    )
    include_documentation: bool = Field(
        default=True,
        description="Whether to include documentation in generated code"
    )
    include_docker: bool = Field(
        default=False,
        description="Whether to include Docker configuration"
    )
    include_ci_cd: bool = Field(
        default=False,
        description="Whether to include CI/CD configuration"
    )
    streaming: bool = Field(
        default=True,
        description="Whether to stream the response"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens to generate"
    )
    temperature: float = Field(
        default=0.7,
        description="Temperature for generation (0.0-1.0)"
    )
    custom_parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom parameters for specific model providers"
    )


class DreamRequest(BaseModel):
    """Request model for DreamEngine endpoints"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the request"
    )
    user_id: str = Field(
        ...,
        description="User identifier"
    )
    input_text: str = Field(
        ...,
        description="Natural language description of the desired code"
    )
    options: Optional[GenerationOptions] = Field(
        default_factory=GenerationOptions,
        description="Options for code generation"
    )
    
    @validator('input_text')
    def validate_input_text(cls, v):
        """Validate input text is not empty and has reasonable length"""
        if not v or not v.strip():
            raise ValueError("Input text cannot be empty")
        if len(v) < 10:
            raise ValueError("Input text is too short")
        if len(v) > 10000:
            raise ValueError("Input text is too long (max 10000 characters)")
        return v.strip()


class ValidationScore(BaseModel):
    """Score for a validation aspect"""
    score: float = Field(
        ...,
        description="Score from 0.0 to 1.0"
    )
    explanation: str = Field(
        ...,
        description="Explanation of the score"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )


class ValidationResult(BaseModel):
    """Result of idea validation"""
    feasibility: ValidationScore = Field(
        ...,
        description="Technical feasibility score"
    )
    complexity: ValidationScore = Field(
        ...,
        description="Complexity assessment"
    )
    clarity: ValidationScore = Field(
        ...,
        description="Clarity of requirements"
    )
    security_considerations: ValidationScore = Field(
        ...,
        description="Security considerations"
    )
    overall_score: float = Field(
        ...,
        description="Overall validation score from 0.0 to 1.0"
    )
    detected_project_type: ProjectType = Field(
        ...,
        description="Detected project type"
    )
    detected_language: ProgrammingLanguage = Field(
        ...,
        description="Detected programming language"
    )
    detected_database: Optional[DatabaseType] = Field(
        default=None,
        description="Detected database type"
    )
    estimated_time: str = Field(
        ...,
        description="Estimated development time"
    )
    summary: str = Field(
        ...,
        description="Summary of validation"
    )


class GeneratedFile(BaseModel):
    """A generated code file"""
    filename: str = Field(
        ...,
        description="Filename including path"
    )
    content: str = Field(
        ...,
        description="File content"
    )
    language: str = Field(
        ...,
        description="Programming language"
    )
    purpose: str = Field(
        ...,
        description="Purpose of the file"
    )


class SecurityIssue(BaseModel):
    """Security issue found in generated code"""
    severity: str = Field(
        ...,
        description="Issue severity (low, medium, high, critical)"
    )
    description: str = Field(
        ...,
        description="Issue description"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location in code (file:line)"
    )
    recommendation: str = Field(
        ...,
        description="Recommendation to fix the issue"
    )


class CodeQualityIssue(BaseModel):
    """Code quality issue found in generated code"""
    type: str = Field(
        ...,
        description="Issue type"
    )
    description: str = Field(
        ...,
        description="Issue description"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location in code (file:line)"
    )
    recommendation: str = Field(
        ...,
        description="Recommendation to fix the issue"
    )


class DeploymentStep(BaseModel):
    """Step in deployment process"""
    step_number: int = Field(
        ...,
        description="Step number"
    )
    description: str = Field(
        ...,
        description="Step description"
    )
    command: Optional[str] = Field(
        default=None,
        description="Command to execute"
    )
    expected_output: Optional[str] = Field(
        default=None,
        description="Expected command output"
    )
    verification: Optional[str] = Field(
        default=None,
        description="How to verify step completion"
    )


class GenerationResult(BaseModel):
    """Result of code generation"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the result"
    )
    request_id: str = Field(
        ...,
        description="ID of the original request"
    )
    user_id: str = Field(
        ...,
        description="User identifier"
    )
    status: str = Field(
        default="success",
        description="Status of generation"
    )
    message: str = Field(
        default="Code generated successfully",
        description="Status message"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Timestamp of generation"
    )
    project_type: ProjectType = Field(
        ...,
        description="Type of project generated"
    )
    programming_language: ProgrammingLanguage = Field(
        ...,
        description="Programming language used"
    )
    database_type: Optional[DatabaseType] = Field(
        default=None,
        description="Database type used"
    )
    files: List[GeneratedFile] = Field(
        default_factory=list,
        description="Generated code files"
    )
    main_file: Optional[str] = Field(
        default=None,
        description="Main entry point file"
    )
    explanation: str = Field(
        ...,
        description="Explanation of generated code"
    )
    architecture: str = Field(
        ...,
        description="Architecture description"
    )
    security_issues: List[SecurityIssue] = Field(
        default_factory=list,
        description="Security issues found"
    )
    quality_issues: List[CodeQualityIssue] = Field(
        default_factory=list,
        description="Code quality issues found"
    )
    deployment_steps: List[DeploymentStep] = Field(
        default_factory=list,
        description="Deployment steps"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required dependencies"
    )
    environment_variables: List[str] = Field(
        default_factory=list,
        description="Required environment variables"
    )
    model_provider: ModelProvider = Field(
        ...,
        description="LLM provider used for generation"
    )
    generation_time_seconds: float = Field(
        ...,
        description="Time taken for generation in seconds"
    )


class StreamingChunk(BaseModel):
    """Chunk of streaming response"""
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the chunk"
    )
    request_id: str = Field(
        ...,
        description="ID of the original request"
    )
    chunk_index: int = Field(
        ...,
        description="Index of this chunk in the sequence"
    )
    content: str = Field(
        ...,
        description="Chunk content"
    )
    content_type: str = Field(
        default="text",
        description="Content type (text, code, etc.)"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="File path if this chunk is part of a file"
    )
    is_final: bool = Field(
        default=False,
        description="Whether this is the final chunk"
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(
        default="healthy",
        description="Service status"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Current timestamp"
    )
    service: str = Field(
        default="DreamEngine - AI Debugger Factory Extension",
        description="Service name"
    )
    version: str = Field(
        default="1.0.0",
        description="Service version"
    )
    providers: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of each provider"
    )


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = Field(
        default="error",
        description="Error status"
    )
    message: str = Field(
        ...,
        description="Error message"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Error timestamp"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Error code"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="ID of the original request"
    )


class RateLimitStatus(BaseModel):
    """Rate limit status"""
    user_id: str = Field(
        ...,
        description="User identifier"
    )
    requests_remaining: int = Field(
        ...,
        description="Number of requests remaining in current period"
    )
    requests_limit: int = Field(
        ...,
        description="Total request limit for current period"
    )
    reset_time: str = Field(
        ...,
        description="When the rate limit will reset"
    )
    is_limited: bool = Field(
        ...,
        description="Whether the user is currently rate limited"
    )


class Config:
    """Pydantic model configuration"""
    json_schema_extra = {
        "examples": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "input_text": "Create a FastAPI backend for a task management application with user authentication, CRUD operations for tasks, and PostgreSQL database.",
                "options": {
                    "model_provider": "openai",
                    "project_type": "web_api",
                    "programming_language": "python",
                    "database_type": "postgresql",
                    "security_level": "standard",
                    "include_tests": True,
                    "include_documentation": True
                }
            }
        ]
    }
