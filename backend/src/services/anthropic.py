"""Anthropic Claude integration service."""

import os
import asyncio
from typing import AsyncGenerator

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

from ..config import Settings


settings = Settings()


class AnthropicService:
    """Service for Anthropic Claude API interactions."""

    def __init__(self):
        if AsyncAnthropic is None:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic"
            )

        api_key = settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = AsyncAnthropic(api_key=api_key) if api_key else None
        self.default_model = "claude-3-5-sonnet-20241022"

    def is_available(self) -> bool:
        """Check if Anthropic API is configured."""
        return self.client is not None

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> str:
        """Send a chat request and get a non-streaming response."""
        if not self.client:
            return "Anthropic API not configured. Please set ANTHROPIC_API_KEY."

        try:
            # Convert messages format for Anthropic
            anthropic_messages = []
            system_prompt = system
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    anthropic_messages.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        }
                    )

            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=temperature,
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        system: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response."""
        if not self.client:
            yield "Anthropic API not configured."
            return

        try:
            anthropic_messages = []
            system_prompt = system
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    anthropic_messages.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        }
                    )

            async with self.client.messages.stream(
                model=model or self.default_model,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Error: {str(e)}"


anthropic_service = AnthropicService()
