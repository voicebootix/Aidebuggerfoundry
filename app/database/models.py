"""
Complete Pydantic Models for AI Debugger Factory
Comprehensive request/response models for all API endpoints
Enhanced with validation and documentation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# ==========================================
# BASE MODELS AND ENUMS
# ==========================================

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    BUILDING = "building"
    DEBUGGING = "debugging"
    DEPLOYED = "deployed"

class ConversationState(str, Enum):
    DISCOVERY = "discovery"
    VALIDATION = "validation"
    STRATEGY = "strategy"
    AGREEMENT = "agreement"
    CODE_GENERATION = "code_generation"
    COMPLETED = "completed"

# ==========================================
# USER AND AUTHENTICATION MODELS
# ==========================================

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserRegistrationResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    access_token: str
    token_type: str
    message: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: EmailStr
    full_name: str
    is_verified: bool

class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    is_verified: bool
    member_since: str
    total_projects: int
    total_revenue: float
    account_status: str

# ==========================================
# VOICE CONVERSATION MODELS (REVOLUTIONARY)
# ==========================================

class VoiceConversationRequest(BaseModel):
    initial_input: str = Field(..., min_length=1, max_length=2000, description="Founder's initial business idea or technical requirement")
    voice_mode: bool = Field(default=False, description="Whether input came from voice")
    founder_background: Optional[str] = Field(None, description="Optional founder background information")

class VoiceConversationResponse(BaseModel):
    session_id: str
    ai_response: str
    conversation_state: str
    founder_type_detected: str
    validation_suggested: bool
    next_actions: List[str]

class ConversationTurnRequest(BaseModel):
    user_response: str = Field(..., min_length=1, max_length=2000)
    voice_mode: bool = Field(default=False)

class ConversationTurnResponse(BaseModel):
    ai_response: str
    conversation_state: str
    next_actions: List[str]
    session_id: str

class VoiceTranscriptionResponse(BaseModel):
    transcription: str
    confidence: Optional[float]
    processing_time: float
    session_id: str

class FounderAgreementResponse(BaseModel):
    agreement_id: str
    project_id: str
    business_specification: Dict[str, Any]
    ai_commitments: Dict[str, Any]
    success_criteria: Dict[str, Any]
    ready_for_code_generation: bool

class ConversationHistoryResponse(BaseModel):
    session_id: str
    conversation_history: List[Dict[str, Any]]
    founder_type_detected: str
    conversation_state: str
    business_validation_requested: bool
    strategy_validated: bool
    founder_ai_agreement: Optional[Dict[str, Any]]

# ==========================================
# BUSINESS INTELLIGENCE MODELS (SMART)
# ==========================================

class MarketAnalysisRequest(BaseModel):
    conversation_id: Optional[str] = None  # ← Made optional with default None
    business_idea: Dict[str, Any] = Field(..., description="Structured business idea from conversation")

class MarketAnalysisResponse(BaseModel):
    analysis_id: str
    market_size: str
    growth_rate: str
    key_trends: List[str]
    opportunities: List[str]
    threats: List[str]
    confidence_score: float
    recommendations: List[str]

class CompetitorResearchRequest(BaseModel):
    conversation_id: str
    business_domain: str
    solution_type: str

class CompetitorAnalysisResponse(BaseModel):
    direct_competitors: List[Dict[str, Any]]
    indirect_competitors: List[Dict[str, Any]]
    competitive_advantages: List[str]
    market_gaps: List[str]
    differentiation_strategy: str
    competitive_positioning_score: float

class BusinessModelValidationRequest(BaseModel):
    conversation_id: str
    business_idea: Dict[str, Any]

class BusinessModelValidationResponse(BaseModel):
    feasibility_score: float
    market_potential: str
    revenue_projection: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    validation_summary: str

class BusinessPlanRequest(BaseModel):
    conversation_id: str
    business_idea: Dict[str, Any]

class BusinessPlanResponse(BaseModel):
    business_plan: Dict[str, Any]
    executive_summary: Dict[str, Any]
    implementation_timeline: Dict[str, Any]
    confidence_score: float

class BusinessValidationSummaryResponse(BaseModel):
    validation_id: str
    conversation_id: str
    market_analysis: Optional[Dict[str, Any]]
    competitor_research: Optional[Dict[str, Any]]
    business_model_validation: Optional[Dict[str, Any]]
    strategy_recommendations: Optional[Dict[str, Any]]
    overall_validation_score: Optional[float]
    created_at: str

# ==========================================
# DREAM ENGINE MODELS (LAYER 1 BUILD)
# ==========================================

class StrategicAnalysisRequest(BaseModel):
    project_id: str
    founder_agreement: Optional[Dict[str, Any]] = None  # ← ADD THIS LINE
    additional_requirements: Optional[str] = Field(None, description="Additional technical or business requirements")

class StrategicAnalysisResponse(BaseModel):
    analysis_id: str
    project_id: str
    business_context: Dict[str, Any]
    technical_requirements: Dict[str, Any]
    architecture_recommendations: Dict[str, Any]
    implementation_strategy: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timeline_estimate: str
    ready_for_code_generation: bool

class CodeGenerationRequest(BaseModel):
    analysis_id: str
    custom_requirements: Optional[Dict[str, Any]] = Field(None, description="Custom technical requirements")

class CodeGenerationResponse(BaseModel):
    generation_id: str
    project_id: str
    generated_files: List[Dict[str, Any]]
    project_structure: Dict[str, Any]
    deployment_instructions: str
    testing_guide: str
    quality_score: float
    ready_for_github_upload: bool
    estimated_deployment_time: str

class StreamCodeGenerationRequest(BaseModel):
    analysis_id: str
    stream_updates: bool = Field(default=True)

class CodeGenerationStatusResponse(BaseModel):
    generation_id: str
    project_id: str
    status: str
    progress_percentage: int
    quality_score: Optional[float]
    files_generated: int
    estimated_completion: str

# ==========================================
# DEBUG ENGINE MODELS (LAYER 2 DEBUG)
# ==========================================

class StartDebugSessionRequest(BaseModel):
    project_id: str
    initial_focus: Optional[str] = Field(None, description="Initial debugging focus area")

class DebugSessionResponse(BaseModel):
    session_id: str
    project_id: str
    monaco_workspace_id: str
    initial_analysis: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    files_available: List[str]
    collaboration_enabled: bool
    github_sync_available: bool

class DebugRequestAnalysis(BaseModel):
    debug_request: str = Field(..., min_length=5, max_length=1000, description="Specific debugging request or question")

class DebugResponseAnalysis(BaseModel):
    session_id: str
    ai_response: str
    suggestions: List[Dict[str, Any]]
    code_changes: Dict[str, Any]
    next_steps: List[str]
    confidence: float

class ApplyDebugChangesRequest(BaseModel):
    changes: Dict[str, Any] = Field(..., description="Code changes to apply")

class ApplyChangesResponse(BaseModel):
    success: bool
    message: str
    updated_analysis: Dict[str, Any]
    github_synced: bool
    next_suggestions: List[str]

class DebugSessionSummaryResponse(BaseModel):
    session_id: str
    metrics: Dict[str, Any]
    suggestions_available: int
    conversation_length: int
    last_activity: Optional[str]
    overall_code_quality: float
    issues_resolved: int
    time_saved: str

class DebugReportResponse(BaseModel):
    report_id: str
    session_id: str
    report_data: Dict[str, Any]
    generated_at: str
    download_url: str

# ==========================================
# GITHUB INTEGRATION MODELS
# ==========================================

class CreateGitHubRepositoryRequest(BaseModel):
    project_id: str
    repository_name: str = Field(..., min_length=3, max_length=100)
    github_token: str = Field(..., description="GitHub personal access token")
    private: bool = Field(default=True)

class GitHubRepositoryResponse(BaseModel):
    repository_name: str
    repository_url: str
    clone_url: str
    default_branch: str
    private: bool
    ready_for_upload: bool

class UploadCodeToGitHubRequest(BaseModel):
    commit_message: Optional[str] = Field(None, max_length=200)

class GitHubUploadResponse(BaseModel):
    success: bool
    repository_url: Optional[str]
    files_uploaded: int
    upload_results: List[Dict[str, Any]]
    commit_message: str
    ready_for_layer2_debug: bool

class SyncDebugChangesRequest(BaseModel):
    changed_files: Dict[str, str] = Field(..., description="Files with their updated content")

class GitHubSyncResponse(BaseModel):
    success: bool
    synced_files: int
    sync_results: List[Dict[str, Any]]
    commit_message: str
    last_sync: str

class GitHubRepositoryStatusResponse(BaseModel):
    project_id: str
    repository_url: Optional[str]
    has_repository: bool
    last_upload: Optional[str]
    files_in_repo: int
    recent_commits: List[Dict[str, Any]]
    sync_status: str

# ==========================================
# SMART CONTRACT MODELS (PATENT-WORTHY)
# ==========================================

class CreateSmartContractRequest(BaseModel):
    project_id: str
    founder_wallet_address: str = Field(..., description="Founder's blockchain wallet address")
    web3_provider_url: str
    revenue_split: Optional[Dict[str, float]] = Field(None, description="Custom revenue split (default 80/20)")

class SmartContractResponse(BaseModel):
    contract_id: str
    project_id: str
    contract_address: str
    founder_address: str
    platform_address: str
    revenue_split: Dict[str, float]
    digital_fingerprint: str
    status: str
    created_at: str

class TrackRevenueRequest(BaseModel):
    revenue_amount: float = Field(..., gt=0, description="Revenue amount to track and distribute")
    currency: str = Field(default="USD")

class RevenueTrackingResponse(BaseModel):
    transaction_id: str
    contract_id: str
    revenue_amount: float
    founder_share: float
    platform_share: float
    transaction_hash: Optional[str]
    currency: str
    processed_at: str

class DetectUnauthorizedUsageRequest(BaseModel):
    code_sample: str = Field(..., min_length=100, description="Code sample to check for unauthorized usage")

class UnauthorizedUsageDetectionResponse(BaseModel):
    unauthorized_usage_detected: bool
    project_id: Optional[str]
    digital_fingerprint: Optional[str]
    confidence: float
    evidence: List[str]
    recommended_action: str

class ProjectRevenueSummaryResponse(BaseModel):
    project_id: str
    total_revenue: float
    founder_earnings: float
    platform_earnings: float
    transaction_count: int
    smart_contract_address: Optional[str]
    last_transaction: Optional[str]

# ==========================================
# CONTRACT METHOD MODELS (PATENT-WORTHY)
# ==========================================

class RegisterAgreementRequest(BaseModel):
    project_id: str

class ContractComplianceResponse(BaseModel):
    contract_id: str
    project_id: str
    compliance_monitoring_enabled: bool
    initial_compliance_score: float
    monitoring_rules: Dict[str, Any]
    auto_correction_enabled: bool

class MonitorComplianceRequest(BaseModel):
    ai_output: Dict[str, Any] = Field(..., description="AI output to monitor for compliance")

class ComplianceMonitoringResponse(BaseModel):
    contract_id: str
    compliance_score: float
    violations_detected: List[Dict[str, Any]]
    recommendations: List[str]
    auto_correction_applied: bool
    monitoring_timestamp: str

class ComplianceReportResponse(BaseModel):
    project_id: str
    overall_compliance_score: float
    total_outputs_monitored: int
    violations_detected: int
    auto_corrections_applied: int
    compliance_trend: str
    last_monitoring: Optional[str]

# ==========================================
# PROJECT MANAGEMENT MODELS
# ==========================================

class CreateProjectRequest(BaseModel):
    project_name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    technology_stack: Optional[List[str]] = Field(None, description="Preferred technology stack")

class ProjectCreateResponse(BaseModel):
    project_id: str
    project_name: str
    description: str
    status: str
    created_at: str
    next_steps: List[str]

class ProjectSummaryResponse(BaseModel):
    project_id: str
    project_name: str
    status: str
    technology_stack: List[str]
    created_at: str
    last_modified: str
    has_conversation: bool
    has_generated_code: bool
    has_github_repo: bool
    has_debug_session: bool
    completion_percentage: int

class ProjectDetailResponse(BaseModel):
    project_id: str
    project_name: str
    description: str
    status: str
    technology_stack: List[str]
    created_at: str
    founder_ai_agreement: Optional[Dict[str, Any]]
    conversation_history: List[Dict[str, Any]]
    github_repo_url: Optional[str]
    deployment_url: Optional[str]
    smart_contract_address: Optional[str]
    layer_1_status: str
    layer_2_status: str
    revenue_generated: float
    completion_percentage: int

class UpdateProjectStatusRequest(BaseModel):
    status: ProjectStatus
    deployment_url: Optional[str] = None
    notes: Optional[str] = None

# ==========================================
# DATABASE TABLE MODELS (SQLAlchemy-style for reference)
# ==========================================

class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    full_name: Optional[str]
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime]

class VoiceConversation(BaseModel):
    id: str
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]]
    founder_type_detected: Optional[str]
    business_validation_requested: bool = False
    strategy_validated: bool = False
    founder_ai_agreement: Optional[Dict[str, Any]]
    conversation_state: str = "active"
    created_at: datetime
    updated_at: Optional[datetime]

class Project(BaseModel):
    id: str
    project_name: str
    user_id: str
    conversation_session_id: Optional[str]
    founder_ai_agreement: Optional[Dict[str, Any]]
    github_repo_url: Optional[str]
    deployment_url: Optional[str]
    smart_contract_address: Optional[str]
    technology_stack: List[str]
    status: str = "planning"
    created_at: datetime
    updated_at: Optional[datetime]

class DreamSession(BaseModel):
    id: str
    project_id: str
    user_input: str
    strategic_analysis: Optional[Dict[str, Any]]
    generated_files: Optional[Dict[str, Any]]
    generation_quality_score: Optional[float]
    status: str = "pending"
    created_at: datetime

class DebugSessionModel(BaseModel):
    id: str
    project_id: str
    debug_request: str
    analysis_results: Optional[Dict[str, Any]]
    suggestions: Optional[Dict[str, Any]]
    code_modifications: Optional[Dict[str, Any]]
    monaco_workspace_state: Optional[Dict[str, Any]]
    collaboration_users: List[str] = []
    github_sync_history: List[Dict[str, Any]] = []
    status: str = "active"
    created_at: datetime

class BusinessValidation(BaseModel):
    id: str
    conversation_id: str
    market_analysis: Optional[Dict[str, Any]]
    competitor_research: Optional[Dict[str, Any]]
    business_model_validation: Optional[Dict[str, Any]]
    strategy_recommendations: Optional[Dict[str, Any]]
    validation_score: Optional[float]
    created_at: datetime

class ContractCompliance(BaseModel):
    id: str
    project_id: str
    founder_contract: Dict[str, Any]
    compliance_monitoring: List[Dict[str, Any]] = []
    deviation_alerts: List[Dict[str, Any]] = []
    compliance_score: float = 1.0
    created_at: datetime

class RevenueSharing(BaseModel):
    id: str
    project_id: str
    smart_contract_address: Optional[str]
    revenue_tracked: float = 0.0
    platform_share: float = 0.0
    digital_fingerprint: Optional[str]
    status: str = "active"
    created_at: datetime
