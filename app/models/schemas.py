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
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


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
