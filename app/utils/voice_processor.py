import os
import logging
import tempfile
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import aiofiles
import httpx
from fastapi import UploadFile

# Import your existing logger
from app.utils.logger import setup_logger

logger = setup_logger()

class VoiceInputProcessor:
    """
    Production-ready Voice Input Processor using OpenAI Whisper API
    Integrated with your existing DreamEngine architecture
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.whisper_endpoint = "https://api.openai.com/v1/audio/transcriptions"
        self.max_file_size = 25 * 1024 * 1024  # 25MB OpenAI limit
        self.supported_formats = {
            'audio/webm', 'audio/mp4', 'audio/mpeg', 'audio/mpga', 
            'audio/m4a', 'audio/wav', 'audio/flac'
        }
        
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found. Voice transcription will not work.")
    
    async def process_voice_file(self, audio_file: UploadFile) -> Dict[str, Any]:
        """
        Process uploaded voice file and return transcription + structured analysis
        
        Args:
            audio_file: FastAPI UploadFile object
            
        Returns:
            Dictionary with transcription and structured prompt data
        """
        try:
            # Validate file
            validation_result = await self._validate_audio_file(audio_file)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Create temporary file for processing
            temp_file_path = await self._save_temp_file(audio_file)
            
            try:
                # Transcribe audio using OpenAI Whisper
                transcription_result = await self._transcribe_audio(temp_file_path)
                
                if not transcription_result["success"]:
                    return {
                        "status": "error",
                        "message": transcription_result["error"],
                        "timestamp": datetime.now().isoformat()
                    }
                
                transcribed_text = transcription_result["text"]
                
                # Parse and structure the transcribed text
                structured_result = await self._structure_transcription(transcribed_text)
                
                return {
                    "status": "success",
                    "transcribed_text": transcribed_text,
                    "structured_prompt": structured_result,
                    "processing_time": transcription_result.get("processing_time", 0),
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Voice processing error: {str(e)}")
            return {
                "status": "error",
                "message": f"Voice processing failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _validate_audio_file(self, audio_file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded audio file"""
        
        # Check if API key is available
        if not self.openai_api_key:
            return {
                "valid": False,
                "error": "Voice transcription service not configured. Please contact administrator."
            }
        
        # Check file size
        if hasattr(audio_file, 'size') and audio_file.size > self.max_file_size:
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            }
        
        # Check content type
        if audio_file.content_type and audio_file.content_type not in self.supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported audio format: {audio_file.content_type}"
            }
        
        # Check filename extension
        if audio_file.filename:
            ext = audio_file.filename.lower().split('.')[-1]
            supported_extensions = {'webm', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'flac', 'mp3'}
            if ext not in supported_extensions:
                return {
                    "valid": False,
                    "error": f"Unsupported file extension: .{ext}"
                }
        
        return {"valid": True}
    
    async def _save_temp_file(self, audio_file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        
        # Generate unique temporary filename
        file_ext = "webm"  # Default extension
        if audio_file.filename:
            file_ext = audio_file.filename.split('.')[-1].lower()
        
        temp_file_path = os.path.join(
            tempfile.gettempdir(),
            f"voice_input_{uuid.uuid4()}.{file_ext}"
        )
        
        # Save file content
        async with aiofiles.open(temp_file_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        logger.info(f"Saved temp audio file: {temp_file_path}")
        return temp_file_path
    
    async def _transcribe_audio(self, file_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API"""
        
        start_time = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                
                # Prepare request
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                
                # Read audio file
                async with aiofiles.open(file_path, 'rb') as f:
                    audio_content = await f.read()
                
                # Prepare form data
                files = {
                    'file': (os.path.basename(file_path), audio_content, 'audio/webm'),
                }
                
                data = {
                    'model': 'whisper-1',
                    'response_format': 'json',
                    'language': 'en'  # Can be made configurable
                }
                
                # Make API request
                response = await client.post(
                    self.whisper_endpoint,
                    headers=headers,
                    files=files,
                    data=data
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    result = response.json()
                    transcribed_text = result.get('text', '').strip()
                    
                    if not transcribed_text:
                        return {
                            "success": False,
                            "error": "No speech detected in audio file"
                        }
                    
                    logger.info(f"Transcription successful: {len(transcribed_text)} characters")
                    return {
                        "success": True,
                        "text": transcribed_text,
                        "processing_time": processing_time
                    }
                else:
                    error_msg = f"OpenAI API error: {response.status_code}"
                    try:
                        error_details = response.json()
                        error_msg += f" - {error_details.get('error', {}).get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Transcription request timed out. Please try with a shorter audio file."
            }
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "success": False,
                "error": f"Transcription failed: {str(e)}"
            }
    
    async def _structure_transcription(self, text: str) -> Dict[str, Any]:
        """
        Parse transcribed text and structure it for the DreamEngine
        This uses simple heuristics but could be enhanced with LLM analysis
        """
        
        # Basic intent detection
        build_keywords = [
            'create', 'build', 'make', 'develop', 'generate', 'design', 'implement',
            'application', 'app', 'website', 'api', 'system', 'platform', 'tool'
        ]
        
        debug_keywords = [
            'fix', 'debug', 'error', 'issue', 'problem', 'broken', 'not working',
            'bug', 'crash', 'failing', 'wrong'
        ]
        
        text_lower = text.lower()
        
        # Determine intent
        has_build_intent = any(keyword in text_lower for keyword in build_keywords)
        has_debug_intent = any(keyword in text_lower for keyword in debug_keywords)
        
        if has_debug_intent and not has_build_intent:
            intent = "debug"
        else:
            intent = "build"  # Default to build
        
        # Extract project type hints
        project_type = self._detect_project_type(text_lower)
        
        # Extract technology hints
        tech_hints = self._detect_technologies(text_lower)
        
        # Extract features/requirements
        features = self._extract_features(text)
        
        # Create structured prompt
        structured_prompt = {
            "title": self._generate_title(text),
            "intent": intent,
            "project_type": project_type,
            "technologies": tech_hints,
            "features": features,
            "raw_transcription": text,
            "confidence": self._calculate_confidence(text),
            "processed_at": datetime.now().isoformat()
        }
        
        return structured_prompt
    
    def _detect_project_type(self, text: str) -> Optional[str]:
        """Detect project type from transcribed text"""
        
        type_keywords = {
            "web_api": ["api", "rest", "backend", "server", "endpoint"],
            "web_app": ["website", "web app", "frontend", "dashboard", "portal"],
            "mobile_app": ["mobile", "app", "ios", "android", "phone"],
            "cli_tool": ["command line", "cli", "terminal", "script"],
            "microservice": ["microservice", "service", "distributed"]
        }
        
        for project_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return project_type
        
        return None
    
    def _detect_technologies(self, text: str) -> Dict[str, Optional[str]]:
        """Detect technology preferences from text"""
        
        technologies = {
            "language": None,
            "database": None,
            "framework": None
        }
        
        # Language detection
        language_keywords = {
            "python": ["python", "django", "flask", "fastapi"],
            "javascript": ["javascript", "node", "react", "vue", "angular"],
            "java": ["java", "spring", "springboot"],
            "typescript": ["typescript"],
            "go": ["golang", "go"],
            "rust": ["rust"]
        }
        
        for lang, keywords in language_keywords.items():
            if any(keyword in text for keyword in keywords):
                technologies["language"] = lang
                break
        
        # Database detection
        db_keywords = {
            "postgresql": ["postgres", "postgresql"],
            "mysql": ["mysql"],
            "mongodb": ["mongo", "mongodb"],
            "sqlite": ["sqlite"],
            "redis": ["redis"]
        }
        
        for db, keywords in db_keywords.items():
            if any(keyword in text for keyword in keywords):
                technologies["database"] = db
                break
        
        # Framework detection
        framework_keywords = {
            "fastapi": ["fastapi"],
            "django": ["django"],
            "flask": ["flask"],
            "express": ["express"],
            "react": ["react"],
            "vue": ["vue"]
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in text for keyword in keywords):
                technologies["framework"] = framework
                break
        
        return technologies
    
    def _extract_features(self, text: str) -> list:
        """Extract mentioned features from text"""
        
        feature_keywords = [
            "authentication", "login", "user management", "auth",
            "database", "storage", "data",
            "api", "rest", "endpoint",
            "search", "filter", "sort",
            "upload", "download", "file",
            "notification", "email", "sms",
            "payment", "billing", "subscription",
            "admin", "dashboard", "analytics",
            "security", "encryption", "privacy"
        ]
        
        found_features = []
        text_lower = text.lower()
        
        for feature in feature_keywords:
            if feature in text_lower:
                found_features.append(feature)
        
        return found_features
    
    def _generate_title(self, text: str) -> str:
        """Generate a title from the transcription"""
        
        # Take first sentence or first 50 characters
        sentences = text.split('.')
        if sentences and len(sentences[0].strip()) > 0:
            title = sentences[0].strip()
        else:
            title = text[:50].strip()
        
        # Clean up title
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title or "Voice Project Request"
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text analysis"""
        
        score = 0.5  # Base score
        
        # Length factor
        if len(text) > 100:
            score += 0.2
        elif len(text) > 50:
            score += 0.1
        
        # Technical detail factor
        tech_words = ["api", "database", "authentication", "frontend", "backend", "function"]
        tech_count = sum(1 for word in tech_words if word in text.lower())
        score += min(tech_count * 0.1, 0.3)
        
        # Clarity factor (simple heuristic)
        if len(text.split()) > 10:  # More than 10 words
            score += 0.1
        
        return min(score, 1.0)


# Integration function for your existing voice endpoint
async def process_voice_input_fixed(audio_file: UploadFile) -> Dict[str, Any]:
    """
    Fixed function to replace the one in your existing voice_processor.py
    This integrates directly with your current FastAPI endpoint
    """
    processor = VoiceInputProcessor()
    return await processor.process_voice_file(audio_file)


# Enhanced error handling for the voice endpoint
class VoiceProcessingError(Exception):
    """Custom exception for voice processing errors"""
    def __init__(self, message: str, error_code: str = "VOICE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
