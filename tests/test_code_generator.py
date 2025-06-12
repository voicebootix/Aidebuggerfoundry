import pytest
from app.utils.code_generator import generate_backend_code
from app.models.prompt import PromptOptions


@pytest.fixture
def simple_contract():
    return {
        "endpoints": [
            {"path": "/api/items", "method": "GET"}
        ],
        "schemas": {"Item": {"type": "object", "properties": {"id": {"type": "integer"}}}}
    }


def test_generate_backend_code_with_dict(simple_contract):
    options = {"use_database": False, "modular_structure": False, "generate_tests": True}
    result = generate_backend_code("prompt", simple_contract, options)
    assert "database/db.py" not in result["files_generated"]
    assert result["structure_type"] == "monolithic"
    assert result["tests_generated"] is True


def test_generate_backend_code_with_promptoptions(simple_contract):
    options = PromptOptions(use_database=True, modular_structure=True, generate_tests=False)
    result = generate_backend_code("prompt", simple_contract, options)
    assert "database/db.py" in result["files_generated"]
    assert result["structure_type"] == "modular"
    assert result["tests_generated"] is False
