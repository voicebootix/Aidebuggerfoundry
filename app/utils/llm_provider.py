"""
Enhanced LLM Provider - Multi-Provider with Intelligent Failover
Supports OpenAI, Anthropic, Google with automatic failover
Enhanced with rate limiting and cost optimization
"""

import asyncio
import openai
import anthropic
import os
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    KIMIDEV = "kimidev"

@dataclass
class LLMResponse:
    content: str
    provider: LLMProvider
    model: str
    tokens_used: int
    cost_estimate: float
    response_time: float

class EnhancedLLMProvider:
    """Multi-LLM provider with intelligent failover"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        if api_keys is None:
         api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY")
        }
        
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_keys.get("anthropic")) if api_keys.get("anthropic") else None
        
        # ADD THE OPENAI CLIENT LINE HERE:
        self.openai_client = openai.AsyncOpenAI(api_key=api_keys.get("openai")) if api_keys.get("openai") else None
        
        # KimiDev client சேர்க்கவும்
        import httpx
        self.kimidev_client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {api_keys.get('openrouter')}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mydreamengine.com",
                "X-Title": "MyDreamEngine"
            },
            timeout=60.0
        ) if api_keys.get("openrouter") else None
        
        self.providers = [LLMProvider.KIMIDEV, LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        
    async def initialize(self):
        """Initialize the LLM provider"""
        try:
            # Test connections if API keys are available
            if self.openai_client:
                logging.info("✅ OpenAI client initialized")
            if self.anthropic_client:
                logging.info("✅ Anthropic client initialized")  # ADD THIS
            if self.kimidev_client:
                logging.info("✅ KimiDev client initialized")
            
            self.initialized = True
            logging.info("✅ LLM Provider initialized successfully")
        except Exception as e:
            logging.error(f"❌ LLM Provider initialization failed: {e}")
            raise
        
    async def generate_completion(self, 
                                prompt: str,
                                model: str = "auto",
                                temperature: float = 0.7) -> str:
        """Generate completion with automatic failover"""
        
        if not self.initialized:
            await self.initialize()
        
        for provider in self.providers:
            try:
                # REPLACE the KimiDev case in generate_completion with:
                if provider == LLMProvider.KIMIDEV and self.kimidev_client:
                    response = await self.kimidev_client.post(
                        "/chat/completions",
                        json={
                            "model": "moonshotai/kimi-dev-72b:free",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": temperature,
                            "max_tokens": 4000,
                            "top_p": 0.8
                        }
                    )
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Enhanced error handling
                    if "choices" not in response_data or not response_data["choices"]:
                        raise Exception("Invalid response format from KimiDev API")
                    
                    choice = response_data["choices"][0]
                    if "message" not in choice or "content" not in choice["message"]:
                        raise Exception("Missing content in KimiDev API response")
                    
                    return choice["message"]["content"]
                
                elif provider == LLMProvider.OPENAI and self.openai_client:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=4000
                    )
                    return response.choices[0].message.content

                # REPLACE the Anthropic case with:
                elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
                    response = await self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    # Enhanced error handling
                    if not response.content or not response.content[0]:
                        raise Exception("Empty response from Anthropic API")
                    
                    if not hasattr(response.content[0], 'text'):
                        raise Exception("Invalid response format from Anthropic API")
                    
                    return response.content[0].text
                    
            except Exception as e:
                logging.warning(f"Provider {provider.value} failed: {e}")
                continue
        
        raise Exception("All LLM providers failed")

    async def generate_business_analysis(self, business_idea: str) -> Dict[str, Any]:
        """Generate business analysis"""
        prompt = f"""
        Analyze this business idea comprehensively:
        
        Business Idea: {business_idea}
        
        Provide analysis in the following format:
        1. Market Opportunity
        2. Competitive Landscape
        3. Revenue Potential
        4. Risk Assessment
        5. Strategic Recommendations
        """
        
        response = await self.generate_completion(prompt)
        return {
            "analysis": response,
            "business_idea": business_idea,
            "status": "completed"
        }

    async def generate_code_project(self, project_description: str, tech_stack: str = "fastapi-react") -> Dict[str, Any]:
        """Generate code project"""
        prompt = f"""
        Generate a complete application based on this description:
        
        Project: {project_description}
        Tech Stack: {tech_stack}
        
        Provide:
        1. Project structure
        2. Key files and their contents
        3. Setup instructions
        4. Deployment guide
        """
        
        response = await self.generate_completion(prompt)
        return {
            "generated_code": response,
            "project_description": project_description,
            "tech_stack": tech_stack,
            "status": "completed"
        }

# Create the global instance that main.py expects
llm_provider = EnhancedLLMProvider()

