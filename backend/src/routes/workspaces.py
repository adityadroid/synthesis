"""Workspace routes for team collaboration."""

import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr

from ..db import get_db
from ..models import (
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceInvite,
    WorkspaceConversation,
    WorkspaceRole,
    WorkspaceInviteStatus,
)
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# Request/Response schemas
class CreateWorkspaceRequest(BaseModel):
    name: str
    description: str | None = None


class UpdateWorkspaceRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    is_default: bool
    created_at: str
    updated_at: str
    my_role: str | None = None

    model_config = {"from_attributes": True}


class WorkspaceMemberResponse(BaseModel):
    id: str
    user_id: str
    user_email: str | None = None
    user_name: str | None = None
    role: str
    joined_at: str

    model_config = {"from_attributes": True}


class CreateInviteRequest(BaseModel):
    email: str
    role: str = "member"


class InviteResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    token: str
    expires_at: str
    invited_by_email: str | None = None

    model_config = {"from_attributes": True}


class ShareConversationRequest(BaseModel):
    conversation_id: str
    visibility: str = "workspace"


class SharedConversationResponse(BaseModel):
    id: str
    conversation_id: str
    conversation_title: str | None
    visibility: str
    shared_by_email: str | None = None
    created_at: str


# Helper functions
async def get_workspace_with_role(
    db: AsyncSession, workspace_id: str, user_id: str
) -> tuple[Workspace | None, WorkspaceRole | None]:
    """Get workspace and user's role in it."""
    # Check if user is owner
    result = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id, Workspace.owner_id == user_id
        )
    )
    workspace = result.scalar_one_or_none()
    if workspace:
        return workspace, WorkspaceRole.OWNER

    # Check membership
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(Workspace.id == workspace_id, WorkspaceMember.user_id == user_id)
    )
    workspace = result.scalar_one_or_none()
    if workspace:
        member_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        member = member_result.scalar_one_or_none()
        return workspace, member.role if member else None

    return None, None


def check_permission(role: WorkspaceRole | None, required: list[WorkspaceRole]) -> bool:
    """Check if role has required permissions."""
    if role is None:
        return False
    return role in required


# Routes
@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all workspaces the user has access to."""
    # Get owned workspaces
    result = await db.execute(select(Workspace).where(Workspace.owner_id == user_id))
    owned = result.scalars().all()

    # Get member workspaces
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == user_id)
    )
    member_of = result.scalars().all()

    # Combine and build response
    workspaces = []
    for w in owned:
        workspaces.append(
            WorkspaceResponse(
                id=w.id,
                name=w.name,
                description=w.description,
                owner_id=w.owner_id,
                is_default=w.is_default,
                created_at=w.created_at.isoformat(),
                updated_at=w.updated_at.isoformat(),
                my_role=WorkspaceRole.OWNER.value,
            )
        )

    for w in member_of:
        member_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == w.id, WorkspaceMember.user_id == user_id
            )
        )
        member = member_result.scalar_one_or_none()
        workspaces.append(
            WorkspaceResponse(
                id=w.id,
                name=w.name,
                description=w.description,
                owner_id=w.owner_id,
                is_default=w.is_default,
                created_at=w.created_at.isoformat(),
                updated_at=w.updated_at.isoformat(),
                my_role=member.role.value if member else None,
            )
        )

    return workspaces


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(
    request: CreateWorkspaceRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace."""
    workspace = Workspace(
        id=str(uuid.uuid4()),
        name=request.name,
        description=request.description,
        owner_id=user_id,
        is_default=False,
    )
    db.add(workspace)

    # Add owner as a member
    member = WorkspaceMember(
        id=str(uuid.uuid4()),
        workspace_id=workspace.id,
        user_id=user_id,
        role=WorkspaceRole.OWNER,
    )
    db.add(member)

    await db.flush()
    await db.refresh(workspace)

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        owner_id=workspace.owner_id,
        is_default=workspace.is_default,
        created_at=workspace.created_at.isoformat(),
        updated_at=workspace.updated_at.isoformat(),
        my_role=WorkspaceRole.OWNER.value,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a workspace by ID."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        owner_id=workspace.owner_id,
        is_default=workspace.is_default,
        created_at=workspace.created_at.isoformat(),
        updated_at=workspace.updated_at.isoformat(),
        my_role=role.value if role else None,
    )


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    request: UpdateWorkspaceRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a workspace (owner/admin only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if not check_permission(role, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this workspace",
        )

    if request.name is not None:
        workspace.name = request.name
    if request.description is not None:
        workspace.description = request.description
    workspace.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(workspace)

    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        owner_id=workspace.owner_id,
        is_default=workspace.is_default,
        created_at=workspace.created_at.isoformat(),
        updated_at=workspace.updated_at.isoformat(),
        my_role=role.value if role else None,
    )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a workspace (owner only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if role != WorkspaceRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this workspace",
        )

    await db.delete(workspace)
    await db.flush()

    return {"message": "Workspace deleted successfully"}


