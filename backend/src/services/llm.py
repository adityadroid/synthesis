"""LLM service for OpenAI integration with streaming support."""

import os
import asyncio
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI

from ..config import Settings
from ..models import MessageRole
from ..services.conversation import get_conversation_messages


settings = Settings()


class LLMService:
    """Service for LLM interactions."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        )
        self.default_model = "gpt-4o-mini"

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """Send a chat request and get a non-streaming response."""
        if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            # Return a mock response if no API key
            return "This is a demo response. Configure OPENAI_API_KEY to enable AI responses."

        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"Error: {str(e)}"

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Send a chat request and yield tokens as they arrive."""
        if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
            # Return a mock streaming response if no API key
            demo_response = "This is a demo response. Configure OPENAI_API_KEY to enable AI responses."
            for char in demo_response:
                yield char
                await asyncio.sleep(0.01)
            return

        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"Error: {str(e)}"

    def build_messages(
        self,
        conversation_history: list,
        user_message: str,
    ) -> list[dict[str, str]]:
        """Build message format for OpenAI API."""
        messages = []

        # Add conversation history
        for msg in conversation_history:
            messages.append(
                {
                    "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                    "content": msg.content,
                }
            )

        # Add current user message
        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        return messages


# Import asyncio for the demo streaming
import asyncio

llm_service = LLMService()
