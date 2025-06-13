
"""
DreamEngine - Main Backend Module
Converts founder conversations into deployable code through a structured AI pipeline.
Integrates with AI Debugger Factory BuildBot (Layer 1).
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator, Union

import httpx
import openai
import anthropic
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sse_starlette.sse import EventSourceResponse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# REQUIRED: Use existing utility imports
from app.config import settings
from app.utils.logger import setup_logger
from app.database.db import get_db # Assuming get_db is async, if not, adjust
from app.models.dream_models import (
    DreamRequest, GenerationResult, ValidationResult, StreamingChunk, 
    HealthCheckResponse, GenerationOptions, ModelProvider, SecurityIssue,
    CodeQualityIssue, GeneratedFile, DeploymentStep, RateLimitStatus, ErrorResponse
)

# REQUIRED: Initialize logger using existing setup
logger = setup_logger()

# REQUIRED: Router with /api/v1/ prefix pattern
router = APIRouter(prefix="/api/v1/dreamengine", tags=["dreamengine"])

# --- Constants and Configuration ---
MAX_INPUT_LENGTH = 10000
MIN_INPUT_LENGTH = 10
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.7

# Rate Limiting Configuration (can be moved to a more sophisticated store like Redis)
RATE_LIMIT_REQUESTS = int(os.getenv("DREAMENGINE_RATE_LIMIT", "100"))
RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("DREAMENGINE_RATE_LIMIT_PERIOD", "3600"))
user_request_counts: Dict[str, List[datetime]] = {}

# --- LLM Client Implementations ---

class OpenAIClient:
    """Client for OpenAI GPT-4 API"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        logger.info("OpenAIClient initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type((openai.APIError, httpx.RequestError)))
    async def generate_streaming(self, prompt: str, max_tokens: Optional[int], temperature: float) -> AsyncGenerator[str, None]:
        """Generate code using OpenAI GPT-4 streaming."""
        logger.info(f"OpenAI: Streaming generation for prompt (first 50 chars): {prompt[:50]}...")
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview", # Or other suitable model
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
                temperature=temperature
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI APIConnectionError: {str(e)}")
            raise HTTPException(status_code=503, detail=f"OpenAI service unavailable: {str(e)}")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI RateLimitError: {str(e)}")
            raise HTTPException(status_code=429, detail=f"OpenAI rate limit exceeded: {str(e)}")
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI AuthenticationError: {str(e)}")
            raise HTTPException(status_code=401, detail=f"OpenAI authentication failed: {str(e)}")
        except openai.APIError as e:
            logger.error(f"OpenAI APIError: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"OpenAI HTTPX RequestError: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Network error connecting to OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI streaming: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected OpenAI error: {str(e)}")

class AnthropicClient:
    """Client for Anthropic Claude API"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        logger.info("AnthropicClient initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type((anthropic.APIError, httpx.RequestError)))
    async def generate_streaming(self, prompt: str, max_tokens: Optional[int], temperature: float) -> AsyncGenerator[str, None]:
        """Generate code using Anthropic Claude streaming."""
        logger.info(f"Anthropic: Streaming generation for prompt (first 50 chars): {prompt[:50]}...")
        try:
            async with self.client.messages.stream(
                model="claude-3-opus-20240229", # Or other suitable model
                max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic APIConnectionError: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Anthropic service unavailable: {str(e)}")
        except anthropic.RateLimitError as e:
            logger.error(f"Anthropic RateLimitError: {str(e)}")
            raise HTTPException(status_code=429, detail=f"Anthropic rate limit exceeded: {str(e)}")
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic AuthenticationError: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Anthropic authentication failed: {str(e)}")
        except anthropic.APIError as e:
            logger.error(f"Anthropic APIError: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Anthropic API error: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Anthropic HTTPX RequestError: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Network error connecting to Anthropic: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic streaming: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected Anthropic error: {str(e)}")

class GoogleClient:
    """Client for Google Gemini API"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro") # Or other suitable model
        logger.info("GoogleClient initialized.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type(Exception)) # Broad exception for Gemini, refine if specific errors are known
    async def generate_streaming(self, prompt: str, max_tokens: Optional[int], temperature: float) -> AsyncGenerator[str, None]:
        """Generate code using Google Gemini streaming."""
        logger.info(f"Google: Streaming generation for prompt (first 50 chars): {prompt[:50]}...")
        # Note: Gemini API has specific ways to handle streaming, this is a simplified example.
        # Actual implementation might require using `generate_content_async` with `stream=True`
        # and handling `GenerationConfig` for max_tokens and temperature.
        try:
            # Gemini's Python SDK does not directly support async iteration for streaming in the same way as OpenAI/Anthropic.
            # A common pattern is to use `generate_content(..., stream=True)` and iterate, 
            # but for async, one might need to wrap synchronous calls or use an async-compatible library if available.
            # This is a conceptual async adaptation.
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens or DEFAULT_MAX_TOKENS,
                    temperature=temperature
                )
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}")
            # Map to HTTPException based on common Google API error types if possible
            if "API key not valid" in str(e):
                 raise HTTPException(status_code=401, detail=f"Google authentication failed: {str(e)}")
            if "quota" in str(e).lower():
                 raise HTTPException(status_code=429, detail=f"Google rate limit exceeded: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Google API error: {str(e)}")

