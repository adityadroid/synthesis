"""Routes for conversation export and import."""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Conversation
from ..services.export import export_service
from ..services import conversation as conversation_service
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "markdown",
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export a conversation in the specified format.

    Formats: markdown, json, pdf
    """
    conversation = await conversation_service.get_conversation(
        db, conversation_id, user_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await conversation_service.get_conversation_messages(db, conversation_id)

    conv_dict = {
        "id": conversation.id,
        "title": conversation.title,
        "model": conversation.model,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }

    msgs_dict = [
        {
            "id": m.id,
            "role": m.role.value if hasattr(m.role, "value") else m.role,
            "content": m.content,
            "token_count": m.token_count,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]

    if format == "json":
        content = export_service.export_to_json(conv_dict, msgs_dict)
        filename = f"{conversation.title or 'conversation'}.json"
        return {
            "content": content,
            "filename": filename,
            "content_type": "application/json",
        }

    elif format == "pdf":
        # Return HTML that can be converted to PDF client-side
        content = await export_service.export_to_pdf_html(conv_dict, msgs_dict)
        filename = f"{conversation.title or 'conversation'}.html"
        return {
            "content": content,
            "filename": filename,
            "content_type": "text/html",
        }

    else:  # markdown (default)
        content = export_service.export_to_markdown(conv_dict, msgs_dict)
        filename = f"{conversation.title or 'conversation'}.md"
        return {
            "content": content,
            "filename": filename,
            "content_type": "text/markdown",
        }


@router.post("/import")
async def import_conversation(
    file_content: str,
    format: str = "json",
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import a conversation from JSON or Markdown format.

    Creates a new conversation with the imported messages.
    """
    try:
        if format == "json":
            data = export_service.import_from_json(file_content)
        elif format == "markdown":
            data = export_service.import_from_markdown(file_content)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format. Use 'json' or 'markdown'.",
            )

        conversation_data = data["conversation"]
        messages_data = data["messages"]

        # Create new conversation
        new_conversation = await conversation_service.create_conversation(
            db, user_id, title=conversation_data.get("title", "Imported Conversation")
        )

        # Import messages
        from ..models import MessageRole

        for msg_data in messages_data:
            role_str = msg_data.get("role", "user")
            role = MessageRole.USER if role_str == "user" else MessageRole.ASSISTANT

            await conversation_service.add_message(
                db,
                new_conversation.id,
                role,
                msg_data.get("content", ""),
            )

        return {
            "conversation_id": new_conversation.id,
            "title": new_conversation.title,
            "message_count": len(messages_data),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
