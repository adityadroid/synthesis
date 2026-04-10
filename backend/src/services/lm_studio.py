"""LM Studio service for local model support."""

import httpx
from typing import AsyncGenerator


class LMStudioService:
    """Service for LM Studio (OpenAI-compatible API)."""

    def __init__(self, base_url: str = "http://localhost:1234"):
        self.base_url = base_url
        # LM Studio uses OpenAI-compatible API
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=120.0,
            headers={"Content-Type": "application/json"},
        )

    async def is_available(self) -> bool:
        """Check if LM Studio is running."""
        try:
            response = await self.client.get("/v1/models")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict]:
        """List available LM Studio models."""
        try:
            response = await self.client.get("/v1/models")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []
        except Exception:
            return []

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "local-model",
        **kwargs,
    ) -> str:
        """Send a chat request to LM Studio."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs,
        }
        response = await self.client.post("/v1/chat/completions", json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        raise Exception(f"LM Studio request failed: {response.status_code}")

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str = "local-model",
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from LM Studio."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs,
        }
        async with self.client.stream(
            "POST", "/v1/chat/completions", json=payload
        ) as response:
            if response.status_code != 200:
                yield f"Error: LM Studio returned {response.status_code}"
                return

            async for line in response.aiter_lines():
                if line and line.startswith("data: "):
                    if line.strip() == "data: [DONE]":
                        return
                    try:
                        import json

                        chunk = json.loads(line[6:])
                        content = (
                            chunk.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
lm_studio_service = LMStudioService()
