"""Tool calling routes for function execution."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any

from ..services.tools import tool_registry, ToolCall, ToolResult
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/tools", tags=["tools"])


class ToolResponse(BaseModel):
    """Tool definition response."""

    name: str
    description: str
    parameters: dict
    category: str


class ToolCallRequest(BaseModel):
    """Execute a tool call."""

    name: str
    arguments: dict


class ToolCallResponse(BaseModel):
    """Tool call response."""

    tool_call_id: str
    output: str | dict | None
    error: str | None
    is_error: bool


class ToolExecutionRequest(BaseModel):
    """Execute one or more tool calls."""

    calls: list[dict]  # List of tool calls from LLM


class ToolExecutionResponse(BaseModel):
    """Response from tool execution."""

    results: list[ToolCallResponse]


@router.get("", response_model=list[ToolResponse])
async def list_tools(
    user_id: str = Depends(get_current_user),
):
    """List all available tools."""
    tools = tool_registry.list_tools()
    return [
        ToolResponse(
            name=t.name,
            description=t.description,
            parameters=t.parameters,
            category=t.category.value
            if hasattr(t.category, "value")
            else str(t.category),
        )
        for t in tools
    ]


@router.post("/execute", response_model=ToolCallResponse)
async def execute_tool(
    request: ToolCallRequest,
    user_id: str = Depends(get_current_user),
):
    """Execute a single tool call."""
    tool_call = ToolCall(
        id=f"call_{user_id[:8]}_{ToolCallRequest.__name__.lower()}",
        name=request.name,
        arguments=request.arguments,
    )

    result = await tool_registry.execute(tool_call)

    return ToolCallResponse(
        tool_call_id=result.tool_call_id,
        output=result.output,
        error=result.error,
        is_error=result.is_error,
    )


@router.post("/execute-batch", response_model=ToolExecutionResponse)
async def execute_tools(
    request: ToolExecutionRequest,
    user_id: str = Depends(get_current_user),
):
    """Execute multiple tool calls."""
    results = []

    for i, call_data in enumerate(request.calls):
        try:
            tool_call = ToolCall(
                id=call_data.get("id", f"call_{i}"),
                name=call_data["function"]["name"],
                arguments=call_data["function"].get("arguments", {}),
            )
            result = await tool_registry.execute(tool_call)
            results.append(
                ToolCallResponse(
                    tool_call_id=result.tool_call_id,
                    output=result.output,
                    error=result.error,
                    is_error=result.is_error,
                )
            )
        except Exception as e:
            results.append(
                ToolCallResponse(
                    tool_call_id=call_data.get("id", f"call_{i}"),
                    output=None,
                    error=str(e),
                    is_error=True,
                )
            )

    return ToolExecutionResponse(results=results)


@router.get("/openai-format")
async def get_openai_tools(
    user_id: str = Depends(get_current_user),
):
    """Get tools in OpenAI function calling format."""
    return tool_registry.get_openai_functions()
