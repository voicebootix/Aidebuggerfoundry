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

async def process_voice_input_fixed(audio_file: UploadFile) -> Dict[str, Any]:
    """
    Main voice processing function - replaces the problematic import
    """
    processor = VoiceInputProcessor()
    return await processor.process_voice_file(audio_file)

def parse_prompt(transcribed_text: str) -> Dict[str, Any]:
    """
    Parse transcribed text into structured prompt data
    """
    return {
        "original_text": transcribed_text,
        "processed_text": transcribed_text.strip(),
        "word_count": len(transcribed_text.split()),
        "confidence": 0.8,  # Default confidence
        "language": "en"
    }

def enhance_prompt(prompt_data: Dict[str, Any]) -> str:
    """
    Enhance the parsed prompt for better code generation
    """
    text = prompt_data.get("processed_text", "")
    
    # Add context if the prompt is too short
    if len(text.split()) < 5:
        text = f"Create a simple application that {text}"
    
    # Ensure it's clear it's a development request
    if not any(keyword in text.lower() for keyword in ["create", "build", "develop", "make"]):
        text = f"Build {text}"
    
    return text

class VoiceInputProcessor:
    """Production-ready Voice Input Processor using OpenAI Whisper API"""
    
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
        """Process uploaded voice file and return transcription + structured analysis"""
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
                structured_result = parse_prompt(transcribed_text)
                enhanced_text = enhance_prompt(structured_result)
                
                return {
                    "status": "success",
                    "transcribed_text": enhanced_text,
                    "original_text": transcribed_text,
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
                "error": "Voice transcription service not configured. Please set OPENAI_API_KEY."
            }
        
        # Check file size
        if hasattr(audio_file, 'size') and audio_file.size > self.max_file_size:
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            }
        
        return {"valid": True}
    
    async def _save_temp_file(self, audio_file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        
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
                    'language': 'en'
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
