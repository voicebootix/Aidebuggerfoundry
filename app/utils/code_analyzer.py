import ast
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CodeIssue:
    """Represents a code issue or bug"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    suggested_fix: str
    confidence: float

@dataclass
class CodeComponent:
    """Represents a code component (function, class, etc.)"""
    name: str
    type: str  # function, class, variable, etc.
    file_path: str
    start_line: int
    end_line: int
    dependencies: List[str]
    complexity_score: int

class CodeAnalyzer:
    """
    Advanced code analysis using AST parsing and pattern recognition
    """
    
    def __init__(self):
        self.common_patterns = self._load_pattern_library()
        
    def _load_pattern_library(self) -> Dict:
        """Load common code patterns and anti-patterns"""
        return {
            "security_issues": [
                r"eval\(",
                r"exec\(",
                r"os\.system\(",
                r"subprocess\.call\(",
                r"sql.*\+.*%s",  # SQL injection pattern
            ],
            "performance_issues": [
                r"for .* in range\(len\(",  # Use enumerate instead
                r"\.append\(.* in .*for",   # List comprehension opportunity
            ],
            "code_smells": [
                r"def .{50,}:",  # Very long function names
                r"if .* and .* and .* and .*:",  # Complex conditionals
            ]
        }
    
    async def analyze_for_bugs(self, codebase: Dict[str, str], issue_description: str, 
                             original_intent: str) -> Dict:
        """Analyze code for potential bugs"""
        try:
            all_issues = []
            analyzed_files = {}
            
            for filename, content in codebase.items():
                if filename.endswith('.py'):
                    file_analysis = await self._analyze_python_file(filename, content)
                    analyzed_files[filename] = file_analysis
                    
                    # Find issues related to user's description
                    relevant_issues = self._find_relevant_issues(
                        file_analysis.get("issues", []),
                        issue_description
                    )
                    all_issues.extend(relevant_issues)
            
            # Prioritize issues based on severity and relevance
            prioritized_issues = self._prioritize_issues(all_issues, issue_description)
            
            return {
                "issues": prioritized_issues[:10],  # Top 10 issues
                "files_analyzed": list(analyzed_files.keys()),
                "overall_confidence": self._calculate_confidence(prioritized_issues),
                "analysis_summary": self._generate_analysis_summary(prioritized_issues),
                "recommended_actions": self._get_recommended_actions(prioritized_issues)
            }
            
        except Exception as e:
            logger.error(f"❌ Bug analysis failed: {str(e)}")
            return {"issues": [], "error": str(e)}
    
    async def _analyze_python_file(self, filename: str, content: str) -> Dict:
        """Analyze a Python file using AST"""
        try:
            tree = ast.parse(content)
            analyzer = PythonASTAnalyzer(filename, content)
            
            # Perform various analyses
            issues = []
            issues.extend(analyzer.find_syntax_issues())
            issues.extend(analyzer.find_logic_issues())
            issues.extend(analyzer.find_security_issues())
            issues.extend(analyzer.find_performance_issues())
            
            components = analyzer.extract_components()
            dependencies = analyzer.find_dependencies()
            complexity = analyzer.calculate_complexity()
            
            return {
                "issues": issues,
                "components": components,
                "dependencies": dependencies,
                "complexity_score": complexity,
                "lines_of_code": len(content.split('\n')),
                "functions": analyzer.count_functions(),
                "classes": analyzer.count_classes()
            }
            
        except SyntaxError as e:
            return {
                "issues": [{
                    "type": "syntax_error",
                    "line": e.lineno,
                    "description": f"Syntax error: {e.msg}",
                    "severity": "critical"
                }],
                "error": "Syntax error in file"
            }
        except Exception as e:
            logger.error(f"❌ Python file analysis failed: {str(e)}")
            return {"issues": [], "error": str(e)}
    
    async def analyze_integration_points(self, codebase: Dict[str, str], 
                                       feature_description: str) -> Dict:
        """Analyze where new features should be integrated"""
        try:
            integration_points = []
            
            for filename, content in codebase.items():
                if filename.endswith('.py'):
                    points = self._find_integration_points(filename, content, feature_description)
                    integration_points.extend(points)
            
            # Score and rank integration points
            scored_points = self._score_integration_points(integration_points, feature_description)
            
            return {
                "integration_points": scored_points[:5],  # Top 5 points
                "feasibility_score": self._calculate_feasibility(scored_points),
                "recommended_approach": self._recommend_integration_approach(scored_points),
                "impact_analysis": self._analyze_integration_impact(scored_points, codebase)
            }
            
        except Exception as e:
            logger.error(f"❌ Integration analysis failed: {str(e)}")
            return {}
    
    async def identify_modification_target(self, codebase: Dict[str, str], 
                                         target_component: str, modification_type: str) -> Dict:
        """Identify specific code components to modify"""
        try:
            potential_targets = []
            
            for filename, content in codebase.items():
                targets = self._find_modification_targets(
                    filename, content, target_component, modification_type
                )
                potential_targets.extend(targets)
            
            # Find best match
            best_match = self._find_best_target_match(potential_targets, target_component)
            
            if best_match:
                return {
                    "component_name": best_match["name"],
                    "file_path": best_match["file"],
                    "start_line": best_match["start_line"],
                    "end_line": best_match["end_line"],
                    "component_type": best_match["type"],
                    "confidence": best_match["confidence"],
                    "dependencies": best_match.get("dependencies", []),
                    "modification_strategy": self._suggest_modification_strategy(best_match, modification_type)
                }
            else:
                return {
                    "error": "Target component not found",
                    "suggestions": self._suggest_alternatives(target_component, codebase)
                }
                
        except Exception as e:
            logger.error(f"❌ Target identification failed: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_code_quality(self, codebase: Dict[str, str], original_intent: str) -> Dict:
        """Comprehensive code quality analysis"""
        try:
            quality_metrics = {}
            total_score = 0
            file_count = 0
            
            for filename, content in codebase.items():
                if filename.endswith('.py'):
                    file_metrics = self._analyze_file_quality(filename, content)
                    quality_metrics[filename] = file_metrics
                    total_score += file_metrics.get("overall_score", 0)
                    file_count += 1
            
            overall_score = total_score / file_count if file_count > 0 else 0
            
            return {
                "overall_score": round(overall_score, 2),
                "file_metrics": quality_metrics,
                "strengths": self._identify_code_strengths(quality_metrics),
                "weaknesses": self._identify_code_weaknesses(quality_metrics),
                "improvement_areas": self._suggest_improvement_areas(quality_metrics),
                "adherence_to_intent": self._check_intent_adherence(codebase, original_intent)
            }
            
        except Exception as e:
            logger.error(f"❌ Quality analysis failed: {str(e)}")
            return {}

class PythonASTAnalyzer(ast.NodeVisitor):
    """AST-based Python code analyzer"""
    
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content
        self.lines = content.split('\n')
        self.issues = []
        self.components = []
        self.current_class = None
        self.current_function = None
        
    def find_syntax_issues(self) -> List[Dict]:
        """Find syntax-related issues"""
        issues = []
        
        # Check for common syntax issues
        for i, line in enumerate(self.lines, 1):
            if re.search(r'print\s+[^(]', line):  # Python 2 style print
                issues.append({
                    "type": "syntax_modernization",
                    "line": i,
                    "description": "Use print() function instead of print statement",
                    "severity": "low",
                    "suggested_fix": line.replace('print ', 'print(') + ')'
                })
                
        return issues
    
    def find_logic_issues(self) -> List[Dict]:
        """Find logical issues in code"""
        issues = []
        
        # Look for common logical issues
        for i, line in enumerate(self.lines, 1):
            if 'if True:' in line:
                issues.append({
                    "type": "logic_issue",
                    "line": i,
                    "description": "Unconditional if statement - always True",
                    "severity": "medium",
                    "suggested_fix": "Remove condition or add proper logic"
                })
                
        return issues
    
    def find_security_issues(self) -> List[Dict]:
        """Find security-related issues"""
        issues = []
        
        for pattern_name, patterns in [("security_issues", self.patterns.get("security_issues", []))]:
            for i, line in enumerate(self.lines, 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        issues.append({
                            "type": "security_vulnerability",
                            "line": i,
                            "description": f"Potential security issue: {pattern}",
                            "severity": "high",
                            "suggested_fix": "Use safer alternatives"
                        })
                        
        return issues
    
    # Additional analysis methods...