# Member management
@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberResponse])
async def list_members(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all members of a workspace."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    result = await db.execute(
        select(WorkspaceMember, User)
        .join(User, WorkspaceMember.user_id == User.id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    members = result.all()

    return [
        WorkspaceMemberResponse(
            id=m.id,
            user_id=m.user_id,
            user_email=u.email,
            user_name=u.full_name,
            role=m.role.value,
            joined_at=m.joined_at.isoformat(),
        )
        for m, u in members
    ]


@router.delete("/{workspace_id}/members/{member_id}")
async def remove_member(
    workspace_id: str,
    member_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from workspace (admin/owner only, or self-leave)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # Get the member to remove
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.id == member_id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    # Check permissions
    can_remove = (
        role in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]  # Admin action
        or member.user_id == user_id  # Self-leave
    )

    if not can_remove:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove this member",
        )

    # Can't remove the owner
    if member.role == WorkspaceRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the workspace owner",
        )

    await db.delete(member)
    await db.flush()

    return {"message": "Member removed successfully"}


@router.patch("/{workspace_id}/members/{member_id}/role")
async def update_member_role(
    workspace_id: str,
    member_id: str,
    request: dict,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a member's role (owner only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if role != WorkspaceRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can change roles",
        )

    new_role = request.get("role")
    if new_role not in [r.value for r in WorkspaceRole]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )

    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.id == member_id,
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    if member.role == WorkspaceRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change the owner's role",
        )

    member.role = WorkspaceRole(new_role)
    await db.flush()

    return {"message": "Role updated successfully"}


