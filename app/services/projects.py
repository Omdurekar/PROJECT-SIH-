from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.database import projects as db_projects
from app.database import audit as db_audit

def create_project_service(db: Session, project_in: ProjectCreate, username: str = "System") -> ProjectResponse:
    existing = db_projects.get_project_by_code(db, project_in.project_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project code {project_in.project_code} already exists."
        )

    project = db_projects.create_project(db, project_in)

    db_audit.create_audit_entry(
        db,
        action="PROJECT_CREATE",
        entity_type="Project",
        entity_id=str(project.id),
        username=username,
        details=f"Created project {project.project_code}: {project.name}"
    )

    return ProjectResponse.model_validate(project)

def list_projects_service(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    delay_level: Optional[str] = None,
    name: Optional[str] = None
) -> List[ProjectResponse]:
    projects = db_projects.list_projects(db, skip=skip, limit=limit, department=department, delay_level=delay_level, name=name)
    return [ProjectResponse.model_validate(p) for p in projects]

def get_project_service(db: Session, project_id: int) -> ProjectResponse:
    project = db_projects.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )
    return ProjectResponse.model_validate(project)

def update_project_service(
    db: Session,
    project_id: int,
    project_in: ProjectUpdate,
    username: str = "System"
) -> ProjectResponse:
    project = db_projects.update_project(db, project_id, project_in)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    db_audit.create_audit_entry(
        db,
        action="PROJECT_UPDATE",
        entity_type="Project",
        entity_id=str(project_id),
        username=username,
        details=f"Updated project fields"
    )

    return ProjectResponse.model_validate(project)

def delete_project_service(db: Session, project_id: int, username: str = "System") -> dict:
    success = db_projects.delete_project(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    db_audit.create_audit_entry(
        db,
        action="PROJECT_DELETE",
        entity_type="Project",
        entity_id=str(project_id),
        username=username,
        details=f"Deleted project {project_id}"
    )

    return {"message": f"Project {project_id} deleted successfully."}


# --- Dataset Project Retrieval Services ---
from app.database import dataset_projects as db_dataset_projects

def get_dataset_project_by_name_service(db: Session, project_name: str):
    projects = db_dataset_projects.get_dataset_project_by_name(db, project_name=project_name)
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No dataset project found matching name '{project_name}'."
        )
    return projects

def get_dataset_project_by_id_service(db: Session, global_project_id: str):
    project = db_dataset_projects.get_dataset_project_by_id(db, global_project_id=global_project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset project with ID '{global_project_id}' not found."
        )
    return project

def search_dataset_projects_service(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None
):
    return db_dataset_projects.search_dataset_projects(
        db, skip=skip, limit=limit, search=search, sector=sector, state=state, status=status
    )
