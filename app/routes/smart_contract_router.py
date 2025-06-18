from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import logging

from app.utils.smart_contract_system import smart_contract_system

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/smart-contracts", tags=["smart-contracts"])

class ContractCreationRequest(BaseModel):
    strategy_output: Dict[str, Any]
    founder_input: Dict[str, Any]

class ContractApprovalRequest(BaseModel):
    contract_id: str
    founder_approval: bool

@router.post("/create")
async def create_smart_contract(request: ContractCreationRequest):
    """Create technical specification contract"""
    try:
        contract = smart_contract_system.create_technical_contract(
            request.strategy_output,
            request.founder_input
        )
        
        return {
            "status": "success",
            "contract": contract,
            "message": "Technical contract created. Please review specifications."
        }
        
    except Exception as e:
        logger.error(f"Smart contract creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve")
async def approve_contract(request: ContractApprovalRequest):
    """Approve technical contract"""
    try:
        if request.founder_approval:
            # Mark as approved and ready for generation
            return {
                "status": "approved",
                "message": "Technical specifications approved. Code generation will follow these requirements.",
                "contract_id": request.contract_id
            }
        else:
            return {
                "status": "rejected",
                "message": "Contract rejected. Please modify requirements.",
                "contract_id": request.contract_id
            }
        
    except Exception as e:
        logger.error(f"Contract approval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}/compliance")
async def check_compliance(contract_id: str):
    """Check contract compliance"""
    try:
        # In real implementation, this would get the actual generated code
        mock_generated_code = {}  # Would be actual code files
        
        compliance_report = smart_contract_system.monitor_contract_compliance(
            contract_id, 
            mock_generated_code
        )
        
        return compliance_report
        
    except Exception as e:
        logger.error(f"Compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}/report")
async def get_founder_report(contract_id: str):
    """Get user-friendly contract report"""
    try:
        report = smart_contract_system.generate_founder_report(contract_id)
        return report
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
