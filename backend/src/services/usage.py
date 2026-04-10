"""Token counting and cost estimation service."""

from typing import Optional


# Token pricing per 1M tokens (as of 2024)
TOKEN_PRICING = {
    # OpenAI
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
    # Anthropic
    "claude-3-5-sonnet-latest": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-latest": {"input": 0.8, "output": 4.0},
    "claude-3-opus-latest": {"input": 15.0, "output": 75.0},
    # Ollama (free, local)
    "ollama/*": {"input": 0.0, "output": 0.0},
    # LM Studio (free, local)
    "lm-studio/*": {"input": 0.0, "output": 0.0},
}


class TokenCounter:
    """Service for token counting and cost estimation."""

    # Rough estimate: ~4 characters per token for English
    CHARS_PER_TOKEN = 4

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (simple approximation)."""
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN)

    def estimate_message_tokens(
        self,
        role: str,
        content: str,
    ) -> int:
        """
        Estimate tokens for a message including overhead.

        OpenAI charges ~3-4 tokens overhead per message
        plus the content tokens.
        """
        content_tokens = self.estimate_tokens(content)
        overhead = 4  # Conservative estimate
        return content_tokens + overhead

    def estimate_conversation_tokens(
        self,
        messages: list[dict],
    ) -> int:
        """Estimate total tokens for a conversation."""
        total = 0
        for msg in messages:
            total += self.estimate_message_tokens(
                msg.get("role", "user"),
                msg.get("content", ""),
            )
        # Add overhead for message array structure
        total += 3
        return total

    def get_model_pricing(self, model: str) -> dict:
        """Get pricing for a model."""
        # Try exact match first
        if model in TOKEN_PRICING:
            return TOKEN_PRICING[model]

        # Try prefix match for wildcards
        for key, pricing in TOKEN_PRICING.items():
            if key.endswith("/*"):
                prefix = key[:-2]
                if model.startswith(prefix):
                    return pricing

        # Default pricing (assume OpenAI GPT-3.5 if unknown)
        return {"input": 0.5, "output": 1.5}

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost in USD for given token counts."""
        pricing = self.get_model_pricing(model)

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def estimate_message_cost(
        self,
        model: str,
        input_text: str,
        output_text: str,
    ) -> float:
        """Estimate cost for a single message exchange."""
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)
        return self.calculate_cost(model, input_tokens, output_tokens)

    def estimate_conversation_cost(
        self,
        model: str,
        messages: list[dict],
    ) -> float:
        """Estimate total cost for a conversation."""
        if not messages:
            return 0.0

        total_cost = 0.0

        for i, msg in enumerate(messages):
            # For assistant messages, we can count output tokens
            # For user/system messages, we count input tokens
            if msg.get("role") == "assistant":
                output_tokens = self.estimate_tokens(msg.get("content", ""))
                # Estimate input as the assistant's response context
                if i > 0:
                    prev_msg = messages[i - 1]
                    input_tokens = self.estimate_message_tokens(
                        prev_msg.get("role", "user"),
                        prev_msg.get("content", ""),
                    )
                    total_cost += self.calculate_cost(
                        model, input_tokens, output_tokens
                    )
            else:
                # Just track for future assistant response
                pass

        return total_cost


class UsageTracker:
    """Track usage statistics per user."""

    def __init__(self):
        self._usage: dict[str, dict] = {}

    def record_usage(
        self,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        conversation_id: str,
    ) -> dict:
        """Record a usage event."""
        if user_id not in self._usage:
            self._usage[user_id] = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "conversations": {},
                "models": {},
            }

        usage = self._usage[user_id]
        cost = TokenCounter().calculate_cost(model, input_tokens, output_tokens)

        # Update totals
        usage["total_input_tokens"] += input_tokens
        usage["total_output_tokens"] += output_tokens
        usage["total_cost"] += cost

        # Update conversation stats
        if conversation_id not in usage["conversations"]:
            usage["conversations"][conversation_id] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "message_count": 0,
            }

        conv_usage = usage["conversations"][conversation_id]
        conv_usage["input_tokens"] += input_tokens
        conv_usage["output_tokens"] += output_tokens
        conv_usage["cost"] += cost
        conv_usage["message_count"] += 1

        # Update model stats
        if model not in usage["models"]:
            usage["models"][model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "message_count": 0,
            }

        model_usage = usage["models"][model]
        model_usage["input_tokens"] += input_tokens
        model_usage["output_tokens"] += output_tokens
        model_usage["cost"] += cost
        model_usage["message_count"] += 1

        return {"cost": cost, "total_cost": usage["total_cost"]}

    def get_user_usage(self, user_id: str) -> dict:
        """Get usage statistics for a user."""
        return self._usage.get(
            user_id,
            {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "conversations": {},
                "models": {},
            },
        )

    def get_conversation_usage(self, user_id: str, conversation_id: str) -> dict:
        """Get usage for a specific conversation."""
        user_usage = self._usage.get(user_id, {})
        return user_usage.get("conversations", {}).get(
            conversation_id,
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "message_count": 0,
            },
        )


# Singleton instances
token_counter = TokenCounter()
usage_tracker = UsageTracker()
