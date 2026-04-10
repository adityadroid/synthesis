"""Routes for LLM models management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..services.llm_factory import llm_factory, LLMProvider
from ..services.ollama import ollama_service
from ..services.lm_studio import lm_studio_service
from ..services.custom_api import custom_api_service
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/models", tags=["models"])


class AddCustomEndpointRequest(BaseModel):
    name: str
    base_url: str
    api_key: str
    model: str = "default"


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    owned_by: str | None = None


class ProviderModels(BaseModel):
    provider: str
    models: list[ModelInfo]


@router.get("", response_model=list[ProviderModels])
async def list_all_models(user_id: str = Depends(get_current_user)):
    """
    List all available models from all providers.
    """
    all_models: list[ProviderModels] = []

    # OpenAI models (hardcoded for now)
    openai_models = [
        ModelInfo(id="gpt-4o", name="GPT-4o", provider="openai", owned_by="openai"),
        ModelInfo(
            id="gpt-4o-mini", name="GPT-4o Mini", provider="openai", owned_by="openai"
        ),
        ModelInfo(
            id="gpt-4-turbo", name="GPT-4 Turbo", provider="openai", owned_by="openai"
        ),
        ModelInfo(
            id="gpt-3.5-turbo",
            name="GPT-3.5 Turbo",
            provider="openai",
            owned_by="openai",
        ),
    ]
    all_models.append(ProviderModels(provider="openai", models=openai_models))

    # Anthropic models (hardcoded for now)
    anthropic_models = [
        ModelInfo(
            id="claude-3-5-sonnet-latest",
            name="Claude 3.5 Sonnet",
            provider="anthropic",
        ),
        ModelInfo(
            id="claude-3-5-haiku-latest", name="Claude 3.5 Haiku", provider="anthropic"
        ),
        ModelInfo(
            id="claude-3-opus-latest", name="Claude 3 Opus", provider="anthropic"
        ),
    ]
    all_models.append(ProviderModels(provider="anthropic", models=anthropic_models))

    # Ollama models
    try:
        ollama_models_data = await ollama_service.list_models()
        ollama_models = [
            ModelInfo(
                id=f"ollama/{m.get('name', 'unknown')}",
                name=m.get("name", "unknown"),
                provider="ollama",
            )
            for m in ollama_models_data
        ]
        all_models.append(ProviderModels(provider="ollama", models=ollama_models))
    except Exception:
        all_models.append(ProviderModels(provider="ollama", models=[]))

    # LM Studio models
    try:
        lm_models_data = await lm_studio_service.list_models()
        lm_models = [
            ModelInfo(
                id=f"lm-studio/{m.get('id', 'unknown')}",
                name=m.get("id", "unknown"),
                provider="lm-studio",
                owned_by=m.get("owned_by"),
            )
            for m in lm_models_data
        ]
        all_models.append(ProviderModels(provider="lm_studio", models=lm_models))
    except Exception:
        all_models.append(ProviderModels(provider="lm_studio", models=[]))

    # Custom endpoints
    custom_endpoints = custom_api_service.list_endpoints()
    for ep in custom_endpoints:
        all_models.append(
            ProviderModels(
                provider=f"custom/{ep['name']}",
                models=[
                    ModelInfo(
                        id=f"custom/{ep['name']}",
                        name=ep.get("model", "default"),
                        provider=f"custom/{ep['name']}",
                    )
                ],
            )
        )

    return all_models


@router.get("/status")
async def get_provider_status(user_id: str = Depends(get_current_user)):
    """
    Get the status of all LLM providers.
    """
    return llm_factory.get_provider_status()


@router.post("/custom-endpoints", status_code=status.HTTP_201_CREATED)
async def add_custom_endpoint(
    request: AddCustomEndpointRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Add a custom API endpoint.
    """
    endpoint = custom_api_service.add_endpoint(
        name=request.name,
        base_url=request.base_url,
        api_key=request.api_key,
        model=request.model,
    )
    return {
        "name": endpoint.name,
        "base_url": endpoint.base_url,
        "model": endpoint.model,
    }


@router.get("/custom-endpoints")
async def list_custom_endpoints(user_id: str = Depends(get_current_user)):
    """
    List all configured custom endpoints.
    """
    return custom_api_service.list_endpoints()


@router.delete("/custom-endpoints/{name}")
async def delete_custom_endpoint(
    name: str,
    user_id: str = Depends(get_current_user),
):
    """
    Remove a custom endpoint.
    """
    if custom_api_service.remove_endpoint(name):
        return {"message": f"Endpoint '{name}' removed"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Endpoint '{name}' not found",
    )


@router.post("/custom-endpoints/{name}/test")
async def test_custom_endpoint(
    name: str,
    user_id: str = Depends(get_current_user),
):
    """
    Test connection to a custom endpoint.
    """
    endpoint = custom_api_service.get_endpoint(name)
    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Endpoint '{name}' not found",
        )
    result = await custom_api_service.test_connection(endpoint)
    return result


# ==================== Custom Model Management ====================


class CustomModelCreate(BaseModel):
    """Request to create a custom model."""

    name: str
    display_name: str
    description: str | None = None
    model_type: str = "custom"
    base_url: str | None = None
    api_key: str | None = None
    model_id: str
    capabilities: dict | None = None
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


class CustomModelResponse(BaseModel):
    """Custom model response."""

    id: str
    name: str
    display_name: str
    description: str | None
    model_type: str
    base_url: str | None
    model_id: str
    capabilities: dict
    cost_per_1k_input: float
    cost_per_1k_output: float
    request_count: int
    avg_latency_ms: float
    is_enabled: bool
    is_ab_test_enabled: bool
    ab_test_weight: float
    created_at: datetime


