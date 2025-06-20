"""
Security Validator - Enhanced Input/Output Security
Comprehensive security scanning and validation
Enhanced with AI-powered threat detection
"""

import re
import ast
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    severity: str  # "low", "medium", "high", "critical"
    category: str
    description: str
    location: Optional[str]
    remediation: str

class SecurityValidator:
    """Enhanced security validation system"""
    
    def __init__(self):
        self.security_patterns = self._load_security_patterns()
        
    def _load_security_patterns(self) -> Dict:
        """Load security threat patterns"""
        return {
            "sql_injection": [
                r"'\s*or\s*'1'\s*=\s*'1",
                r";\s*drop\s+table",
                r"union\s+select",
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
            ],
            "code_injection": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"os\.system\s*\(",
            ]
        }
    
    async def validate_input(self, user_input: str) -> List[SecurityIssue]:
        """Validate user input for security threats"""
        
        issues = []
        
        # Check for SQL injection
        for pattern in self.security_patterns["sql_injection"]:
            if re.search(pattern, user_input, re.IGNORECASE):
                issues.append(SecurityIssue(
                    severity="high",
                    category="sql_injection",
                    description="Potential SQL injection detected",
                    location="user_input",
                    remediation="Sanitize input and use parameterized queries"
                ))
        
        # Check for XSS
        for pattern in self.security_patterns["xss"]:
            if re.search(pattern, user_input, re.IGNORECASE):
                issues.append(SecurityIssue(
                    severity="medium",
                    category="xss",
                    description="Potential XSS attack detected",
                    location="user_input",
                    remediation="Escape HTML entities and validate input"
                ))
        
        return issues
    
    async def scan_generated_code(self, code: str) -> List[SecurityIssue]:
        """Scan generated code for security vulnerabilities"""
        
        issues = []
        
        # Check for dangerous functions
        dangerous_patterns = [
            (r"eval\s*\(", "critical", "Use of eval() function"),
            (r"exec\s*\(", "critical", "Use of exec() function"),
            (r"os\.system\s*\(", "high", "Use of os.system()"),
            (r"subprocess\.call\s*\(", "medium", "Use of subprocess.call()"),
        ]
        
        for pattern, severity, description in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(SecurityIssue(
                    severity=severity,
                    category="dangerous_function",
                    description=description,
                    location="generated_code",
                    remediation="Use safer alternatives or add proper validation"
                ))
        
        return issues