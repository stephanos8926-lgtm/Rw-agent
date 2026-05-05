from pydantic import create_model, Field, ValidationError
from typing import Any, Dict, List, Type
import yaml

class ToolValidator:
    """
    Dynamically creates Pydantic models from YAML-defined tool schemas
    to ensure robust input validation.
    """
    
    @staticmethod
    def create_model_from_schema(name: str, schema: Dict[str, Any]) -> Type:
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        fields = {}
        for prop_name, prop_details in properties.items():
            prop_type = prop_details.get("type", "string")
            python_type: Any = Any
            
            if prop_type == "string":
                python_type = str
            elif prop_type == "integer":
                python_type = int
            elif prop_type == "boolean":
                python_type = bool
            elif prop_type == "number":
                python_type = float
            elif prop_type == "array":
                python_type = List[Any]
            elif prop_type == "object":
                python_type = Dict[str, Any]
                
            # Handle required / optional
            default = ... if prop_name in required else None
            fields[prop_name] = (python_type, Field(default=default, description=prop_details.get("description", "")))
            
        return create_model(name, **fields)

    @staticmethod
    def validate_tool_call(tool_name: str, args: Dict[str, Any], schema: Dict[str, Any]):
        try:
            Model = ToolValidator.create_model_from_schema(tool_name, schema.get("parameters", {}))
            return Model(**args)
        except ValidationError as e:
            raise ValueError(f"Invalid parameters for {tool_name}: {e.json()}")
