"""Custom API endpoint service for OpenAI-compatible APIs."""

import httpx
from typing import AsyncGenerator


class CustomAPIEndpoint:
    """Represents a custom API endpoint configuration."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        model: str = "default",
    ):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.model = model


class CustomAPIService:
    """Service for custom OpenAI-compatible API endpoints."""

    def __init__(self):
        self.endpoints: dict[str, CustomAPIEndpoint] = {}

    def add_endpoint(
        self,
        name: str,
        base_url: str,
        api_key: str,
        model: str = "default",
    ) -> CustomAPIEndpoint:
        """Add a custom API endpoint."""
        endpoint = CustomAPIEndpoint(name, base_url, api_key, model)
        self.endpoints[name] = endpoint
        return endpoint

    def remove_endpoint(self, name: str) -> bool:
        """Remove a custom API endpoint."""
        if name in self.endpoints:
            del self.endpoints[name]
            return True
        return False

    def get_endpoint(self, name: str) -> CustomAPIEndpoint | None:
        """Get a custom API endpoint by name."""
        return self.endpoints.get(name)

    def list_endpoints(self) -> list[dict]:
        """List all configured endpoints."""
        return [
            {
                "name": ep.name,
                "base_url": ep.base_url,
                "model": ep.model,
            }
            for ep in self.endpoints.values()
        ]

    async def test_connection(self, endpoint: CustomAPIEndpoint) -> dict:
        """Test connection to a custom endpoint."""
        client = httpx.AsyncClient(
            base_url=endpoint.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {endpoint.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            response = await client.get("/v1/models")
            if response.status_code == 200:
                return {"success": True, "models": response.json().get("data", [])}
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await client.aclose()

    async def chat(
        self,
        endpoint_name: str,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> str:
        """Send a chat request to a custom endpoint."""
        endpoint = self.get_endpoint(endpoint_name)
        if not endpoint:
            raise ValueError(f"Endpoint '{endpoint_name}' not found")

        client = httpx.AsyncClient(
            base_url=endpoint.base_url,
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {endpoint.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            payload = {
                "model": endpoint.model,
                "messages": messages,
                "stream": False,
                **kwargs,
            }
            response = await client.post("/v1/chat/completions", json=payload)
            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
            raise Exception(f"Custom API request failed: {response.status_code}")
        finally:
            await client.aclose()

    async def stream_chat(
        self,
        endpoint_name: str,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from a custom endpoint."""
        endpoint = self.get_endpoint(endpoint_name)
        if not endpoint:
            yield f"Error: Endpoint '{endpoint_name}' not found"
            return

        client = httpx.AsyncClient(
            base_url=endpoint.base_url,
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {endpoint.api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            payload = {
                "model": endpoint.model,
                "messages": messages,
                "stream": True,
                **kwargs,
            }
            async with client.stream(
                "POST", "/v1/chat/completions", json=payload
            ) as response:
                if response.status_code != 200:
                    yield f"Error: Custom API returned {response.status_code}"
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
        finally:
            await client.aclose()


# Singleton instance
custom_api_service = CustomAPIService()
