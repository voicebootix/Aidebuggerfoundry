"""
Business Intelligence API Router (INTELLIGENT)
Optional but intelligent business validation and strategy analysis
Real market research and competitor analysis APIs
"""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import uuid
import asyncpg
import json

from app.database.db import get_db
from app.database.models import *
from app.utils.business_intelligence import BusinessIntelligence, MarketAnalysis, CompetitorAnalysis, BusinessValidation
from app.utils.logger import get_logger
from app.utils.auth_utils import get_optional_current_user
from app.services import service_manager


router = APIRouter(tags=["Smart Business Validation"])
logger = get_logger("business_intelligence_api")

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

@router.post("/analyze-market", response_model=MarketAnalysisResponse)
async def analyze_market_opportunity(
    request: MarketAnalysisRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Comprehensive market opportunity analysis
    Real-time market research and validation
    """
    try:
        user_id = current_user.get("id") if current_user else DEMO_USER_ID
        user_email = current_user.get("email") if current_user else "demo@example.com"
        
        # Check if business intelligence service is available
        if not service_manager.business_intelligence:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Business intelligence service is not available. Please ensure LLM provider is configured."
            )
        
        # Extract business idea text
        if isinstance(request.business_idea, dict):
            business_idea_text = request.business_idea.get("description", str(request.business_idea))
        else:
            business_idea_text = str(request.business_idea)
        
        # Perform market analysis
        market_analysis = await service_manager.business_intelligence.analyze_market_opportunity(
            business_idea=business_idea_text
        )
        
        # Generate conversation ID if not provided
        conversation_id = getattr(request, 'conversation_id', None)
        if not conversation_id:
            conversation_id = f"conv_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Store validation record - Fixed missing user_id
        validation_id = str(uuid.uuid4())
        
        # First check if we need to update existing record
        existing = await db.fetchrow(
            "SELECT id FROM business_validations WHERE conversation_id = $1",
            conversation_id
        )
        
        if existing:
            # Update existing record
            await db.execute(
                """UPDATE business_validations 
                SET market_analysis = $1, updated_at = NOW()
                WHERE conversation_id = $2""",
                json.dumps({
                    "market_size": market_analysis.market_size,
                    "growth_rate": market_analysis.growth_rate,
                    "key_trends": market_analysis.key_trends,
                    "opportunities": market_analysis.opportunities,
                    "threats": market_analysis.threats,
                    "confidence_score": market_analysis.confidence_score
                }),
                conversation_id
            )
            validation_id = existing['id']
        else:
            # Insert new record with user_id
            await db.execute(
                """INSERT INTO business_validations 
                (id, conversation_id, user_id, market_analysis, created_at)
                VALUES ($1, $2, $3, $4, NOW())""",
                validation_id,
                conversation_id,
                user_id,
                json.dumps({
                    "market_size": market_analysis.market_size,
                    "growth_rate": market_analysis.growth_rate,
                    "key_trends": market_analysis.key_trends,
                    "opportunities": market_analysis.opportunities,
                    "threats": market_analysis.threats,
                    "confidence_score": market_analysis.confidence_score
                })
            )
        
        logger.info(f"Market analysis completed for user: {user_id}, conversation: {conversation_id}")
        
        return MarketAnalysisResponse(
            analysis_id=validation_id,
            market_size=market_analysis.market_size,
            growth_rate=market_analysis.growth_rate,
            key_trends=market_analysis.key_trends,
            opportunities=market_analysis.opportunities,
            threats=market_analysis.threats,
            confidence_score=market_analysis.confidence_score,
            recommendations=[
                "Proceed with MVP development", 
                "Validate with target customers", 
                "Monitor competition closely"
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Market analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market analysis failed: {str(e)}"
        )

@router.post("/research-competitors")
async def research_competitors(
    request: CompetitorResearchRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    AI-powered competitor research and analysis
    Comprehensive competitive landscape analysis
    """
    try:
        user_id = current_user.get("id") if current_user else DEMO_USER_ID
        
        # Check service availability
        if not service_manager.business_intelligence:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business intelligence service is not available."
            )
        
        # Perform competitor research
        competitor_analysis = await service_manager.business_intelligence.research_competitors(
            business_domain=request.business_domain,
            solution_type=request.solution_type
        )
        
        # Update existing validation record
        existing = await db.fetchrow(
            "SELECT id FROM business_validations WHERE conversation_id = $1",
            request.conversation_id
        )
        
        if existing:
            await db.execute(
                """UPDATE business_validations 
                SET competitor_research = $1, updated_at = NOW()
                WHERE conversation_id = $2""",
                json.dumps({
                    "direct_competitors": competitor_analysis.direct_competitors,
                    "indirect_competitors": competitor_analysis.indirect_competitors,
                    "competitive_advantages": competitor_analysis.competitive_advantages,
                    "market_gaps": competitor_analysis.market_gaps,
                    "differentiation_strategy": competitor_analysis.differentiation_strategy
                }),
                request.conversation_id
            )
        
        return CompetitorAnalysisResponse(
            direct_competitors=competitor_analysis.direct_competitors,
            indirect_competitors=competitor_analysis.indirect_competitors,
            competitive_advantages=competitor_analysis.competitive_advantages,
            market_gaps=competitor_analysis.market_gaps,
            differentiation_strategy=competitor_analysis.differentiation_strategy,
            competitive_positioning_score=0.8
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_structured("error", "Competitor research failed", {
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor research failed: {str(e)}"
        )

@router.post("/validate-business-model")
async def validate_business_model(
    request: BusinessModelValidationRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Comprehensive business model validation
    Revenue model feasibility and recommendations
    """
    try:
        user_id = current_user.get("id") if current_user else DEMO_USER_ID
        
        # Check service availability
        if not service_manager.business_intelligence:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Business intelligence service is not available."
            )
        
        # Get market analysis for context
        db_validation = await db.fetchrow(
            "SELECT * FROM business_validations WHERE conversation_id = $1",
            request.conversation_id
        )
        
        if not db_validation or not db_validation['market_analysis']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Market analysis required before business model validation"
            )
        
        # Convert to MarketAnalysis object
        market_data = json.loads(db_validation['market_analysis'])
        market_analysis = MarketAnalysis(
            market_size=market_data["market_size"],
            growth_rate=market_data["growth_rate"],
            key_trends=market_data["key_trends"],
            opportunities=market_data["opportunities"],
            threats=market_data["threats"],
            confidence_score=market_data["confidence_score"]
        )
        
        # Validate business model
        validation = await service_manager.business_intelligence.validate_business_model(
            business_idea=request.business_idea,
            market_analysis=market_analysis
        )
        
        # Update validation record
        await db.execute(
            """UPDATE business_validations 
            SET business_model_validation = $1, validation_score = $2, updated_at = NOW()
            WHERE conversation_id = $3""",
            json.dumps({
                "feasibility_score": validation.feasibility_score,
                "market_potential": validation.market_potential,
                "revenue_projection": validation.revenue_projection,
                "risk_assessment": validation.risk_assessment,
                "recommendations": validation.recommendations
            }),
            validation.feasibility_score,
            request.conversation_id
        )
        
        return BusinessModelValidationResponse(
            feasibility_score=validation.feasibility_score,
            market_potential=validation.market_potential,
            revenue_projection=validation.revenue_projection,
            risk_assessment=validation.risk_assessment,
            recommendations=validation.recommendations,
            validation_summary=f"Business model shows {validation.market_potential.lower()} potential with {validation.feasibility_score:.1%} feasibility"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_structured("error", "Business model validation failed", {
            "user_id": user_id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business model validation failed: {str(e)}"
        )

@router.post("/generate-business-plan")
async def generate_comprehensive_business_plan(
    request: BusinessPlanRequest,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Generate comprehensive AI-powered business plan
    Complete business strategy and implementation plan
    """
    
    try:
        # Get complete validation data
        db_validation = await db.fetchrow(
            "SELECT * FROM business_validations WHERE conversation_id = $1",
            request.conversation_id
        )
        
        if not db_validation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business validation required before generating business plan"
            )
        
        # Create business plan from validation data
        business_plan = await service_manager.business_intelligence.create_business_plan(
            business_idea=request.business_idea,
            market_analysis=MarketAnalysis(**json.loads(db_validation['market_analysis'])),
            competitor_analysis=CompetitorAnalysis(**json.loads(db_validation['competitor_research'])),
            validation=BusinessValidation(**json.loads(db_validation['business_model_validation']))
        )
        
        # Store business plan
        await db.execute(
            """UPDATE business_validations 
            SET strategy_recommendations = $1, updated_at = NOW()
            WHERE conversation_id = $2""",
            json.dumps(business_plan),
            request.conversation_id
        )
        
        return BusinessPlanResponse(
            business_plan=business_plan,
            executive_summary=business_plan["executive_summary"],
            implementation_timeline=business_plan["implementation_plan"],
            confidence_score=business_plan["confidence_score"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Business plan generation failed", {
            "user_id": current_user.get("id"),
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business plan generation failed: {str(e)}"
        )

@router.get("/validation-summary/{conversation_id}")
async def get_validation_summary(
    conversation_id: str,
    db: asyncpg.Connection = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get complete business validation summary"""
    
    db_validation = await db.fetchrow(
        "SELECT * FROM business_validations WHERE conversation_id = $1",
        conversation_id
    )
    
    if not db_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business validation not found"
        )
    
    return BusinessValidationSummaryResponse(
        validation_id=db_validation['id'],
        conversation_id=conversation_id,
        market_analysis=json.loads(db_validation['market_analysis']),
        competitor_research=json.loads(db_validation['competitor_research']),
        business_model_validation=json.loads(db_validation['business_model_validation']),
        strategy_recommendations=json.loads(db_validation['strategy_recommendations']),
        overall_validation_score=db_validation['validation_score'],
        created_at=db_validation['created_at'].isoformat()
    )
    
