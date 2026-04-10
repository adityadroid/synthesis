"""Tool calling service for function execution."""

import json
from typing import Any, Callable
from enum import Enum


class ToolCategory(str, Enum):
    """Categories for tools."""

    SEARCH = "search"
    CALCULATOR = "calculator"
    CODE = "code"
    DATA = "data"
    UTILITY = "utility"


class ToolDefinition:
    """Definition of a callable tool."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable[..., Any],
        category: ToolCategory = ToolCategory.UTILITY,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
        self.category = category

    def to_openai_format(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolCall:
    """Represents a tool call from the LLM."""

    def __init__(self, id: str, name: str, arguments: dict):
        self.id = id
        self.name = name
        self.arguments = arguments

    @classmethod
    def from_dict(cls, data: dict) -> "ToolCall":
        return cls(
            id=data.get("id", ""),
            name=data["function"]["name"],
            arguments=json.loads(data["function"]["arguments"])
            if isinstance(data["function"]["arguments"], str)
            else data["function"]["arguments"],
        )


class ToolResult:
    """Result of a tool execution."""

    def __init__(self, tool_call_id: str, output: str | dict, error: str | None = None):
        self.tool_call_id = tool_call_id
        self.output = output
        self.error = error
        self.is_error = error is not None

    def to_dict(self) -> dict:
        return {
            "tool_call_id": self.tool_call_id,
            "output": self.output if not self.is_error else None,
            "error": self.error,
            "is_error": self.is_error,
        }


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_openai_functions(self) -> list[dict]:
        """Get all tools in OpenAI format."""
        return [tool.to_openai_format() for tool in self._tools.values()]

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call."""
        tool = self.get(tool_call.name)
        if not tool:
            return ToolResult(
                tool_call_id=tool_call.id,
                output="",
                error=f"Tool '{tool_call.name}' not found",
            )

        try:
            result = tool.handler(**tool_call.arguments)
            # Handle async results
            import asyncio

            if asyncio.iscoroutine(result):
                result = await result
            return ToolResult(
                tool_call_id=tool_call.id,
                output=json.dumps(result) if isinstance(result, dict) else str(result),
            )
        except TypeError as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                output="",
                error=f"Invalid arguments: {str(e)}",
            )
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                output="",
                error=f"Execution error: {str(e)}",
            )


# Global registry
tool_registry = ToolRegistry()


# Built-in tools
def register_builtin_tools():
    """Register built-in tools."""

    # Calculator tool
    tool_registry.register(
        ToolDefinition(
            name="calculator",
            description="Calculate a mathematical expression. Use for arithmetic, percentages, and basic math.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', '100 * 0.15')",
                    },
                },
                "required": ["expression"],
            },
            handler=lambda expression: eval(
                expression,
                {"__builtins__": {}},
                {
                    "sqrt": lambda x: x**0.5,
                    "abs": abs,
                    "round": round,
                    "min": min,
                    "max": max,
                    "pow": pow,
                },
            ),
            category=ToolCategory.CALCULATOR,
        )
    )

    # Current date/time tool
    tool_registry.register(
        ToolDefinition(
            name="get_current_time",
            description="Get the current date and time. Useful for time-related queries.",
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=lambda: {
                "date": "2024-01-01",  # Will be overridden at runtime
                "iso": "2024-01-01T00:00:00",
            },
            category=ToolCategory.UTILITY,
        )
    )

    # Text tools
    tool_registry.register(
        ToolDefinition(
            name="text_length",
            description="Get the length of a text string in characters.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to measure",
                    },
                },
                "required": ["text"],
            },
            handler=lambda text: len(text),
            category=ToolCategory.UTILITY,
        )
    )

    tool_registry.register(
        ToolDefinition(
            name="word_count",
            description="Count the number of words in a text.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to count words in",
                    },
                },
                "required": ["text"],
            },
            handler=lambda text: len(text.split()),
            category=ToolCategory.UTILITY,
        )
    )


# Initialize built-in tools
register_builtin_tools()


# Function to add search tool (called separately to avoid circular imports)
def add_search_tool():
    """Add web search tool to registry."""
    from .search import search_service

    async def web_search(query: str, num_results: int = 5) -> dict:
        """Search the web for information."""
        response = await search_service.search(query, num_results)
        return {
            "query": response.query,
            "results": [r.to_dict() for r in response.results],
            "formatted": search_service.format_results_for_llm(response),
        }

    tool_registry.register(
        ToolDefinition(
            name="web_search",
            description="Search the web for current information, news, or facts. Use this when you need up-to-date information or want to verify facts.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5, max: 10)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            handler=web_search,
            category=ToolCategory.SEARCH,
        )
    )
