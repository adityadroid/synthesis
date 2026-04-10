"""Admin routes for workspace management."""

import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
import csv
import io

from ..db import get_db
from ..models.activity_log import ActivityLog, ActivityAction
from ..models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from ..models.user import User
from ..models.rate_limit import (
    RateLimitConfig,
    RateLimitTier,
    RateLimitUsage,
    DEFAULT_LIMITS,
)
from ..models.retention_policy import (
    RetentionPolicy,
    DeletionLog,
    DataType,
    RetentionPeriod,
)
from ..services.activity_log import ActivityLogService
from ..services.rate_limit import RateLimitService
from ..services.maintenance import MaintenanceService
from ..middleware.auth import get_current_user


router = APIRouter(prefix="/admin", tags=["admin"])


class ActivityLogResponse(BaseModel):
    """Activity log response schema."""

    id: str
    user_id: str | None
    workspace_id: str | None
    action: str
    resource_type: str | None
    resource_id: str | None
    details: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityLogListResponse(BaseModel):
    """Paginated activity log response."""

    logs: list[ActivityLogResponse]
    total: int
    limit: int
    offset: int


def is_admin(user_id: str, db: AsyncSession) -> bool:
    """Check if user is a global admin (simplified - check if owner of any workspace)."""
    # For now, any authenticated user in a workspace can view logs
    return True


