from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.config.database import get_db

from app.models.schemas import (
    UserCreate, UserLogin, Token, UserResponse,
    OTPVerifyRequest, OTPResendRequest, OTPResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    ProgressCreate, ProgressResponse,
    RiskCreate, RiskUpdate, RiskResponse,
    PredictionRequest, PredictionResponse,
    DashboardOverview,
    DatasetProjectResponse, TopRiskProjectResponse, ModelSummaryResponse, SHAPSummaryResponse
)

from app.services import auth as auth_service
from app.services import otp as otp_service
from app.services import projects as projects_service
from app.services import milestones as milestones_service
from app.services import progress as progress_service
from app.services import predictions as predictions_service
from app.services import risks as risks_service
from app.services import dashboard as dashboard_service
from app.services import model_analytics as model_analytics_service
from app.database import audit as db_audit

router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Health Check ---
@router.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "SIH26103 Monitoring Backend"}


# --- Authentication Endpoints ---
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user_service(db, user_in)

@auth_router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_user_service(db, credentials)

@auth_router.post("/verify-otp", response_model=OTPResponse)
def verify_otp_endpoint(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    return otp_service.verify_otp_service(db, request.email, request.otp_code)

@auth_router.post("/resend-otp", response_model=OTPResponse)
def resend_otp_endpoint(request: OTPResendRequest, db: Session = Depends(get_db)):
    return otp_service.request_otp_service(db, request.email)




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
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List monitored projects with optional filtering by name, department, or delay level.
    """
    return projects_service.list_projects_service(
        db, skip=skip, limit=limit, department=department, delay_level=delay_level, name=name
    )

@router.get("/projects/top-risk", response_model=List[TopRiskProjectResponse], tags=["Projects Dataset"])
def get_top_risk_projects(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Retrieve top ongoing projects with highest predicted delay and financial overrun risks.
    """
    return model_analytics_service.get_top_risk_projects_service(db, limit=limit)

@router.get("/projects/by-name/{project_name}", response_model=List[DatasetProjectResponse], tags=["Projects Dataset"])
def get_dataset_project_by_name_route(project_name: str, db: Session = Depends(get_db)):
    """
    Retrieve project details from the historical monitoring dataset by project name.
    """
    return projects_service.get_dataset_project_by_name_service(db, project_name=project_name)

@router.get("/projects/by-id/{global_project_id}", response_model=DatasetProjectResponse, tags=["Projects Dataset"])
def get_dataset_project_by_id_route(global_project_id: str, db: Session = Depends(get_db)):
    """
    Retrieve project details by global project ID.
    """
    return projects_service.get_dataset_project_by_id_service(db, global_project_id=global_project_id)

@router.get("/projects/dataset/search", response_model=List[DatasetProjectResponse], tags=["Projects Dataset"])
def search_dataset_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search and filter monitored dataset projects by name, sector, state, or status.
    """
    return projects_service.search_dataset_projects_service(
        db, skip=skip, limit=limit, search=search, sector=sector, state=state, status=status
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


# --- Dataset Projects & Top Risk Retrieval Endpoints ---
@router.get("/project/{project_name}", response_model=List[DatasetProjectResponse], tags=["Projects Dataset"])
@router.get("/projects/by-name/{project_name}", response_model=List[DatasetProjectResponse], tags=["Projects Dataset"])
def get_dataset_project_by_name(project_name: str, db: Session = Depends(get_db)):
    """
    Retrieve project details from the historical monitoring dataset by project name.
    """
    return projects_service.get_dataset_project_by_name_service(db, project_name=project_name)

@router.get("/projects/by-id/{global_project_id}", response_model=DatasetProjectResponse, tags=["Projects Dataset"])
def get_dataset_project_by_id(global_project_id: str, db: Session = Depends(get_db)):
    """
    Retrieve project details by global project ID.
    """
    return projects_service.get_dataset_project_by_id_service(db, global_project_id=global_project_id)

@router.get("/projects/top-risk", response_model=List[TopRiskProjectResponse], tags=["Projects Dataset"])
def get_top_risk_projects(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Retrieve top ongoing projects with highest predicted delay and financial overrun risks.
    """
    return model_analytics_service.get_top_risk_projects_service(db, limit=limit)

@router.get("/projects/dataset/search", response_model=List[DatasetProjectResponse], tags=["Projects Dataset"])
def search_dataset_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    sector: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search and filter monitored dataset projects by name, sector, state, or status.
    """
    return projects_service.search_dataset_projects_service(
        db, skip=skip, limit=limit, search=search, sector=sector, state=state, status=status
    )


# --- Machine Learning Model Analytics & Explainability Endpoints ---
@router.get("/ml/models", response_model=List[ModelSummaryResponse], tags=["Machine Learning Analytics"])
def list_model_summaries(db: Session = Depends(get_db)):
    """
    List all trained machine learning model performance summaries.
    """
    return model_analytics_service.list_model_summaries_service(db)

@router.get("/ml/models/{model_key}", response_model=ModelSummaryResponse, tags=["Machine Learning Analytics"])
def get_model_summary(model_key: str, db: Session = Depends(get_db)):
    """
    Get detailed evaluation metrics, cross-validation scores, hyperparameters, and leakage audit for a specific model key.
    """
    return model_analytics_service.get_model_summary_service(db, model_key=model_key)

@router.get("/ml/explainability/shap", response_model=SHAPSummaryResponse, tags=["Machine Learning Analytics"])
def get_shap_explainability(db: Session = Depends(get_db)):
    """
    Get consolidated SHAP feature importance explainability breakdown across models.
    """
    return model_analytics_service.get_shap_explainability_service(db)
