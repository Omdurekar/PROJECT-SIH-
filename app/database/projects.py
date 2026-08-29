from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.orm import Project
from app.models.schemas import ProjectCreate, ProjectUpdate

def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    return db.query(Project).filter(Project.id == project_id).first()

def get_project_by_code(db: Session, project_code: str) -> Optional[Project]:
    return db.query(Project).filter(Project.project_code == project_code).first()

def get_project_by_name(db: Session, name: str) -> List[Project]:
    return db.query(Project).filter(func.lower(Project.name).contains(name.lower().strip())).all()

def list_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    delay_level: Optional[str] = None,
    name: Optional[str] = None
) -> List[Project]:
    query = db.query(Project)
    if name:
        query = query.filter(func.lower(Project.name).contains(name.lower().strip()))
    if department:
        query = query.filter(Project.department == department)
    if delay_level:
        query = query.filter(Project.delay_level == delay_level)
    return query.order_by(Project.id.desc()).offset(skip).limit(limit).all()

def create_project(db: Session, project_in: ProjectCreate) -> Project:
    db_project = Project(
        project_code=project_in.project_code,
        name=project_in.name,
        department=project_in.department,
        project_type=project_in.project_type,
        location=project_in.location,
        budget=project_in.budget,
        planned_start_date=project_in.planned_start_date,
        planned_end_date=project_in.planned_end_date,
        planned_duration_days=project_in.planned_duration_days,
        expenditure=0.0,
        completion_percentage=0.0,
        time_elapsed_days=0,
        status="IN_PROGRESS",
        delay_level="LOW",
        risk_score=0.0
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project_in: ProjectUpdate) -> Optional[Project]:
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return None
    
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int) -> bool:
    db_project = get_project_by_id(db, project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True

def get_project_stats(db: Session):
    total = db.query(func.count(Project.id)).scalar() or 0
    low = db.query(func.count(Project.id)).filter(Project.delay_level == "LOW").scalar() or 0
    med = db.query(func.count(Project.id)).filter(Project.delay_level == "MEDIUM").scalar() or 0
    high = db.query(func.count(Project.id)).filter(Project.delay_level == "HIGH").scalar() or 0
    total_budget = db.query(func.sum(Project.budget)).scalar() or 0.0
    total_expenditure = db.query(func.sum(Project.expenditure)).scalar() or 0.0
    avg_completion = db.query(func.avg(Project.completion_percentage)).scalar() or 0.0

    return {
        "total_projects": total,
        "delay_distribution": {"LOW": low, "MEDIUM": med, "HIGH": high},
        "total_budget": round(float(total_budget), 2),
        "utilized_budget": round(float(total_expenditure), 2),
        "avg_completion_percentage": round(float(avg_completion), 2)
    }
