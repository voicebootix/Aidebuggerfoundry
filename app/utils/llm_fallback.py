import os
import logging
from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProviderWithFallback:
    """
    Smart LLM provider that falls back to OpenAI when other providers' API keys are missing
    """
    
    def __init__(self):
        # Get API keys from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Track which providers are available
        self.available_providers = self._check_available_providers()
        
        # Log provider status
        self._log_provider_status()
    
    def _check_available_providers(self) -> Dict[str, bool]:
        """Check which providers have valid API keys"""
        return {
            "openai": bool(self.openai_api_key),
            "anthropic": bool(self.anthropic_api_key),
            "google": bool(self.google_api_key)
        }
    
    def _log_provider_status(self):
        """Log which providers are available"""
        available = [provider for provider, available in self.available_providers.items() if available]
        unavailable = [provider for provider, available in self.available_providers.items() if not available]
        
        logger.info(f"✅ Available LLM providers: {', '.join(available) if available else 'None'}")
        if unavailable:
            logger.warning(f"⚠️  Unavailable providers (will fallback to OpenAI): {', '.join(unavailable)}")
            
        if not self.openai_api_key:
            logger.error("❌ No API keys available! Please set at least OPENAI_API_KEY")
    
    def get_provider_for_request(self, preferred_provider: str = "auto") -> str:
        """
        Determine which provider to use based on availability and preference
        """
        
        # If auto-detect, choose best available provider
        if preferred_provider == "auto":
            if self.available_providers["anthropic"]:
                return "anthropic"
            elif self.available_providers["openai"]:
                return "openai"
            elif self.available_providers["google"]:
                return "google"
            else:
                return "openai"  # Fallback even without key (will error gracefully)
        
        # If specific provider requested, check if available
        if preferred_provider in self.available_providers:
            if self.available_providers[preferred_provider]:
                return preferred_provider
            else:
                # Fallback to OpenAI if preferred provider unavailable
                logger.warning(f"🔄 {preferred_provider.title()} API key not available, falling back to OpenAI")
                return "openai"
        
        # Default to OpenAI
        return "openai"
    
    async def generate_code(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code using the best available provider
        """
        preferred_provider = options.get("model_provider", "auto")
        actual_provider = self.get_provider_for_request(preferred_provider)
        
        logger.info(f"🎯 Using {actual_provider.title()} for code generation")
        
        try:
            if actual_provider == "openai":
                return await self._generate_with_openai(prompt, options)
            elif actual_provider == "anthropic":
                return await self._generate_with_anthropic(prompt, options)
            elif actual_provider == "google":
                return await self._generate_with_google(prompt, options)
            else:
                # Ultimate fallback
                return await self._generate_with_openai(prompt, options)
                
        except Exception as e:
            # If preferred provider fails, try OpenAI as fallback
            if actual_provider != "openai" and self.available_providers["openai"]:
                logger.warning(f"🔄 {actual_provider.title()} failed, falling back to OpenAI: {str(e)}")
                return await self._generate_with_openai(prompt, options)
            else:
                raise e
    
    async def generate_streaming(self, prompt: str, options: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate code with streaming using the best available provider
        """
        preferred_provider = options.get("model_provider", "auto")
        actual_provider = self.get_provider_for_request(preferred_provider)
        
        logger.info(f"🎯 Using {actual_provider.title()} for streaming generation")
        
        try:
            if actual_provider == "openai":
                async for chunk in self._stream_with_openai(prompt, options):
                    yield chunk
            elif actual_provider == "anthropic":
                # Fallback to OpenAI for streaming if Anthropic not available
                if self.available_providers["openai"]:
                    logger.warning("🔄 Anthropic streaming not configured, using OpenAI")
                    async for chunk in self._stream_with_openai(prompt, options):
                        yield chunk
                else:
                    raise Exception("No streaming provider available")
            elif actual_provider == "google":
                # Fallback to OpenAI for streaming if Google not available
                if self.available_providers["openai"]:
                    logger.warning("🔄 Google streaming not configured, using OpenAI")
                    async for chunk in self._stream_with_openai(prompt, options):
                        yield chunk
                else:
                    raise Exception("No streaming provider available")
                    
        except Exception as e:
            # If preferred provider fails, try OpenAI as fallback
            if actual_provider != "openai" and self.available_providers["openai"]:
                logger.warning(f"🔄 {actual_provider.title()} streaming failed, falling back to OpenAI")
                async for chunk in self._stream_with_openai(prompt, options):
                    yield chunk
            else:
                raise e
    
    async def _generate_with_openai(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using OpenAI API"""
        
        if not self.openai_api_key:
            raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
        
        import openai
        openai.api_key = self.openai_api_key
        
        try:
            # Enhanced prompt for better code generation
            enhanced_prompt = self._create_code_generation_prompt(prompt, options)
            
            response = await openai.ChatCompletion.acreate(
                model=options.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software developer. Generate clean, production-ready code with comprehensive documentation."
                    },
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=options.get("max_tokens", 4000),
                temperature=options.get("temperature", 0.7)
            )
            
            # Parse the response and structure it
            generated_content = response.choices[0].message.content
            return self._parse_generated_content(generated_content, options)
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _stream_with_openai(self, prompt: str, options: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream code generation using OpenAI API"""
        
        if not self.openai_api_key:
            raise Exception("OpenAI API key not configured for streaming")
        
        import openai
        openai.api_key = self.openai_api_key
        
        try:
            enhanced_prompt = self._create_code_generation_prompt(prompt, options)
            
            stream = await openai.ChatCompletion.acreate(
                model=options.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert software developer. Generate clean, production-ready code."
                    },
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=options.get("max_tokens", 4000),
                temperature=options.get("temperature", 0.7),
                stream=True
            )
            
            chunk_index = 0
            accumulated_content = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_content += content
                    
                    yield {
                        "content_type": "code_fragment",
                        "content": content,
                        "chunk_index": chunk_index,
                        "is_final": False,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    chunk_index += 1
                    
                    # Small delay to prevent overwhelming the frontend
                    await asyncio.sleep(0.05)
            
            # Send final chunk with complete result
            final_result = self._parse_generated_content(accumulated_content, options)
            yield {
                "content_type": "final_result",
                "content": final_result,
                "chunk_index": chunk_index,
                "is_final": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {str(e)}")
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    async def _generate_with_anthropic(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using Anthropic API (placeholder - implement when key available)"""
        
        if not self.anthropic_api_key:
            # This should never be called if key is missing due to fallback logic
            raise Exception("Anthropic API key not configured")
        
        # TODO: Implement Anthropic API integration when key is available
        logger.info("🚧 Anthropic integration not yet implemented, this is a placeholder")
        
        # For now, fallback to OpenAI
        return await self._generate_with_openai(prompt, options)
    
    async def _generate_with_google(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using Google API (placeholder - implement when key available)"""
        
        if not self.google_api_key:
            # This should never be called if key is missing due to fallback logic
            raise Exception("Google API key not configured")
        
        # TODO: Implement Google API integration when key is available
        logger.info("🚧 Google integration not yet implemented, this is a placeholder")
        
        # For now, fallback to OpenAI
        return await self._generate_with_openai(prompt, options)
    
    def _create_code_generation_prompt(self, user_prompt: str, options: Dict[str, Any]) -> str:
        """Create an enhanced prompt for better code generation"""
        
        project_type = options.get("project_type", "web_api")
        language = options.get("programming_language", "python")
        include_tests = options.get("include_tests", True)
        include_docs = options.get("include_documentation", True)
        
        enhanced_prompt = f"""
Generate a complete, production-ready {project_type} project based on this requirement:

{user_prompt}

Requirements:
- Programming Language: {language}
- Project Type: {project_type}
- Include Tests: {include_tests}
- Include Documentation: {include_docs}

Please provide:
1. Complete, functional code files
2. Clear file structure
3. Installation and setup instructions
4. API documentation (if applicable)

Structure your response with clear file separations and explanations.
"""
        
        return enhanced_prompt.strip()
    
    def _parse_generated_content(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the generated content into structured format"""
        
        # This is a simplified parser - you can enhance this based on your needs
        files = []
        
        # Try to extract code blocks and file names
        import re
        
        # Pattern to match code blocks with optional filenames
        code_pattern = r'```(?:(\w+)\s+)?(?:# (\S+\.?\w*)\s+)?(.*?)```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        if matches:
            for i, (language, filename, code) in enumerate(matches):
                if not filename:
                    ext = self._get_extension_for_language(language or options.get("programming_language", "python"))
                    filename = f"generated_file_{i+1}.{ext}"
                
                files.append({
                    "filename": filename,
                    "content": code.strip(),
                    "language": language or self._detect_language_from_filename(filename),
                    "purpose": f"Generated {language or 'code'} file"
                })
        else:
            # If no code blocks found, treat entire content as a single file
            ext = self._get_extension_for_language(options.get("programming_language", "python"))
            files.append({
                "filename": f"main.{ext}",
                "content": content.strip(),
                "language": options.get("programming_language", "python"),
                "purpose": "Generated code file"
            })
        
        return {
            "files": files,
            "main_file": files[0]["filename"] if files else None,
            "explanation": "Code generated successfully using AI assistance",
            "architecture": f"Generated {options.get('project_type', 'application')} with {len(files)} files",
            "deployment_steps": [
                {"step_number": 1, "description": "Install dependencies", "command": "pip install -r requirements.txt"},
                {"step_number": 2, "description": "Run the application", "command": "python main.py"}
            ]
        }
    
    def _get_extension_for_language(self, language: str) -> str:
        """Get file extension for programming language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "ruby": "rb",
            "php": "php"
        }
        return extensions.get(language.lower(), "txt")
    
    def _detect_language_from_filename(self, filename: str) -> str:
        """Detect programming language from filename"""
        if '.' not in filename:
            return "text"
        
        ext = filename.split('.')[-1].lower()
        language_map = {
            "py": "python",
            "js": "javascript", 
            "ts": "typescript",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rs": "rust",
            "rb": "ruby",
            "php": "php"
        }
        
        return language_map.get(ext, "text")

# Convenience function for easy import
def get_llm_provider():
    """Get an instance of the LLM provider with fallback"""
    return LLMProviderWithFallback()
