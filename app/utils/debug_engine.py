"""
Debug Engine - AI-Powered Code Analysis and Debugging
Integrates with Monaco Editor for professional debugging experience
Enhanced with real-time collaboration and GitHub sync
"""

import asyncio
import json
import uuid
import ast
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import openai

@dataclass
class CodeAnalysis:
    file_path: str
    issues_found: List[Dict]
    suggestions: List[Dict]
    complexity_score: float
    quality_score: float

@dataclass
class DebugSuggestion:
    type: str  # "bug_fix", "optimization", "feature_enhancement"
    description: str
    code_changes: Dict
    confidence: float
    impact: str  # "low", "medium", "high"

@dataclass
class DebugSession:
    session_id: str
    project_id: str
    user_id: str
    codebase_snapshot: Dict
    analysis_results: List[CodeAnalysis]
    suggestions: List[DebugSuggestion]
    conversation_history: List[Dict]
    status: str

class DebugEngine:
    """Advanced AI debugging and code analysis engine"""
    
    def __init__(self, llm_provider, monaco_integration, github_integration):
        self.llm_provider = llm_provider
        self.monaco_integration = monaco_integration
        self.github_integration = github_integration
        self.active_sessions: Dict[str, DebugSession] = {}
        
    async def start_debug_session(self, project_id: str, user_id: str, codebase: Dict) -> DebugSession:
        """Initialize new debugging session"""
        
        session_id = str(uuid.uuid4())
        
        # Create debug session
        session = DebugSession(
            session_id=session_id,
            project_id=project_id,
            user_id=user_id,
            codebase_snapshot=codebase,
            analysis_results=[],
            suggestions=[],
            conversation_history=[],
            status="initializing"
        )
        
        # Perform initial code analysis
        analysis_results = await self._analyze_codebase(codebase)
        session.analysis_results = analysis_results
        
        # Generate initial suggestions
        suggestions = await self._generate_initial_suggestions(analysis_results)
        session.suggestions = suggestions
        
        session.status = "active"
        self.active_sessions[session_id] = session
        
        return session
    
    async def _analyze_codebase(self, codebase: Dict) -> List[CodeAnalysis]:
        """Comprehensive codebase analysis"""
        
        analysis_results = []
        
        for file_path, file_content in codebase.items():
            if file_path.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                analysis = await self._analyze_file(file_path, file_content)
                analysis_results.append(analysis)
        
        return analysis_results
    
    async def _analyze_file(self, file_path: str, file_content: str) -> CodeAnalysis:
        """Analyze individual file for issues and improvements"""
        
        file_extension = file_path.split('.')[-1]
        
        analysis_prompt = f"""
        Analyze this {file_extension} file for issues and improvements:
        
        File: {file_path}
        Content:
        ```{file_extension}
        {file_content}
        ```
        
        Provide comprehensive analysis covering:
        1. Code quality issues
        2. Potential bugs and vulnerabilities
        3. Performance optimization opportunities
        4. Best practices violations
        5. Maintainability concerns
        
        Return JSON format:
        {{
            "issues_found": [
                {{
                    "type": "bug|performance|security|style|maintainability",
                    "severity": "low|medium|high|critical",
                    "line_number": 42,
                    "description": "Detailed issue description",
                    "suggestion": "How to fix this issue"
                }}
            ],
            "suggestions": [
                {{
                    "type": "optimization|refactoring|feature_enhancement",
                    "description": "Improvement suggestion",
                    "code_example": "Example of improved code",
                    "benefit": "Expected benefit"
                }}
            ],
            "complexity_score": 0.75,
            "quality_score": 0.85,
            "overall_assessment": "File assessment summary"
        }}
        """
        
        try:
            response = await self.llm_provider.generate_completion(
                prompt=analysis_prompt,
                model="gpt-4",
                temperature=0.1
            )
            
            result = json.loads(response)
            
            return CodeAnalysis(
                file_path=file_path,
                issues_found=result["issues_found"],
                suggestions=result["suggestions"],
                complexity_score=result["complexity_score"],
                quality_score=result["quality_score"]
            )
            
        except Exception as e:
            # Fallback basic analysis
            return CodeAnalysis(
                file_path=file_path,
                issues_found=[],
                suggestions=[
                    {
                        "type": "review",
                        "description": f"Manual review recommended for {file_path}",
                        "code_example": "",
                        "benefit": "Ensure code quality"
                    }
                ],
                complexity_score=0.5,
                quality_score=0.7
            )
    
    async def _generate_initial_suggestions(self, analysis_results: List[CodeAnalysis]) -> List[DebugSuggestion]:
        """Generate initial debugging suggestions from analysis"""
        
        suggestions = []
        
        # Priority: Critical and high severity issues first
        critical_issues = []
        for analysis in analysis_results:
            for issue in analysis.issues_found:
                if issue["severity"] in ["critical", "high"]:
                    critical_issues.append((analysis.file_path, issue))
        
        # Generate suggestions for critical issues
        for file_path, issue in critical_issues:
            suggestion = DebugSuggestion(
                type="bug_fix",
                description=f"Fix {issue['severity']} {issue['type']} in {file_path}: {issue['description']}",
                code_changes={
                    "file": file_path,
                    "line": issue["line_number"],
                    "suggestion": issue["suggestion"]
                },
                confidence=0.9 if issue["severity"] == "critical" else 0.8,
                impact="high" if issue["severity"] == "critical" else "medium"
            )
            suggestions.append(suggestion)
        
        # Generate optimization suggestions
        for analysis in analysis_results:
            if analysis.quality_score < 0.7:
                suggestion = DebugSuggestion(
                    type="optimization",
                    description=f"Improve code quality in {analysis.file_path}",
                    code_changes={
                        "file": analysis.file_path,
                        "suggestions": analysis.suggestions
                    },
                    confidence=0.7,
                    impact="medium"
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    async def process_debug_request(self, session_id: str, user_request: str) -> Dict:
        """Process user debugging request"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Add user request to conversation history
        session.conversation_history.append({
            "role": "user",
            "content": user_request,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze request and generate response
        debug_response = await self._generate_debug_response(session, user_request)
        
        # Add AI response to conversation history
        session.conversation_history.append({
            "role": "assistant",
            "content": debug_response["message"],
            "suggestions": debug_response.get("suggestions", []),
            "code_changes": debug_response.get("code_changes", {}),
            "timestamp": datetime.now().isoformat()
        })
        
        return debug_response
    
    async def _generate_debug_response(self, session: DebugSession, user_request: str) -> Dict:
        """Generate AI debugging response"""
        
        # Context from codebase and previous analysis
        context = {
            "codebase_files": list(session.codebase_snapshot.keys()),
            "analysis_summary": self._summarize_analysis_results(session.analysis_results),
            "conversation_history": session.conversation_history[-5:],  # Last 5 messages
            "current_suggestions": [s.description for s in session.suggestions]
        }
        
        debug_prompt = f"""
        You are an expert AI debugging assistant helping with code analysis and improvements.
        
        User Request: "{user_request}"
        
        Context:
        - Project files: {context["codebase_files"]}
        - Previous analysis: {context["analysis_summary"]}
        - Recent conversation: {context["conversation_history"]}
        - Current suggestions: {context["current_suggestions"]}
        
        Provide helpful debugging assistance:
        1. Understand what the user is asking for
        2. Provide specific, actionable advice
        3. Include code examples when relevant
        4. Suggest next steps
        
        If the user is asking about:
        - Specific bugs: Provide detailed analysis and fix suggestions
        - Performance: Suggest optimization strategies
        - New features: Help implement and integrate properly
        - Code review: Provide comprehensive feedback
        - Testing: Suggest testing strategies and implementations
        
        Return JSON format:
        {{
            "message": "Detailed response to user request",
            "suggestions": [
                {{
                    "title": "Suggestion title",
                    "description": "Detailed description",
                    "code_example": "Code example if applicable",
                    "priority": "high|medium|low"
                }}
            ],
            "code_changes": {{
                "file_path": "path/to/file.py",
                "changes": [
                    {{
                        "line_number": 42,
                        "original": "original code",
                        "modified": "improved code",
                        "explanation": "Why this change improves the code"
                    }}
                ]
            }},
            "next_steps": ["step1", "step2"],
            "confidence": 0.9
        }}
        """
        
        try:
            response = await self.llm_provider.generate_completion(
                prompt=debug_prompt,
                model="gpt-4",
                temperature=0.2
            )
            
            return json.loads(response)
            
        except Exception as e:
            return {
                "message": f"I understand you're asking about: {user_request}. Let me help you with that. Could you provide more specific details about what you'd like me to analyze or improve?",
                "suggestions": [
                    {
                        "title": "Provide More Context",
                        "description": "Please share specific files or error messages you'd like me to examine",
                        "priority": "high"
                    }
                ],
                "code_changes": {},
                "next_steps": ["Share specific code snippets", "Describe the exact issue"],
                "confidence": 0.6
            }
    
    async def _summarize_analysis_results(self, analysis_results: List[CodeAnalysis]) -> str:
        """Summarize analysis results for context"""
        
        total_issues = sum(len(analysis.issues_found) for analysis in analysis_results)
        avg_quality = sum(analysis.quality_score for analysis in analysis_results) / len(analysis_results) if analysis_results else 0
        
        issue_types = {}
        for analysis in analysis_results:
            for issue in analysis.issues_found:
                issue_type = issue["type"]
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return f"Found {total_issues} total issues. Average quality score: {avg_quality:.2f}. Issue breakdown: {issue_types}"
    
    async def apply_code_changes(self, session_id: str, changes: Dict) -> Dict:
        """Apply suggested code changes to codebase"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        try:
            # Apply changes to codebase snapshot
            file_path = changes["file_path"]
            if file_path in session.codebase_snapshot:
                # Apply line-by-line changes
                lines = session.codebase_snapshot[file_path].split('\n')
                
                for change in changes["changes"]:
                    line_num = change["line_number"] - 1  # Convert to 0-based index
                    if 0 <= line_num < len(lines):
                        lines[line_num] = change["modified"]
                
                # Update codebase snapshot
                session.codebase_snapshot[file_path] = '\n'.join(lines)
                
                # Re-analyze modified file
                new_analysis = await self._analyze_file(file_path, session.codebase_snapshot[file_path])
                
                # Update analysis results
                session.analysis_results = [
                    analysis for analysis in session.analysis_results 
                    if analysis.file_path != file_path
                ]
                session.analysis_results.append(new_analysis)
                
                return {
                    "success": True,
                    "message": f"Successfully applied changes to {file_path}",
                    "updated_analysis": {
                        "quality_score": new_analysis.quality_score,
                        "issues_found": len(new_analysis.issues_found)
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"File {file_path} not found in codebase"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to apply changes: {str(e)}"
            }
    
    async def get_session_summary(self, session_id: str) -> Dict:
        """Get comprehensive session summary"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        # Calculate overall metrics
        total_files = len(session.codebase_snapshot)
        total_issues = sum(len(analysis.issues_found) for analysis in session.analysis_results)
        avg_quality = sum(analysis.quality_score for analysis in session.analysis_results) / len(session.analysis_results) if session.analysis_results else 0
        
        # Group issues by severity
        issues_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for analysis in session.analysis_results:
            for issue in analysis.issues_found:
                severity = issue.get("severity", "low")
                issues_by_severity[severity] += 1
        
        return {
            "session_id": session_id,
            "status": session.status,
            "metrics": {
                "total_files": total_files,
                "total_issues": total_issues,
                "average_quality_score": round(avg_quality, 2),
                "issues_by_severity": issues_by_severity
            },
            "suggestions_available": len(session.suggestions),
            "conversation_length": len(session.conversation_history),
            "last_activity": session.conversation_history[-1]["timestamp"] if session.conversation_history else None
        }
    
    async def export_debug_report(self, session_id: str) -> Dict:
        """Export comprehensive debugging report"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        report = {
            "session_info": {
                "session_id": session_id,
                "project_id": session.project_id,
                "created_at": session.conversation_history[0]["timestamp"] if session.conversation_history else None,
                "status": session.status
            },
            "codebase_analysis": {
                "files_analyzed": len(session.analysis_results),
                "total_issues": sum(len(analysis.issues_found) for analysis in session.analysis_results),
                "average_quality_score": sum(analysis.quality_score for analysis in session.analysis_results) / len(session.analysis_results) if session.analysis_results else 0
            },
            "detailed_analysis": [
                {
                    "file_path": analysis.file_path,
                    "quality_score": analysis.quality_score,
                    "complexity_score": analysis.complexity_score,
                    "issues_count": len(analysis.issues_found),
                    "issues": analysis.issues_found,
                    "suggestions": analysis.suggestions
                }
                for analysis in session.analysis_results
            ],
            "ai_suggestions": [
                {
                    "type": suggestion.type,
                    "description": suggestion.description,
                    "confidence": suggestion.confidence,
                    "impact": suggestion.impact
                }
                for suggestion in session.suggestions
            ],
            "conversation_summary": {
                "total_interactions": len(session.conversation_history),
                "key_topics": await self._extract_conversation_topics(session.conversation_history)
            }
        }
        
        return report
    
    async def _extract_conversation_topics(self, conversation_history: List[Dict]) -> List[str]:
        """Extract key topics from conversation history"""
        
        # Simple keyword extraction - can be enhanced with NLP
        user_messages = [msg["content"] for msg in conversation_history if msg["role"] == "user"]
        combined_text = " ".join(user_messages).lower()
        
        # Common debugging topics
        topics = []
        topic_keywords = {
            "bug_fixing": ["bug", "error", "issue", "problem", "fix"],
            "performance": ["slow", "performance", "optimize", "speed"],
            "testing": ["test", "testing", "unit test", "integration"],
            "refactoring": ["refactor", "clean", "organize", "structure"],
            "features": ["add", "feature", "implement", "new"],
            "security": ["security", "vulnerability", "secure", "auth"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                topics.append(topic.replace("_", " ").title())
        
        return topics if topics else ["General debugging"]