# --- Security and Validation ---

class SecurityValidator:
    """Comprehensive security validation for inputs and outputs."""

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize input text to prevent common injection attacks."""
        if not isinstance(text, str):
            logger.warning("Sanitize_input received non-string type, returning as is.")
            return str(text) # Or raise error

        logger.info(f"Sanitizing input (first 50 chars): {text[:50]}...")
        # Basic sanitization: remove null bytes, strip leading/trailing whitespace
        sanitized_text = text.replace("\x00", "").strip()
        
        # SQL Injection (very basic, consider more robust libraries for production)
        sql_patterns = ["--", ";", "xp_cmdshell", "DROP TABLE", "SELECT * FROM"]
        for pattern in sql_patterns:
            if pattern.lower() in sanitized_text.lower():
                logger.warning(f"Potential SQL injection pattern found: {pattern}")
                # For now, we log and proceed. In a stricter mode, this could raise an error or replace the pattern.
                # sanitized_text = sanitized_text.replace(pattern, "") # Example replacement
        
        # XSS (very basic, use libraries like bleach for production)
        xss_patterns = ["<script>", "javascript:", "onerror="]
        for pattern in xss_patterns:
            if pattern.lower() in sanitized_text.lower():
                logger.warning(f"Potential XSS pattern found: {pattern}")
                # sanitized_text = sanitized_text.replace("<", "&lt;").replace(">", "&gt;") # Example escaping

        if len(sanitized_text) > MAX_INPUT_LENGTH:
            logger.warning(f"Input text truncated to {MAX_INPUT_LENGTH} characters.")
            sanitized_text = sanitized_text[:MAX_INPUT_LENGTH]
        
        logger.info("Input sanitization complete.")
        return sanitized_text

    @staticmethod
    def validate_code_safety(code: str, language: str = "python") -> Dict[str, List[SecurityIssue]]:
        """Validate generated code for common security vulnerabilities."""
        logger.info(f"Validating code safety for language: {language} (code length: {len(code)})...")
        issues: List[SecurityIssue] = []
        report: Dict[str, Any] = {"issues": issues, "overall_status": "safe"}

        # Example checks (these are very basic and illustrative)
        # For production, integrate with static analysis tools (e.g., Bandit for Python, Snyk, SonarQube)

        if "os.system(" in code or "subprocess.call(" in code or "eval(" in code:
            issues.append(SecurityIssue(
                severity="high",
                description="Potential command injection via os.system, subprocess.call, or eval.",
                recommendation="Avoid direct shell command execution. Use safer alternatives or sanitize inputs rigorously."
            ))

        if "pickle.loads(" in code or "dill.loads(" in code:
             issues.append(SecurityIssue(
                severity="high",
                description="Potential arbitrary code execution via insecure deserialization (pickle/dill).",
                recommendation="Avoid pickle/dill for untrusted data. Use safer serialization formats like JSON."
            ))

        # Basic check for hardcoded secrets (very naive)
        secret_keywords = ["api_key", "secret", "password", "token"]
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "=" in line and any(kw in line.lower() for kw in secret_keywords):
                parts = line.split("=")
                if len(parts) > 1 and any(char in parts[1] for char in ["'", "\""]):
                    issues.append(SecurityIssue(
                        severity="medium",
                        description="Potential hardcoded secret found.",
                        location=f"line {i+1}",
                        recommendation="Store secrets in environment variables or a secure vault, not in code."
                    ))
        
        if issues:
            report["overall_status"] = "unsafe"
            logger.warning(f"Code safety validation found {len(issues)} issues.")
        else:
            logger.info("Code safety validation passed with no critical issues found.")
        
        return report

# --- Rate Limiting --- 
class RateLimiter:
    """Production rate limiting with user tracking."""
    async def check_rate_limit(self, user_id: str) -> RateLimitStatus:
        """Check and update rate limit for a user."""
        now = datetime.now()
        if user_id not in user_request_counts:
            user_request_counts[user_id] = []

        # Remove timestamps older than the rate limit period
        user_request_counts[user_id] = [
            t for t in user_request_counts[user_id] 
            if now - t < timedelta(seconds=RATE_LIMIT_PERIOD_SECONDS)
        ]

        requests_made = len(user_request_counts[user_id])
        requests_remaining = RATE_LIMIT_REQUESTS - requests_made
        is_limited = requests_made >= RATE_LIMIT_REQUESTS
        
        reset_time = (user_request_counts[user_id][0] + timedelta(seconds=RATE_LIMIT_PERIOD_SECONDS)).isoformat() \
            if user_request_counts[user_id] and is_limited else (now + timedelta(seconds=RATE_LIMIT_PERIOD_SECONDS)).isoformat()

        status_obj = RateLimitStatus(
            user_id=user_id,
            requests_remaining=max(0, requests_remaining),
            requests_limit=RATE_LIMIT_REQUESTS,
            reset_time=reset_time,
            is_limited=is_limited
        )

        if is_limited:
            logger.warning(f"Rate limit exceeded for user {user_id}. Remaining: {status_obj.requests_remaining}")
            return status_obj
        
        user_request_counts[user_id].append(now)
        logger.info(f"Rate limit check passed for user {user_id}. Remaining: {status_obj.requests_remaining}")
        return status_obj

# --- DreamEngine Core Logic ---

class DreamEngine:
    """Core DreamEngine logic for converting founder conversations to code."""

    def __init__(self, config: Optional[Dict[str, str]] = None):
        """Initialize DreamEngine with configuration and LLM clients."""
        self.logger = setup_logger() # Use existing logger
        self.config = config or {}
        self.rate_limiter = RateLimiter()

        # Initialize LLM clients (API keys from environment variables)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

        self.clients: Dict[ModelProvider, Any] = {}
        if self.openai_api_key:
            self.clients[ModelProvider.OPENAI] = OpenAIClient(self.openai_api_key)
        else:
            self.logger.warning("OpenAI API key not found. OpenAI provider will be unavailable.")
        
        if self.anthropic_api_key:
            self.clients[ModelProvider.ANTHROPIC] = AnthropicClient(self.anthropic_api_key)
        else:
            self.logger.warning("Anthropic API key not found. Anthropic provider will be unavailable.")

        if self.google_api_key:
            self.clients[ModelProvider.GOOGLE] = GoogleClient(self.google_api_key)
        else:
            self.logger.warning("Google API key not found. Google provider will be unavailable.")
        
        if not self.clients:
            self.logger.error("No LLM API keys configured. DreamEngine will not be functional.")
            # raise ValueError("At least one LLM API key (OpenAI, Anthropic, or Google) must be configured.")

        self.default_provider = ModelProvider(os.getenv("DREAMENGINE_DEFAULT_PROVIDER", "auto"))
        self.logger.info(f"DreamEngine initialized. Default provider: {self.default_provider}. Available clients: {list(self.clients.keys())}")

    def _get_llm_client(self, provider: ModelProvider) -> Any:
        """Get the LLM client for the specified provider."""
        if provider == ModelProvider.AUTO:
            # Simple auto-selection logic (prefer OpenAI, then Anthropic, then Google)
            if ModelProvider.OPENAI in self.clients: return self.clients[ModelProvider.OPENAI]
            if ModelProvider.ANTHROPIC in self.clients: return self.clients[ModelProvider.ANTHROPIC]
            if ModelProvider.GOOGLE in self.clients: return self.clients[ModelProvider.GOOGLE]
            self.logger.error("Auto provider selection failed: No clients available.")
            raise HTTPException(status_code=503, detail="No LLM providers available.")
        
        client = self.clients.get(provider)
        if not client:
            self.logger.error(f"LLM provider '{provider.value}' not available or API key missing.")
            raise HTTPException(status_code=503, detail=f"LLM provider '{provider.value}' not available.")
        return client

    async def _log_operation(self, operation_data: Dict[str, Any]):
        """Log operation to meta/dream_log.json."""
        try:
            log_dir = "../../meta"
            log_file = os.path.join(log_dir, "dream_log.json")
            os.makedirs(log_dir, exist_ok=True)

            dream_log: Dict[str, List] = {"operations": []}
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    try:
                        dream_log = json.load(f)
                        if not isinstance(dream_log.get("operations"), list):
                           dream_log["operations"] = [] 
                    except json.JSONDecodeError:
                        self.logger.warning(f"Could not decode {log_file}, reinitializing.")
                        dream_log["operations"] = [] 
            
            dream_log["operations"].append(operation_data)
            
            with open(log_file, "w") as f:
                json.dump(dream_log, f, indent=2)
            self.logger.info(f"Operation logged to {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to log operation: {str(e)}")

    async def process_founder_input(self, request: DreamRequest) -> GenerationResult:
        """Main processing pipeline for founder input."""
        start_time = datetime.now()
        self.logger.info(f"Processing founder input for user {request.user_id}, request ID {request.id}")

        # 1. Input sanitization and validation
        sanitized_input = SecurityValidator.sanitize_input(request.input_text)
        if len(sanitized_input) < MIN_INPUT_LENGTH:
            raise HTTPException(status_code=400, detail=f"Input text too short (min {MIN_INPUT_LENGTH} chars).")

        # (Rate limiting check would typically be middleware or earlier in request lifecycle)
        # For this structure, we call it here.
        rate_limit_status = await self.rate_limiter.check_rate_limit(request.user_id)
        if rate_limit_status.is_limited:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again after {rate_limit_status.reset_time}.")

        # 2. Intent classification (Simplified - LLM can do this implicitly)
        # 3. Project type detection (Simplified - LLM can infer or use options)
        # 4. Technical feasibility analysis (Can be part of validation endpoint or initial LLM pass)
        
        # 5. LLM prompt engineering
        # This is a crucial step and would involve complex logic based on project type, language, etc.
        # For now, a generic prompt structure:
        prompt = f"""
        Generate a complete, enterprise-grade software project based on the following founder's description.
        The project should be production-ready, secure, and performant.

        Founder's Description:
        {sanitized_input}

        Generation Options:
        - Project Type: {request.options.project_type.value if request.options.project_type else 'auto-detect'}
        - Programming Language: {request.options.programming_language.value if request.options.programming_language else 'auto-detect'}
        - Database: {request.options.database_type.value if request.options.database_type else 'auto-detect'}
        - Security Level: {request.options.security_level.value}
        - Include Tests: {request.options.include_tests}
        - Include Documentation: {request.options.include_documentation}
        - Include Docker: {request.options.include_docker}
        - Include CI/CD: {request.options.include_ci_cd}

        Output Requirements:
        - Provide all necessary code files, including main application, models, routes, utilities, tests, etc.
        - Structure the project logically.
        - Include clear explanations for the architecture and key components.
        - List all dependencies and required environment variables.
        - Provide step-by-step deployment instructions.
        - Ensure code is secure and follows best practices for the specified security level.
        - If streaming, provide code in chunks, indicating file paths.
        
        Format the output as a JSON object containing:
        `files`: A list of objects, each with `filename` (string, full path) and `content` (string, file content).
        `explanation`: A detailed explanation of the generated code and architecture (string, markdown format).
        `architecture`: A summary of the project architecture (string, markdown format).
        `deployment_steps`: A list of objects, each with `step_number` (int), `description` (string), and optionally `command` (string).
        `dependencies`: A list of required dependencies (strings).
        `environment_variables`: A list of required environment variables (strings).
        `project_type_detected`: The detected project type (string, from ProjectType enum).
        `language_detected`: The detected programming language (string, from ProgrammingLanguage enum).
        `database_detected`: The detected database type (string, from DatabaseType enum, or null).
        """

        # 6. Code generation (non-streaming for this method)
        # For non-streaming, we'd collect all chunks from the streaming method.
        # This is a conceptual placeholder for how one might adapt a streaming generator for a non-streaming call.
        generated_content_parts = []
        provider = request.options.model_provider
        llm_client = self._get_llm_client(provider)
        
        self.logger.info(f"Using LLM provider: {provider.value}")
        async for chunk_content in llm_client.generate_streaming(prompt, request.options.max_tokens, request.options.temperature):
            generated_content_parts.append(chunk_content)
        
        full_generated_text = "".join(generated_content_parts)
        
        # Attempt to parse the LLM output as JSON
        try:
            parsed_llm_output = json.loads(full_generated_text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM output as JSON: {str(e)}. Output (first 500 chars): {full_generated_text[:500]}")
            raise HTTPException(status_code=500, detail="LLM generated invalid JSON output.")

        # 7. Code validation and security scanning
        # For each generated file, perform validation. This is simplified.
        all_code_for_scan = "\n".join([file_obj.get("content", "") for file_obj in parsed_llm_output.get("files", [])])
        security_report = SecurityValidator.validate_code_safety(all_code_for_scan)
        
        # (Code quality scanning would go here too)
        quality_issues: List[CodeQualityIssue] = [] # Placeholder

        # 8. Response formatting and logging
        end_time = datetime.now()
        generation_time_seconds = (end_time - start_time).total_seconds()

        # Map parsed LLM output to GenerationResult model
        # This requires careful mapping and validation of LLM output structure
        # Example mapping (highly dependent on LLM's adherence to the prompt's JSON structure)
        result = GenerationResult(
            request_id=request.id,
            user_id=request.user_id,
            project_type=parsed_llm_output.get("project_type_detected", ProjectType.OTHER.value),
            programming_language=parsed_llm_output.get("language_detected", ProgrammingLanguage.OTHER.value),
            database_type=parsed_llm_output.get("database_detected"),
            files=[GeneratedFile(**f) for f in parsed_llm_output.get("files", [])],
            main_file=next((f["filename"] for f in parsed_llm_output.get("files", []) if "main" in f["filename"] or "app" in f["filename"]), None),
            explanation=parsed_llm_output.get("explanation", "No explanation provided."),
            architecture=parsed_llm_output.get("architecture", "No architecture description provided."),
            security_issues=[SecurityIssue(**si) for si in security_report.get("issues", [])],
            quality_issues=quality_issues, # Add actual quality issues
            deployment_steps=[DeploymentStep(**ds) for ds in parsed_llm_output.get("deployment_steps", [])],
            dependencies=parsed_llm_output.get("dependencies", []),
            environment_variables=parsed_llm_output.get("environment_variables", []),
            model_provider=provider,
            generation_time_seconds=generation_time_seconds
        )

        await self._log_operation({
            "timestamp": end_time.isoformat(),
            "operation": "dream_generation_process",
            "request_id": request.id,
            "user_id": request.user_id,
            "success": True,
            "provider": provider.value,
            "generation_time_seconds": generation_time_seconds
        })
        self.logger.info(f"Dream generation successful for user {request.user_id}. Time: {generation_time_seconds:.2f}s")
        return result

    async def generate_code_streaming(self, request: DreamRequest) -> AsyncGenerator[StreamingChunk, None]:
        """Stream code generation with real-time updates."""
        self.logger.info(f"Streaming code generation for user {request.user_id}, request ID {request.id}")
        
        sanitized_input = SecurityValidator.sanitize_input(request.input_text)
        rate_limit_status = await self.rate_limiter.check_rate_limit(request.user_id)
        if rate_limit_status.is_limited:
            # For streaming, we might yield an error chunk or raise directly.
            # Raising directly is simpler if the EventSourceResponse handles it.
            # However, the spec implies SSE, so yielding an error chunk might be better.
            yield StreamingChunk(
                request_id=request.id,
                chunk_index=0,
                content=json.dumps({"error": f"Rate limit exceeded. Try again after {rate_limit_status.reset_time}."}),
                content_type="error",
                is_final=True
            )
            return

        # (Prompt engineering similar to non-streaming version, but adapted for streaming output)
        # The LLM would need to be prompted to output structured chunks, e.g., JSON objects for each part.
        # This is a complex part of the implementation.
        # For this example, we'll assume the LLM yields text that we wrap into chunks.
        # A more robust solution would have the LLM yield JSON like: 
        # {"type": "file_start", "path": "app/main.py"}, {"type": "code", "content": "..."}, {"type": "file_end"}
        
        prompt = f"Stream the generation of a project based on: {sanitized_input}. Options: {request.options.dict(exclude_none=True)}. Output code and explanations in manageable chunks. Indicate file paths clearly. Mark the final chunk." 
        # This prompt is highly simplified. Real prompt would be much more detailed.

        provider = request.options.model_provider
        llm_client = self._get_llm_client(provider)
        chunk_index = 0
        try:
            async for content_chunk in llm_client.generate_streaming(prompt, request.options.max_tokens, request.options.temperature):
                yield StreamingChunk(
                    request_id=request.id,
                    chunk_index=chunk_index,
                    content=content_chunk,
                    content_type="code_fragment" # Or infer based on LLM output structure
                )
                chunk_index += 1
            
            # Yield a final chunk with metadata (if LLM doesn't provide it explicitly)
            yield StreamingChunk(
                request_id=request.id,
                chunk_index=chunk_index,
                content=json.dumps({"message": "Streaming complete."}), # Placeholder for final metadata
                content_type="metadata",
                is_final=True
            )
            self.logger.info(f"Streaming completed for request {request.id}")
            await self._log_operation({
                "timestamp": datetime.now().isoformat(),
                "operation": "dream_generation_stream_success",
                "request_id": request.id,
                "user_id": request.user_id,
                "success": True,
                "provider": provider.value
            })
        except HTTPException as e: # Re-raise HTTPExceptions from LLM clients
            self.logger.error(f"HTTPException during streaming for {request.id}: {e.detail}")
            # Yield an error chunk for SSE client to handle
            yield StreamingChunk(
                request_id=request.id,
                chunk_index=chunk_index,
                content=json.dumps({"error": e.detail, "status_code": e.status_code}),
                content_type="error",
                is_final=True
            )
            await self._log_operation({
                "timestamp": datetime.now().isoformat(),
                "operation": "dream_generation_stream_error",
                "request_id": request.id,
                "user_id": request.user_id,
                "success": False,
                "error": e.detail
            })
        except Exception as e:
            self.logger.error(f"Unexpected error during streaming for {request.id}: {str(e)}")
            yield StreamingChunk(
                request_id=request.id,
                chunk_index=chunk_index,
                content=json.dumps({"error": f"Internal server error during streaming: {str(e)}"}),
                content_type="error",
                is_final=True
            )
            await self._log_operation({
                "timestamp": datetime.now().isoformat(),
                "operation": "dream_generation_stream_error",
                "request_id": request.id,
                "user_id": request.user_id,
                "success": False,
                "error": str(e)
            })

    async def validate_idea(self, request: DreamRequest) -> ValidationResult:
        """Pre-generation validation and analysis of the founder's idea."""
        self.logger.info(f"Validating idea for user {request.user_id}, request ID {request.id}")
        sanitized_input = SecurityValidator.sanitize_input(request.input_text)
        
        rate_limit_status = await self.rate_limiter.check_rate_limit(request.user_id)
        if rate_limit_status.is_limited:
            raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again after {rate_limit_status.reset_time}.")

        # This would typically involve an LLM call to analyze the idea.
        # The prompt would ask the LLM to assess feasibility, complexity, clarity, etc.
        # and return a structured JSON response matching ValidationResult.
        # Placeholder for LLM call and result parsing:
        validation_prompt = f"""
        Analyze the following founder's project idea and provide a structured validation report.
        Idea: "{sanitized_input}"
        Options: {request.options.dict(exclude_none=True)}

        Assess the following aspects and provide a score (0.0-1.0), explanation, and recommendations for each:
        - Technical Feasibility
        - Complexity
        - Clarity of Requirements
        - Security Considerations

        Also provide:
        - Overall Score (0.0-1.0)
        - Detected Project Type (from ProjectType enum: {', '.join([pt.value for pt in ModelProvider])} etc.)
        - Detected Programming Language (from ProgrammingLanguage enum)
        - Detected Database Type (from DatabaseType enum, or null)
        - Estimated Development Time (e.g., "2-4 weeks", "3-6 months")
        - A concise Summary of the validation.

        Return the entire response as a single JSON object matching the Pydantic model ValidationResult.
        """
        provider = request.options.model_provider
        llm_client = self._get_llm_client(provider)
        
        llm_response_parts = []
        async for chunk in llm_client.generate_streaming(validation_prompt, 2048, 0.5): # Lower temp for analysis
            llm_response_parts.append(chunk)
        full_llm_response = "".join(llm_response_parts)

        try:
            parsed_validation_data = json.loads(full_llm_response)
            # Ensure all fields of ValidationResult are present and correctly typed
            # This is a critical step; the LLM must be prompted very carefully.
            # Add robust parsing and default value handling here.
            validation_result = ValidationResult(**parsed_validation_data) 
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            self.logger.error(f"Failed to parse validation LLM output: {str(e)}. Output: {full_llm_response[:500]}")
            raise HTTPException(status_code=500, detail="LLM generated invalid validation data.")

        await self._log_operation({
            "timestamp": datetime.now().isoformat(),
            "operation": "dream_validation",
            "request_id": request.id,
            "user_id": request.user_id,
            "success": True,
            "overall_score": validation_result.overall_score
        })
        self.logger.info(f"Idea validation successful for user {request.user_id}.")
        return validation_result

