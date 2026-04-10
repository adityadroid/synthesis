"""Conversation service for managing chat threads."""

from datetime import datetime
from typing import Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Conversation, Message, MessageRole
from ..models.chat import ConversationResponse


async def create_conversation(
    db: AsyncSession,
    user_id: str,
    title: str | None = None,
    model: str | None = None,
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        title=title,
        model=model,
    )
    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)
    return conversation


async def get_conversation(
    db: AsyncSession,
    conversation_id: str,
    user_id: str,
) -> Conversation | None:
    """Get a conversation by ID for a specific user."""
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_default_conversation(
    db: AsyncSession,
    user_id: str,
) -> Conversation:
    """Get or create the default conversation for a user."""
    # Get the most recent conversation
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        # Create a new conversation
        conversation = await create_conversation(db, user_id, title="New Chat")
    return conversation


async def add_message(
    db: AsyncSession,
    conversation_id: str,
    role: MessageRole,
    content: str,
    token_count: int | None = None,
) -> Message:
    """Add a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        token_count=token_count,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_message(
    db: AsyncSession,
    message_id: str,
) -> Message | None:
    """Get a message by ID."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalar_one_or_none()


async def update_message(
    db: AsyncSession,
    message_id: str,
    content: str,
) -> Message | None:
    """Update a message's content."""
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    if message:
        message.content = content
        await db.flush()
        await db.refresh(message)
    return message


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: str,
) -> list[Message]:
    """Get all messages for a conversation in chronological order."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def update_conversation_title(
    db: AsyncSession,
    conversation_id: str,
    title: str,
) -> Conversation | None:
    """Update conversation title."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        await db.flush()
        await db.refresh(conversation)
    return conversation


def to_conversation_response(conversation: Conversation) -> ConversationResponse:
    """Convert conversation model to response."""
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        model=conversation.model,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )
