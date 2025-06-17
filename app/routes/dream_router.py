@router.post("/validate-idea")
async def validate_idea(request: IdeaValidationRequest):
    """Start conversational strategy validation"""
    try:
        from app.utils.strategy_consultant import strategy_consultant
        
        result = await strategy_consultant.start_strategy_conversation(
            user_id=request.user_id or "anonymous",
            initial_idea=request.idea
        )
        
        return {
            "status": "success", 
            "validation_type": "conversational_analysis",
            **result
        }
        
    except Exception as e:
        logger.error(f"❌ Strategy validation failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Strategy validation failed: {str(e)}"
        }

@router.post("/continue-strategy-conversation")
async def continue_strategy_conversation(
    session_id: str,
    user_response: str
):
    """Continue strategy conversation"""
    try:
        from app.utils.strategy_consultant import strategy_consultant
        
        result = await strategy_consultant.continue_conversation(
            session_id=session_id,
            user_response=user_response
        )
        
        return {"status": "success", **result}
        
    except Exception as e:
        logger.error(f"❌ Strategy conversation failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Conversation failed: {str(e)}"
        }
