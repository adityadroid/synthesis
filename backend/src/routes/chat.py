"""Chat routes for messaging and streaming."""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import MessageRole
from ..models.chat import (
    SendMessageRequest,
    UpdateMessageRequest,
    MessageResponse,
    ConversationResponse,
    ChatResponse,
    StreamChunk,
)
from ..services import auth as auth_service
from ..services import conversation as conversation_service
from ..services.llm import llm_service
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and get an immediate response (non-streaming).
    Creates a conversation if none exists.
    """
    # Get or create conversation
    if request.conversation_id:
        conversation = await conversation_service.get_conversation(
            db, request.conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Get or create default conversation
        conversation = await conversation_service.get_or_create_default_conversation(
            db, user_id
        )

    # Add user message to conversation
    user_message = await conversation_service.add_message(
        db, conversation.id, MessageRole.USER, request.message
    )

    # Get conversation history for context
    history = await conversation_service.get_conversation_messages(db, conversation.id)

    # Build messages for LLM
    messages = llm_service.build_messages(history, request.message)

    # Get LLM response
    response_content = await llm_service.chat(messages)

    # Add assistant message to conversation
    assistant_message = await conversation_service.add_message(
        db, conversation.id, MessageRole.ASSISTANT, response_content
    )

    # Update conversation title if it's the first message
    if not conversation.title:
        title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        await conversation_service.update_conversation_title(db, conversation.id, title)
        await conversation_service.get_conversation(db, conversation.id, user_id)

    return ChatResponse(
        message=MessageResponse(
            id=assistant_message.id,
            role=assistant_message.role,
            content=assistant_message.content,
            token_count=assistant_message.token_count,
            created_at=assistant_message.created_at.isoformat(),
        ),
        conversation=ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            model=conversation.model,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        ),
    )


@router.get("/conversations")
async def get_conversations(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all conversations for the current user."""
    from sqlalchemy import select, desc
    from ..models import Conversation

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
    )
    conversations = result.scalars().all()

    return [
        ConversationResponse(
            id=c.id,
            title=c.title,
            model=c.model,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages for a conversation."""
    conversation = await conversation_service.get_conversation(
        db, conversation_id, user_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await conversation_service.get_conversation_messages(db, conversation_id)

    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            token_count=m.token_count,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.patch("/messages/{message_id}")
async def update_message(
    message_id: str,
    request: UpdateMessageRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update/edit a message. Only user messages can be edited.
    """
    message = await conversation_service.get_message(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Verify ownership
    conversation = await conversation_service.get_conversation(
        db, message.conversation_id, user_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this message",
        )

    # Only allow editing user messages
    if message.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only edit user messages",
        )

    # Update the message
    updated = await conversation_service.update_message(db, message_id, request.content)

    return MessageResponse(
        id=updated.id,
        role=updated.role,
        content=updated.content,
        token_count=updated.token_count,
        created_at=updated.created_at.isoformat(),
    )


async def generate_stream(
    db: AsyncSession,
    conversation_id: str,
    user_message: str,
    user_id: str,
) -> AsyncGenerator[str, None]:
    """Generate streaming response."""
    # Get conversation history
    history = await conversation_service.get_conversation_messages(db, conversation_id)

    # Build messages for LLM
    messages = llm_service.build_messages(history, user_message)

    # Stream the response
    full_response = ""
    async for chunk in llm_service.stream_chat(messages):
        full_response += chunk
        yield f"data: {StreamChunk(content=chunk).model_dump_json()}\n\n"

    # Store the complete message
    await conversation_service.add_message(
        db, conversation_id, MessageRole.ASSISTANT, full_response
    )

    # Send done message
    yield f"data: {StreamChunk(content='', done=True).model_dump_json()}\n\n"


@router.post("/stream/{conversation_id}")
async def stream_message(
    conversation_id: str,
    request: SendMessageRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and get a streaming response via SSE.
    """
    # Verify conversation exists
    conversation = await conversation_service.get_conversation(
        db, conversation_id, user_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Add user message
    await conversation_service.add_message(
        db, conversation_id, MessageRole.USER, request.message
    )

    # Return streaming response
    return StreamingResponse(
        generate_stream(db, conversation_id, request.message, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
