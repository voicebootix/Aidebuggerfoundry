import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import base64
import requests

# Set up logger
logger = logging.getLogger(__name__)

class VoiceInputProcessor:
    """
    Voice Input Processor for AI Debugger Factory
    
    This class is responsible for:
    - Converting voice input to text
    - Parsing text into structured prompts
    - Routing prompts to appropriate agents
    """
    
    def __init__(self, voice_api_key: str = None, voice_api_endpoint: str = None):
        """
        Initialize the Voice Input Processor
        
        Args:
            voice_api_key: API key for voice transcription service
            voice_api_endpoint: Endpoint for voice transcription service
        """
        self.voice_api_key = voice_api_key or os.getenv("VOICE_API_KEY")
        self.voice_api_endpoint = voice_api_endpoint or os.getenv("VOICE_API_ENDPOINT", "https://api.openai.com/v1/audio/transcriptions")
        
        # Ensure we have the required credentials
        if not self.voice_api_key:
            logger.warning("Voice API key not provided. Voice transcription may be limited.")
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.voice_api_key:
            return {
                "status": "error",
                "message": "Voice API key not provided",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                return {
                    "status": "error",
                    "message": f"Audio file {audio_file_path} not found",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.voice_api_key}"
            }
            
            with open(audio_file_path, "rb") as audio_file:
                files = {
                    "file": (os.path.basename(audio_file_path), audio_file, "audio/mpeg")
                }
                
                data = {
                    "model": "whisper-1",
                    "response_format": "json"
                }
                
                # Make the API request
                response = requests.post(
                    self.voice_api_endpoint,
                    headers=headers,
                    files=files,
                    data=data
                )
                
                response.raise_for_status()
                result = response.json()
                
                return {
                    "status": "success",
                    "text": result.get("text", ""),
                    "timestamp": datetime.now().isoformat()
                }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {
                "status": "error",
                "message": f"Error transcribing audio: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing audio file: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parse text to determine intent and extract structured prompt
        
        Args:
            text: Transcribed text
            
        Returns:
            Dictionary containing parsed intent and structured prompt
        """
        try:
            # This is a simplified implementation that would be replaced with
            # actual LLM-based intent parsing in a production environment
            
            # Detect build vs debug intent
            is_debug = any(keyword in text.lower() for keyword in [
                "debug", "fix", "issue", "problem", "error", "broken", "not working"
            ])
            
            # Extract title
            title = text.split(".")[0] if "." in text else text[:50] + "..."
            
            # Create structured prompt
            structured_prompt = {
                "title": title,
                "intent": "debug" if is_debug else "build",
                "raw_text": text,
                "parsed_at": datetime.now().isoformat()
            }
            
            # Add additional fields based on intent
            if is_debug:
                structured_prompt["issue_type"] = self._detect_issue_type(text)
                structured_prompt["severity"] = self._detect_severity(text)
            else:
                structured_prompt["features"] = self._extract_features(text)
                structured_prompt["entities"] = self._extract_entities(text)
            
            return {
                "status": "success",
                "intent": "debug" if is_debug else "build",
                "structured_prompt": structured_prompt,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error parsing intent: {str(e)}")
            return {
                "status": "error",
                "message": f"Error parsing intent: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_issue_type(self, text: str) -> str:
        """Detect the type of issue from text"""
        if any(keyword in text.lower() for keyword in ["api", "endpoint", "contract"]):
            return "contract_drift"
        elif any(keyword in text.lower() for keyword in ["build", "ci", "pipeline"]):
            return "broken_build"
        elif any(keyword in text.lower() for keyword in ["test", "unit test", "integration test"]):
            return "test_failure"
        else:
            return "general_issue"
    
    def _detect_severity(self, text: str) -> str:
        """Detect the severity of the issue from text"""
        if any(keyword in text.lower() for keyword in ["critical", "urgent", "emergency", "immediately"]):
            return "critical"
        elif any(keyword in text.lower() for keyword in ["high", "important", "serious"]):
            return "high"
        elif any(keyword in text.lower() for keyword in ["medium", "moderate"]):
            return "medium"
        else:
            return "low"
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract features from text"""
        features = []
        
        # This is a simplified implementation that would be replaced with
        # actual NLP-based feature extraction in a production environment
        
        # Look for common feature indicators
        indicators = ["feature", "functionality", "ability to", "should be able to", "implement"]
        
        for indicator in indicators:
            if indicator in text.lower():
                # Find sentences containing the indicator
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        features.append(sentence.strip())
        
        return features
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        entities = []
        
        # This is a simplified implementation that would be replaced with
        # actual NLP-based entity extraction in a production environment
        
        # Look for common entity indicators
        indicators = ["model", "entity", "data", "table", "object"]
        
        for indicator in indicators:
            if indicator in text.lower():
                # Find sentences containing the indicator
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        entities.append(sentence.strip())
        
        return entities
    
    def route_prompt(self, structured_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a structured prompt to the appropriate agent
        
        Args:
            structured_prompt: Structured prompt
            
        Returns:
            Dictionary containing routing information
        """
        intent = structured_prompt.get("intent", "build")
        
        if intent == "debug":
            target_agent = "DebugBot"
            target_endpoint = "/api/v1/debug"
        else:
            target_agent = "BuildBot"
            target_endpoint = "/api/v1/build"
        
        return {
            "status": "success",
            "target_agent": target_agent,
            "target_endpoint": target_endpoint,
            "prompt": structured_prompt,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_voice_input(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Process voice input from audio file
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing processing results
        """
        # Transcribe audio
        transcription_result = self.transcribe_audio(audio_file_path)
        
        if transcription_result["status"] != "success":
            return transcription_result
        
        transcribed_text = transcription_result["text"]
        
        # Parse intent
        intent_result = self.parse_intent(transcribed_text)
        
        if intent_result["status"] != "success":
            return intent_result
        
        structured_prompt = intent_result["structured_prompt"]
        
        # Route prompt
        routing_result = self.route_prompt(structured_prompt)
        
        return {
            "status": "success",
            "transcribed_text": transcribed_text,
            "structured_prompt": structured_prompt,
            "routing": routing_result,
            "timestamp": datetime.now().isoformat()
        }

class PromptIntentParser:
    """
    Prompt Intent Parser for AI Debugger Factory
    
    This class is responsible for:
    - Parsing text prompts to determine intent
    - Converting unstructured prompts to structured format
    - Extracting key information from prompts
    """
    
    def __init__(self):
        """Initialize the Prompt Intent Parser"""
        pass
    
    def parse_prompt(self, prompt_text: str) -> Dict[str, Any]:
        """
        Parse a text prompt to determine intent and extract structured information
        
        Args:
            prompt_text: The prompt text
            
        Returns:
            Dictionary containing parsed intent and structured prompt
        """
        try:
            # This is a simplified implementation that would be replaced with
            # actual LLM-based intent parsing in a production environment
            
            # Detect build vs debug intent
            is_debug = any(keyword in prompt_text.lower() for keyword in [
                "debug", "fix", "issue", "problem", "error", "broken", "not working"
            ])
            
            # Extract title
            title = prompt_text.split(".")[0] if "." in prompt_text else prompt_text[:50] + "..."
            
            # Create structured prompt
            structured_prompt = {
                "title": title,
                "intent": "debug" if is_debug else "build",
                "raw_text": prompt_text,
                "parsed_at": datetime.now().isoformat()
            }
            
            # Add additional fields based on intent
            if is_debug:
                structured_prompt["issue_type"] = self._detect_issue_type(prompt_text)
                structured_prompt["severity"] = self._detect_severity(prompt_text)
            else:
                structured_prompt["features"] = self._extract_features(prompt_text)
                structured_prompt["entities"] = self._extract_entities(prompt_text)
                structured_prompt["requirements"] = self._extract_requirements(prompt_text)
            
            return {
                "status": "success",
                "intent": "debug" if is_debug else "build",
                "structured_prompt": structured_prompt,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error parsing prompt: {str(e)}")
            return {
                "status": "error",
                "message": f"Error parsing prompt: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_issue_type(self, text: str) -> str:
        """Detect the type of issue from text"""
        if any(keyword in text.lower() for keyword in ["api", "endpoint", "contract"]):
            return "contract_drift"
        elif any(keyword in text.lower() for keyword in ["build", "ci", "pipeline"]):
            return "broken_build"
        elif any(keyword in text.lower() for keyword in ["test", "unit test", "integration test"]):
            return "test_failure"
        else:
            return "general_issue"
    
    def _detect_severity(self, text: str) -> str:
        """Detect the severity of the issue from text"""
        if any(keyword in text.lower() for keyword in ["critical", "urgent", "emergency", "immediately"]):
            return "critical"
        elif any(keyword in text.lower() for keyword in ["high", "important", "serious"]):
            return "high"
        elif any(keyword in text.lower() for keyword in ["medium", "moderate"]):
            return "medium"
        else:
            return "low"
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract features from text"""
        features = []
        
        # This is a simplified implementation that would be replaced with
        # actual NLP-based feature extraction in a production environment
        
        # Look for common feature indicators
        indicators = ["feature", "functionality", "ability to", "should be able to", "implement"]
        
        for indicator in indicators:
            if indicator in text.lower():
                # Find sentences containing the indicator
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        features.append(sentence.strip())
        
        return features
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        entities = []
        
        # This is a simplified implementation that would be replaced with
        # actual NLP-based entity extraction in a production environment
        
        # Look for common entity indicators
        indicators = ["model", "entity", "data", "table", "object"]
        
        for indicator in indicators:
            if indicator in text.lower():
                # Find sentences containing the indicator
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        entities.append(sentence.strip())
        
        return entities
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements from text"""
        requirements = []
        
        # This is a simplified implementation that would be replaced with
        # actual NLP-based requirement extraction in a production environment
        
        # Look for common requirement indicators
        indicators = ["must", "should", "need", "require", "has to"]
        
        for indicator in indicators:
            if indicator in text.lower():
                # Find sentences containing the indicator
                sentences = text.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        requirements.append(sentence.strip())
        
        return requirements
    
    def enhance_prompt(self, prompt_text: str) -> Dict[str, Any]:
        """
        Enhance a prompt with additional context and structure
        
        Args:
            prompt_text: The prompt text
            
        Returns:
            Dictionary containing enhanced prompt
        """
        # Parse the prompt first
        parse_result = self.parse_prompt(prompt_text)
        
        if parse_result["status"] != "success":
            return parse_result
        
        structured_prompt = parse_result["structured_prompt"]
        
        # Enhance the prompt based on intent
        if structured_prompt["intent"] == "debug":
            # Add debugging context
            structured_prompt["suggested_fixes"] = self._suggest_fixes(prompt_text)
            structured_prompt["related_components"] = self._identify_related_components(prompt_text)
        else:
            # Add building context
            structured_prompt["suggested_architecture"] = self._suggest_architecture(prompt_text)
            structured_prompt["tech_stack"] = self._suggest_tech_stack(prompt_text)
        
        return {
            "status": "success",
            "enhanced_prompt": structured_prompt,
            "timestamp": datetime.now().isoformat()
        }
    
    def _suggest_fixes(self, text: str) -> List[str]:
        """Suggest fixes based on the issue description"""
        # This would be replaced with actual LLM-based suggestion generation
        return [
            "Check for syntax errors in the code",
            "Verify API contract compliance",
            "Run tests to identify failing components"
        ]
    
    def _identify_related_components(self, text: str) -> List[str]:
        """Identify components related to the issue"""
        # This would be replaced with actual component identification logic
        components = []
        
        if "api" in text.lower():
            components.append("API Layer")
        if "database" in text.lower() or "db" in text.lower():
            components.append("Database Layer")
        if "frontend" in text.lower() or "ui" in text.lower():
            components.append("Frontend")
        if "test" in text.lower():
            components.append("Test Suite")
        
        return components or ["Unknown"]
    
    def _suggest_architecture(self, text: str) -> str:
        """Suggest architecture based on the prompt"""
        # This would be replaced with actual architecture suggestion logic
        if "microservice" in text.lower():
            return "Microservices Architecture"
        elif "serverless" in text.lower():
            return "Serverless Architecture"
        else:
            return "Monolithic Architecture"
    
    def _suggest_tech_stack(self, text: str) -> Dict[str, str]:
        """Suggest tech stack based on the prompt"""
        # This would be replaced with actual tech stack suggestion logic
        tech_stack = {
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "frontend": "React",
            "deployment": "Docker"
        }
        
        if "node" in text.lower() or "javascript" in text.lower():
            tech_stack["backend"] = "Node.js/Express"
        
        if "mongo" in text.lower() or "nosql" in text.lower():
            tech_stack["database"] = "MongoDB"
        
        if "vue" in text.lower():
            tech_stack["frontend"] = "Vue.js"
        elif "angular" in text.lower():
            tech_stack["frontend"] = "Angular"
        
        return tech_stack

# Create singleton instances
voice_processor = VoiceInputProcessor()
prompt_parser = PromptIntentParser()

def process_voice_input(audio_file_path: str) -> Dict[str, Any]:
    """
    Process voice input from audio file
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Dictionary containing processing results
    """
    return voice_processor.process_voice_input(audio_file_path)

def parse_prompt(prompt_text: str) -> Dict[str, Any]:
    """
    Parse a text prompt to determine intent and extract structured information
    
    Args:
        prompt_text: The prompt text
        
    Returns:
        Dictionary containing parsed intent and structured prompt
    """
    return prompt_parser.parse_prompt(prompt_text)

def enhance_prompt(prompt_text: str) -> Dict[str, Any]:
    """
    Enhance a prompt with additional context and structure
    
    Args:
        prompt_text: The prompt text
        
    Returns:
        Dictionary containing enhanced prompt
    """
    return prompt_parser.enhance_prompt(prompt_text)
