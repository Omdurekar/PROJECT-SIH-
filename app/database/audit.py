from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.orm import AuditLog

def create_audit_entry(
    db: Session,
    action: str,
    entity_type: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[str] = None
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        username=username or "System",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details=details
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def list_audit_logs(db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
