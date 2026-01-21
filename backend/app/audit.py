"""
Audit logging utility for tracking all important actions
"""

from typing import Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import AuditLog, User
import json


def serialize_for_json(obj: Any) -> Any:
    """Convert non-serializable objects to JSON-compatible types"""
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    else:
        return obj


async def log_action(
    db: AsyncSession,
    user_id: Optional[int] = None,
    action: str = "",
    entity_type: str = "",
    entity_id: Optional[int] = None,
    description: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None
) -> AuditLog:
    """
    Log an action to the audit log
    
    Args:
        db: Database session
        user_id: ID of user performing the action
        action: Action type (e.g., 'CREATE_EMPLOYEE', 'UPDATE_EMPLOYEE', 'DELETE_EMPLOYEE')
        entity_type: Type of entity affected (e.g., 'EMPLOYEE', 'LEAVE', 'SCHEDULE')
        entity_id: ID of the affected entity
        description: Human-readable description of the action
        old_values: Previous values (for updates)
        new_values: New values (for updates)
        ip_address: Client IP address
        user_agent: Client user agent
        status: Status of action (success, failed, partial)
        error_message: Error details if action failed
    
    Returns:
        AuditLog: The created audit log entry
    """
    
    # Serialize date objects to ISO format strings for JSON storage
    serialized_old_values = serialize_for_json(old_values) if old_values else None
    serialized_new_values = serialize_for_json(new_values) if new_values else None
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        old_values=serialized_old_values,
        new_values=serialized_new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        error_message=error_message,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    await db.flush()
    
    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> tuple[list[AuditLog], int]:
    """
    Retrieve audit logs with optional filtering
    
    Returns:
        Tuple of (logs list, total count)
    """
    from sqlalchemy.orm import selectinload
    
    filters = []
    
    if action:
        filters.append(AuditLog.action == action)
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    if user_id:
        filters.append(AuditLog.user_id == user_id)
    
    # Get total count
    count_query = select(AuditLog)
    if filters:
        count_query = count_query.filter(*filters)
    count_result = await db.execute(count_query)
    total_count = len(count_result.scalars().all())
    
    # Get paginated results with eager loading of user
    query = select(AuditLog).options(selectinload(AuditLog.user))
    if filters:
        query = query.filter(*filters)
    query = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs, total_count
