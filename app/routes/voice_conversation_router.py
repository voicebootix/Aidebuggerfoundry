"""
VoiceBotics AI Cofounder API Router (PATENT-WORTHY)
Revolutionary API endpoints for natural founder conversations
Transforms voice/text conversations into deployable applications
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime
import uuid
import asyncpg
from app.services import service_manager

from app.database.db import get_db
from app.database.models import *
from app.utils.voice_conversation_engine import VoiceConversationEngine, FounderType, ConversationState
from app.utils.voice_processor import VoiceProcessor
from app.utils.business_intelligence import BusinessIntelligence
from app.utils.contract_method import ContractMethod
from app.utils.logger import get_logger
from app.utils.security_validator import SecurityValidator
from app.utils.auth_utils import get_current_user
from typing import Dict
from app.utils.auth_utils import get_current_user, get_optional_current_user
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["VoiceBotics AI Cofounder"])
logger = get_logger("voice_conversation_api")
security_validator = SecurityValidator()

# Initialize core components (these would be dependency injected in production)
#voice_processor = None  # Will be initialized with API keys
#conversation_engine = None  # Will be initialized with dependencies
#business_intelligence = None  # Will be initialized with LLM provider

@router.post("/start-conversation", response_model=VoiceConversationResponse)
async def start_ai_cofounder_conversation(
    request: VoiceConversationRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Start revolutionary AI cofounder conversation
    PATENT-WORTHY: Natural business conversations → deployed applications
    """
    
    try:
        
        # Handle demo mode when user is not authenticated
        user_id = current_user.get("id") if current_user else "demo_user"
        user_email = current_user.get("email") if current_user else "demo@example.com"

        # Validate and sanitize input
        security_issues = await security_validator.validate_input(request.initial_input)
        if security_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security validation failed: {security_issues[0].description}"
            )
        
        # Initialize conversation engine if needed
        global conversation_engine
        if not conversation_engine:
            conversation_engine = VoiceConversationEngine(
                openai_client=None,  # Initialize with actual client
                business_intelligence=business_intelligence,
                contract_method=ContractMethod(None)
            )
        
        # Start conversation session
        session = await conversation_engine.start_cofounder_conversation(
            user_id=user_id,
            initial_input=request.initial_input
        )
        
        # REPLACE WITH:
        await db.execute(
                """INSERT INTO voice_conversations 
                (id, session_id, user_id, conversation_history, founder_type_detected, 
                business_validation_requested, conversation_state, founder_ai_agreement, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())""",
            session.session_id, session.session_id, user_id, 
            json.dumps(session.conversation_history),
            session.founder_profile.type.value if session.founder_profile else "unknown",
            session.validation_requested, session.current_state.value, None
        )
        
        logger.log_structured("info", "AI cofounder conversation started", {
            "session_id": session.session_id,
            "user_id": user_id,
            "founder_type": session.founder_profile.type.value if session.founder_profile else "unknown"
        })
        
        return VoiceConversationResponse(
            session_id=session.session_id,
            ai_response=session.conversation_history[-1]["content"],
            conversation_state=session.current_state.value,
            founder_type_detected=session.founder_profile.type.value if session.founder_profile else "unknown",
            validation_suggested=session.founder_profile.type == FounderType.BUSINESS if session.founder_profile else False,
            next_actions=["Continue conversation", "Request business validation", "Proceed to code generation"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to start conversation", {
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start AI cofounder conversation: {str(e)}"
        )

@router.post("/process-turn/{session_id}")
async def process_conversation_turn(
    session_id: str,
    request: ConversationTurnRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Process user response in ongoing conversation"""
    
    try:
        user_id = current_user.get("id") if current_user else "demo_user"
        # Validate session ownership
        db_conversation = await db.fetchrow(
            "SELECT * FROM voice_conversations WHERE session_id = $1 AND user_id = $2",
            session_id, user_id
        )

        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
        # Validate input
        security_issues = await security_validator.validate_input(request.user_response)
        if security_issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security validation failed: {security_issues[0].description}"
            )
        
        # Process conversation turn
        response = await conversation_engine.process_conversation_turn(
            session_id=session_id,
            user_response=request.user_response
        )
        
        # Update database
        updated_history = db_conversation.conversation_history + [
            {
                "role": "user",
                "content": request.user_response,
                "timestamp": datetime.now().isoformat()
            },
            {
                "role": "assistant", 
                "content": response["ai_response"],
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        await db.execute(
            """UPDATE voice_conversations 
               SET conversation_history = $1, conversation_state = $2, updated_at = NOW()
               WHERE session_id = $3""",
            json.dumps(updated_history), response["conversation_state"], session_id
        )
        
        return ConversationTurnResponse(
            ai_response=response["ai_response"],
            conversation_state=response["conversation_state"],
            next_actions=response["next_actions"],
            session_id=session_id
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to process conversation turn", {
            "session_id": session_id,
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process conversation: {str(e)}"
        )

@router.post("/transcribe-audio/{session_id}")
async def transcribe_voice_input(
    session_id: str,
    audio_file: UploadFile = File(...),
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Transcribe voice input for conversation
    Revolutionary voice-to-conversation interface
    """
    
    try:
        # Check if voice processor is available
        if not service_manager.voice_processor:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice transcription service is not available. Please ensure OPENAI_API_KEY is configured."
            )
        
        # Validate session
        user_id = current_user.get("id") if current_user else "demo_user"
        db_conversation = await db.fetchrow(
            "SELECT * FROM voice_conversations WHERE session_id = $1 AND user_id = $2",
            session_id, user_id
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid audio file format: {audio_file.content_type}"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Transcribe audio using initialized voice processor
        transcription_result = await service_manager.voice_processor.transcribe_audio(
            audio_data=audio_data,
            audio_format=audio_file.content_type.split('/')[-1]
        )
        
        if not transcription_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transcription failed: {transcription_result.error_message}"
            )
            
        # Transcribe audio
        transcription_result = await voice_processor.transcribe_audio(
            audio_data=audio_data,
            audio_format=audio_file.content_type.split('/')[-1]
        )
        
        if not transcription_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transcription failed: {transcription_result.error_message}"
            )
        
        logger.log_structured("info", "Voice transcription completed", {
            "session_id": session_id,
            "user_id": user_id,
            "processing_time": transcription_result.processing_time,
            "confidence": transcription_result.confidence
        })
        
        return VoiceTranscriptionResponse(
            transcription=transcription_result.transcription,
            confidence=transcription_result.confidence,
            processing_time=transcription_result.processing_time,
            session_id=session_id
        )
        
    except Exception as e:
        logger.log_structured("error", "Voice transcription failed", {
            "session_id": session_id,
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice transcription failed: {str(e)}"
        )

@router.post("/create-agreement/{session_id}")
async def create_founder_ai_agreement(
    session_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Create binding founder-AI agreement (Contract Method)
    PATENT-WORTHY: AI-generated binding agreements
    """
    
    try:
        # Validate session
        user_id = current_user.get("id") if current_user else "demo_user"
        db_conversation = await db.fetchrow(
            "SELECT * FROM voice_conversations WHERE session_id = $1 AND user_id = $2",
            session_id, user_id
        )
        
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
        # Create founder-AI agreement
        agreement = await conversation_engine.create_founder_ai_agreement(session_id)
        
        # Update conversation with agreement
        db_conversation.founder_ai_agreement = agreement
        db_conversation.conversation_state = "agreement_created"
        db.commit()
        
        # Create project from agreement
        project = Project(
            project_name=agreement["business_specification"]["solution_description"][:100],
            user_id=user_id,
            conversation_session_id=session_id,
            founder_ai_agreement=agreement,
            technology_stack=agreement["ai_commitments"]["technology_stack"],
            status="planning"
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        logger.log_structured("info", "Founder-AI agreement created", {
            "session_id": session_id,
            "user_id": user_id,
            "project_id": project.id,
            "agreement_id": agreement["agreement_id"]
        })
        
        return FounderAgreementResponse(
            agreement_id=agreement["agreement_id"],
            project_id=project.id,
            business_specification=agreement["business_specification"],
            ai_commitments=agreement["ai_commitments"],
            success_criteria=agreement["success_criteria"],
            ready_for_code_generation=True
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to create agreement", {
            "session_id": session_id,
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agreement: {str(e)}"
        )

@router.get("/conversation/{session_id}")
async def get_conversation_history(
    session_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get complete conversation history"""
    
    user_id = current_user.get("id") if current_user else "demo_user"
    db_conversation = await db.fetchrow(
        "SELECT * FROM voice_conversations WHERE session_id = $1 AND user_id = $2",
        session_id, user_id
    )
    
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationHistoryResponse(
        session_id=session_id,
        conversation_history=db_conversation.conversation_history,
        founder_type_detected=db_conversation.founder_type_detected,
        conversation_state=db_conversation.conversation_state,
        business_validation_requested=db_conversation.business_validation_requested,
        strategy_validated=db_conversation.strategy_validated,
        founder_ai_agreement=db_conversation.founder_ai_agreement
    )

@router.get("/sessions")
async def get_user_conversation_sessions(
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get all conversation sessions for user"""
    
    conversations = db.query(VoiceConversation).filter(
        VoiceConversation.user_id == current_user.id
    ).order_by(VoiceConversation.created_at.desc()).all()
    
    return {
        "sessions": [
            {
                "session_id": conv.session_id,
                "conversation_state": conv.conversation_state,
                "founder_type_detected": conv.founder_type_detected,
                "created_at": conv.created_at.isoformat(),
                "last_message": conv.conversation_history[-1]["content"] if conv.conversation_history else None
            }
            for conv in conversations
        ]
    }
    # UPDATE ALL ROUTE DEPENDENCIES
async def example_route(
    db: asyncpg.Connection = Depends(get_db),  # Changed from Session
    current_user: Dict = Depends(get_optional_current_user)  # Changed from User
):
    # Use asyncpg operations instead of SQLAlchemy
    # Example:
    # OLD: db.query(User).filter(User.id == user_id).first()
    # NEW: await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    pass
