from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any
import logging

from app.utils.contract_generator import contract_generator
from app.utils.contract_enforcer import AutonomousContractEnforcer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/contracts", tags=["contracts"])

# Initialize enforcer
contract_enforcer = AutonomousContractEnforcer()

class ContractCreationRequest(BaseModel):
    strategy_analysis: Dict[str, Any]
    founder_clarifications: Dict[str, Any]

class ContractApprovalRequest(BaseModel):
    contract_id: str
    founder_signature: str

@router.post("/create")
async def create_contract(request: ContractCreationRequest):
    """Create formal contract from strategy analysis"""
    try:
        contract = contract_generator.create_formal_contract(
            request.strategy_analysis,
            request.founder_clarifications
        )
        
        return {
            "status": "success",
            "contract": contract,
            "message": "Formal contract created. Please review and approve."
        }
        
    except Exception as e:
        logger.error(f"Contract creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve")
async def approve_contract(request: ContractApprovalRequest):
    """Approve contract and start generation"""
    try:
        # Mark contract as approved
        contract_enforcer.active_contracts[request.contract_id] = {
            "approved_at": datetime.now().isoformat(),
            "founder_signature": request.founder_signature,
            "status": "active"
        }
        
        return {
            "status": "approved",
            "message": "Contract approved. Code generation will begin.",
            "contract_id": request.contract_id
        }
        
    except Exception as e:
        logger.error(f"Contract approval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}/compliance")
async def check_contract_compliance(contract_id: str):
    """Real-time contract compliance check"""
    try:
        compliance_report = contract_enforcer.generate_compliance_report(contract_id)
        return compliance_report
        
    except Exception as e:
        logger.error(f"Compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