# Invitations
@router.get("/{workspace_id}/invites", response_model=list[InviteResponse])
async def list_invites(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pending invites (admin/owner only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if not check_permission(role, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view invites",
        )

    result = await db.execute(
        select(WorkspaceInvite, User)
        .join(User, WorkspaceInvite.invited_by == User.id)
        .where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.status == WorkspaceInviteStatus.PENDING,
        )
    )
    invites = result.all()

    return [
        InviteResponse(
            id=i.id,
            email=i.email,
            role=i.role.value,
            status=i.status.value,
            token=i.token,
            expires_at=i.expires_at.isoformat(),
            invited_by_email=u.email if u else None,
        )
        for i, u in invites
    ]


@router.post("/{workspace_id}/invites", response_model=InviteResponse)
async def create_invite(
    workspace_id: str,
    request: CreateInviteRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create an invite to the workspace (admin/owner only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if not check_permission(role, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to invite members",
        )

    token, expires_at = WorkspaceInvite.create_expiring_token()

    invite = WorkspaceInvite(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        email=request.email,
        role=WorkspaceRole(request.role),
        status=WorkspaceInviteStatus.PENDING,
        invited_by=user_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(invite)
    await db.flush()
    await db.refresh(invite)

    # Get inviter email
    user_result = await db.execute(select(User).where(User.id == user_id))
    inviter = user_result.scalar_one_or_none()

    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role.value,
        status=invite.status.value,
        token=invite.token,
        expires_at=invite.expires_at.isoformat(),
        invited_by_email=inviter.email if inviter else None,
    )


@router.post("/invites/{token}/accept")
async def accept_invite(
    token: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept a workspace invite."""
    result = await db.execute(
        select(WorkspaceInvite).where(WorkspaceInvite.token == token)
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    if invite.status != WorkspaceInviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite is no longer valid",
        )

    if invite.expires_at < datetime.utcnow():
        invite.status = WorkspaceInviteStatus.EXPIRED
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite has expired",
        )

    # Get user email to verify
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user or user.email.lower() != invite.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite was sent to a different email",
        )

    # Check if already a member
    existing = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invite.workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this workspace",
        )

    # Add as member
    member = WorkspaceMember(
        id=str(uuid.uuid4()),
        workspace_id=invite.workspace_id,
        user_id=user_id,
        role=invite.role,
    )
    db.add(member)

    # Update invite status
    invite.status = WorkspaceInviteStatus.ACCEPTED
    invite.accepted_at = datetime.utcnow()

    await db.flush()

    return {"message": "Invite accepted", "workspace_id": invite.workspace_id}


@router.delete("/{workspace_id}/invites/{invite_id}")
async def revoke_invite(
    workspace_id: str,
    invite_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an invite (admin/owner only)."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    if not check_permission(role, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke invites",
        )

    result = await db.execute(
        select(WorkspaceInvite).where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.id == invite_id,
        )
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    await db.delete(invite)
    await db.flush()

    return {"message": "Invite revoked successfully"}


# Shared conversations
@router.get(
    "/{workspace_id}/conversations", response_model=list[SharedConversationResponse]
)
async def list_shared_conversations(
    workspace_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List shared conversations in a workspace."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    result = await db.execute(
        select(WorkspaceConversation, User)
        .join(User, WorkspaceConversation.shared_by == User.id)
        .where(WorkspaceConversation.workspace_id == workspace_id)
    )
    shared = result.all()

    # Get conversation titles
    response = []
    for wc, u in shared:
        conv_result = await db.execute(
            select(Conversation).where(Conversation.id == wc.conversation_id)
        )
        conv = conv_result.scalar_one_or_none()
        response.append(
            SharedConversationResponse(
                id=wc.id,
                conversation_id=wc.conversation_id,
                conversation_title=conv.title if conv else None,
                visibility=wc.visibility,
                shared_by_email=u.email if u else None,
                created_at=wc.created_at.isoformat(),
            )
        )

    return response


@router.post("/{workspace_id}/conversations", response_model=SharedConversationResponse)
async def share_conversation(
    workspace_id: str,
    request: ShareConversationRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Share a conversation to the workspace."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # Check conversation ownership
    conv_result = await db.execute(
        select(Conversation).where(
            Conversation.id == request.conversation_id, Conversation.user_id == user_id
        )
    )
    conv = conv_result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or not owned by you",
        )

    shared = WorkspaceConversation(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        conversation_id=request.conversation_id,
        shared_by=user_id,
        visibility=request.visibility,
    )
    db.add(shared)
    await db.flush()

    return SharedConversationResponse(
        id=shared.id,
        conversation_id=shared.conversation_id,
        conversation_title=conv.title,
        visibility=shared.visibility,
        shared_by_email=None,
        created_at=shared.created_at.isoformat(),
    )


@router.delete("/{workspace_id}/conversations/{conversation_id}")
async def unshare_conversation(
    workspace_id: str,
    conversation_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unshare a conversation from the workspace."""
    workspace, role = await get_workspace_with_role(db, workspace_id, user_id)

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    result = await db.execute(
        select(WorkspaceConversation).where(
            WorkspaceConversation.workspace_id == workspace_id,
            WorkspaceConversation.conversation_id == conversation_id,
            WorkspaceConversation.shared_by == user_id,
        )
    )
    shared = result.scalar_one_or_none()

    if not shared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared conversation not found",
        )

    await db.delete(shared)
    await db.flush()

    return {"message": "Conversation unshared"}


# Import Conversation model
from ..models.conversation import Conversation
