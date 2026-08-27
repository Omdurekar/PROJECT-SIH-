from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.orm import Milestone
from app.models.schemas import MilestoneCreate, MilestoneUpdate

def create_milestone(db: Session, milestone_in: MilestoneCreate) -> Milestone:
    db_milestone = Milestone(
        project_id=milestone_in.project_id,
        name=milestone_in.name,
        target_date=milestone_in.target_date,
        status=milestone_in.status or "PENDING",
        completion_percentage=milestone_in.completion_percentage or 0.0,
        is_delayed=1 if (milestone_in.status == "DELAYED") else 0
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

def get_milestones_by_project(db: Session, project_id: int) -> List[Milestone]:
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()

def get_milestone_by_id(db: Session, milestone_id: int) -> Optional[Milestone]:
    return db.query(Milestone).filter(Milestone.id == milestone_id).first()

def update_milestone(db: Session, milestone_id: int, milestone_in: MilestoneUpdate) -> Optional[Milestone]:
    db_milestone = get_milestone_by_id(db, milestone_id)
    if not db_milestone:
        return None

    update_data = milestone_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_milestone, field, value)

    if db_milestone.status == "DELAYED":
        db_milestone.is_delayed = 1

    db.commit()
    db.refresh(db_milestone)
    return db_milestone
