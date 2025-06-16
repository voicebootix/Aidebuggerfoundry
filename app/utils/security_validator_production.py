import re
import ast
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    severity: str  # "critical", "high", "medium", "low"
    issue_type: str
    description: str
    line_number: int
    suggestion: str

class ProductionSecurityValidator:
    """Production-grade security validator with AST analysis"""
    
    def __init__(self):
        self.dangerous_patterns = [
            (r'os\.system\s*\(', "critical", "OS command execution"),
            (r'subprocess\.(run|call|Popen)', "critical", "Subprocess execution"),
            (r'eval\s*\(', "critical", "Dynamic code evaluation"),
            (r'exec\s*\(', "critical", "Dynamic code execution"),
            (r'__import__\s*\(', "high", "Dynamic imports"),
            (r'open\s*\([\'"][^\'"]*/[^\'"]', "medium", "File system access"),
            (r'requests\.(get|post|put|delete)', "medium", "HTTP requests"),
            (r'socket\.(socket|bind|connect)', "medium", "Network socket usage"),
            (r'pickle\.loads?', "high", "Pickle deserialization"),
            (r'yaml\.load\s*\(', "high", "Unsafe YAML loading"),
        ]
        
        self.input_validation_patterns = [
            (r'<script[^>]*>', "high", "XSS script injection"),
            (r'javascript:', "high", "JavaScript injection"),
            (r'SELECT.*FROM.*WHERE', "high", "Potential SQL injection"),
            (r'DROP\s+TABLE', "critical", "SQL table drop"),
            (r'DELETE\s+FROM', "high", "SQL delete operation"),
            (r'INSERT\s+INTO', "medium", "SQL insert operation"),
        ]
    
    def validate_code_safety(self, code: str) -> Dict[str, Any]:
        """Comprehensive code safety validation"""
        
        issues = []
        
        # Pattern-based security checks
        issues.extend(self._check_dangerous_patterns(code))
        
        # AST-based security checks (for Python code)
        if self._is_python_code(code):
            issues.extend(self._ast_security_check(code))
        
        # Input validation checks
        issues.extend(self._check_input_validation(code))
        
        # Calculate security score
        security_score = self._calculate_security_score(issues)
        
        return {
            "is_safe": security_score >= 70,
            "security_score": security_score,
            "issues": [
                {
                    "severity": issue.severity,
                    "type": issue.issue_type,
                    "description": issue.description,
                    "line": issue.line_number,
                    "suggestion": issue.suggestion
                }
                for issue in issues
            ],
            "recommendations": self._generate_recommendations(issues)
        }
    
    def _check_dangerous_patterns(self, code: str) -> List[SecurityIssue]:
        """Check for dangerous code patterns"""
        
        issues = []
        lines = code.split('\n')
        
        for pattern, severity, description in self.dangerous_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        severity=severity,
                        issue_type="dangerous_pattern",
                        description=f"{description} detected",
                        line_number=line_num,
                        suggestion=f"Avoid using {description.lower()} in generated code"
                    ))
        
        return issues
    
    def _ast_security_check(self, code: str) -> List[SecurityIssue]:
        """AST-based security analysis for Python code"""
        
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', '__import__']:
                            issues.append(SecurityIssue(
                                severity="critical",
                                issue_type="dangerous_builtin",
                                description=f"Dangerous builtin function: {node.func.id}",
                                line_number=getattr(node, 'lineno', 0),
                                suggestion=f"Remove or replace {node.func.id} with safer alternative"
                            ))
                
                # Check for attribute access to dangerous modules
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id in ['os', 'subprocess', 'sys']:
                            if node.attr in ['system', 'popen', 'exit']:
                                issues.append(SecurityIssue(
                                    severity="high",
                                    issue_type="dangerous_module",
                                    description=f"Dangerous module usage: {node.value.id}.{node.attr}",
                                    line_number=getattr(node, 'lineno', 0),
                                    suggestion="Use safer alternatives for system operations"
                                ))
        
        except SyntaxError:
            # Not valid Python, skip AST analysis
            pass
        except Exception as e:
            logger.warning(f"AST analysis failed: {str(e)}")
        
        return issues
    
    def _check_input_validation(self, code: str) -> List[SecurityIssue]:
        """Check for input validation issues"""
        
        issues = []
        lines = code.split('\n')
        
        for pattern, severity, description in self.input_validation_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        severity=severity,
                        issue_type="input_validation",
                        description=f"{description} detected",
                        line_number=line_num,
                        suggestion="Add proper input validation and sanitization"
                    ))
        
        return issues
    
    def _is_python_code(self, code: str) -> bool:
        """Check if the code appears to be Python"""
        
        python_indicators = [
            'def ', 'class ', 'import ', 'from ', 'if __name__',
            'async def', 'await ', '@app.', 'fastapi'
        ]
        
        return any(indicator in code.lower() for indicator in python_indicators)
    
    def _calculate_security_score(self, issues: List[SecurityIssue]) -> int:
        """Calculate overall security score (0-100)"""
        
        if not issues:
            return 100
        
        penalty_map = {
            "critical": 30,
            "high": 20, 
            "medium": 10,
            "low": 5
        }
        
        total_penalty = sum(penalty_map.get(issue.severity, 0) for issue in issues)
        
        # Cap the penalty to prevent negative scores
        total_penalty = min(total_penalty, 95)
        
        return max(100 - total_penalty, 5)
    
    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations"""
        
        recommendations = []
        
        if any(issue.severity == "critical" for issue in issues):
            recommendations.append("🚨 Critical security issues detected - manual review required")
        
        if any("injection" in issue.description.lower() for issue in issues):
            recommendations.append("🛡️ Implement input validation and parameterized queries")
        
        if any("system" in issue.description.lower() for issue in issues):
            recommendations.append("⚙️ Avoid system commands, use safe libraries instead")
        
        if any("network" in issue.description.lower() for issue in issues):
            recommendations.append("🌐 Implement proper authentication for network operations")
        
        if not recommendations:
            recommendations.append("✅ Code appears secure, but always test thoroughly")
        
        return recommendations
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        
        # Remove dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Remove potential SQL injection patterns
        text = re.sub(r'\b(DROP|DELETE|INSERT|UPDATE|SELECT)\b', '', text, flags=re.IGNORECASE)
        
        # Limit length
        text = text[:10000]
        
        return text.strip()

# Global instance
security_validator = ProductionSecurityValidator()
