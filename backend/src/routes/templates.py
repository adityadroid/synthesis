"""Template routes."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from datetime import datetime

from ..db import get_db
from ..models.template import Template
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateResponse(BaseModel):
    """Template response schema."""

    id: str
    name: str
    description: str | None
    prompt: str
    category: str
    is_builtin: bool
    use_count: int

    model_config = {"from_attributes": True}


class CreateTemplateRequest(BaseModel):
    """Request to create a template."""

    name: str
    description: str | None = None
    prompt: str
    category: str = "other"


class UpdateTemplateRequest(BaseModel):
    """Request to update a template."""

    name: str | None = None
    description: str | None = None
    prompt: str | None = None
    category: str | None = None


# Built-in templates
BUILTIN_TEMPLATES = [
    {
        "id": "builtin-1",
        "name": "Code Review",
        "description": "Get a thorough code review with suggestions for improvement",
        "prompt": "Please review the following code. Provide feedback on:\n1. Code quality and readability\n2. Potential bugs or issues\n3. Performance considerations\n4. Security concerns\n5. Best practices\n\nHere's the code:\n```\n[PASTE YOUR CODE HERE]\n```",
        "category": "coding",
    },
    {
        "id": "builtin-2",
        "name": "Explain Like I'm 5",
        "description": "Get a complex topic explained simply",
        "prompt": "Explain the following concept in the simplest way possible, as if explaining to a 5-year-old. Use simple words and relatable examples.\n\nTopic: [YOUR TOPIC HERE]",
        "category": "learning",
    },
    {
        "id": "builtin-3",
        "name": "Brainstorm Ideas",
        "description": "Generate creative ideas for any topic",
        "prompt": "Help me brainstorm ideas for [YOUR TOPIC OR PROBLEM]. Generate diverse and creative suggestions, including:\n- Practical solutions\n- Out-of-the-box ideas\n- Unexpected angles\n\nList at least 10 ideas with brief explanations.",
        "category": "brainstorm",
    },
    {
        "id": "builtin-4",
        "name": "Write Email",
        "description": "Draft professional emails quickly",
        "prompt": "Write a professional email for the following purpose:\n\nPurpose: [DESCRIBE THE EMAIL PURPOSE]\n\nTone: [FORMAL/CASUAL/FRIENDLY]\nKey points to include:\n1. [POINT 1]\n2. [POINT 2]\n3. [POINT 3]",
        "category": "writing",
    },
    {
        "id": "builtin-5",
        "name": "Debug Code",
        "description": "Debug and fix problematic code",
        "prompt": "Help me debug the following code. Identify the issues and provide corrected code with explanations.\n\nProblem description: [DESCRIBE THE ISSUE]\n\nCode:\n```\n[YOUR CODE HERE]\n```\n\nError message (if any):\n[PASTE ERROR MESSAGE]",
        "category": "coding",
    },
    {
        "id": "builtin-6",
        "name": "Learn Something New",
        "description": "Structured learning about any topic",
        "prompt": "Teach me about [TOPIC]. Include:\n1. Core concepts (definition and importance)\n2. Real-world examples\n3. Common use cases\n4. Key terminology\n5. Resources for further learning",
        "category": "learning",
    },
    {
        "id": "builtin-7",
        "name": "Analyze Data",
        "description": "Analyze and interpret data",
        "prompt": "Analyze the following data and provide insights:\n\nData:\n[PASTE YOUR DATA]\n\nPlease include:\n1. Key trends and patterns\n2. Statistical summary\n3. Anomalies or outliers\n4. Recommendations based on the data",
        "category": "analysis",
    },
    {
        "id": "builtin-8",
        "name": "Writing Assistant",
        "description": "Help with writing tasks",
        "prompt": "Help me with the following writing task:\n\nType of writing: [ESSAY/BLOG POST/REPORT/OTHER]\nTopic: [TOPIC]\nTarget audience: [AUDIENCE]\nWord count target: [NUMBER] words\nTone: [TONE/STYLE]\n\nKey points to cover:\n1. [POINT 1]\n2. [POINT 2]\n3. [POINT 3]",
        "category": "writing",
    },
]


@router.get("", response_model=list[TemplateResponse])
async def get_templates(
    category: str | None = None,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all templates (builtin + user-created)."""
    templates = []

    # Get builtin templates
    for t in BUILTIN_TEMPLATES:
        templates.append(
            TemplateResponse(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                prompt=t["prompt"],
                category=t["category"],
                is_builtin=True,
                use_count=0,
            )
        )

    # Get user's custom templates
    query = select(Template).where(Template.user_id == user_id)
    if category:
        query = query.where(Template.category == category)
    query = query.order_by(desc(Template.use_count), desc(Template.created_at))

    result = await db.execute(query)
    user_templates = result.scalars().all()

    for t in user_templates:
        templates.append(
            TemplateResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                prompt=t.prompt,
                category=t.category,
                is_builtin=False,
                use_count=t.use_count,
            )
        )

    return templates


@router.get("/categories", response_model=list[str])
async def get_categories():
    """Get all available template categories."""
    return [
        "coding",
        "writing",
        "analysis",
        "brainstorm",
        "learning",
        "productivity",
        "other",
    ]


@router.post("", response_model=TemplateResponse)
async def create_template(
    request: CreateTemplateRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation template."""
    template = Template(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        prompt=request.prompt,
        category=request.category,
        user_id=user_id,
        is_builtin=False,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)

    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        prompt=template.prompt,
        category=template.category,
        is_builtin=False,
        use_count=0,
    )


@router.post("/{template_id}/use", response_model=TemplateResponse)
async def use_template(
    template_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Increment usage count for a template."""
    # Check builtin templates first
    for t in BUILTIN_TEMPLATES:
        if t["id"] == template_id:
            return TemplateResponse(
                id=t["id"],
                name=t["name"],
                description=t["description"],
                prompt=t["prompt"],
                category=t["category"],
                is_builtin=True,
                use_count=0,
            )

    # Check user templates
    result = await db.execute(
        select(Template).where(
            Template.id == template_id,
            Template.user_id == user_id,
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    template.use_count += 1
    await db.flush()

    return TemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        prompt=template.prompt,
        category=template.category,
        is_builtin=False,
        use_count=template.use_count,
    )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user-created template."""
    result = await db.execute(
        select(Template).where(
            Template.id == template_id,
            Template.user_id == user_id,
            Template.is_builtin == False,
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or cannot delete builtin templates",
        )

    await db.delete(template)
    await db.flush()

    return {"message": "Template deleted successfully"}
