import asyncio
import ast
import json
import logging
import re
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from dataclasses import dataclass
import difflib
from pathlib import Path

from fastapi import HTTPException
from pydantic import BaseModel
import openai
import anthropic

from app.utils.project_memory import ProjectMemoryManager
from app.utils.code_analyzer import CodeAnalyzer
from app.utils.precision_updater import PrecisionUpdater
from app.utils.conversation_ai import ConversationAI

logger = logging.getLogger(__name__)

@dataclass
class DebugSession:
    """Represents an active debugging session"""
    session_id: str
    project_id: str
    user_id: str
    conversation_history: List[Dict]
    current_codebase: Dict[str, str]  # filename -> content
    original_intent: str
    last_activity: datetime

class DebugRequest(BaseModel):
    session_id: Optional[str] = None
    project_id: str
    user_input: str
    context: Optional[Dict] = None
    request_type: str = "general"  # general, fix_bug, add_feature, explain_code, etc.

class DebugResponse(BaseModel):
    session_id: str
    status: str
    message: str
    analysis: Dict
    suggested_changes: List[Dict]
    explanation: str
    confidence_score: float
    requires_confirmation: bool = False

class DebugEngine:
    """
    Main DebugBot Engine - Provides intelligent debugging and iteration
    """
    
    def __init__(self):
        self.memory_manager = ProjectMemoryManager()
        self.code_analyzer = CodeAnalyzer()
        self.precision_updater = PrecisionUpdater()
        self.conversation_ai = ConversationAI()
        self.active_sessions: Dict[str, DebugSession] = {}
        
        # LLM clients for debugging
        self.openai_client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def start_debug_session(self, project_id: str, user_id: str) -> str:
        """Initialize a new debugging session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Load project from memory
            project_context = await self.memory_manager.load_project(project_id)
            
            if not project_context:
                raise HTTPException(status_code=404, detail="Project not found")
            
            session = DebugSession(
                session_id=session_id,
                project_id=project_id,
                user_id=user_id,
                conversation_history=[],
                current_codebase=project_context.get("files", {}),
                original_intent=project_context.get("original_prompt", ""),
                last_activity=datetime.now()
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"🔧 Started debug session {session_id} for project {project_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start debug session: {str(e)}")
            raise
    
    async def process_debug_request(self, request: DebugRequest) -> DebugResponse:
        """Main debugging intelligence - processes user requests"""
        try:
            # Get or create session
            session = await self._get_or_create_session(request)
            
            # Analyze user input to understand intent
            user_intent = await self.conversation_ai.analyze_intent(
                request.user_input, 
                session.conversation_history,
                session.current_codebase
            )
            
            logger.info(f"🧠 Detected intent: {user_intent['type']} - {user_intent['summary']}")
            
            # Route to appropriate handler based on intent
            if user_intent["type"] == "bug_report":
                response = await self._handle_bug_report(session, request, user_intent)
            elif user_intent["type"] == "feature_request":
                response = await self._handle_feature_request(session, request, user_intent)
            elif user_intent["type"] == "code_explanation":
                response = await self._handle_code_explanation(session, request, user_intent)
            elif user_intent["type"] == "modify_specific":
                response = await self._handle_specific_modification(session, request, user_intent)
            elif user_intent["type"] == "quality_review":
                response = await self._handle_quality_review(session, request, user_intent)
            else:
                response = await self._handle_general_query(session, request, user_intent)
            
            # Update conversation history
            session.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": request.user_input,
                "intent": user_intent,
                "response": response.dict(),
                "session_id": session.session_id
            })
            
            session.last_activity = datetime.now()
            
            # Save session state
            await self._save_session_state(session)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Debug processing failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Debug processing failed: {str(e)}")
    
    async def _handle_bug_report(self, session: DebugSession, request: DebugRequest, intent: Dict) -> DebugResponse:
        """Handle bug reports and debugging"""
        try:
            # Analyze code for potential issues
            bug_analysis = await self.code_analyzer.analyze_for_bugs(
                session.current_codebase,
                intent["details"],
                session.original_intent
            )
            
            # Generate debugging suggestions
            debug_suggestions = await self._generate_debug_suggestions(
                session.current_codebase,
                intent["details"],
                bug_analysis
            )
            
            # Create suggested fixes
            suggested_changes = []
            for suggestion in debug_suggestions:
                if suggestion.get("confidence", 0) > 0.7:  # High confidence fixes
                    changes = await self.precision_updater.generate_precise_fix(
                        session.current_codebase,
                        suggestion
                    )
                    suggested_changes.extend(changes)
            
            return DebugResponse(
                session_id=session.session_id,
                status="bug_analysis_complete",
                message=f"Found {len(bug_analysis.get('issues', []))} potential issues",
                analysis=bug_analysis,
                suggested_changes=suggested_changes,
                explanation=await self._generate_bug_explanation(bug_analysis, intent),
                confidence_score=bug_analysis.get("overall_confidence", 0.5),
                requires_confirmation=len(suggested_changes) > 0
            )
            
        except Exception as e:
            logger.error(f"❌ Bug analysis failed: {str(e)}")
            raise
    
    async def _handle_feature_request(self, session: DebugSession, request: DebugRequest, intent: Dict) -> DebugResponse:
        """Handle new feature additions"""
        try:
            # Analyze where to add the feature
            integration_analysis = await self.code_analyzer.analyze_integration_points(
                session.current_codebase,
                intent["feature_description"]
            )
            
            # Generate feature implementation
            feature_implementation = await self._generate_feature_code(
                session.current_codebase,
                intent["feature_description"],
                integration_analysis,
                session.original_intent
            )
            
            # Create precise updates
            suggested_changes = await self.precision_updater.generate_feature_integration(
                session.current_codebase,
                feature_implementation,
                integration_analysis
            )
            
            return DebugResponse(
                session_id=session.session_id,
                status="feature_analysis_complete",
                message=f"Analyzed integration for: {intent['feature_description'][:50]}...",
                analysis=integration_analysis,
                suggested_changes=suggested_changes,
                explanation=await self._generate_feature_explanation(feature_implementation, intent),
                confidence_score=integration_analysis.get("feasibility_score", 0.8),
                requires_confirmation=True
            )
            
        except Exception as e:
            logger.error(f"❌ Feature analysis failed: {str(e)}")
            raise
    
    async def _handle_specific_modification(self, session: DebugSession, request: DebugRequest, intent: Dict) -> DebugResponse:
        """Handle specific code modifications like 'change only the login logic'"""
        try:
            # Parse what specifically needs to be changed
            modification_target = await self.code_analyzer.identify_modification_target(
                session.current_codebase,
                intent["target_component"],
                intent["modification_type"]
            )
            
            # Generate precise changes
            suggested_changes = await self.precision_updater.generate_targeted_modification(
                session.current_codebase,
                modification_target,
                intent["modification_details"]
            )
            
            # Analyze impact on other components
            impact_analysis = await self.code_analyzer.analyze_change_impact(
                session.current_codebase,
                suggested_changes
            )
            
            return DebugResponse(
                session_id=session.session_id,
                status="modification_ready",
                message=f"Ready to modify {modification_target.get('component_name', 'target component')}",
                analysis={
                    "target": modification_target,
                    "impact": impact_analysis
                },
                suggested_changes=suggested_changes,
                explanation=await self._generate_modification_explanation(modification_target, intent, impact_analysis),
                confidence_score=modification_target.get("confidence", 0.8),
                requires_confirmation=impact_analysis.get("has_dependencies", False)
            )
            
        except Exception as e:
            logger.error(f"❌ Modification analysis failed: {str(e)}")
            raise
    
    async def _handle_code_explanation(self, session: DebugSession, request: DebugRequest, intent: Dict) -> DebugResponse:
        """Handle requests to explain code or decisions"""
        try:
            # Identify what code to explain
            explanation_target = await self.code_analyzer.identify_explanation_target(
                session.current_codebase,
                intent.get("target_code", "")
            )
            
            # Generate explanation using project memory
            explanation = await self._generate_code_explanation(
                explanation_target,
                session.original_intent,
                session.conversation_history
            )
            
            return DebugResponse(
                session_id=session.session_id,
                status="explanation_ready",
                message="Code explanation generated",
                analysis=explanation_target,
                suggested_changes=[],  # No changes for explanations
                explanation=explanation,
                confidence_score=0.9,
                requires_confirmation=False
            )
            
        except Exception as e:
            logger.error(f"❌ Code explanation failed: {str(e)}")
            raise
    
    async def _handle_quality_review(self, session: DebugSession, request: DebugRequest, intent: Dict) -> DebugResponse:
        """Handle code quality analysis and improvement suggestions"""
        try:
            # Comprehensive code quality analysis
            quality_analysis = await self.code_analyzer.analyze_code_quality(
                session.current_codebase,
                session.original_intent
            )
            
            # Generate improvement suggestions
            improvements = await self._generate_quality_improvements(
                session.current_codebase,
                quality_analysis
            )
            
            # Create actionable changes
            suggested_changes = []
            for improvement in improvements[:5]:  # Top 5 improvements
                if improvement.get("priority", 0) >= 7:  # High priority only
                    changes = await self.precision_updater.generate_quality_fix(
                        session.current_codebase,
                        improvement
                    )
                    suggested_changes.extend(changes)
            
            return DebugResponse(
                session_id=session.session_id,
                status="quality_analysis_complete",
                message=f"Analyzed code quality - found {len(improvements)} improvements",
                analysis=quality_analysis,
                suggested_changes=suggested_changes,
                explanation=await self._generate_quality_explanation(quality_analysis, improvements),
                confidence_score=quality_analysis.get("overall_score", 0.7) / 10,
                requires_confirmation=len(suggested_changes) > 0
            )
            
        except Exception as e:
            logger.error(f"❌ Quality analysis failed: {str(e)}")
            raise
    
    async def _generate_debug_suggestions(self, codebase: Dict, issue_description: str, analysis: Dict) -> List[Dict]:
        """Generate AI-powered debugging suggestions"""
        try:
            prompt = f"""
            Analyze this code issue and provide debugging suggestions:
            
            Issue: {issue_description}
            Analysis: {json.dumps(analysis, indent=2)}
            
            Code files:
            {self._format_codebase_for_prompt(codebase)}
            
            Provide specific, actionable debugging suggestions with confidence scores.
            Focus on root causes, not just symptoms.
            """
            
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response into structured suggestions
            suggestions_text = response.content[0].text
            return self._parse_debug_suggestions(suggestions_text)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate debug suggestions: {str(e)}")
            return []
    
    async def _generate_feature_code(self, codebase: Dict, feature_description: str, 
                                   integration_analysis: Dict, original_intent: str) -> Dict:
        """Generate code for new features"""
        try:
            prompt = f"""
            Generate code to implement this feature:
            
            Feature: {feature_description}
            Original intent: {original_intent}
            Integration points: {json.dumps(integration_analysis, indent=2)}
            
            Current codebase:
            {self._format_codebase_for_prompt(codebase)}
            
            Generate minimal, precise code that integrates cleanly with existing architecture.
            Return structured response with files and modifications.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            
            return self._parse_feature_implementation(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"❌ Failed to generate feature code: {str(e)}")
            return {}
    
    async def apply_suggested_changes(self, session_id: str, change_ids: List[str]) -> Dict:
        """Apply approved changes to the codebase"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Apply changes using precision updater
            updated_codebase = await self.precision_updater.apply_changes(
                session.current_codebase,
                change_ids
            )
            
            # Update session with new codebase
            session.current_codebase = updated_codebase
            session.last_activity = datetime.now()
            
            # Save updated project state
            await self.memory_manager.save_project_state(
                session.project_id,
                updated_codebase,
                session.conversation_history
            )
            
            # Generate update summary
            update_summary = await self._generate_update_summary(change_ids, updated_codebase)
            
            return {
                "status": "changes_applied",
                "updated_files": list(updated_codebase.keys()),
                "change_summary": update_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to apply changes: {str(e)}")
            raise
    
    # Utility methods
    def _format_codebase_for_prompt(self, codebase: Dict) -> str:
        """Format codebase for LLM prompts"""
        formatted = ""
        for filename, content in codebase.items():
            formatted += f"\n## {filename}\n```\n{content[:2000]}...\n```\n"
        return formatted
    
    async def _get_or_create_session(self, request: DebugRequest) -> DebugSession:
        """Get existing session or create new one"""
        if request.session_id and request.session_id in self.active_sessions:
            return self.active_sessions[request.session_id]
        else:
            session_id = await self.start_debug_session(request.project_id, "anonymous")
            return self.active_sessions[session_id]
    
    # Additional helper methods would continue here...
    # (Implementation continues with parsing, analysis, and utility functions)
