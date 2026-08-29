from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.schemas import MilestoneCreate, MilestoneUpdate, MilestoneResponse
from app.database import milestones as db_milestones
from app.database import projects as db_projects
from app.database import audit as db_audit

def create_milestone_service(db: Session, milestone_in: MilestoneCreate, username: str = "System") -> MilestoneResponse:
    project = db_projects.get_project_by_id(db, milestone_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {milestone_in.project_id} not found."
        )

    milestone = db_milestones.create_milestone(db, milestone_in)

    db_audit.create_audit_entry(
        db,
        action="MILESTONE_CREATE",
        entity_type="Milestone",
        entity_id=str(milestone.id),
        username=username,
        details=f"Created milestone '{milestone.name}' for Project {project.project_code}"
    )

    return MilestoneResponse.model_validate(milestone)

def list_milestones_by_project_service(db: Session, project_id: int) -> List[MilestoneResponse]:
    milestones = db_milestones.get_milestones_by_project(db, project_id)
    return [MilestoneResponse.model_validate(m) for m in milestones]

def update_milestone_service(
    db: Session,
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    username: str = "System"
) -> MilestoneResponse:
    milestone = db_milestones.update_milestone(db, milestone_id, milestone_in)
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Milestone with ID {milestone_id} not found."
        )

    db_audit.create_audit_entry(
        db,
        action="MILESTONE_UPDATE",
        entity_type="Milestone",
        entity_id=str(milestone_id),
        username=username,
        details=f"Updated milestone {milestone_id}"
    )

    return MilestoneResponse.model_validate(milestone)
