import logging
import os
from typing import Dict, Any, Union

from app.models.prompt import PromptOptions

# Set up logger
logger = logging.getLogger(__name__)

def setup_logger():
    """Set up and configure logger"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("ai_debugger_factory.log")
        ]
    )
    return logging.getLogger(__name__)

def generate_backend_code(prompt: str, contract: Dict[str, Any], options: Union[Dict[str, Any], PromptOptions]) -> Dict[str, Any]:
    """
    Generate backend code based on a prompt and API contract
    
    Args:
        prompt: The structured product prompt
        contract: The API contract
        options: Code generation options
        
    Returns:
        Dictionary containing generated code information
    """
    logger.info("Generating backend code")
    
    # This is a simplified implementation that would be replaced with
    # actual LLM-based code generation in a production environment
    
    # Extract requirements from the contract
    endpoints = contract.get("endpoints", [])
    schemas = contract.get("schemas", {})
    
    # Normalize options to a dictionary
    if hasattr(options, "dict"):
        options = options.dict()

    # Determine file structure based on options
    modular_structure = options.get("modular_structure", False)
    use_database = options.get("use_database", True)
    generate_tests = options.get("generate_tests", True)
    
    # Generate files
    files_generated = []
    
    # Main app file
    files_generated.append("app/main.py")
    
    # Config file
    files_generated.append("app/config.py")
    
    # Database files if needed
    if use_database:
        files_generated.append("database/db.py")
    
    # Model files
    for schema_name in schemas:
        if modular_structure:
            files_generated.append(f"app/models/{schema_name.lower()}.py")
        else:
            files_generated.append("app/models.py")
            break
    
    # Route files
    if modular_structure:
        # Group endpoints by resource
        resources = {}
        for endpoint in endpoints:
            path = endpoint["path"]
            parts = path.split("/")
            if len(parts) > 2:
                resource = parts[2]  # /api/{resource}/...
                if resource not in resources:
                    resources[resource] = []
                resources[resource].append(endpoint)
        
        # Create route file for each resource
        for resource in resources:
            files_generated.append(f"app/routes/{resource}.py")
    else:
        files_generated.append("app/routes.py")
    
    # Test files
    if generate_tests:
        if modular_structure:
            for resource in resources:
                files_generated.append(f"tests/test_{resource}.py")
        else:
            files_generated.append("tests/test_main.py")
    
    # Return result
    return {
        "files_generated": files_generated,
        "structure_type": "modular" if modular_structure else "monolithic",
        "database_used": use_database,
        "tests_generated": generate_tests
    }