# Instantiate DreamEngine (singleton or managed by DI framework like FastAPI's Depends)
dream_engine_instance = DreamEngine()

# --- API Endpoints ---

@router.post("/process", response_model=GenerationResult, status_code=status.HTTP_201_CREATED)
async def process_dream(
    request_data: DreamRequest, # Changed from 'request' to avoid conflict with FastAPI's Request object
    db=Depends(get_db) # Use existing DB dependency (ensure it's async if needed)
):
    """
    Generate backend code from founder's natural language description.
    MUST follow same pattern as /api/v1/build endpoint.
    """
    logger.info(f"Received /process request for user: {request_data.user_id}, request ID: {request_data.id}")
    try:
        # Main processing logic
        result = await dream_engine_instance.process_founder_input(request_data)
        
        # Success logging (match existing pattern)
        logger.info(f"Dream generation successful for user: {request_data.user_id}, request ID: {request_data.id}")
        
        # Response format matching existing endpoints (GenerationResult model handles this)
        return result
        
    except HTTPException as e: # Re-raise HTTPExceptions to let FastAPI handle them
        logger.error(f"HTTPException in /process for user {request_data.user_id}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error in dream generation (/process) for user {request_data.user_id}: {str(e)}")
        # Log detailed stack trace for unexpected errors
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate code: {str(e)}"
        )

