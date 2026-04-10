"""LLM Factory for managing multiple LLM providers."""

from enum import Enum
from typing import AsyncGenerator

from .llm import LLMService
from .ollama import ollama_service
from .lm_studio import lm_studio_service
from .custom_api import custom_api_service
from .anthropic import anthropic_service


class LLMProvider(Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    CUSTOM = "custom"


class LLMFactory:
    """Factory for creating LLM service instances based on provider."""

    def __init__(self):
        self.openai_service = LLMService()
        self.ollama = ollama_service
        self.lm_studio = lm_studio_service
        self.custom_api = custom_api_service
        self.anthropic = anthropic_service

    def get_provider_for_model(self, model: str) -> LLMProvider:
        """Determine which provider a model belongs to."""
        # Local models typically have specific prefixes or names
        if model.startswith("ollama/"):
            return LLMProvider.OLLAMA
        if model.startswith("lm-studio/") or model.startswith("lmstudio/"):
            return LLMProvider.LM_STUDIO
        if model.startswith("custom/"):
            return LLMProvider.CUSTOM
        # Default to OpenAI for standard model names
        if model.startswith(("gpt-", "o1-", "o3-", "o4-")):
            return LLMProvider.OPENAI
        if model.startswith(("claude-", "sonnet", "haiku")):
            return LLMProvider.ANTHROPIC
        # Check if Ollama or LM Studio are available
        # Default to OpenAI
        return LLMProvider.OPENAI

    def get_provider_status(self) -> dict:
        """Get status of all LLM providers."""
        import asyncio

        status = {
            "openai": {
                "available": True,
                "configured": bool(self.openai_service.client.api_key),
            },
            "anthropic": {"available": False, "configured": False},
            "ollama": {"available": False, "configured": False},
            "lm_studio": {"available": False, "configured": False},
            "custom": {"available": False, "endpoints": []},
        }

        # Check async providers
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Create task to check async
            import asyncio

            async def check_async():
                ollama_available = await self.ollama.is_available()
                lm_available = await self.lm_studio.is_available()
                anthropic_available = self.anthropic.is_available()
                status["ollama"]["available"] = ollama_available
                status["lm_studio"]["available"] = lm_available
                status["anthropic"]["available"] = anthropic_available
                status["anthropic"]["configured"] = anthropic_available
                status["ollama"]["configured"] = True  # Always configured (localhost)
                status["lm_studio"]["configured"] = True
                status["custom"]["endpoints"] = self.custom_api.list_endpoints()
                status["custom"]["available"] = len(self.custom_api.endpoints) > 0

            loop.run_until_complete(check_async())

        return status

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        provider: LLMProvider | None = None,
        **kwargs,
    ) -> str:
        """Send a chat request to the appropriate provider."""
        if provider is None:
            provider = self.get_provider_for_model(model or "gpt-4o-mini")

        if provider == LLMProvider.OLLAMA:
            actual_model = model.replace("ollama/", "") if model else "llama2"
            return await self.ollama.chat(messages, actual_model, **kwargs)

        elif provider == LLMProvider.LM_STUDIO:
            actual_model = (
                model.replace("lm-studio/", "").replace("lmstudio/", "")
                if model
                else "local-model"
            )
            return await self.lm_studio.chat(messages, actual_model, **kwargs)

        elif provider == LLMProvider.CUSTOM:
            endpoint_name = model.replace("custom/", "") if model else None
            if not endpoint_name:
                raise ValueError("Custom endpoint name required")
            return await self.custom_api.chat(endpoint_name, messages, **kwargs)

        elif provider == LLMProvider.ANTHROPIC:
            return await self.anthropic.chat(messages, model, **kwargs)

        else:
            # Default to OpenAI
            return await self.openai_service.chat(messages, model, **kwargs)

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        provider: LLMProvider | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response from the appropriate provider."""
        if provider is None:
            provider = self.get_provider_for_model(model or "gpt-4o-mini")

        if provider == LLMProvider.OLLAMA:
            actual_model = model.replace("ollama/", "") if model else "llama2"
            async for chunk in self.ollama.stream_chat(
                messages, actual_model, **kwargs
            ):
                yield chunk

        elif provider == LLMProvider.LM_STUDIO:
            actual_model = (
                model.replace("lm-studio/", "").replace("lmstudio/", "")
                if model
                else "local-model"
            )
            async for chunk in self.lm_studio.stream_chat(
                messages, actual_model, **kwargs
            ):
                yield chunk

        elif provider == LLMProvider.CUSTOM:
            endpoint_name = model.replace("custom/", "") if model else None
            if not endpoint_name:
                yield "Error: Custom endpoint name required"
                return
            async for chunk in self.custom_api.stream_chat(
                endpoint_name, messages, **kwargs
            ):
                yield chunk

        elif provider == LLMProvider.ANTHROPIC:
            async for chunk in self.anthropic.stream_chat(messages, model, **kwargs):
                yield chunk

        else:
            # Default to OpenAI
            async for chunk in self.openai_service.stream_chat(
                messages, model, **kwargs
            ):
                yield chunk


# Singleton instance
llm_factory = LLMFactory()
