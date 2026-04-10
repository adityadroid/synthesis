"""Routes for usage statistics."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.usage import token_counter, usage_tracker
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/usage", tags=["usage"])


class UsageStats(BaseModel):
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    conversation_count: int
    model_breakdown: dict


class ConversationUsage(BaseModel):
    conversation_id: str
    input_tokens: int
    output_tokens: int
    cost: float
    message_count: int


@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(user_id: str = Depends(get_current_user)):
    """
    Get overall usage statistics for the current user.
    """
    usage = usage_tracker.get_user_usage(user_id)

    return UsageStats(
        total_input_tokens=usage.get("total_input_tokens", 0),
        total_output_tokens=usage.get("total_output_tokens", 0),
        total_cost=usage.get("total_cost", 0.0),
        conversation_count=len(usage.get("conversations", {})),
        model_breakdown=usage.get("models", {}),
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationUsage)
async def get_conversation_usage(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Get usage statistics for a specific conversation.
    """
    usage = usage_tracker.get_conversation_usage(user_id, conversation_id)
    return ConversationUsage(
        conversation_id=conversation_id,
        **usage,
    )


@router.post("/estimate")
async def estimate_cost(
    model: str,
    input_text: str,
    output_text: str = "",
):
    """
    Estimate cost for a message exchange.
    """
    cost = token_counter.estimate_message_cost(model, input_text, output_text)
    input_tokens = token_counter.estimate_tokens(input_text)
    output_tokens = token_counter.estimate_tokens(output_text)

    return {
        "estimated_cost": round(cost, 6),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "pricing": token_counter.get_model_pricing(model),
    }


@router.get("/models/pricing")
async def get_model_pricing():
    """
    Get pricing information for all models.
    """
    from ..services.usage import TOKEN_PRICING

    return TOKEN_PRICING
