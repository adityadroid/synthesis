"""Pydantic models for chat."""

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Send message request schema."""

    message: str = Field(min_length=1)
    conversation_id: str | None = None


class MessageResponse(BaseModel):
    """Message response schema."""

    id: str
    role: str
    content: str
    token_count: int | None
    created_at: str

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation response schema."""

    id: str
    title: str | None
    model: str | None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Chat response schema."""

    message: MessageResponse
    conversation: ConversationResponse


class StreamChunk(BaseModel):
    """Streaming chunk schema."""

    content: str
    done: bool = False
