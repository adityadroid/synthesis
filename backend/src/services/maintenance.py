"""Maintenance service for data retention and cleanup."""

import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_

from ..models.retention_policy import (
    RetentionPolicy,
    DeletionLog,
    DataType,
    RetentionPeriod,
)
from ..models.activity_log import ActivityLog, ActivityAction
from ..models.conversation import Conversation
from ..models.message import Message


class MaintenanceService:
    """Service for data retention policies and cleanup."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_policies(
        self,
        workspace_id: str | None = None,
    ) -> list[RetentionPolicy]:
        """Get retention policies."""
        query = select(RetentionPolicy).where(RetentionPolicy.is_active == True)
        if workspace_id:
            query = query.where(RetentionPolicy.workspace_id == workspace_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_policy(
        self,
        name: str,
        data_type: DataType,
        retention_period: RetentionPeriod,
        workspace_id: str | None = None,
        description: str | None = None,
        auto_delete_enabled: bool = True,
        export_before_delete: bool = True,
    ) -> RetentionPolicy:
        """Create a new retention policy."""
        policy = RetentionPolicy(
            name=name,
            data_type=data_type,
            retention_period=retention_period,
            workspace_id=workspace_id,
            description=description,
            auto_delete_enabled=auto_delete_enabled,
            export_before_delete=export_before_delete,
        )
        self.db.add(policy)
        await self.db.flush()
        await self.db.refresh(policy)
        return policy

    async def execute_cleanup(
        self,
        policy: RetentionPolicy,
        dry_run: bool = False,
    ) -> dict:
        """Execute data cleanup based on a policy."""
        if policy.is_legal_hold:
            return {
                "status": "skipped",
                "reason": "Legal hold is active",
                "records_affected": 0,
            }

        retention_days = policy.get_retention_days()
        if retention_days is None:
            return {
                "status": "skipped",
                "reason": "Retention is set to forever",
                "records_affected": 0,
            }

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        records_affected = 0

        try:
            if policy.data_type == DataType.CONVERSATIONS:
                records_affected = await self._cleanup_conversations(
                    cutoff_date, policy.workspace_id, dry_run
                )
            elif policy.data_type == DataType.MESSAGES:
                records_affected = await self._cleanup_messages(
                    cutoff_date, policy.workspace_id, dry_run
                )
            elif policy.data_type == DataType.ACTIVITY_LOGS:
                records_affected = await self._cleanup_activity_logs(
                    cutoff_date, policy.workspace_id, dry_run
                )

            if not dry_run:
                # Log the deletion
                log = DeletionLog(
                    policy_id=policy.id,
                    workspace_id=policy.workspace_id,
                    data_type=policy.data_type,
                    records_deleted=records_affected,
                    status="completed",
                    reason=f"Retention policy: {policy.name}",
                )
                self.db.add(log)

                # Update policy tracking
                policy.last_run_at = datetime.utcnow()
                policy.records_deleted += records_affected

                await self.db.flush()

            return {
                "status": "completed",
                "records_affected": records_affected,
                "cutoff_date": cutoff_date.isoformat(),
            }

        except Exception as e:
            if not dry_run:
                log = DeletionLog(
                    policy_id=policy.id,
                    workspace_id=policy.workspace_id,
                    data_type=policy.data_type,
                    records_deleted=0,
                    status="failed",
                    error_message=str(e),
                    reason=f"Retention policy: {policy.name}",
                )
                self.db.add(log)
                await self.db.flush()

            return {
                "status": "failed",
                "error": str(e),
                "records_affected": 0,
            }

    async def _cleanup_conversations(
        self,
        cutoff_date: datetime,
        workspace_id: str | None,
        dry_run: bool,
    ) -> int:
        """Clean up old conversations."""
        query = select(func.count(Conversation.id)).where(
            Conversation.created_at < cutoff_date
        )
        if workspace_id:
            query = query.where(Conversation.workspace_id == workspace_id)

        result = await self.db.execute(query)
        count = result.scalar()

        if not dry_run and count > 0:
            # First delete messages
            await self.db.execute(
                delete(Message).where(
                    Message.conversation_id.in_(
                        select(Conversation.id).where(
                            Conversation.created_at < cutoff_date
                        )
                    )
                )
            )
            # Then delete conversations
            delete_query = delete(Conversation).where(
                Conversation.created_at < cutoff_date
            )
            if workspace_id:
                delete_query = delete_query.where(
                    Conversation.workspace_id == workspace_id
                )
            await self.db.execute(delete_query)

        return count

    async def _cleanup_messages(
        self,
        cutoff_date: datetime,
        workspace_id: str | None,
        dry_run: bool,
    ) -> int:
        """Clean up old messages."""
        query = select(func.count(Message.id)).where(Message.created_at < cutoff_date)
        if workspace_id:
            query = query.where(
                Message.conversation_id.in_(
                    select(Conversation.id).where(
                        Conversation.workspace_id == workspace_id
                    )
                )
            )

        result = await self.db.execute(query)
        count = result.scalar()

        if not dry_run and count > 0:
            delete_query = delete(Message).where(Message.created_at < cutoff_date)
            if workspace_id:
                delete_query = delete_query.where(
                    Message.conversation_id.in_(
                        select(Conversation.id).where(
                            Conversation.workspace_id == workspace_id
                        )
                    )
                )
            await self.db.execute(delete_query)

        return count

    async def _cleanup_activity_logs(
        self,
        cutoff_date: datetime,
        workspace_id: str | None,
        dry_run: bool,
    ) -> int:
        """Clean up old activity logs."""
        query = select(func.count(ActivityLog.id)).where(
            ActivityLog.created_at < cutoff_date
        )
        if workspace_id:
            query = query.where(ActivityLog.workspace_id == workspace_id)

        result = await self.db.execute(query)
        count = result.scalar()

        if not dry_run and count > 0:
            delete_query = delete(ActivityLog).where(
                ActivityLog.created_at < cutoff_date
            )
            if workspace_id:
                delete_query = delete_query.where(
                    ActivityLog.workspace_id == workspace_id
                )
            await self.db.execute(delete_query)

        return count

    async def get_deletion_logs(
        self,
        workspace_id: str | None = None,
        limit: int = 100,
    ) -> list[DeletionLog]:
        """Get deletion audit logs."""
        query = select(DeletionLog).order_by(DeletionLog.created_at.desc()).limit(limit)

        if workspace_id:
            query = query.where(DeletionLog.workspace_id == workspace_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def estimate_cleanup(
        self,
        policy: RetentionPolicy,
    ) -> dict:
        """Estimate how many records would be affected."""
        retention_days = policy.get_retention_days()
        if retention_days is None:
            return {
                "retention_days": None,
                "records_affected": 0,
                "message": "Retention is set to forever",
            }

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        if policy.data_type == DataType.CONVERSATIONS:
            query = select(func.count(Conversation.id)).where(
                Conversation.created_at < cutoff_date
            )
        elif policy.data_type == DataType.MESSAGES:
            query = select(func.count(Message.id)).where(
                Message.created_at < cutoff_date
            )
        elif policy.data_type == DataType.ACTIVITY_LOGS:
            query = select(func.count(ActivityLog.id)).where(
                ActivityLog.created_at < cutoff_date
            )
        else:
            return {"error": "Unknown data type"}

        if policy.workspace_id:
            if policy.data_type == DataType.MESSAGES:
                query = query.where(
                    Message.conversation_id.in_(
                        select(Conversation.id).where(
                            Conversation.workspace_id == policy.workspace_id
                        )
                    )
                )
            elif policy.data_type == DataType.CONVERSATIONS:
                query = query.where(Conversation.workspace_id == policy.workspace_id)
            elif policy.data_type == DataType.ACTIVITY_LOGS:
                query = query.where(ActivityLog.workspace_id == policy.workspace_id)

        result = await self.db.execute(query)
        count = result.scalar()

        return {
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "records_affected": count,
            "data_type": policy.data_type.value
            if hasattr(policy.data_type, "value")
            else policy.data_type,
        }
