"""Activity log service for audit trail."""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from ..models.activity_log import ActivityLog, ActivityAction


class ActivityLogService:
    """Service for recording and querying activity logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: ActivityAction,
        user_id: str | None = None,
        workspace_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ActivityLog:
        """Log an activity event."""
        import json

        log_entry = ActivityLog(
            action=action,
            user_id=user_id,
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(log_entry)
        await self.db.flush()
        await self.db.refresh(log_entry)
        return log_entry

    async def get_logs(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
        action: ActivityAction | None = None,
        resource_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ActivityLog]:
        """Query activity logs with filters."""
        query = select(ActivityLog)

        conditions = []
        if user_id:
            conditions.append(ActivityLog.user_id == user_id)
        if workspace_id:
            conditions.append(ActivityLog.workspace_id == workspace_id)
        if action:
            conditions.append(ActivityLog.action == action)
        if resource_type:
            conditions.append(ActivityLog.resource_type == resource_type)
        if start_date:
            conditions.append(ActivityLog.created_at >= start_date)
        if end_date:
            conditions.append(ActivityLog.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(ActivityLog.created_at))
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def export_logs(
        self,
        user_id: str | None = None,
        workspace_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[ActivityLog]:
        """Export logs for compliance reporting."""
        return await self.get_logs(
            user_id=user_id,
            workspace_id=workspace_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Export limit
            offset=0,
        )
