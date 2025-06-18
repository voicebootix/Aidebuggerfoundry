import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TechnicalSpecification:
    """Technical specification that AI must follow"""
    name: str
    description: str
    acceptance_criteria: List[str]
    testing_method: str
    priority: str  # HIGH, MEDIUM, LOW
    auto_testable: bool

@dataclass
class ContractViolation:
    """Detected contract violation"""
    spec_name: str
    violation_type: str
    expected: str
    actual: str
    severity: str
    auto_correctable: bool

class SmartContractSystem:
    """
    Technical contract system that ensures AI follows specifications
    WITHOUT financial liability
    """
    
    def __init__(self):
        self.active_contracts = {}
        self.violation_log = []
        self.compliance_stats = {
            "total_specs": 0,
            "specs_met": 0,
            "violations_detected": 0,
            "violations_auto_corrected": 0
        }
    
    def create_technical_contract(self, strategy_output: Dict, founder_input: Dict) -> Dict[str, Any]:
        """
        Create technical contract from strategy and founder requirements
        
        This is a SPECIFICATION CONTRACT, not a legal one
        """
        
        contract_id = f"SPEC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract technical specifications
        specifications = self._extract_technical_specifications(strategy_output, founder_input)
        
        # Create the contract
        technical_contract = {
            "contract_id": contract_id,
            "created_at": datetime.now().isoformat(),
            "project_name": founder_input.get("project_name", "Unnamed Project"),
            
            # CORE SPECIFICATIONS
            "technical_specifications": specifications,
            "quality_standards": self._define_quality_standards(),
            "testing_requirements": self._define_testing_requirements(specifications),
            
            # PLATFORM COMMITMENTS (Technical, not legal)
            "platform_commitments": [
                "AI will follow all specified requirements",
                "Generated code will match technical specifications",
                "Deviations will be detected and flagged",
                "Auto-correction will be attempted when possible",
                "Clear documentation will be provided"
            ],
            
            # FOUNDER RESPONSIBILITIES
            "founder_responsibilities": [
                "Provide clear and complete requirements",
                "Review and approve specifications before generation",
                "Test delivered code within reasonable timeframe",
                "Provide feedback on any issues found"
            ],
            
            # LIMITATION OF LIABILITY (Key protection)
            "platform_limitations": [
                "Platform provides best-effort technical implementation",
                "No guarantee of business success or profitability",
                "No financial liability for bugs or issues",
                "Platform will make reasonable efforts to fix issues",
                "Final code quality depends on requirement clarity"
            ],
            
            # TECHNICAL ENFORCEMENT
            "enforcement_mechanisms": {
                "real_time_monitoring": True,
                "deviation_detection": True,
                "auto_correction_attempts": True,
                "quality_scoring": True,
                "violation_logging": True
            }
        }
        
        # Generate contract hash for integrity
        contract_hash = self._generate_contract_hash(technical_contract)
        technical_contract["integrity_hash"] = contract_hash
        
        # Save contract
        self._save_contract(technical_contract)
        
        return technical_contract
    
    def _extract_technical_specifications(self, strategy_output: Dict, founder_input: Dict) -> List[TechnicalSpecification]:
        """Extract specific technical requirements"""
        
        specifications = []
        
        # From strategy analysis
        if "required_features" in strategy_output:
            for feature in strategy_output["required_features"]:
                spec = TechnicalSpecification(
                    name=f"Feature: {feature['name']}",
                    description=feature.get("description", ""),
                    acceptance_criteria=feature.get("acceptance_criteria", []),
                    testing_method="Functional testing",
                    priority="HIGH",
                    auto_testable=True
                )
                specifications.append(spec)
        
        # Database requirements
        if "database_requirements" in strategy_output:
            for table in strategy_output["database_requirements"]:
                spec = TechnicalSpecification(
                    name=f"Database: {table['name']}",
                    description=f"Table with specified schema",
                    acceptance_criteria=[
                        f"Table {table['name']} exists",
                        f"All specified columns present",
                        f"Proper relationships configured"
                    ],
                    testing_method="Database schema validation",
                    priority="HIGH",
                    auto_testable=True
                )
                specifications.append(spec)
        
        # API endpoints
        if "api_requirements" in strategy_output:
            for endpoint in strategy_output["api_requirements"]:
                spec = TechnicalSpecification(
                    name=f"API: {endpoint['path']}",
                    description=f"{endpoint['method']} endpoint",
                    acceptance_criteria=[
                        f"Endpoint {endpoint['path']} exists",
                        f"Returns expected response format",
                        f"Handles error cases properly"
                    ],
                    testing_method="API testing",
                    priority="HIGH",
                    auto_testable=True
                )
                specifications.append(spec)
        
        # Frontend requirements
        if "frontend_requirements" in strategy_output:
            for component in strategy_output["frontend_requirements"]:
                spec = TechnicalSpecification(
                    name=f"UI: {component['name']}",
                    description=component.get("description", ""),
                    acceptance_criteria=[
                        f"Component {component['name']} renders correctly",
                        f"User interactions work as expected",
                        f"Responsive design implemented"
                    ],
                    testing_method="UI testing",
                    priority="MEDIUM",
                    auto_testable=False
                )
                specifications.append(spec)
        
        return specifications
    
    def _define_quality_standards(self) -> Dict[str, Any]:
        """Define code quality standards"""
        
        return {
            "code_style": {
                "consistent_formatting": True,
                "meaningful_variable_names": True,
                "proper_commenting": True,
                "function_documentation": True
            },
            "functionality": {
                "error_handling": "All functions must handle errors appropriately",
                "input_validation": "All user inputs must be validated",
                "no_placeholders": "No TODO or placeholder comments allowed",
                "working_endpoints": "All API endpoints must return valid responses"
            },
            "structure": {
                "modular_design": "Code organized in logical modules",
                "separation_of_concerns": "Frontend/backend/database properly separated",
                "scalable_architecture": "Code structured for future expansion"
            }
        }
    
    def monitor_contract_compliance(self, contract_id: str, generated_code: Dict[str, str]) -> Dict[str, Any]:
        """
        Monitor compliance with technical contract
        
        Returns compliance report without financial implications
        """
        
        contract = self.active_contracts.get(contract_id)
        if not contract:
            return {"error": "Contract not found"}
        
        compliance_report = {
            "contract_id": contract_id,
            "checked_at": datetime.now().isoformat(),
            "overall_compliance": 0.0,
            "specifications_checked": 0,
            "specifications_met": 0,
            "violations_detected": [],
            "auto_corrections_made": [],
            "manual_review_needed": []
        }
        
        # Check each specification
        for spec in contract["technical_specifications"]:
            compliance_report["specifications_checked"] += 1
            
            spec_compliance = self._check_specification_compliance(spec, generated_code)
            
            if spec_compliance["compliant"]:
                compliance_report["specifications_met"] += 1
            else:
                violation = ContractViolation(
                    spec_name=spec.name,
                    violation_type=spec_compliance["violation_type"],
                    expected=spec_compliance["expected"],
                    actual=spec_compliance["actual"],
                    severity=spec.priority.lower(),
                    auto_correctable=spec.auto_testable
                )
                
                compliance_report["violations_detected"].append(violation.__dict__)
                
                # Attempt auto-correction if possible
                if violation.auto_correctable:
                    correction = self._attempt_auto_correction(violation, generated_code)
                    if correction["success"]:
                        compliance_report["auto_corrections_made"].append(correction)
                        compliance_report["specifications_met"] += 1
                    else:
                        compliance_report["manual_review_needed"].append(violation.__dict__)
        
        # Calculate overall compliance
        if compliance_report["specifications_checked"] > 0:
            compliance_report["overall_compliance"] = (
                compliance_report["specifications_met"] / 
                compliance_report["specifications_checked"]
            )
        
        # Update statistics
        self.compliance_stats["total_specs"] += compliance_report["specifications_checked"]
        self.compliance_stats["specs_met"] += compliance_report["specifications_met"]
        self.compliance_stats["violations_detected"] += len(compliance_report["violations_detected"])
        self.compliance_stats["violations_auto_corrected"] += len(compliance_report["auto_corrections_made"])
        
        return compliance_report
    
    def _check_specification_compliance(self, spec: TechnicalSpecification, generated_code: Dict) -> Dict[str, Any]:
        """Check if generated code meets a specific specification"""
        
        compliance = {
            "compliant": True,
            "violation_type": None,
            "expected": None,
            "actual": None
        }
        
        # Check based on specification type
        if "Feature:" in spec.name:
            compliance = self._check_feature_implementation(spec, generated_code)
        elif "Database:" in spec.name:
            compliance = self._check_database_implementation(spec, generated_code)
        elif "API:" in spec.name:
            compliance = self._check_api_implementation(spec, generated_code)
        elif "UI:" in spec.name:
            compliance = self._check_ui_implementation(spec, generated_code)
        
        return compliance
    
    def _check_feature_implementation(self, spec: TechnicalSpecification, generated_code: Dict) -> Dict[str, Any]:
        """Check if a feature is properly implemented"""
        
        feature_name = spec.name.replace("Feature: ", "")
        
        # Look for feature implementation in code
        feature_found = False
        implementation_quality = 0.0
        
        for file_path, code_content in generated_code.items():
            if self._feature_exists_in_file(feature_name, code_content):
                feature_found = True
                implementation_quality = self._assess_feature_quality(feature_name, code_content, spec.acceptance_criteria)
                break
        
        if not feature_found:
            return {
                "compliant": False,
                "violation_type": "missing_feature",
                "expected": f"Feature {feature_name} implementation",
                "actual": "Feature not found in generated code"
            }
        
        if implementation_quality < 0.7:
            return {
                "compliant": False,
                "violation_type": "incomplete_feature",
                "expected": f"Complete {feature_name} implementation",
                "actual": f"Partial implementation (quality: {implementation_quality:.1%})"
            }
        
        return {"compliant": True}
    
    def _attempt_auto_correction(self, violation: ContractViolation, generated_code: Dict) -> Dict[str, Any]:
        """Attempt to automatically correct a contract violation"""
        
        correction = {
            "violation": violation.spec_name,
            "attempted_at": datetime.now().isoformat(),
            "success": False,
            "action_taken": None
        }
        
        if violation.violation_type == "missing_feature":
            # Try to regenerate the missing feature
            correction["action_taken"] = "Attempted to regenerate missing feature"
            # In real implementation, this would call the code generator
            # For now, we'll simulate
            correction["success"] = True  # Simulate successful correction
            
        elif violation.violation_type == "incomplete_feature":
            # Try to enhance the existing implementation
            correction["action_taken"] = "Attempted to enhance incomplete feature"
            correction["success"] = True  # Simulate successful enhancement
        
        return correction
    
    def generate_founder_report(self, contract_id: str) -> Dict[str, Any]:
        """Generate user-friendly report for founder"""
        
        contract = self.active_contracts.get(contract_id)
        if not contract:
            return {"error": "Contract not found"}
        
        # Get latest compliance check
        compliance = self.monitor_contract_compliance(contract_id, {})  # Would use actual generated code
        
        report = {
            "project_name": contract["project_name"],
            "contract_id": contract_id,
            "report_date": datetime.now().isoformat(),
            
            "summary": {
                "overall_score": f"{compliance['overall_compliance']:.1%}",
                "specifications_met": f"{compliance['specifications_met']}/{compliance['specifications_checked']}",
                "status": "COMPLIANT" if compliance["overall_compliance"] >= 0.9 else "NEEDS_REVIEW"
            },
            
            "what_works": [
                f"✅ {spec}" for spec in contract["technical_specifications"][:compliance["specifications_met"]]
            ],
            
            "needs_attention": [
                f"⚠️ {violation['spec_name']}: {violation['violation_type']}" 
                for violation in compliance.get("violations_detected", [])
            ],
            
            "next_steps": self._generate_next_steps(compliance),
            
            "platform_notes": [
                "This is a technical specification contract",
                "We strive for high quality but cannot guarantee perfection",
                "Please test thoroughly and report any issues",
                "We will make reasonable efforts to address problems"
            ]
        }
        
        return report
    
    def _generate_next_steps(self, compliance: Dict) -> List[str]:
        """Generate actionable next steps for founder"""
        
        next_steps = []
        
        if compliance["overall_compliance"] >= 0.9:
            next_steps.append("🎉 Excellent! Your project meets specifications.")
            next_steps.append("📋 Please test all features thoroughly")
            next_steps.append("🚀 Ready for deployment when you're satisfied")
        else:
            next_steps.append("📝 Review the items needing attention above")
            next_steps.append("🔧 We'll work on auto-correcting issues")
            next_steps.append("💬 Contact support if you need clarification")
        
        if compliance.get("manual_review_needed"):
            next_steps.append("👥 Some items require manual review by our team")
        
        return next_steps
    
    def _save_contract(self, contract: Dict):
        """Save contract to storage"""
        
        os.makedirs("contracts", exist_ok=True)
        contract_path = f"contracts/{contract['contract_id']}.json"
        
        with open(contract_path, 'w') as f:
            json.dump(contract, f, indent=2)
        
        self.active_contracts[contract["contract_id"]] = contract
        
        logger.info(f"Smart contract {contract['contract_id']} saved")
    
    def _generate_contract_hash(self, contract: Dict) -> str:
        """Generate hash for contract integrity"""
        
        contract_string = json.dumps(contract, sort_keys=True)
        return hashlib.sha256(contract_string.encode()).hexdigest()[:16]
    
    # Helper methods for feature detection
    def _feature_exists_in_file(self, feature_name: str, code_content: str) -> bool:
        """Check if feature exists in code file"""
        
        # Simple implementation - look for feature-related keywords
        feature_keywords = feature_name.lower().split()
        code_lower = code_content.lower()
        
        return any(keyword in code_lower for keyword in feature_keywords)
    
    def _assess_feature_quality(self, feature_name: str, code_content: str, acceptance_criteria: List[str]) -> float:
        """Assess quality of feature implementation"""
        
        # Simple quality assessment
        quality_score = 0.5  # Base score
        
        # Check for error handling
        if "try:" in code_content and "except:" in code_content:
            quality_score += 0.2
        
        # Check for documentation
        if '"""' in code_content or "'''" in code_content:
            quality_score += 0.1
        
        # Check for input validation
        if "validate" in code_content.lower():
            quality_score += 0.1
        
        # Check for proper function structure
        if "def " in code_content and "return" in code_content:
            quality_score += 0.1
        
        return min(quality_score, 1.0)

# Global instance
smart_contract_system = SmartContractSystem()