class ModelPerformanceResponse(BaseModel):
    """Model performance metrics."""

    model_id: str
    request_count: int
    total_tokens: int
    avg_latency_ms: float
    error_rate: float
    total_cost: float
    period_start: datetime
    period_end: datetime


@router.get("/custom-models", response_model=list[CustomModelResponse])
async def list_custom_models(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all custom models."""
    result = await db.execute(
        select(CustomModel).where(
            (CustomModel.user_id == user_id) | (CustomModel.user_id == None)
        )
    )
    models = result.scalars().all()

    return [
        CustomModelResponse(
            id=m.id,
            name=m.name,
            display_name=m.display_name,
            description=m.description,
            model_type=m.model_type.value
            if hasattr(m.model_type, "value")
            else m.model_type,
            base_url=m.base_url,
            model_id=m.model_id,
            capabilities=json.loads(m.capabilities)
            if isinstance(m.capabilities, str)
            else m.capabilities or {},
            cost_per_1k_input=m.cost_per_1k_input,
            cost_per_1k_output=m.cost_per_1k_output,
            request_count=m.request_count,
            avg_latency_ms=m.avg_latency_ms,
            is_enabled=m.is_enabled,
            is_ab_test_enabled=m.is_ab_test_enabled,
            ab_test_weight=m.ab_test_weight,
            created_at=m.created_at,
        )
        for m in models
    ]


@router.post("/custom-models", response_model=CustomModelResponse)
async def create_custom_model(
    request: CustomModelCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new custom model configuration."""
    model = CustomModel(
        user_id=user_id,
        name=request.name,
        display_name=request.display_name,
        description=request.description,
        model_type=ModelType(request.model_type),
        base_url=request.base_url,
        api_key=request.api_key,
        model_id=request.model_id,
        capabilities=json.dumps(request.capabilities or {}),
        cost_per_1k_input=request.cost_per_1k_input,
        cost_per_1k_output=request.cost_per_1k_output,
    )
    db.add(model)
    await db.flush()
    await db.refresh(model)

    return CustomModelResponse(
        id=model.id,
        name=model.name,
        display_name=model.display_name,
        description=model.description,
        model_type=model.model_type.value
        if hasattr(model.model_type, "value")
        else model.model_type,
        base_url=model.base_url,
        model_id=model.model_id,
        capabilities=json.loads(model.capabilities)
        if isinstance(model.capabilities, str)
        else model.capabilities or {},
        cost_per_1k_input=model.cost_per_1k_input,
        cost_per_1k_output=model.cost_per_1k_output,
        request_count=model.request_count,
        avg_latency_ms=model.avg_latency_ms,
        is_enabled=model.is_enabled,
        is_ab_test_enabled=model.is_ab_test_enabled,
        ab_test_weight=model.ab_test_weight,
        created_at=model.created_at,
    )


@router.delete("/custom-models/{model_id}")
async def delete_custom_model(
    model_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a custom model."""
    result = await db.execute(
        select(CustomModel).where(
            CustomModel.id == model_id,
            CustomModel.user_id == user_id,
        )
    )
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    await db.delete(model)
    await db.flush()

    return {"message": "Model deleted"}


@router.get(
    "/custom-models/{model_id}/performance", response_model=ModelPerformanceResponse
)
async def get_model_performance(
    model_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = 7,
):
    """Get performance metrics for a custom model."""
    result = await db.execute(
        select(CustomModel).where(
            CustomModel.id == model_id,
            (CustomModel.user_id == user_id) | (CustomModel.user_id == None),
        )
    )
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Calculate period
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get usage logs
    logs_result = await db.execute(
        select(ModelUsageLog).where(
            ModelUsageLog.model_id == model_id,
            ModelUsageLog.created_at >= period_start,
        )
    )
    logs = list(logs_result.scalars().all())

    if logs:
        total_requests = len(logs)
        total_tokens = sum(l.input_tokens + l.output_tokens for l in logs)
        total_latency = sum(l.latency_ms for l in logs)
        errors = sum(1 for l in logs if not l.success)
        total_cost = sum(l.cost for l in logs)

        avg_latency = total_latency / total_requests if total_requests > 0 else 0
        error_rate = errors / total_requests if total_requests > 0 else 0
    else:
        total_requests = model.request_count
        total_tokens = model.total_tokens
        avg_latency = model.avg_latency_ms
        error_rate = (
            model.error_count / model.request_count if model.request_count > 0 else 0
        )
        total_cost = (model.total_tokens * model.cost_per_1k_input / 1000) + (
            model.total_tokens * model.cost_per_1k_output / 1000
        )

    return ModelPerformanceResponse(
        model_id=model_id,
        request_count=total_requests,
        total_tokens=total_tokens,
        avg_latency_ms=avg_latency,
        error_rate=error_rate,
        total_cost=total_cost,
        period_start=period_start,
        period_end=period_end,
    )


@router.post("/custom-models/{model_id}/toggle-ab-test")
async def toggle_ab_test(
    model_id: str,
    enabled: bool,
    weight: float = 0.5,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable/disable A/B testing for a model."""
    result = await db.execute(
        select(CustomModel).where(
            CustomModel.id == model_id,
            CustomModel.user_id == user_id,
        )
    )
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    model.is_ab_test_enabled = enabled
    model.ab_test_weight = max(0.0, min(1.0, weight))
    await db.flush()

    return {
        "is_ab_test_enabled": model.is_ab_test_enabled,
        "ab_test_weight": model.ab_test_weight,
    }
