"""
Voice Processor - Production OpenAI Whisper Integration
Handles voice transcription and text-to-speech conversion
Enhanced with error handling and audio format optimization
"""

import asyncio
import openai
import io
import base64
import tempfile
import os
from typing import Dict, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class VoiceProcessingResult:
    success: bool
    transcription: Optional[str]
    confidence: Optional[float]
    processing_time: float
    error_message: Optional[str]

class VoiceProcessor:
    """Production-ready voice processing with OpenAI Whisper"""
    
    def __init__(self, openai_api_key: str):
        self.client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
        self.max_file_size = 25 * 1024 * 1024
        self._initialized = False 
        
    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "webm") -> VoiceProcessingResult:
        """Transcribe audio using OpenAI Whisper"""
        
        start_time = datetime.now()
        
        if not self._initialized:
            return VoiceProcessingResult(
                success=False,
                transcription=None,
                confidence=None,
                processing_time=0,
                error_message="Voice processor not initialized"
            )
        
        try:
            # Validate audio format
            if not audio_format.startswith('.'):
                audio_format = f'.{audio_format}'
            
            if audio_format not in self.supported_formats:
                return VoiceProcessingResult(
                    success=False,
                    transcription=None,
                    confidence=None,
                    processing_time=0,
                    error_message=f"Unsupported audio format: {audio_format}"
                )
            
            # ✅ FIX: Add minimum file size validation
            if len(audio_data) < 1000:  # Less than 1KB
                return VoiceProcessingResult(
                    success=False,
                    transcription=None,
                    confidence=None,
                    processing_time=0,
                    error_message="Audio file too small - minimum 1KB required"
                )
            
            # Validate maximum file size
            if len(audio_data) > self.max_file_size:
                return VoiceProcessingResult(
                    success=False,
                    transcription=None,
                    confidence=None,
                    processing_time=0,
                    error_message=f"Audio file too large: {len(audio_data)} bytes (max: {self.max_file_size})"
                )
            
            # ✅ FIX: Add empty file check
            if len(audio_data) == 0:
                return VoiceProcessingResult(
                    success=False,
                    transcription=None,
                    confidence=None,
                    processing_time=0,
                    error_message="Audio file is empty"
                )
            
            # Create temporary file for OpenAI API
            with tempfile.NamedTemporaryFile(suffix=audio_format, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Call OpenAI Whisper API
                with open(temp_file_path, 'rb') as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="json"
                    )
                
                # Extract transcription and confidence
                transcription = response.text if hasattr(response, 'text') else ""
                confidence = getattr(response, 'confidence', None)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return VoiceProcessingResult(
                    success=True,
                    transcription=transcription,
                    confidence=confidence,
                    processing_time=processing_time,
                    error_message=None
                )
                
            except openai.APIError as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                error_msg = f"OpenAI API error: {str(e)}"
                self.logger.error(error_msg)
                
                return VoiceProcessingResult(
                    success=False,
                    transcription=None,
                    confidence=None,
                    processing_time=processing_time,
                    error_message=error_msg
                )
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Voice processing error: {str(e)}"
            self.logger.error(error_msg)
            
            return VoiceProcessingResult(
                success=False,
                transcription=None,
                confidence=None,
                processing_time=processing_time,
                error_message=error_msg
            )
            
    async def initialize(self):
        """Initialize voice processor with proper test audio"""
        try:
            if not self.client.api_key:
                self.logger.warning("OpenAI API key not provided for voice processing")
                return False
            
            # ✅ FIX: Create valid test audio (1 second of silence in WAV format)
            sample_rate = 16000  # 16kHz for Whisper
            duration = 1.0  # 1 second
            num_samples = int(sample_rate * duration)
            
            # Create proper WAV file with header
            import struct
            
            # WAV file header (44 bytes)
            wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                b'RIFF',           # ChunkID
                36 + num_samples * 2,  # ChunkSize
                b'WAVE',           # Format
                b'fmt ',           # Subchunk1ID
                16,                # Subchunk1Size (PCM)
                1,                 # AudioFormat (PCM)
                1,                 # NumChannels (mono)
                sample_rate,       # SampleRate
                sample_rate * 2,   # ByteRate
                2,                 # BlockAlign
                16,                # BitsPerSample
                b'data',           # Subchunk2ID
                num_samples * 2    # Subchunk2Size
            )
            
            # Audio data (silence)
            audio_data = b'\x00' * (num_samples * 2)  # 16-bit samples
            test_audio = wav_header + audio_data
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(test_audio)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="json"
                    )
                
                # ✅ FIX: Don't ignore any API errors
                self._initialized = True
                self.logger.info("Voice processor initialized successfully")
                return True
                
            except openai.APIError as e:
                self.logger.error(f"Voice API test failed: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Voice processor test failed: {e}")
                return False
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            self.logger.error(f"Voice processor initialization failed: {e}")
            return False
    
    async def transcribe_base64_audio(self, base64_audio: str, audio_format: str = "webm") -> VoiceProcessingResult:
        """Transcribe base64-encoded audio"""
        
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            
            # Process with standard transcription method
            return await self.transcribe_audio(audio_data, audio_format)
            
        except Exception as e:
            return VoiceProcessingResult(
                success=False,
                transcription=None,
                confidence=None,
                processing_time=0,
                error_message=f"Base64 decoding error: {str(e)}"
            )
    
    async def generate_speech(self, text: str, voice: str = "alloy") -> Optional[bytes]:
        """Generate speech from text using OpenAI TTS"""
        
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Speech generation error: {str(e)}")
            return None
    
    def validate_audio_input(self, audio_data: bytes, audio_format: str) -> Dict[str, Any]:
        """Validate audio input parameters"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check format
        if not audio_format.startswith('.'):
            audio_format = f'.{audio_format}'
        
        if audio_format not in self.supported_formats:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Unsupported format: {audio_format}")
        
        # Check size
        if len(audio_data) > self.max_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"File too large: {len(audio_data)} bytes")
        
        if len(audio_data) < 1000:  # Less than 1KB
            validation_result["warnings"].append("Audio file seems very small")
        
        return validation_result

# Global instance removed - all voice processing goes through ServiceManager
# Use service_manager.voice_processor instead of importing this module's instance
# This ensures proper initialization and prevents 400 errors from uninitialized instances

