from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime

class PromptOptions(BaseModel):
    """Options for prompt processing"""
    use_database: bool = True
    generate_tests: bool = True
    modular_structure: bool = False
    include_frontend: bool = False
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"

class PromptRequest(BaseModel):
    """Request model for prompt processing"""
    id: UUID = Field(default_factory=uuid4)
    title: str
    prompt: str
    options: Optional[PromptOptions] = Field(default_factory=PromptOptions)
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v
    
    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v

class PromptResponse(BaseModel):
    """Response model for prompt processing"""
    id: UUID
    title: str
    status: str
    message: str
    contract: Dict[str, Any]
    files_generated: List[str]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "E-commerce API",
                "status": "success",
                "message": "Backend code generated successfully",
                "contract": {
                    "endpoints": [
                        {
                            "path": "/api/products",
                            "method": "GET",
                            "description": "Get all products",
                            "parameters": [],
                            "responses": {
                                "200": {
                                    "description": "List of products",
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "integer"},
                                                        "name": {"type": "string"},
                                                        "price": {"type": "number"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "schemas": {
                        "Product": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "price": {"type": "number"}
                            }
                        }
                    }
                },
                "files_generated": [
                    "app/main.py",
                    "app/models/product.py",
                    "app/routes/product.py",
                    "tests/test_product.py"
                ],
                "timestamp": "2025-06-12T06:52:31.123456"
            }
        }

class VoicePromptRequest(BaseModel):
    """Request model for voice prompt processing"""
    id: UUID = Field(default_factory=uuid4)
    audio_file: str
    options: Optional[PromptOptions] = Field(default_factory=PromptOptions)

class VoicePromptResponse(BaseModel):
    """Response model for voice prompt processing"""
    id: UUID
    transcribed_text: str
    structured_prompt: str
    status: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
