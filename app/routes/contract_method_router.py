"""
Contract Method API Router (PATENT-WORTHY)
Revolutionary AI agent compliance and monitoring endpoints
Patent-worthy AI behavior enforcement and deviation detection
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.database.db import get_db
from app.database.models import *
from app.utils.contract_method import ContractMethod, FounderContract, ComplianceMonitor, DeviationAlert
from app.utils.logger import get_logger
from app.utils.auth_utils import get_current_user, get_optional_current_user
from app.utils.auth_utils import get_optional_current_user


router = APIRouter(tags=["AI Compliance System"])
logger = get_logger("contract_method_api")

# Initialize contract method system
contract_method = None  # Will be initialized with LLM provider

@router.post("/register-agreement", response_model=ContractComplianceResponse)
async def register_founder_agreement(
    request: RegisterAgreementRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Register founder agreement for AI compliance monitoring
    PATENT-WORTHY: AI agent behavior enforcement system
    """
    
    try:
        # Validate project access
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.user_id == (current_user.get("id") if current_user else "demo_user")
        ).first()
        
        if not project or not project.founder_ai_agreement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project or founder agreement not found"
            )
        
        # Initialize contract method if needed
        global contract_method
        if not contract_method:
            contract_method = ContractMethod(llm_provider=None)
        
        # Create founder contract for compliance monitoring
        founder_contract = await contract_method.create_founder_agreement(
            project_id=project.id,
            founder_id=current_user.id,
            requirements=project.founder_ai_agreement
        )
        
        # Store compliance record in database
        db_compliance = ContractCompliance(
            project_id=project.id,
            founder_contract=founder_contract.__dict__,
            compliance_monitoring=[],
            deviation_alerts=[],
            compliance_score=1.0
        )
        
        db.add(db_compliance)
        db.commit()
        db.refresh(db_compliance)
        
        logger.log_structured("info", "Founder agreement registered for compliance", {
            "project_id": project.id,
            "user_id": current_user.id,
            "contract_id": founder_contract.contract_id
        })
        
        return ContractComplianceResponse(
            contract_id=founder_contract.contract_id,
            project_id=project.id,
            compliance_monitoring_enabled=True,
            initial_compliance_score=1.0,
            monitoring_rules=founder_contract.compliance_rules,
            auto_correction_enabled=founder_contract.compliance_rules["auto_correction_enabled"]
        )
        
    except Exception as e:
        logger.log_structured("error", "Failed to register agreement", {
            "project_id": request.project_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agreement: {str(e)}"
        )

@router.post("/monitor-compliance/{contract_id}")
async def monitor_ai_output_compliance(
    contract_id: str,
    request: MonitorComplianceRequest,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Monitor AI output for compliance with founder contract
    Real-time AI behavior monitoring and deviation detection
    """
    
    try:
        # Validate contract access
        db_compliance = db.query(ContractCompliance).filter(
            ContractCompliance.project_id.in_(
                db.query(Project.id).filter(Project.user_id == (current_user.get("id") if current_user else "demo_user"))
            )
        ).first()
        
        if not db_compliance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract compliance record not found"
            )
        
        # Monitor compliance
        compliance_analysis = await contract_method.monitor_ai_compliance(
            contract_id=contract_id,
            ai_output=request.ai_output
        )
        
        # Update compliance record
        if db_compliance.compliance_monitoring:
            db_compliance.compliance_monitoring.append({
                "timestamp": datetime.now().isoformat(),
                "output_analyzed": True,
                "compliance_score": compliance_analysis["compliance_score"],
                "violations_detected": len(compliance_analysis.get("violations", []))
            })
        else:
            db_compliance.compliance_monitoring = [{
                "timestamp": datetime.now().isoformat(),
                "output_analyzed": True,
                "compliance_score": compliance_analysis["compliance_score"],
                "violations_detected": len(compliance_analysis.get("violations", []))
            }]
        
        db_compliance.compliance_score = compliance_analysis["compliance_score"]
        db.commit()
        
        logger.log_structured("info", "AI compliance monitored", {
            "contract_id": contract_id,
            "user_id": current_user.id,
            "compliance_score": compliance_analysis["compliance_score"]
        })
        
        return ComplianceMonitoringResponse(
            contract_id=contract_id,
            compliance_score=compliance_analysis["compliance_score"],
            violations_detected=compliance_analysis.get("violations", []),
            recommendations=compliance_analysis.get("recommendations", []),
            auto_correction_applied=False,  # Would be determined by system
            monitoring_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.log_structured("error", "Compliance monitoring failed", {
            "contract_id": contract_id,
            "user_id": current_user.id,
            "error": str(e)
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance monitoring failed: {str(e)}"
        )

@router.get("/compliance-report/{project_id}")
async def get_compliance_report(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """Get comprehensive AI compliance report for project"""
    
    # Validate project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == (current_user.get("id") if current_user else "demo_user")
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_compliance = db.query(ContractCompliance).filter(
        ContractCompliance.project_id == project.id
    ).first()
    
    if not db_compliance:
        return ComplianceReportResponse(
            project_id=project_id,
            overall_compliance_score=1.0,
            total_outputs_monitored=0,
            violations_detected=0,
            auto_corrections_applied=0,
            compliance_trend="stable",
            last_monitoring=None
        )
    
    return ComplianceReportResponse(
        project_id=project_id,
        overall_compliance_score=db_compliance.compliance_score,
        total_outputs_monitored=len(db_compliance.compliance_monitoring),
        violations_detected=len(db_compliance.deviation_alerts),
        auto_corrections_applied=0,  # Would be calculated from monitoring history
        compliance_trend="improving",
        last_monitoring=db_compliance.compliance_monitoring[-1]["timestamp"] if db_compliance.compliance_monitoring else None
    )
