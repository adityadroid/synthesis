"""Routes for usage statistics and analytics."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional

from ..services.usage import token_counter, usage_tracker
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/usage", tags=["usage"])


class UsageStats(BaseModel):
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    conversation_count: int
    message_count: int
    model_breakdown: dict


class ModelStats(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    message_count: int
    cost: float


class DailyUsage(BaseModel):
    date: str
    input_tokens: int
    output_tokens: int
    message_count: int
    cost: float


class CostReport(BaseModel):
    period_start: str
    period_end: str
    total_cost: float
    daily_breakdown: list[DailyUsage]
    by_model: list[ModelStats]
    top_conversations: list[dict]


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
        message_count=usage.get("message_count", 0),
        model_breakdown=usage.get("models", {}),
    )


@router.get("/dashboard", response_model=CostReport)
async def get_usage_dashboard(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, all"),
    user_id: str = Depends(get_current_user),
):
    """
    Get detailed usage analytics dashboard.
    """
    # Calculate date range
    now = datetime.utcnow()
    if period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "30d":
        start_date = now - timedelta(days=30)
    elif period == "90d":
        start_date = now - timedelta(days=90)
    else:
        start_date = datetime(2020, 1, 1)

    usage = usage_tracker.get_user_usage(user_id)
    models_data = usage.get("models", {})
    conversations = usage.get("conversations", {})

    # Build model breakdown
    model_stats = []
    for model, data in models_data.items():
        model_stats.append(
            ModelStats(
                model=model,
                input_tokens=data.get("input_tokens", 0),
                output_tokens=data.get("output_tokens", 0),
                message_count=data.get("message_count", 0),
                cost=data.get("cost", 0.0),
            )
        )

    # Sort by cost descending
    model_stats.sort(key=lambda x: x.cost, reverse=True)

    # Build top conversations
    top_convs = []
    for conv_id, data in conversations.items():
        top_convs.append(
            {
                "conversation_id": conv_id,
                "message_count": data.get("message_count", 0),
                "cost": data.get("cost", 0.0),
                "input_tokens": data.get("input_tokens", 0),
                "output_tokens": data.get("output_tokens", 0),
            }
        )
    top_convs.sort(key=lambda x: x["cost"], reverse=True)
    top_convs = top_convs[:10]  # Top 10

    # Generate daily breakdown (mock for now - would need time-series storage)
    daily = []
    current = start_date
    while current <= now:
        daily.append(
            DailyUsage(
                date=current.strftime("%Y-%m-%d"),
                input_tokens=0,  # Would need time-series data
                output_tokens=0,
                message_count=0,
                cost=0.0,
            )
        )
        current += timedelta(days=1)

    return CostReport(
        period_start=start_date.strftime("%Y-%m-%d"),
        period_end=now.strftime("%Y-%m-%d"),
        total_cost=usage.get("total_cost", 0.0),
        daily_breakdown=daily,
        by_model=model_stats,
        top_conversations=top_convs,
    )


@router.get("/cost-report", response_model=CostReport)
async def get_cost_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
):
    """
    Generate cost report for a date range.
    """
    # Parse dates
    now = datetime.utcnow()
    start = (
        datetime.strptime(start_date, "%Y-%m-%d")
        if start_date
        else now - timedelta(days=30)
    )
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now

    usage = usage_tracker.get_user_usage(user_id)
    models_data = usage.get("models", {})
    conversations = usage.get("conversations", {})

    # Build model breakdown
    model_stats = [
        ModelStats(
            model=model,
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            message_count=data.get("message_count", 0),
            cost=data.get("cost", 0.0),
        )
        for model, data in models_data.items()
    ]
    model_stats.sort(key=lambda x: x.cost, reverse=True)

    # Build conversations list
    conv_list = [
        {
            "conversation_id": conv_id,
            "message_count": data.get("message_count", 0),
            "cost": data.get("cost", 0.0),
            "input_tokens": data.get("input_tokens", 0),
            "output_tokens": data.get("output_tokens", 0),
        }
        for conv_id, data in conversations.items()
    ]
    conv_list.sort(key=lambda x: x["cost"], reverse=True)

    # Generate daily breakdown
    daily = []
    current = start
    while current <= end:
        daily.append(
            DailyUsage(
                date=current.strftime("%Y-%m-%d"),
                input_tokens=0,
                output_tokens=0,
                message_count=0,
                cost=0.0,
            )
        )
        current += timedelta(days=1)

    return CostReport(
        period_start=start.strftime("%Y-%m-%d"),
        period_end=end.strftime("%Y-%m-%d"),
        total_cost=usage.get("total_cost", 0.0),
        daily_breakdown=daily,
        by_model=model_stats,
        top_conversations=conv_list[:20],
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
