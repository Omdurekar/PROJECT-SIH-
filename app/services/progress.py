from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.schemas import ProgressCreate, ProgressResponse
from app.database import progress as db_progress
from app.database import projects as db_projects
from app.database import audit as db_audit

def create_progress_update_service(db: Session, progress_in: ProgressCreate, username: str = "System") -> ProgressResponse:
    project = db_projects.get_project_by_id(db, progress_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {progress_in.project_id} not found."
        )

    # Record progress update
    progress = db_progress.create_progress_update(db, progress_in)

    # Update project state
    prev_completion = project.completion_percentage
    project.completion_percentage = progress_in.completion_percentage
    project.expenditure = progress_in.expenditure
    if progress_in.completion_percentage >= 100.0:
        project.status = "COMPLETED"

    db.commit()

    db_audit.create_audit_entry(
        db,
        action="PROGRESS_UPDATE",
        entity_type="Project",
        entity_id=str(project.id),
        username=username,
        details=f"Updated progress from {prev_completion}% to {progress_in.completion_percentage}%"
    )

    return ProgressResponse.model_validate(progress)

def get_progress_history_service(db: Session, project_id: int) -> List[ProgressResponse]:
    history = db_progress.get_progress_history_by_project(db, project_id)
    return [ProgressResponse.model_validate(p) for p in history]
