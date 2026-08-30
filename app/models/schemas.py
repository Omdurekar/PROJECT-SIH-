import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# --- User & Auth ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "Monitoring Officer"
    department: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    department: Optional[str]
    is_verified: bool = False
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., pattern=r"^\d{6}$", description="6-digit numeric OTP")

class OTPResendRequest(BaseModel):
    email: EmailStr

class OTPResponse(BaseModel):
    message: str
    email: str
    is_verified: Optional[bool] = None


# --- Milestone ---
class MilestoneCreate(BaseModel):
    project_id: int
    name: str
    target_date: str
    status: Optional[str] = "PENDING"
    completion_percentage: Optional[float] = 0.0

class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    target_date: Optional[str] = None
    status: Optional[str] = None
    completion_percentage: Optional[float] = None

class MilestoneResponse(BaseModel):
    id: int
    project_id: int
    name: str
    target_date: str
    status: str
    completion_percentage: float
    is_delayed: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Progress Update ---
class ProgressCreate(BaseModel):
    project_id: int
    completion_percentage: float = Field(..., ge=0.0, le=100.0)
    expenditure: float = Field(..., ge=0.0)
    reported_by: Optional[str] = "System User"
    remarks: Optional[str] = None

class ProgressResponse(BaseModel):
    id: int
    project_id: int
    reported_by: str
    completion_percentage: float
    expenditure: float
    remarks: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Risk ---
class RiskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    category: Optional[str] = "Operational"
    severity: Optional[str] = "MEDIUM"
    mitigation_plan: Optional[str] = None

class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    mitigation_plan: Optional[str] = None

class RiskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    category: str
    severity: str
    status: str
    mitigation_plan: Optional[str]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Project ---
class ProjectCreate(BaseModel):
    project_code: str
    name: str
    department: str
    project_type: str
    location: str
    budget: float = Field(..., gt=0.0)
    planned_start_date: str
    planned_end_date: str
    planned_duration_days: int = Field(..., gt=0)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    project_type: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[float] = None
    planned_end_date: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    project_code: str
    name: str
    department: str
    project_type: str
    location: str
    budget: float
    expenditure: float
    planned_start_date: str
    planned_end_date: str
    actual_start_date: Optional[str]
    actual_end_date: Optional[str]
    planned_duration_days: int
    time_elapsed_days: int
    completion_percentage: float
    status: str
    delay_level: str
    risk_score: float
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Machine Learning Prediction ---
class PredictionRequest(BaseModel):
    budget: float = Field(..., gt=0)
    expenditure: float = Field(..., ge=0)
    planned_duration_days: int = Field(..., gt=0)
    time_elapsed_days: int = Field(..., ge=0)
    completion_percentage: float = Field(..., ge=0, le=100)
    total_milestones: int = Field(..., ge=1)
    completed_milestones: int = Field(..., ge=0)
    delayed_milestones: int = Field(..., ge=0)
    pending_milestones: int = Field(..., ge=0)
    risk_score: float = Field(0.0, ge=0.0, le=10.0)
    project_id: Optional[int] = None

class PredictionResponse(BaseModel):
    project_id: Optional[int] = None
    delay_level: str  # LOW, MEDIUM, HIGH
    confidence: float
    derived_metrics: Dict[str, float]
    predicted_at: str


# --- Dashboard Overview ---
class DashboardOverview(BaseModel):
    total_projects: int
    delay_distribution: Dict[str, int]  # {"LOW": x, "MEDIUM": y, "HIGH": z}
    total_budget: float
    utilized_budget: float
    avg_completion_percentage: float
    high_priority_projects: List[ProjectResponse]
    department_summary: Dict[str, Dict[str, Any]]


# --- Dataset Project Schemas ---
class DatasetProjectResponse(BaseModel):
    id: int
    global_project_id: str
    project_name_clean: str
    report_date: Optional[str] = None
    project_status: Optional[str] = None
    sector_clean: Optional[str] = None
    agency_clean: Optional[str] = None
    state_clean: Optional[str] = None
    cost_original: Optional[float] = None
    cost_anticipated: Optional[float] = None
    cost_revised: Optional[float] = None
    cost_overrun_amount_calc: Optional[float] = None
    cost_overrun_percent_clean: Optional[float] = None
    time_overrun_months_calc: Optional[float] = None
    total_planned_duration_months: Optional[float] = None
    project_age_months: Optional[float] = None
    remaining_schedule_months: Optional[float] = None
    physical_progress_clean: Optional[float] = None
    time_overrun_prediction: Optional[int] = None
    time_overrun_probability: Optional[float] = None
    cost_overrun_prediction: Optional[int] = None
    cost_overrun_probability: Optional[float] = None
    risk_class_prediction: Optional[int] = None
    risk_class_probability: Optional[float] = None
    risk_class_0_probability: Optional[float] = None
    risk_class_1_probability: Optional[float] = None
    risk_class_2_probability: Optional[float] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Top Risk Projects Schema ---
class TopRiskProjectResponse(BaseModel):
    id: int
    global_project_id: str
    project_name_clean: str
    report_date: Optional[str] = None
    project_status: Optional[str] = None
    predicted_risk_class: Optional[int] = None
    predicted_risk_probability: Optional[float] = None
    cost_original: Optional[float] = None
    cost_anticipated: Optional[float] = None
    time_overrun_months_calc: Optional[float] = None
    analysis_details: Optional[Any] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Model Analytics & Explainability Schemas ---
class ModelSummaryResponse(BaseModel):
    id: int
    model_key: str
    model_name: str
    task: str
    target: str
    target_definition: Optional[str] = None
    dataset_info: Optional[Any] = None
    best_model_parameters: Optional[Any] = None
    test_performance: Optional[Any] = None
    cross_validation_results: Optional[Any] = None
    leakage_audit: Optional[Any] = None
    top_feature_importance: Optional[Any] = None
    shap_summary: Optional[Any] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class SHAPSummaryResponse(BaseModel):
    time_overrun: Optional[Dict[str, Any]] = None
    cost_overrun: Optional[Dict[str, Any]] = None
    risk_class: Optional[Dict[str, Any]] = None