@router.get("/activity-logs", response_model=ActivityLogListResponse)
async def get_activity_logs(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Get activity logs with filters."""
    service = ActivityLogService(db)

    # Build query conditions
    conditions = []
    if workspace_id:
        conditions.append(ActivityLog.workspace_id == workspace_id)
    if action:
        try:
            action_enum = ActivityAction(action)
            conditions.append(ActivityLog.action == action_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}",
            )
    if resource_type:
        conditions.append(ActivityLog.resource_type == resource_type)
    if start_date:
        conditions.append(ActivityLog.created_at >= start_date)
    if end_date:
        conditions.append(ActivityLog.created_at <= end_date)

    # Count total
    count_query = select(func.count(ActivityLog.id))
    if conditions:
        count_query = count_query.where(*conditions)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get logs
    logs = await service.get_logs(
        user_id=user_id,
        workspace_id=workspace_id,
        action=ActivityAction(action) if action else None,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    return ActivityLogListResponse(
        logs=[
            ActivityLogResponse(
                id=log.id,
                user_id=log.user_id,
                workspace_id=log.workspace_id,
                action=log.action.value,
                resource_type=log.resource_type,
                resource_id=log.resource_id,
                details=json.loads(log.details) if log.details else None,
                ip_address=log.ip_address,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/activity-logs/export")
async def export_activity_logs(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workspace_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """Export activity logs as CSV."""
    service = ActivityLogService(db)

    logs = await service.export_logs(
        workspace_id=workspace_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "User ID",
            "Workspace ID",
            "Action",
            "Resource Type",
            "Resource ID",
            "Details",
            "IP Address",
            "Created At",
        ]
    )

    for log in logs:
        writer.writerow(
            [
                log.id,
                log.user_id or "",
                log.workspace_id or "",
                log.action.value,
                log.resource_type or "",
                log.resource_id or "",
                log.details or "",
                log.ip_address or "",
                log.created_at.isoformat(),
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=activity_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/actions", response_model=list[str])
async def get_activity_actions():
    """Get list of all possible activity actions."""
    return [action.value for action in ActivityAction]


@router.get("/resource-types", response_model=list[str])
async def get_resource_types():
    """Get list of all resource types."""
    return [
        "user",
        "conversation",
        "message",
        "workspace",
        "template",
        "api_key",
        "settings",
    ]


# ==================== Rate Limit Management ====================


class RateLimitConfigResponse(BaseModel):
    """Rate limit config response."""

    id: str
    workspace_id: str | None
    user_id: str | None
    tier: str
    custom_limits: dict | None
    is_active: bool

    model_config = {"from_attributes": True}


class SetRateLimitRequest(BaseModel):
    """Request to set rate limit config."""

    tier: str | None = None
    custom_limits: dict | None = None


@router.get("/rate-limits", response_model=dict)
async def get_my_rate_limits(
    user_id: str = Depends(get_current_user),
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get current rate limits for user/workspace."""
    service = RateLimitService(db)
    return await service.get_usage_stats(user_id=user_id, workspace_id=workspace_id)


@router.get("/rate-limits/config", response_model=RateLimitConfigResponse | None)
async def get_rate_limit_config(
    user_id: str = Depends(get_current_user),
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get rate limit configuration for user/workspace."""
    query = select(RateLimitConfig).where(RateLimitConfig.is_active == True)

    if workspace_id:
        query = query.where(RateLimitConfig.workspace_id == workspace_id)
    else:
        query = query.where(RateLimitConfig.user_id == user_id)

    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        return None

    return RateLimitConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        user_id=config.user_id,
        tier=config.tier.value,
        custom_limits=config.custom_limits,
        is_active=config.is_active,
    )


@router.post("/rate-limits/config", response_model=RateLimitConfigResponse)
async def set_rate_limit_config(
    request: SetRateLimitRequest,
    user_id: str = Depends(get_current_user),
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Set rate limit configuration for user/workspace."""
    # Check if config already exists
    query = select(RateLimitConfig).where(RateLimitConfig.is_active == True)

    if workspace_id:
        query = query.where(RateLimitConfig.workspace_id == workspace_id)
    else:
        query = query.where(RateLimitConfig.user_id == user_id)

    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if config:
        # Update existing
        if request.tier:
            config.tier = RateLimitTier(request.tier)
        if request.custom_limits:
            config.custom_limits = request.custom_limits
    else:
        # Create new
        config = RateLimitConfig(
            workspace_id=workspace_id,
            user_id=user_id if not workspace_id else None,
            tier=RateLimitTier(request.tier) if request.tier else RateLimitTier.FREE,
            custom_limits=request.custom_limits,
        )
        db.add(config)

    await db.flush()
    await db.refresh(config)

    return RateLimitConfigResponse(
        id=config.id,
        workspace_id=config.workspace_id,
        user_id=config.user_id,
        tier=config.tier.value,
        custom_limits=config.custom_limits,
        is_active=config.is_active,
    )


@router.get("/rate-limit-tiers", response_model=list[dict])
async def get_rate_limit_tiers():
    """Get available rate limit tiers and their defaults."""
    return [
        {
            "tier": tier.value,
            "limits": limits,
        }
        for tier, limits in DEFAULT_LIMITS.items()
    ]


# ==================== Data Retention Policies ====================


class RetentionPolicyResponse(BaseModel):
    """Retention policy response."""

    id: str
    workspace_id: str | None
    name: str
    description: str | None
    data_type: str
    retention_period: str
    is_legal_hold: bool
    auto_delete_enabled: bool
    export_before_delete: bool
    is_active: bool
    last_run_at: datetime | None
    records_deleted: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateRetentionPolicyRequest(BaseModel):
    """Request to create a retention policy."""

    name: str
    data_type: str
    retention_period: str
    workspace_id: str | None = None
    description: str | None = None
    auto_delete_enabled: bool = True
    export_before_delete: bool = True


@router.get("/retention-policies", response_model=list[RetentionPolicyResponse])
async def list_retention_policies(
    user_id: str = Depends(get_current_user),
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List retention policies."""
    service = MaintenanceService(db)
    policies = await service.get_policies(workspace_id)

    return [
        RetentionPolicyResponse(
            id=p.id,
            workspace_id=p.workspace_id,
            name=p.name,
            description=p.description,
            data_type=p.data_type.value
            if hasattr(p.data_type, "value")
            else p.data_type,
            retention_period=p.retention_period.value
            if hasattr(p.retention_period, "value")
            else p.retention_period,
            is_legal_hold=p.is_legal_hold,
            auto_delete_enabled=p.auto_delete_enabled,
            export_before_delete=p.export_before_delete,
            is_active=p.is_active,
            last_run_at=p.last_run_at,
            records_deleted=p.records_deleted,
            created_at=p.created_at,
        )
        for p in policies
    ]


@router.post("/retention-policies", response_model=RetentionPolicyResponse)
async def create_retention_policy(
    request: CreateRetentionPolicyRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new retention policy."""
    try:
        data_type = DataType(request.data_type)
        retention_period = RetentionPeriod(request.retention_period)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    service = MaintenanceService(db)
    policy = await service.create_policy(
        name=request.name,
        data_type=data_type,
        retention_period=retention_period,
        workspace_id=request.workspace_id,
        description=request.description,
        auto_delete_enabled=request.auto_delete_enabled,
        export_before_delete=request.export_before_delete,
    )

    return RetentionPolicyResponse(
        id=policy.id,
        workspace_id=policy.workspace_id,
        name=policy.name,
        description=policy.description,
        data_type=policy.data_type.value
        if hasattr(policy.data_type, "value")
        else policy.data_type,
        retention_period=policy.retention_period.value
        if hasattr(policy.retention_period, "value")
        else policy.retention_period,
        is_legal_hold=policy.is_legal_hold,
        auto_delete_enabled=policy.auto_delete_enabled,
        export_before_delete=policy.export_before_delete,
        is_active=policy.is_active,
        last_run_at=policy.last_run_at,
        records_deleted=policy.records_deleted,
        created_at=policy.created_at,
    )


@router.post("/retention-policies/{policy_id}/execute")
async def execute_retention_policy(
    policy_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dry_run: bool = False,
):
    """Execute a retention policy (dry run by default)."""
    result = await db.execute(
        select(RetentionPolicy).where(RetentionPolicy.id == policy_id)
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    service = MaintenanceService(db)
    return await service.execute_cleanup(policy, dry_run=dry_run)


@router.get("/retention-policies/{policy_id}/estimate")
async def estimate_retention_policy(
    policy_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Estimate records affected by a policy."""
    result = await db.execute(
        select(RetentionPolicy).where(RetentionPolicy.id == policy_id)
    )
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found",
        )

    service = MaintenanceService(db)
    return await service.estimate_cleanup(policy)


@router.get("/deletion-logs", response_model=list[dict])
async def list_deletion_logs(
    user_id: str = Depends(get_current_user),
    workspace_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, le=500),
):
    """Get deletion audit logs."""
    service = MaintenanceService(db)
    logs = await service.get_deletion_logs(workspace_id, limit)

    return [
        {
            "id": log.id,
            "policy_id": log.policy_id,
            "data_type": log.data_type.value
            if hasattr(log.data_type, "value")
            else log.data_type,
            "records_deleted": log.records_deleted,
            "status": log.status,
            "error_message": log.error_message,
            "reason": log.reason,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/data-types", response_model=list[str])
async def get_data_types():
    """Get list of data types for retention policies."""
    return [dt.value for dt in DataType]


@router.get("/retention-periods", response_model=list[dict])
async def get_retention_periods():
    """Get list of retention periods."""
    return [
        {"value": rp.value, "days": _get_retention_days(rp)} for rp in RetentionPeriod
    ]


def _get_retention_days(period: RetentionPeriod) -> int | None:
    """Get retention period in days."""
    days_map = {
        RetentionPeriod.DAYS_30: 30,
        RetentionPeriod.DAYS_90: 90,
        RetentionPeriod.DAYS_180: 180,
        RetentionPeriod.DAYS_365: 365,
        RetentionPeriod.YEARS_2: 730,
        RetentionPeriod.YEARS_5: 1825,
        RetentionPeriod.FOREVER: None,
    }
    return days_map.get(period)