@router.post("/validate", response_model=ValidationResult)
async def validate_idea_endpoint( # Renamed from validate_idea to avoid conflict with method
    request_data: DreamRequest
):
    """Pre-generation validation and analysis of the founder's idea."""
    logger.info(f"Received /validate request for user: {request_data.user_id}, request ID: {request_data.id}")
    try:
        result = await dream_engine_instance.validate_idea(request_data)
        logger.info(f"Idea validation successful for user: {request_data.user_id}")
        return result
    except HTTPException as e:
        logger.error(f"HTTPException in /validate for user {request_data.user_id}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error in idea validation (/validate) for user {request_data.user_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate idea: {str(e)}"
        )

@router.post("/stream") # POST to initiate, then EventSource connects to GET with params
async def stream_generation_post(request_data: DreamRequest, http_request: Request):
    """Initiates the streaming generation process. Client then connects via GET."""
    logger.info(f"Received POST /stream request to initiate for user: {request_data.user_id}, request ID: {request_data.id}")
    # This endpoint could store the request or signal a worker.
    # For simplicity, we'll assume the GET /stream will handle the actual streaming logic based on request_id.
    # Here, we just acknowledge the request to start streaming.
    # The actual streaming will be handled by a GET endpoint that EventSource connects to.
    # This is a common pattern: POST to create/initiate, GET to stream.
    # However, the spec implies the POST itself might be where EventSource connects, which is unusual.
    # Let's assume the client will make a GET request to a /stream endpoint after this POST.
    # Or, if the POST itself should stream, the return type needs to be EventSourceResponse.
    # Given the prompt, it seems the POST itself should return the stream.

    rate_limit_status = await dream_engine_instance.rate_limiter.check_rate_limit(request_data.user_id)
    if rate_limit_status.is_limited:
         # This error won't be streamed as SSE if raised here before EventSourceResponse
         raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again after {rate_limit_status.reset_time}.")

    async def event_generator():
        try:
            async for chunk in dream_engine_instance.generate_code_streaming(request_data):
                if await http_request.is_disconnected():
                    logger.info(f"Client disconnected during stream for request {request_data.id}")
                    break
                yield {"event": "message", "data": chunk.model_dump_json()} # Use model_dump_json for Pydantic v2
        except Exception as e:
            logger.error(f"Error during event_generator for stream {request_data.id}: {str(e)}")
            # Yield a final error message if possible
            error_chunk = StreamingChunk(
                request_id=request_data.id,
                chunk_index=9999, # Ensure it's last
                content=json.dumps({"error": f"Streaming error: {str(e)}"}),
                content_type="error",
                is_final=True
            )
            yield {"event": "message", "data": error_chunk.model_dump_json()}

    return EventSourceResponse(event_generator())


