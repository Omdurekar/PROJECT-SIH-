from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.config.database import get_db

from app.models.schemas import (
    UserCreate, UserLogin, Token, UserResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    ProgressCreate, ProgressResponse,
    RiskCreate, RiskUpdate, RiskResponse,
    PredictionRequest, PredictionResponse,
    DashboardOverview
)

from app.services import auth as auth_service
from app.services import projects as projects_service
from app.services import milestones as milestones_service
from app.services import progress as progress_service
from app.services import predictions as predictions_service
from app.services import risks as risks_service
from app.services import dashboard as dashboard_service
from app.database import audit as db_audit

router = APIRouter()

# --- Health Check ---
@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "SIH26103 Monitoring Backend"}


# --- Authentication Endpoints ---
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user_service(db, user_in)

@router.post("/login", response_model=Token, tags=["Authentication"])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_user_service(db, credentials)


# --- Projects Endpoints ---
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    return projects_service.create_project_service(db, project_in)

@router.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department: Optional[str] = None,
    delay_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return projects_service.list_projects_service(
        db, skip=skip, limit=limit, department=department, delay_level=delay_level
    )

@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def get_project(project_id: int, db: Session = Depends(get_db)):
    return projects_service.get_project_service(db, project_id)

@router.put("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db)):
    return projects_service.update_project_service(db, project_id, project_in)

@router.delete("/projects/{project_id}", tags=["Projects"])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    return projects_service.delete_project_service(db, project_id)


# --- Milestones Endpoints ---
@router.post("/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED, tags=["Milestones"])
def create_milestone(milestone_in: MilestoneCreate, db: Session = Depends(get_db)):
    return milestones_service.create_milestone_service(db, milestone_in)

@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneResponse], tags=["Milestones"])
def get_project_milestones(project_id: int, db: Session = Depends(get_db)):
    return milestones_service.list_milestones_by_project_service(db, project_id)

@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse, tags=["Milestones"])
def update_milestone(milestone_id: int, milestone_in: MilestoneUpdate, db: Session = Depends(get_db)):
    return milestones_service.update_milestone_service(db, milestone_id, milestone_in)


# --- Progress Updates Endpoints ---
@router.post("/progress", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED, tags=["Progress"])
def record_progress(progress_in: ProgressCreate, db: Session = Depends(get_db)):
    return progress_service.create_progress_update_service(db, progress_in)

@router.get("/projects/{project_id}/progress", response_model=List[ProgressResponse], tags=["Progress"])
def get_project_progress(project_id: int, db: Session = Depends(get_db)):
    return progress_service.get_progress_history_service(db, project_id)


# --- Machine Learning Delay Prediction ---
@router.post("/predict", response_model=PredictionResponse, tags=["Machine Learning"])
def predict_delay(request: PredictionRequest, db: Session = Depends(get_db)):
    return predictions_service.predict_project_delay_service(db, request)


# --- Risks Endpoints ---
@router.get("/risks", response_model=List[RiskResponse], tags=["Risks"])
def list_risks(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    return risks_service.list_risks_service(db, project_id=project_id)

@router.post("/risks", response_model=RiskResponse, status_code=status.HTTP_201_CREATED, tags=["Risks"])
def create_risk(risk_in: RiskCreate, db: Session = Depends(get_db)):
    return risks_service.create_risk_service(db, risk_in)

@router.put("/risks/{risk_id}", response_model=RiskResponse, tags=["Risks"])
def update_risk(risk_id: int, risk_in: RiskUpdate, db: Session = Depends(get_db)):
    return risks_service.update_risk_service(db, risk_id, risk_in)


# --- Dashboard Overview Endpoint ---
@router.get("/dashboard/overview", response_model=DashboardOverview, tags=["Dashboard"])
def get_dashboard_overview(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_overview_service(db)


# --- Governance & Audit Logs ---
@router.get("/audit-logs", tags=["Governance"])
def list_audit_logs(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db)):
    logs = db_audit.list_audit_logs(db, skip=skip, limit=limit)
    return [
        {
            "id": l.id,
            "username": l.username,
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "timestamp": l.timestamp.isoformat()
        } for l in logs
    ]
