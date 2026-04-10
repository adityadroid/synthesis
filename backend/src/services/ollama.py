"""Ollama service for local model support."""

import httpx
from typing import AsyncGenerator


class OllamaService:
    """Service for Ollama local LLM interactions."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict]:
        """List available Ollama models."""
        try:
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            return []
        except Exception:
            return []

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str = "llama2",
    ) -> str:
        """Send a chat request to Ollama."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        response = await self.client.post("/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("message", {}).get("content", "")
        raise Exception(f"Ollama request failed: {response.status_code}")

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str = "llama2",
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Ollama."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        async with self.client.stream("POST", "/api/chat", json=payload) as response:
            if response.status_code != 200:
                yield f"Error: Ollama returned {response.status_code}"
                return

            async for line in response.aiter_lines():
                if line:
                    try:
                        import json

                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def generate(
        self,
        prompt: str,
        model: str = "llama2",
        **kwargs,
    ) -> str:
        """Generate text using Ollama (non-chat endpoint)."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }
        response = await self.client.post("/api/generate", json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        raise Exception(f"Ollama request failed: {response.status_code}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
ollama_service = OllamaService()
