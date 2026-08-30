from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.orm import DatasetProject

def get_dataset_project_by_name(db: Session, project_name: str) -> List[DatasetProject]:
    """
    Search dataset projects by name (case-insensitive substring match or exact match).
    """
    query = db.query(DatasetProject).filter(
        func.lower(DatasetProject.project_name_clean).contains(project_name.lower().strip())
    )
    return query.all()

def get_dataset_project_by_id(db: Session, global_project_id: str) -> Optional[DatasetProject]:
    """
    Get a single dataset project by global_project_id.
    """
    return db.query(DatasetProject).filter(DatasetProject.global_project_id == global_project_id).first()

def search_dataset_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None
) -> List[DatasetProject]:
    """
    List and filter dataset projects.
    """
    query = db.query(DatasetProject)
    if search:
        search_pattern = f"%{search.lower().strip()}%"
        query = query.filter(
            or_(
                func.lower(DatasetProject.project_name_clean).like(search_pattern),
                func.lower(DatasetProject.global_project_id).like(search_pattern),
                func.lower(DatasetProject.agency_clean).like(search_pattern)
            )
        )
    if sector:
        query = query.filter(func.lower(DatasetProject.sector_clean) == sector.lower())
    if state:
        query = query.filter(func.lower(DatasetProject.state_clean) == state.lower())
    if status:
        query = query.filter(func.lower(DatasetProject.project_status) == status.lower())
    
    return query.offset(skip).limit(limit).all()
