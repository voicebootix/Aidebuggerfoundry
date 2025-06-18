import json
import logging
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TechnicalSpecification:
    """Technical specification that AI must follow"""
    name: str
    description: str
    acceptance_criteria: List[str]
    testing_method: str
    priority: str  # HIGH, MEDIUM, LOW
    auto_testable: bool

class ContractGenerator:
    """
    API Contract Generator for AI Debugger Factory
    
    This class is responsible for generating API contracts from structured product prompts.
    It follows the contract-first design philosophy, ensuring that all generated code
    adheres to the contract derived from the original prompt intent.
    """
    
    def __init__(self):
        """Initialize the contract generator"""
        self.contract_file_path = "contracts/"
        self.prompt_log_path = "logs/"
        
        # Ensure directories exist
        os.makedirs(self.contract_file_path, exist_ok=True)
        os.makedirs(self.prompt_log_path, exist_ok=True)
    
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
        logger.info("Syncing contract with generated code files")
        
        # Update contract with code mappings
        contract["code_mappings"] = {}
        
        for file_path, content in code_files.items():
            contract["code_mappings"][file_path] = {
                "content_hash": self._generate_content_hash(content),
                "endpoints_implemented": self._extract_endpoints_from_code(content),
                "schemas_implemented": self._extract_schemas_from_code(content)
            }
        
        contract["last_synced"] = datetime.now().isoformat()
        
        # Save updated contract
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
            "coverage": {
                "endpoints": 0.0,
                "schemas": 0.0
            }
        }
        
        # Check endpoint implementation
        total_endpoints = len(contract["endpoints"])
        implemented_endpoints = 0
        
        for endpoint_path, endpoint_spec in contract["endpoints"].items():
            # Check if this endpoint is implemented
            implemented = False
            for file_path, content in code_files.items():
                if self._file_implements_endpoint(file_path, content, endpoint_path):
                    implemented = True
                    break
            
            if implemented:
                implemented_endpoints += 1
            else:
                results["compliant"] = False
                results["issues"].append({
                    "type": "missing_endpoint",
                    "endpoint": endpoint_path,
                    "description": f"Endpoint {endpoint_path} is not implemented"
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
        feature_matches = re.finditer(r"(?:feature|function):\s*([^\n]+)", prompt, re.IGNORECASE)
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
    
    def _generate_endpoints(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate API endpoints based on requirements
        
        Args:
            requirements: Extracted requirements
            
        Returns:
            Dictionary of API endpoints
        """
        endpoints = {}
        
        # Generate endpoints from entities
        for entity in requirements.get("entities", []):
            entity_name = entity.lower().replace(" ", "_")
            
            endpoints[f"/api/{entity_name}"] = {
                "method": "GET",
                "description": f"List all {entity}",
                "parameters": [],
                "responses": {
                    "200": {"description": f"List of {entity} items"}
                }
            }
            
            endpoints[f"/api/{entity_name}/{{id}}"] = {
                "method": "GET",
                "description": f"Get a specific {entity}",
                "parameters": ["id"],
                "responses": {
                    "200": {"description": f"Single {entity} item"},
                    "404": {"description": "Item not found"}
                }
            }
            
            endpoints[f"/api/{entity_name}"] = {
                "method": "POST",
                "description": f"Create a new {entity}",
                "parameters": [],
                "responses": {
                    "201": {"description": f"Created {entity}"},
                    "400": {"description": "Bad request"}
                }
            }
        
        # Generate endpoints from features
        for feature in requirements.get("features", []):
            feature_name = feature.lower().replace(" ", "_")
            endpoints[f"/api/{feature_name}"] = {
                "method": "POST",
                "description": f"Execute {feature}",
                "parameters": [],
                "responses": {
                    "200": {"description": f"Feature {feature} executed successfully"}
                }
            }
        
        # Add default health endpoint
        endpoints["/health"] = {
            "method": "GET",
            "description": "Health check endpoint",
            "parameters": [],
            "responses": {
                "200": {"description": "Service is healthy"}
            }
        }
        
        return endpoints
    
    def _generate_schemas(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate data schemas based on requirements
        
        Args:
            requirements: Extracted requirements
            
        Returns:
            Dictionary of data schemas
        """
        schemas = {}
        
        # Generate schemas from entities
        for entity in requirements.get("entities", []):
            schema_name = entity.replace(" ", "")
            schemas[schema_name] = {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": f"Unique identifier for {entity}"},
                    "name": {"type": "string", "description": f"Name of the {entity}"},
                    "created_at": {"type": "string", "format": "date-time", "description": "Creation timestamp"},
                    "updated_at": {"type": "string", "format": "date-time", "description": "Last update timestamp"}
                },
                "required": ["id", "name"]
            }
        
        return schemas
    
    def _file_implements_endpoint(self, file_path: str, content: str, endpoint_path: str) -> bool:
        """
        Check if a file implements a specific endpoint
        
        Args:
            file_path: Path to the file
            content: Content of the file
            endpoint_path: Endpoint path to check
            
        Returns:
            True if the file implements the endpoint, False otherwise
        """
        # Clean the endpoint path for pattern matching
        clean_path = endpoint_path.replace("{", "").replace("}", "").replace("/api/", "/")
        
        # Check if the file contains route definitions
        route_patterns = [
            f'@app.get("{endpoint_path}")',
            f'@app.post("{endpoint_path}")',
            f'@app.put("{endpoint_path}")',
            f'@app.delete("{endpoint_path}")',
            f"'{endpoint_path}'",
            f'"{endpoint_path}"'
        ]
        
        return any(pattern in content for pattern in route_patterns)
    
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
        # Check if the file is a model file
        if "model" in file_path or "schema" in file_path:
            # Check if the file contains the schema name
            class_pattern = f"class\\s+{schema_name}"
            pydantic_pattern = f"class\\s+{schema_name}\\s*\\(\\s*BaseModel\\s*\\)"
            
            class_match = re.search(class_pattern, content, re.IGNORECASE)
            pydantic_match = re.search(pydantic_pattern, content, re.IGNORECASE)
            
            return class_match is not None or pydantic_match is not None
        
        return False
    
    def _save_contract(self, contract: Dict[str, Any]):
        """
        Save contract to file
        
        Args:
            contract: Contract to save
        """
        contract_id = contract.get("info", {}).get("title", "unknown").replace(" ", "_")
        filename = f"{contract_id}_contract.json"
        filepath = os.path.join(self.contract_file_path, filename)
        
        with open(filepath, 'w') as f:
            json.dump(contract, f, indent=2)
        
        logger.info(f"Contract saved to {filepath}")
    
    def _generate_content_hash(self, content: str) -> str:
        """
        Generate hash for content
        
        Args:
            content: Content to hash
            
        Returns:
            Hash string
        """
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def _extract_endpoints_from_code(self, content: str) -> List[str]:
        """
        Extract implemented endpoints from code content
        
        Args:
            content: Code content
            
        Returns:
            List of endpoint paths
        """
        endpoints = []
        
        # Simple regex to find FastAPI route decorators
        route_pattern = r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
        matches = re.findall(route_pattern, content)
        
        for method, path in matches:
            endpoints.append(f"{method.upper()} {path}")
        
        return endpoints
    
    def _extract_schemas_from_code(self, content: str) -> List[str]:
        """
        Extract implemented schemas from code content
        
        Args:
            content: Code content
            
        Returns:
            List of schema names
        """
        schemas = []
        
        # Simple regex to find class definitions
        class_pattern = r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\)'
        matches = re.findall(class_pattern, content)
        
        schemas.extend(matches)
        
        return schemas


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
