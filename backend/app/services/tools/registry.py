from typing import Any, Dict, List, Callable
import inspect
import logging

logger = logging.getLogger("mcp_tools")

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, func: Callable):
        """
        Decorator to register a function as a tool.
        Automatically generates OpenAI-compatible JSON schema from docstring/type hints.
        """
        name = func.__name__
        self._tools[name] = func
        
        # Simple schema generation (In real app, use Pydantic or inspection lib)
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or "No description."
        
        logger.debug(f"Registering tool: {name}")
        
        # Construct basic schema
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == "self": continue
            param_type = "string" # Default simplification
            if param.annotation == int: param_type = "integer"
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
                
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": doc,
                "parameters": parameters
            }
        }
        self._schemas.append(schema)
        return func

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    @property
    def schemas(self) -> List[Dict[str, Any]]:
        return self._schemas

# Global Registry
registry = ToolRegistry()

# --- Placeholder Implementation of Core Tools ---

@registry.register
def read_file(path: str) -> str:
    """
    Reads the content of a file from the filesystem.
    Args:
        path: The absolute path to the file.
    """
    logger.info(f"Tool Exec: read_file({path})")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read file {path}: {e}")
        return f"Error: {str(e)}"

@registry.register
def write_file(path: str, content: str) -> str:
    """
    Writes content to a file. Overwrites if exists.
    Args:
        path: The absolute path.
        content: The text content to write.
    """
    logger.info(f"Tool Exec: write_file({path})")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "Success"
    except Exception as e:
        logger.error(f"Failed to write file {path}: {e}")
        return f"Error: {str(e)}"

@registry.register
def run_shell(command: str) -> str:
    """
    Executes a shell command. Use with caution.
    Args:
        command: The command line string.
    """
    logger.info(f"Tool Exec: run_shell({command})")
    # For security in this phase, we might mock or restrict this
    return f"Simulated execution of: {command}"