@router.get("/health", response_model=HealthCheckResponse)
async def dream_health_check():
    """Health check matching existing pattern."""
    logger.info("DreamEngine health check requested.")
    provider_status: Dict[str, bool] = {}
    if dream_engine_instance.openai_api_key: provider_status["openai"] = True
    if dream_engine_instance.anthropic_api_key: provider_status["anthropic"] = True
    if dream_engine_instance.google_api_key: provider_status["google"] = True
    
    return HealthCheckResponse(
        status="healthy",
        service="DreamEngine - AI Debugger Factory Extension",
        providers=provider_status
    )

@router.post("/cancel", status_code=status.HTTP_200_OK)
async def cancel_generation(request_body: Dict[str, str]):
    """Endpoint to signal cancellation of an ongoing (streaming) request."""
    # This is conceptual. True cancellation of LLM generation is complex and provider-specific.
    # For now, this might log the intent or manage server-side state if generation is task-based.
    request_id = request_body.get("request_id")
    user_id = request_body.get("user_id")
    logger.info(f"Received cancellation request for ID: {request_id}, user: {user_id}")
    # (Add logic here to stop a streaming task if possible, e.g., by setting a flag)
    # For EventSource, the client closing the connection is the primary way to stop.
    return {"message": f"Cancellation signal received for request {request_id}. If streaming, close connection."}


# --- Integration with main.py ---
# To integrate, add the following to your main.py:
#
# from app.utils.dream_engine import router as dream_router
# app.include_router(dream_router)
#

