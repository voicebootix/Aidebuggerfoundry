
"""
VOICE PROCESSOR - AI DEBUGGER FACTORY
CRITICAL FIX: IndentationError resolved + Production ready
"""

import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import UploadFile
import openai
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

class VoiceInputProcessor:
    """Production-ready voice input processor with OpenAI Whisper integration"""
    
    def __init__(self):
        """Initialize the voice processor with proper error handling"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        # Configuration
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit
        self.supported_formats = [
            "audio/webm", "audio/mp3", "audio/mpeg", "audio/wav", 
            "audio/m4a", "audio/ogg", "video/webm"
        ]
        self.supported_extensions = ["webm", "mp3", "wav", "m4a", "ogg"]
        
        # Initialize OpenAI client if API key is available
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            logger.warning("⚠️ OPENAI_API_KEY not found - voice features disabled")
    
    async def process_voice_file(self, audio_file: UploadFile) -> Dict[str, Any]:
        """
        Main entry point for voice file processing
        
        Args:
            audio_file: Uploaded audio file from FastAPI
            
        Returns:
            Dict with processing results or error information
        """
        try:
            logger.info(f"🎤 Processing voice file: {audio_file.filename}")
            
            # Validate the audio file first
            validation_result = await self._validate_audio_file(audio_file)
            if not validation_result["valid"]:
                logger.error(f"❌ Audio validation failed: {validation_result['error']}")
                return {
                    "status": "error",
                    "message": validation_result["error"],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Create temporary file for processing
            temp_file_path = None
            try:
                # Read and save audio file to temporary location
                audio_content = await audio_file.read()
                
                # Create temporary file with appropriate extension
                file_extension = self._get_file_extension(audio_file.filename)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
                    temp_file.write(audio_content)
                    temp_file_path = temp_file.name
                
                logger.info(f"📁 Created temp file: {temp_file_path}")
                
                # Transcribe audio using OpenAI Whisper API
                transcription_result = await self._transcribe_audio(temp_file_path)
                
                if not transcription_result["success"]:
                    logger.error(f"❌ Transcription failed: {transcription_result['error']}")
                    return {
                        "status": "error",
                        "message": transcription_result["error"],
                        "timestamp": datetime.now().isoformat()
                    }
                
                transcribed_text = transcription_result["text"]
                logger.info(f"✅ Transcription successful: {len(transcribed_text)} characters")
                
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
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info(f"🧹 Cleaned up temp file: {temp_file_path}")
                    
        except Exception as e:
            logger.error(f"❌ Voice processing error: {str(e)}")
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
                "error": "Voice transcription service not configured. Missing OPENAI_API_KEY."
            }
        
        # Check file size
        if hasattr(audio_file, 'size') and audio_file.size and audio_file.size > self.max_file_size:
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            }
        
        # Check content type
        if audio_file.content_type and audio_file.content_type not in self.supported_formats:
            logger.warning(f"⚠️ Unknown content type: {audio_file.content_type}, proceeding anyway")
        
        # Check filename extension
        if audio_file.filename:
            ext = audio_file.filename.lower().split('.')[-1] if '.' in audio_file.filename else ''
            if ext and ext not in self.supported_extensions:
                return {
                    "valid": False,
                    "error": f"Unsupported file type. Supported: {', '.join(self.supported_extensions)}"
                }
        
        return {"valid": True}
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """Extract file extension from filename"""
        if not filename:
            return "webm"  # Default extension
        
        ext = filename.lower().split('.')[-1] if '.' in filename else 'webm'
        return ext if ext in self.supported_extensions else "webm"
    
    async def _transcribe_audio(self, file_path: str) -> Dict[str, Any]:
        """Real audio transcription using OpenAI Whisper API"""
        
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not initialized. Check your API key."
            }
        
        try:
            start_time = datetime.now()
            
            logger.info(f"🔄 Starting transcription for: {file_path}")
            
            # Open audio file and send to Whisper
            with open(file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Get transcribed text
            transcribed_text = transcription.strip() if transcription else ""
            
            if not transcribed_text:
                return {
                    "success": False,
                    "error": "No speech detected in audio file"
                }
            
            logger.info(f"✅ Transcription completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "text": transcribed_text,
                "processing_time": processing_time
            }
            
        except openai.BadRequestError as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
            return {
                "success": False,
                "error": "Audio file format not supported or file corrupted. Please try with a shorter audio file."
            }
        except Exception as e:
            logger.error(f"❌ Transcription error: {str(e)}")
            return {
                "success": False,
                "error": f"Transcription failed: {str(e)}"
            }
    
    async def _structure_transcription(self, text: str) -> Dict[str, Any]:
        """Parse transcribed text and structure it for the DreamEngine"""
        
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
            "confidence": self._calculate_confidence(text),
            "raw_text": text
        }
        
        logger.info(f"📝 Structured prompt: intent={intent}, type={project_type}")
        
        return structured_prompt
    
    def _detect_project_type(self, text: str) -> str:
        """Detect the type of project from transcribed text"""
        
        web_keywords = ['website', 'web app', 'frontend', 'backend', 'full stack']
        mobile_keywords = ['mobile app', 'ios', 'android', 'react native', 'flutter']
        api_keywords = ['api', 'rest api', 'graphql', 'microservice', 'backend']
        desktop_keywords = ['desktop app', 'gui', 'tkinter', 'pyqt', 'electron']
        data_keywords = ['data analysis', 'machine learning', 'ai', 'dashboard', 'visualization']
        
        if any(keyword in text for keyword in web_keywords):
            return "web_application"
        elif any(keyword in text for keyword in mobile_keywords):
            return "mobile_application"
        elif any(keyword in text for keyword in api_keywords):
            return "api_service"
        elif any(keyword in text for keyword in desktop_keywords):
            return "desktop_application"
        elif any(keyword in text for keyword in data_keywords):
            return "data_project"
        else:
            return "general_application"
    
    def _detect_technologies(self, text: str) -> list:
        """Extract technology mentions from transcribed text"""
        
        tech_map = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'vue', 'angular'],
            'database': ['database', 'mysql', 'postgresql', 'mongo', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
            'mobile': ['react native', 'flutter', 'ios', 'android', 'swift', 'kotlin']
        }
        
        detected_techs = []
        
        for category, keywords in tech_map.items():
            if any(keyword in text for keyword in keywords):
                detected_techs.append(category)
        
        return detected_techs
    
    def _extract_features(self, text: str) -> list:
        """Extract feature requirements from transcribed text"""
        
        # Simple feature extraction based on common patterns
        features = []
        
        feature_patterns = {
            'authentication': ['login', 'signup', 'authentication', 'user accounts'],
            'payment': ['payment', 'stripe', 'paypal', 'billing', 'subscription'],
            'real_time': ['real time', 'live updates', 'websockets', 'chat'],
            'file_upload': ['file upload', 'image upload', 'file sharing'],
            'search': ['search', 'filter', 'query'],
            'notifications': ['notifications', 'email alerts', 'push notifications']
        }
        
        text_lower = text.lower()
        
        for feature, keywords in feature_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                features.append(feature)
        
        return features
    
    def _generate_title(self, text: str) -> str:
        """Generate a project title from transcribed text"""
        
        # Take first sentence or first 50 characters
        sentences = text.split('. ')
        
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

