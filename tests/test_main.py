import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app
from app.models.prompt import PromptRequest, PromptOptions
from app.utils.contract_generator import generate_api_contract

# Create test client
client = TestClient(app)

@pytest.fixture
def sample_prompt_request():
    """Sample prompt request for testing"""
    return {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "title": "E-commerce API",
        "prompt": """
        Create an e-commerce API with the following features:
        - Product catalog with categories
        - User authentication and profiles
        - Shopping cart functionality
        - Order processing and history
        - Payment integration with Stripe
        """,
        "options": {
            "use_database": True,
            "generate_tests": True,
            "modular_structure": True,
            "include_frontend": False,
            "llm_provider": "openai",
            "llm_model": "gpt-4"
        }
    }

@pytest.fixture
def mock_db():
    """Mock database handler"""
    mock = MagicMock()
    mock.save_prompt.return_value = 1
    mock.save_contract.return_value = 1
    mock.save_generated_code.return_value = 1
    mock.save_build_log.return_value = 1
    return mock

def test_root_endpoint():
    """Test the root endpoint serves HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "DreamEngine" in response.text

@patch("app.main.generate_api_contract")
@patch("app.main.generate_backend_code")
@patch("app.main.get_db")
def test_build_from_prompt_success(mock_get_db, mock_generate_backend_code, mock_generate_api_contract, sample_prompt_request, mock_db):
    """Test successful build from prompt"""
    # Setup mocks
    mock_get_db.return_value = mock_db
    
    mock_contract = {
        "endpoints": [
            {
                "path": "/api/products",
                "method": "GET",
                "description": "Get all products"
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
    }
    mock_generate_api_contract.return_value = mock_contract
    
    mock_code_result = {
        "files_generated": [
            "app/main.py",
            "app/models/product.py",
            "app/routes/product.py",
            "tests/test_product.py"
        ]
    }
    mock_generate_backend_code.return_value = mock_code_result
    
    # Create temporary meta directory for testing
    os.makedirs("../../meta", exist_ok=True)
    with open("../../meta/prompt_log.json", "w") as f:
        json.dump({"prompts": []}, f)
    
    # Make request
    response = client.post("/api/v1/build", json=sample_prompt_request)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["title"] == sample_prompt_request["title"]
    assert response.json()["id"] == sample_prompt_request["id"]
    assert "contract" in response.json()
    assert "files_generated" in response.json()
    
    # Verify mocks were called
    mock_generate_api_contract.assert_called_once_with(sample_prompt_request["prompt"])
    expected_options = PromptOptions(**sample_prompt_request["options"])
    mock_generate_backend_code.assert_called_once_with(
        sample_prompt_request["prompt"],
        mock_contract,
        expected_options
    )
    
    # Clean up
    if os.path.exists("../../meta/prompt_log.json"):
        os.remove("../../meta/prompt_log.json")

@patch("app.main.generate_api_contract")
@patch("app.main.get_db")
def test_build_from_prompt_error(mock_get_db, mock_generate_api_contract, sample_prompt_request, mock_db):
    """Test error handling in build from prompt"""
    # Setup mocks
    mock_get_db.return_value = mock_db
    mock_generate_api_contract.side_effect = Exception("Test error")
    
    # Create temporary meta directory for testing
    os.makedirs("../../meta", exist_ok=True)
    with open("../../meta/prompt_log.json", "w") as f:
        json.dump({"prompts": []}, f)
    
    # Make request
    response = client.post("/api/v1/build", json=sample_prompt_request)
    
    # Verify response
    assert response.status_code == 500
    assert "error" in response.json()
    assert "Test error" in response.json()["detail"]
    
    # Clean up
    if os.path.exists("../../meta/prompt_log.json"):
        os.remove("../../meta/prompt_log.json")

def test_prompt_request_validation():
    """Test PromptRequest validation"""
    # Valid request
    valid_request = PromptRequest(
        title="Test API",
        prompt="Create a test API"
    )
    assert valid_request.title == "Test API"
    assert valid_request.prompt == "Create a test API"
    assert isinstance(valid_request.id, UUID)
    assert isinstance(valid_request.options, PromptOptions)
    
    # Invalid request - empty title
    with pytest.raises(ValueError):
        PromptRequest(
            title="",
            prompt="Create a test API"
        )
    
    # Invalid request - empty prompt
    with pytest.raises(ValueError):
        PromptRequest(
            title="Test API",
            prompt=""
        )

def test_contract_generator():
    """Test contract generator"""
    prompt = """
    Create an e-commerce API with the following features:
    - Product catalog with categories
    - User authentication and profiles
    - Shopping cart functionality
    - Order processing and history
    - Payment integration with Stripe
    """
    
    contract = generate_api_contract(prompt)
    
    # Verify contract structure
    assert "info" in contract
    assert "endpoints" in contract
    assert "schemas" in contract
    assert "requirements" in contract
    assert "generated_at" in contract
    
    # Verify endpoints
    assert isinstance(contract["endpoints"], list)
    
    # Verify schemas
    assert isinstance(contract["schemas"], dict)


@patch("app.main.VoiceInputProcessor")
def test_process_voice_success(mock_voice_proc):
    """Test voice endpoint with multipart form"""
    mock_instance = MagicMock()
    mock_instance.process_voice_input.return_value = {
        "status": "success",
        "transcribed_text": "hello world",
        "structured_prompt": {"title": "Test", "intent": "build"},
    }
    mock_voice_proc.return_value = mock_instance

    files = {"audio_file": ("test.wav", b"data", "audio/wav")}
    response = client.post("/api/v1/voice", files=files)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["transcribed_text"] == "hello world"


def test_process_voice_missing_file():
    """Audio file is required"""
    response = client.post("/api/v1/voice")
    assert response.status_code == 422
