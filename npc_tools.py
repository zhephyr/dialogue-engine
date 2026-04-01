from typing import Dict, Any, Callable, Type
import json
import inspect
from pydantic import BaseModel

class NPCTool:
    """Base class for an NPC Tool Capability."""
    name: str = ""
    description: str = ""
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Returns the JSON schema for this tool's expected kwargs (dummy implementation for now)."""
        return {"type": "object", "properties": {}}

    def execute(self, npc, world_state, **kwargs) -> str:
        """Execute the tool on behalf of the NPC."""
        raise NotImplementedError

class CheckFactTool(NPCTool):
    name = "CheckFact"
    description = "Check your current knowledge or ask the engine to verify a fact from the world."
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The topic or fact to check"}
            },
            "required": ["topic"]
        }
        
    def execute(self, npc, world_state, topic: str = "", **kwargs) -> str:
        # Simplistic implementation
        if npc.knows_fact(topic):
            return f"Fact verified internally: I know about {topic}."
        return f"World checked: No immediate facts found for {topic}."

class RecallMemoryTool(NPCTool):
    name = "RecallMemory"
    description = "Recall past memories or conversation turns."
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords of memory to recall"}
            },
            "required": ["query"]
        }
        
    def execute(self, npc, world_state, query: str = "", **kwargs) -> str:
        results = [m for m in npc.memory if query.lower() in m.content.lower()]
        if not results:
            return "I don't recall anything about that."
        return "\\n".join([f"- {m.content}" for m in results[:3]])


TOOL_REGISTRY: Dict[str, NPCTool] = {
    "CheckFact": CheckFactTool(),
    "RecallMemory": RecallMemoryTool()
}

def get_all_tool_schemas() -> str:
    schemas = []
    for name, tool in TOOL_REGISTRY.items():
        schemas.append({
            "name": name,
            "description": tool.description,
            "schema": tool.get_schema()
        })
    return json.dumps(schemas, indent=2)

def execute_tool(tool_name: str, npc, world_state, kwargs: Dict[str, Any]) -> str:
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return f"Tool {tool_name} not found."
    try:
        return tool.execute(npc, world_state, **kwargs)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
