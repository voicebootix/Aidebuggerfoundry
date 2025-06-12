import json
import logging
import os
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

from app.config import settings

# Set up logger
logger = logging.getLogger(__name__)

class ContractGenerator:
    """
    API Contract Generator for AI Debugger Factory
    
    This class is responsible for generating API contracts from structured product prompts.
    It follows the contract-first design philosophy, ensuring that all generated code
    adheres to the contract derived from the original prompt intent.
    """
    
    def __init__(self):
        """Initialize the contract generator"""
        self.contract_file_path = settings.CONTRACT_FILE_PATH
        self.prompt_log_path = settings.PROMPT_LOG_PATH
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.contract_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.prompt_log_path), exist_ok=True)
    
    def generate_api_contract(self, prompt: str) -> Dict[str, Any]:
        """
        Generate an API contract from a structured product prompt
        
        Args:
            prompt: The structured product prompt
            
        Returns:
            A dictionary containing the API contract
        """
        logger.info("Generating API contract from prompt")
        
        # Parse the prompt to extract key requirements
        requirements = self._extract_requirements(prompt)
        
        # Generate endpoints based on requirements
        endpoints = self._generate_endpoints(requirements)
        
        # Generate schemas based on requirements
        schemas = self._generate_schemas(requirements)
        
        # Create the contract
        contract = {
            "info": {
                "title": requirements.get("title", "Generated API"),
                "version": "1.0.0",
                "description": requirements.get("description", "API generated from prompt")
            },
            "endpoints": endpoints,
            "schemas": schemas,
            "requirements": requirements,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save the contract to file
        self._save_contract(contract)
        
        return contract
    
    def sync_contract(self, contract: Dict[str, Any], code_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Sync the API contract with generated code files
        
        Args:
            contract: The API contract
            code_files: Dictionary of generated code files
            
        Returns:
            Updated API contract with code mappings
        """
        logger.info("Syncing API contract with generated code")
        
        # Add code mappings to the contract
        contract["code_mappings"] = {}
        
        # Map endpoints to code files
        for endpoint in contract["endpoints"]:
            path = endpoint["path"]
            method = endpoint["method"]
            endpoint_key = f"{method}:{path}"
            
            # Find the code file that implements this endpoint
            for file_path, content in code_files.items():
                if self._file_implements_endpoint(file_path, content, path, method):
                    if endpoint_key not in contract["code_mappings"]:
                        contract["code_mappings"][endpoint_key] = []
                    
                    contract["code_mappings"][endpoint_key].append(file_path)
        
        # Map schemas to code files
        for schema_name, schema in contract["schemas"].items():
            # Find the code file that implements this schema
            for file_path, content in code_files.items():
                if self._file_implements_schema(file_path, content, schema_name):
                    if schema_name not in contract["code_mappings"]:
                        contract["code_mappings"][schema_name] = []
                    
                    contract["code_mappings"][schema_name].append(file_path)
        
        # Update the contract file
        self._save_contract(contract)
        
        return contract
    
    def verify_contract_compliance(self, contract: Dict[str, Any], code_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Verify that generated code complies with the API contract
        
        Args:
            contract: The API contract
            code_files: Dictionary of generated code files
            
        Returns:
            Verification results
        """
        logger.info("Verifying contract compliance")
        
        results = {
            "compliant": True,
            "issues": [],
            "warnings": [],
            "coverage": {
                "endpoints": 0,
                "schemas": 0
            }
        }
        
        # Check endpoint implementation
        total_endpoints = len(contract["endpoints"])
        implemented_endpoints = 0
        
        for endpoint in contract["endpoints"]:
            path = endpoint["path"]
            method = endpoint["method"]
            endpoint_key = f"{method}:{path}"
            
            # Check if this endpoint is implemented
            implemented = False
            for file_path, content in code_files.items():
                if self._file_implements_endpoint(file_path, content, path, method):
                    implemented = True
                    break
            
            if implemented:
                implemented_endpoints += 1
            else:
                results["compliant"] = False
                results["issues"].append({
                    "type": "missing_endpoint",
                    "endpoint": endpoint_key,
                    "description": f"Endpoint {method} {path} is not implemented"
                })
        
        # Check schema implementation
        total_schemas = len(contract["schemas"])
        implemented_schemas = 0
        
        for schema_name, schema in contract["schemas"].items():
            # Check if this schema is implemented
            implemented = False
            for file_path, content in code_files.items():
                if self._file_implements_schema(file_path, content, schema_name):
                    implemented = True
                    break
            
            if implemented:
                implemented_schemas += 1
            else:
                results["compliant"] = False
                results["issues"].append({
                    "type": "missing_schema",
                    "schema": schema_name,
                    "description": f"Schema {schema_name} is not implemented"
                })
        
        # Calculate coverage
        if total_endpoints > 0:
            results["coverage"]["endpoints"] = implemented_endpoints / total_endpoints
        
        if total_schemas > 0:
            results["coverage"]["schemas"] = implemented_schemas / total_schemas
        
        return results
    
    def _extract_requirements(self, prompt: str) -> Dict[str, Any]:
        """
        Extract key requirements from a structured product prompt
        
        Args:
            prompt: The structured product prompt
            
        Returns:
            Dictionary of requirements
        """
        # This is a simplified implementation that would be replaced with
        # actual LLM-based extraction in a production environment
        
        # Extract title
        title_match = re.search(r"(?:title|name|project):\s*([^\n]+)", prompt, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Generated API"
        
        # Extract description
        desc_match = re.search(r"(?:description|about):\s*([^\n]+)", prompt, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else "API generated from prompt"
        
        # Extract entities (simplified)
        entities = []
        entity_matches = re.finditer(r"(?:entity|model|data):\s*([^\n]+)", prompt, re.IGNORECASE)
        for match in entity_matches:
            entities.append(match.group(1).strip())
        
        # Extract endpoints (simplified)
        endpoints = []
        endpoint_matches = re.finditer(r"(?:endpoint|api|route):\s*([^\n]+)", prompt, re.IGNORECASE)
        for match in endpoint_matches:
            endpoints.append(match.group(1).strip())
        
        # Extract features (simplified)
        features = []
        feature_matches = re.finditer(r"(?:feature|functionality):\s*([^\n]+)", prompt, re.IGNORECASE)
        for match in feature_matches:
            features.append(match.group(1).strip())
        
        return {
            "title": title,
            "description": description,
            "entities": entities,
            "endpoints": endpoints,
            "features": features,
            "raw_prompt": prompt
        }
    
    def _generate_endpoints(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate API endpoints based on requirements
        
        Args:
            requirements: Dictionary of requirements
            
        Returns:
            List of endpoint definitions
        """
        # This is a simplified implementation that would be replaced with
        # actual LLM-based generation in a production environment
        
        endpoints = []
        
        # Generate CRUD endpoints for each entity
        for entity in requirements.get("entities", []):
            # Normalize entity name
            entity_name = entity.lower().strip()
            entity_plural = f"{entity_name}s"  # Simplified pluralization
            
            # GET all
            endpoints.append({
                "path": f"/api/{entity_plural}",
                "method": "GET",
                "description": f"Get all {entity_plural}",
                "parameters": [],
                "responses": {
                    "200": {
                        "description": f"List of {entity_plural}",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": f"#/components/schemas/{entity_name.capitalize()}"
                                    }
                                }
                            }
                        }
                    }
                }
            })
            
            # GET by ID
            endpoints.append({
                "path": f"/api/{entity_plural}/{{id}}",
                "method": "GET",
                "description": f"Get {entity_name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": f"{entity_name.capitalize()} found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{entity_name.capitalize()}"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": f"{entity_name.capitalize()} not found"
                    }
                }
            })
            
            # POST
            endpoints.append({
                "path": f"/api/{entity_plural}",
                "method": "POST",
                "description": f"Create a new {entity_name}",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{entity_name.capitalize()}Create"
                            }
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": f"{entity_name.capitalize()} created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{entity_name.capitalize()}"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            })
            
            # PUT
            endpoints.append({
                "path": f"/api/{entity_plural}/{{id}}",
                "method": "PUT",
                "description": f"Update {entity_name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{entity_name.capitalize()}Update"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": f"{entity_name.capitalize()} updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{entity_name.capitalize()}"
                                }
                            }
                        }
                    },
                    "404": {
                        "description": f"{entity_name.capitalize()} not found"
                    },
                    "400": {
                        "description": "Invalid input"
                    }
                }
            })
            
            # DELETE
            endpoints.append({
                "path": f"/api/{entity_plural}/{{id}}",
                "method": "DELETE",
                "description": f"Delete {entity_name} by ID",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "204": {
                        "description": f"{entity_name.capitalize()} deleted"
                    },
                    "404": {
                        "description": f"{entity_name.capitalize()} not found"
                    }
                }
            })
        
        # Add custom endpoints from requirements
        for endpoint_desc in requirements.get("endpoints", []):
            # This would be replaced with actual LLM-based parsing in a production environment
            # For now, just add a placeholder endpoint
            endpoints.append({
                "path": f"/api/custom/{len(endpoints)}",
                "method": "GET",
                "description": endpoint_desc,
                "parameters": [],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            })
        
        return endpoints
    
    def _generate_schemas(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate API schemas based on requirements
        
        Args:
            requirements: Dictionary of requirements
            
        Returns:
            Dictionary of schema definitions
        """
        # This is a simplified implementation that would be replaced with
        # actual LLM-based generation in a production environment
        
        schemas = {}
        
        # Generate schemas for each entity
        for entity in requirements.get("entities", []):
            # Normalize entity name
            entity_name = entity.lower().strip()
            entity_capitalized = entity_name.capitalize()
            
            # Base schema
            schemas[entity_capitalized] = {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"}
                },
                "required": ["id", "name"]
            }
            
            # Create schema (without ID)
            schemas[f"{entity_capitalized}Create"] = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name"]
            }
            
            # Update schema (without ID)
            schemas[f"{entity_capitalized}Update"] = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        
        return schemas
    
    def _save_contract(self, contract: Dict[str, Any]) -> None:
        """
        Save the API contract to file
        
        Args:
            contract: The API contract
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.contract_file_path), exist_ok=True)
        
        # Save the contract
        with open(self.contract_file_path, "w") as f:
            json.dump(contract, f, indent=2)
        
        logger.info(f"API contract saved to {self.contract_file_path}")
    
    def _file_implements_endpoint(self, file_path: str, content: str, path: str, method: str) -> bool:
        """
        Check if a file implements a specific endpoint
        
        Args:
            file_path: Path to the file
            content: Content of the file
            path: Endpoint path
            method: HTTP method
            
        Returns:
            True if the file implements the endpoint, False otherwise
        """
        # This is a simplified implementation that would be replaced with
        # more sophisticated parsing in a production environment
        
        # Normalize path and method for comparison
        path = path.lower()
        method = method.upper()
        
        # Check if the file is a route file
        if "route" in file_path or "api" in file_path:
            # Check if the file contains the path and method
            path_pattern = re.escape(path).replace("\\{", "{").replace("\\}", "}")
            method_pattern = f"{method}\\s*\\("
            
            path_match = re.search(path_pattern, content, re.IGNORECASE)
            method_match = re.search(method_pattern, content, re.IGNORECASE)
            
            return path_match is not None and method_match is not None
        
        return False
    
    def _file_implements_schema(self, file_path: str, content: str, schema_name: str) -> bool:
        """
        Check if a file implements a specific schema
        
        Args:
            file_path: Path to the file
            content: Content of the file
            schema_name: Name of the schema
            
        Returns:
            True if the file implements the schema, False otherwise
        """
        # This is a simplified implementation that would be replaced with
        # more sophisticated parsing in a production environment
        
        # Check if the file is a model file
        if "model" in file_path or "schema" in file_path:
            # Check if the file contains the schema name
            class_pattern = f"class\\s+{schema_name}"
            pydantic_pattern = f"class\\s+{schema_name}\\s*\\(\\s*BaseModel\\s*\\)"
            
            class_match = re.search(class_pattern, content, re.IGNORECASE)
            pydantic_match = re.search(pydantic_pattern, content, re.IGNORECASE)
            
            return class_match is not None or pydantic_match is not None
        
        return False

# Create a singleton instance
contract_generator = ContractGenerator()

def generate_api_contract(prompt: str) -> Dict[str, Any]:
    """
    Generate an API contract from a structured product prompt
    
    Args:
        prompt: The structured product prompt
        
    Returns:
        A dictionary containing the API contract
    """
    return contract_generator.generate_api_contract(prompt)

def sync_contract(contract: Dict[str, Any], code_files: Dict[str, str]) -> Dict[str, Any]:
    """
    Sync the API contract with generated code files
    
    Args:
        contract: The API contract
        code_files: Dictionary of generated code files
        
    Returns:
        Updated API contract with code mappings
    """
    return contract_generator.sync_contract(contract, code_files)

def verify_contract_compliance(contract: Dict[str, Any], code_files: Dict[str, str]) -> Dict[str, Any]:
    """
    Verify that generated code complies with the API contract
    
    Args:
        contract: The API contract
        code_files: Dictionary of generated code files
        
    Returns:
        Verification results
    """
    return contract_generator.verify_contract_compliance(contract, code_files)
