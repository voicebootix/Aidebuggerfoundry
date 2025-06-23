
"""
Business Intelligence API Router (INTELLIGENT)
Optional but intelligent business validation and strategy analysis
Real market research and competitor analysis APIs
"""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
import uuid
from app.utils.auth_utils import get_current_user, get_optional_current_user

from app.database.db import get_db
from app.database.models import *
from app.utils.business_intelligence import BusinessIntelligence, MarketAnalysis, CompetitorAnalysis, BusinessValidation
from app.utils.logger import get_logger
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["Smart Business Validation"])
logger = get_logger("business_intelligence_api")

# Initialize business intelligence engine
business_intelligence = None  # Will be initialized with LLM provider

@router.post("/analyze-market", response_model=MarketAnalysisResponse)
async def analyze_market_opportunity(
    request: MarketAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Comprehensive market opportunity analysis
    Real-time market research and validation
    """
    
    try:
        # Handle demo mode
        user_id = current_user.get("id") if current_user else "demo_user"
        user_email = current_user.get("email") if current_user else "demo@example.com"
        
        # Initialize business intelligence if needed
        global business_intelligence
        if not business_intelligence:
            from app.utils.llm_provider import EnhancedLLMProvider
            llm_provider = EnhancedLLMProvider()
            business_intelligence = BusinessIntelligence(llm_provider.openai_client)
        
        # Handle business_idea whether it's string or dict
        if isinstance(request.business_idea, dict):
            business_idea_text = request.business_idea.get("description", str(request.business_idea))
        else:
            business_idea_text = str(request.business_idea)

        market_analysis = await business_intelligence.analyze_market_opportunity(
            business_idea=business_idea_text
        )
        
        # Generate conversation ID if not provided
        conversation_id = getattr(request, 'conversation_id', None)
        if not conversation_id:
            conversation_id = f"conv_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Store analysis in database
        db_validation = BusinessValidation(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            market_analysis={
                "market_size": market_analysis.market_size,
                "growth_rate": market_analysis.growth_rate,
                "key_trends": market_analysis.key_trends,
                "opportunities": market_analysis.opportunities,
                "threats": market_analysis.threats,
                "confidence_score": market_analysis.confidence_score
            },
            created_at=datetime.utcnow()
        )
        
        db.add(db_validation)
        db.commit()
        db.refresh(db_validation)
        
        logger.info(f"Market analysis completed for user: {user_id}, conversation: {conversation_id}")
        
        return MarketAnalysisResponse(
            analysis_id=db_validation.id,
            market_size=market_analysis.market_size,
            growth_rate=market_analysis.growth_rate,
            key_trends=market_analysis.key_trends,
            opportunities=market_analysis.opportunities,
            threats=market_analysis.threats,
            confidence_score=market_analysis.confidence_score,
            recommendations=["Proceed with MVP development", "Validate with target customers", "Monitor competition closely"]
        )
        
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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    
    """
    AI-powered competitor research and analysis
    Comprehensive competitive landscape analysis
    """
    
    try:
        # Perform competitor research
        competitor_analysis = await business_intelligence.research_competitors(
            business_domain=request.business_domain,
            solution_type=request.solution_type
        )
        
        # Update existing validation record
        db_validation = db.query(BusinessValidation).filter(
            BusinessValidation.conversation_id == request.conversation_id
        ).first()
        
        if db_validation:
            db_validation.competitor_research = {
                "direct_competitors": competitor_analysis.direct_competitors,
                "indirect_competitors": competitor_analysis.indirect_competitors,
                "competitive_advantages": competitor_analysis.competitive_advantages,
                "market_gaps": competitor_analysis.market_gaps,
                "differentiation_strategy": competitor_analysis.differentiation_strategy
            }
            db.commit()
        
        return CompetitorAnalysisResponse(
            direct_competitors=competitor_analysis.direct_competitors,
            indirect_competitors=competitor_analysis.indirect_competitors,
            competitive_advantages=competitor_analysis.competitive_advantages,
            market_gaps=competitor_analysis.market_gaps,
            differentiation_strategy=competitor_analysis.differentiation_strategy,
            competitive_positioning_score=0.8
        )
        
    except Exception as e:
        logger.log_structured("error", "Competitor research failed", {
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor research failed: {str(e)}"
        )

@router.post("/validate-business-model")
async def validate_business_model(
    request: BusinessModelValidationRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Comprehensive business model validation
    Revenue model feasibility and recommendations
    """
    
    try:
        # Get market analysis for context
        db_validation = db.query(BusinessValidation).filter(
            BusinessValidation.conversation_id == request.conversation_id
        ).first()
        
        if not db_validation or not db_validation.market_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Market analysis required before business model validation"
            )
        
        # Convert to MarketAnalysis object
        market_data = db_validation.market_analysis
        market_analysis = MarketAnalysis(
            market_size=market_data["market_size"],
            growth_rate=market_data["growth_rate"],
            key_trends=market_data["key_trends"],
            opportunities=market_data["opportunities"],
            threats=market_data["threats"],
            confidence_score=market_data["confidence_score"]
        )
        
        # Validate business model
        validation = await business_intelligence.validate_business_model(
            business_idea=request.business_idea,
            market_analysis=market_analysis
        )
        
        # Update validation record
        db_validation.business_model_validation = {
            "feasibility_score": validation.feasibility_score,
            "market_potential": validation.market_potential,
            "revenue_projection": validation.revenue_projection,
            "risk_assessment": validation.risk_assessment,
            "recommendations": validation.recommendations
        }
        db_validation.validation_score = validation.feasibility_score
        db.commit()
        
        return BusinessModelValidationResponse(
            feasibility_score=validation.feasibility_score,
            market_potential=validation.market_potential,
            revenue_projection=validation.revenue_projection,
            risk_assessment=validation.risk_assessment,
            recommendations=validation.recommendations,
            validation_summary=f"Business model shows {validation.market_potential.lower()} potential with {validation.feasibility_score:.1%} feasibility"
        )
        
    except Exception as e:
        logger.log_structured("error", "Business model validation failed", {
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business model validation failed: {str(e)}"
        )

@router.post("/generate-business-plan")
async def generate_comprehensive_business_plan(
    request: BusinessPlanRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Generate comprehensive AI-powered business plan
    Complete business strategy and implementation plan
    """
    
    try:
        # Get complete validation data
        db_validation = db.query(BusinessValidation).filter(
            BusinessValidation.conversation_id == request.conversation_id
        ).first()
        
        if not db_validation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business validation required before generating business plan"
            )
        
        # Create business plan from validation data
        business_plan = await business_intelligence.create_business_plan(
            business_idea=request.business_idea,
            market_analysis=MarketAnalysis(**db_validation.market_analysis),
            competitor_analysis=CompetitorAnalysis(**db_validation.competitor_research),
            validation=BusinessValidation(**db_validation.business_model_validation)
        )
        
        # Store business plan
        db_validation.strategy_recommendations = business_plan
        db.commit()
        
        return BusinessPlanResponse(
            business_plan=business_plan,
            executive_summary=business_plan["executive_summary"],
            implementation_timeline=business_plan["implementation_plan"],
            confidence_score=business_plan["confidence_score"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Business plan generation failed", {
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business plan generation failed: {str(e)}"
        )

@router.get("/validation-summary/{conversation_id}")
async def get_validation_summary(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get complete business validation summary"""
    
    db_validation = db.query(BusinessValidation).filter(
        BusinessValidation.conversation_id == conversation_id
    ).first()
    
    if not db_validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business validation not found"
        )
    
    return BusinessValidationSummaryResponse(
        validation_id=db_validation.id,
        conversation_id=conversation_id,
        market_analysis=db_validation.market_analysis,
        competitor_research=db_validation.competitor_research,
        business_model_validation=db_validation.business_model_validation,
        strategy_recommendations=db_validation.strategy_recommendations,
        overall_validation_score=db_validation.validation_score,
        created_at=db_validation.created_at.isoformat()
    )
    
