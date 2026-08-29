from typing import List
from sqlalchemy.orm import Session
from app.models.orm import ProgressUpdate
from app.models.schemas import ProgressCreate

def create_progress_update(db: Session, progress_in: ProgressCreate) -> ProgressUpdate:
    db_progress = ProgressUpdate(
        project_id=progress_in.project_id,
        reported_by=progress_in.reported_by or "System User",
        completion_percentage=progress_in.completion_percentage,
        expenditure=progress_in.expenditure,
        remarks=progress_in.remarks
    )
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

def get_progress_history_by_project(db: Session, project_id: int) -> List[ProgressUpdate]:
    return db.query(ProgressUpdate).filter(ProgressUpdate.project_id == project_id).order_by(ProgressUpdate.created_at.desc()).all()
