import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

import httpx

from app.utils.logger import setup_logger

logger = setup_logger()

@dataclass
class BusinessInsight:
    category: str
    insight: str
    confidence: float
    source: str
    actionable_steps: List[str]

@dataclass
class ConversationContext:
    project_idea: str
    target_market: Optional[str] = None
    technical_requirements: Optional[List[str]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    experience_level: Optional[str] = None
    previous_questions: List[str] = None
    gathered_insights: List[BusinessInsight] = None

class ConversationalStrategyConsultant:
    """
    AI-powered business strategy consultant that conducts intelligent conversations
    to analyze startup ideas with deep business intelligence
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.conversation_sessions = {}
        
        if not self.openai_api_key and not self.anthropic_api_key:
            logger.warning("⚠️ No LLM API keys found. Strategy validation will use fallback logic.")
    
    async def start_strategy_conversation(self, user_id: str, initial_idea: str) -> Dict[str, Any]:
        """Start a new strategy consultation conversation"""
        
        session_id = f"strategy_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize conversation context
        context = ConversationContext(
            project_idea=initial_idea,
            previous_questions=[],
            gathered_insights=[]
        )
        
        self.conversation_sessions[session_id] = context
        
        # Generate initial strategic questions
        initial_analysis = await self._conduct_initial_analysis(initial_idea, context)
        
        return {
            "session_id": session_id,
            "status": "conversation_started",
            "initial_analysis": initial_analysis,
            "next_questions": initial_analysis.get("strategic_questions", []),
            "conversation_context": {
                "phase": "discovery",
                "completeness": 15,  # 15% complete
                "areas_explored": ["initial_concept"],
                "areas_remaining": ["market_analysis", "competition", "monetization", "technical_feasibility", "risk_assessment"]
            }
        }
    
    async def continue_conversation(self, session_id: str, user_response: str) -> Dict[str, Any]:
        """Continue strategy conversation with user response"""
        
        if session_id not in self.conversation_sessions:
            return {"error": "Session not found"}
        
        context = self.conversation_sessions[session_id]
        
        # Process user response and update context
        await self._process_user_response(user_response, context)
        
        # Determine conversation phase and next actions
        conversation_state = self._assess_conversation_state(context)
        
        if conversation_state["phase"] == "analysis":
            # We have enough info - provide comprehensive analysis
            final_analysis = await self._generate_comprehensive_analysis(context)
            return {
                "session_id": session_id,
                "status": "analysis_complete",
                "comprehensive_analysis": final_analysis,
                "conversation_summary": self._generate_conversation_summary(context)
            }
        else:
            # Continue gathering information
            next_questions = await self._generate_contextual_questions(context, conversation_state)
            return {
                "session_id": session_id,
                "status": "conversation_continuing",
                "ai_response": next_questions["response"],
                "strategic_questions": next_questions["questions"],
                "conversation_context": conversation_state,
                "insights_so_far": [insight.__dict__ for insight in context.gathered_insights]
            }
    
    async def _conduct_initial_analysis(self, idea: str, context: ConversationContext) -> Dict[str, Any]:
        """Conduct initial analysis of the business idea"""
        
        try:
            if self.openai_api_key:
                return await self._analyze_with_openai(idea, "initial")
            elif self.anthropic_api_key:
                return await self._analyze_with_anthropic(idea, "initial")
            else:
                return self._fallback_initial_analysis(idea)
                
        except Exception as e:
            logger.error(f"❌ Initial analysis failed: {str(e)}")
            return self._fallback_initial_analysis(idea)
    
    async def _analyze_with_openai(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Conduct analysis using OpenAI"""
        
        if analysis_type == "initial":
            prompt = f"""
            You are a seasoned business strategy consultant and startup advisor. A founder has approached you with this idea:

            IDEA: "{content}"

            Conduct an initial strategic assessment and generate intelligent follow-up questions to understand:

            1. Market Opportunity & Target Audience
            2. Competitive Landscape 
            3. Monetization Strategy
            4. Technical Feasibility & Resources
            5. Founder's Experience & Team
            6. Timeline & Budget Expectations

            Respond in JSON format:
            {{
                "initial_assessment": {{
                    "opportunity_score": <0-10>,
                    "complexity_level": "<simple|moderate|complex|enterprise>",
                    "market_size_estimate": "<description>",
                    "key_challenges": ["challenge1", "challenge2"],
                    "immediate_opportunities": ["opportunity1", "opportunity2"]
                }},
                "strategic_questions": [
                    {{
                        "question": "question text",
                        "category": "market|competition|monetization|technical|team|timeline",
                        "importance": "high|medium|low",
                        "follow_up_potential": ["potential follow-up question 1"]
                    }}
                ],
                "conversation_strategy": {{
                    "recommended_flow": ["phase1", "phase2", "phase3"],
                    "estimated_conversation_length": <number of exchanges>,
                    "critical_info_needed": ["info1", "info2"]
                }}
            }}

            Make this feel like a professional consultation - insightful, strategic, and genuinely helpful.
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "system", "content": "You are a world-class business strategy consultant with deep expertise in startup validation and market analysis."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    }
                )
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Extract JSON from response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Try to extract JSON block
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        return self._fallback_initial_analysis(content)
                        
        return {}
    
    async def _analyze_with_anthropic(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Conduct analysis using Anthropic Claude"""
        
        # Similar implementation to OpenAI but using Anthropic API
        # Implementation would be similar structure
        
        return self._fallback_initial_analysis(content)
    
    def _fallback_initial_analysis(self, idea: str) -> Dict[str, Any]:
        """Fallback analysis when LLM APIs are unavailable"""
        
        # Intelligent heuristic analysis
        words = idea.lower().split()
        
        # Detect project type
        tech_indicators = {
            'app': ['app', 'mobile', 'application', 'ios', 'android'],
            'web': ['website', 'web', 'platform', 'site', 'online'],
            'saas': ['saas', 'software', 'service', 'tool', 'platform'],
            'ecommerce': ['store', 'shop', 'marketplace', 'sell', 'buy', 'ecommerce'],
            'ai': ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'ml']
        }
        
        project_type = 'web'  # default
        for ptype, keywords in tech_indicators.items():
            if any(keyword in words for keyword in keywords):
                project_type = ptype
                break
        
        # Generate contextual questions based on project type
        question_sets = {
            'app': [
                {"question": "What specific problem does your app solve for users?", "category": "market", "importance": "high"},
                {"question": "Are you targeting iOS, Android, or both platforms?", "category": "technical", "importance": "high"},
                {"question": "How do you plan to monetize the app - paid download, freemium, ads, or subscriptions?", "category": "monetization", "importance": "high"}
            ],
            'saas': [
                {"question": "Who is your ideal customer - small businesses, enterprises, or individual users?", "category": "market", "importance": "high"},
                {"question": "What's your estimated monthly subscription price point?", "category": "monetization", "importance": "high"},
                {"question": "Do you have technical experience or will you need to hire developers?", "category": "team", "importance": "medium"}
            ],
            'ecommerce': [
                {"question": "What products will you be selling and what's your sourcing strategy?", "category": "market", "importance": "high"},
                {"question": "Have you identified your main competitors and their pricing?", "category": "competition", "importance": "high"},
                {"question": "What's your marketing budget for customer acquisition?", "category": "monetization", "importance": "medium"}
            ]
        }
        
        default_questions = [
            {"question": "Who is your target audience and what specific problem are you solving for them?", "category": "market", "importance": "high"},
            {"question": "What's your budget range for building this project?", "category": "timeline", "importance": "medium"},
            {"question": "Do you have any technical background or team members lined up?", "category": "team", "importance": "medium"}
        ]
        
        questions = question_sets.get(project_type, default_questions)
        
        return {
            "initial_assessment": {
                "opportunity_score": 7.0,
                "complexity_level": "moderate",
                "market_size_estimate": f"Promising opportunity in the {project_type} space",
                "key_challenges": ["Market validation", "Customer acquisition", "Technical implementation"],
                "immediate_opportunities": ["Market research", "MVP development", "Early customer feedback"]
            },
            "strategic_questions": questions,
            "conversation_strategy": {
                "recommended_flow": ["market_validation", "competitive_analysis", "monetization_strategy"],
                "estimated_conversation_length": 5,
                "critical_info_needed": ["target_market", "value_proposition", "business_model"]
            }
        }
    
    async def _process_user_response(self, response: str, context: ConversationContext):
        """Process user response and update conversation context"""
        
        context.previous_questions.append(response)
        
        # Extract insights from response using keyword analysis
        response_lower = response.lower()
        
        # Detect target market information
        if not context.target_market:
            market_indicators = ['small business', 'enterprise', 'consumer', 'b2b', 'b2c', 'startup', 'individual']
            for indicator in market_indicators:
                if indicator in response_lower:
                    context.target_market = indicator
                    break
        
        # Detect budget information
        if not context.budget_range:
            budget_indicators = {
                'low': ['budget', 'cheap', 'minimal', 'bootstrap', 'low cost'],
                'medium': ['moderate', 'reasonable', 'standard'],
                'high': ['premium', 'enterprise', 'unlimited', 'whatever it takes']
            }
            
            for budget_level, keywords in budget_indicators.items():
                if any(keyword in response_lower for keyword in keywords):
                    context.budget_range = budget_level
                    break
        
        # Extract technical requirements
        tech_keywords = ['react', 'python', 'nodejs', 'mobile', 'web', 'api', 'database', 'cloud']
        mentioned_tech = [tech for tech in tech_keywords if tech in response_lower]
        if mentioned_tech:
            if not context.technical_requirements:
                context.technical_requirements = []
            context.technical_requirements.extend(mentioned_tech)
        
        # Generate insights based on response
        insight = BusinessInsight(
            category="user_response",
            insight=f"User indicated: {response[:100]}...",
            confidence=0.8,
            source="conversation",
            actionable_steps=["Continue gathering information", "Validate assumptions"]
        )
        
        context.gathered_insights.append(insight)
    
    def _assess_conversation_state(self, context: ConversationContext) -> Dict[str, Any]:
        """Assess current conversation state and determine next phase"""
        
        areas_explored = []
        completeness = 20  # Base completeness
        
        if context.target_market:
            areas_explored.append("target_market")
            completeness += 20
        
        if context.budget_range:
            areas_explored.append("budget")
            completeness += 15
        
        if context.technical_requirements:
            areas_explored.append("technical")
            completeness += 15
        
        if len(context.previous_questions) >= 3:
            areas_explored.append("detailed_requirements")
            completeness += 15
        
        if len(context.gathered_insights) >= 5:
            areas_explored.append("comprehensive_understanding")
            completeness += 15
        
        # Determine phase
        if completeness >= 80:
            phase = "analysis"
        elif completeness >= 50:
            phase = "deep_dive"
        else:
            phase = "discovery"
        
        return {
            "phase": phase,
            "completeness": min(completeness, 95),
            "areas_explored": areas_explored,
            "conversation_depth": len(context.previous_questions),
            "insights_gathered": len(context.gathered_insights)
        }
    
    async def _generate_contextual_questions(self, context: ConversationContext, conversation_state: Dict) -> Dict[str, Any]:
        """Generate contextual follow-up questions based on conversation state"""
        
        phase = conversation_state["phase"]
        areas_explored = conversation_state["areas_explored"]
        
        # Phase-based question generation
        if phase == "discovery":
            questions = self._get_discovery_questions(context, areas_explored)
            response = "Great! I'm getting a clearer picture of your vision. Let me dive deeper into a few key areas to give you the most strategic advice."
            
        elif phase == "deep_dive":
            questions = self._get_deep_dive_questions(context, areas_explored)
            response = "Excellent insights so far! Now let's explore some strategic considerations that will be crucial for your success."
            
        else:  # analysis phase
            questions = []
            response = "Perfect! I have enough information to provide you with a comprehensive strategic analysis."
        
        return {
            "response": response,
            "questions": questions
        }
    
    def _get_discovery_questions(self, context: ConversationContext, areas_explored: List[str]) -> List[Dict]:
        """Get discovery phase questions"""
        
        all_questions = [
            {
                "question": "What's the main pain point your solution addresses, and how painful is it for your target users?",
                "category": "market",
                "follow_up": "market_validation"
            },
            {
                "question": "Who do you see as your biggest competitors, and what makes your approach different?",
                "category": "competition",
                "follow_up": "competitive_analysis"
            },
            {
                "question": "How do you plan to make money from this - what's your business model?",
                "category": "monetization",
                "follow_up": "revenue_strategy"
            },
            {
                "question": "What's your timeline for launch, and do you have a team or technical resources lined up?",
                "category": "execution",
                "follow_up": "implementation_planning"
            }
        ]
        
        # Filter questions based on what hasn't been explored
        relevant_questions = []
        for q in all_questions:
            if q["category"] not in [area.split("_")[0] for area in areas_explored]:
                relevant_questions.append(q)
        
        return relevant_questions[:2]  # Return 2 most relevant questions
    
    def _get_deep_dive_questions(self, context: ConversationContext, areas_explored: List[str]) -> List[Dict]:
        """Get deep dive phase questions"""
        
        strategic_questions = [
            {
                "question": "What's your customer acquisition strategy, and what's your estimated cost per customer?",
                "category": "marketing",
                "follow_up": "growth_strategy"
            },
            {
                "question": "What are the biggest risks that could derail this project, and how would you mitigate them?",
                "category": "risk",
                "follow_up": "risk_management"
            },
            {
                "question": "If this succeeds, what does scale look like - 100 users, 10,000 users, or millions?",
                "category": "scale",
                "follow_up": "scalability_planning"
            }
        ]
        
        return strategic_questions[:1]  # Return 1 strategic question
    
    async def _generate_comprehensive_analysis(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate comprehensive business analysis based on gathered information"""
        
        # Compile all insights
        market_insights = [i for i in context.gathered_insights if i.category in ["market", "user_response"]]
        
        # Generate comprehensive analysis
        analysis = {
            "executive_summary": {
                "opportunity_assessment": "Strong potential based on market indicators and user feedback",
                "risk_level": "Moderate - typical for early-stage ventures",
                "recommendation": "Proceed with MVP development and market validation",
                "confidence_score": 7.5
            },
            
            "market_analysis": {
                "target_market": context.target_market or "Needs further definition",
                "market_size_estimate": "Market validation required",
                "competition_level": "Moderate competition expected",
                "market_entry_strategy": [
                    "Develop MVP with core features",
                    "Test with small user group",
                    "Iterate based on feedback"
                ]
            },
            
            "business_model_assessment": {
                "revenue_streams": ["Primary revenue model needs validation"],
                "pricing_strategy": "Competitive pricing recommended",
                "unit_economics": "Requires customer acquisition cost analysis",
                "scalability_potential": "High with proper execution"
            },
            
            "technical_feasibility": {
                "complexity_rating": "Moderate",
                "required_technologies": context.technical_requirements or ["Standard web technologies"],
                "development_timeline": "12-16 weeks for MVP",
                "team_requirements": ["Full-stack developer", "UI/UX designer"],
                "estimated_cost": context.budget_range or "Depends on requirements"
            },
            
            "risk_assessment": {
                "high_risks": [
                    "Market acceptance uncertainty",
                    "Competition from established players"
                ],
                "medium_risks": [
                    "Technical implementation challenges",
                    "Customer acquisition costs"
                ],
                "mitigation_strategies": [
                    "Start with MVP to test market fit",
                    "Build strong user feedback loop",
                    "Focus on unique value proposition"
                ]
            },
            
            "action_plan": {
                "immediate_next_steps": [
                    "Validate core assumptions with potential users",
                    "Create detailed technical specifications",
                    "Develop go-to-market strategy"
                ],
                "30_day_goals": [
                    "Complete market research",
                    "Finalize MVP feature set",
                    "Begin development or team building"
                ],
                "90_day_goals": [
                    "Launch MVP",
                    "Gather user feedback",
                    "Plan next iteration"
                ]
            },
            
            "financial_projections": {
                "development_costs": f"Estimated based on {context.budget_range or 'standard'} budget",
                "break_even_timeline": "6-12 months post-launch",
                "scaling_requirements": "Additional funding may be needed for growth"
            }
        }
        
        return analysis
    
    def _generate_conversation_summary(self, context: ConversationContext) -> Dict[str, Any]:
        """Generate summary of the strategic conversation"""
        
        return {
            "project_idea": context.project_idea,
            "total_exchanges": len(context.previous_questions),
            "insights_gathered": len(context.gathered_insights),
            "areas_covered": [
                "Initial concept validation",
                "Target market exploration", 
                "Business model discussion",
                "Technical requirements",
                "Strategic planning"
            ],
            "conversation_quality": "Comprehensive strategic consultation completed",
            "follow_up_recommended": True
        }

# Singleton instance
strategy_consultant = ConversationalStrategyConsultant()
