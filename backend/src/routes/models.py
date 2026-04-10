"""Routes for LLM models management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

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
