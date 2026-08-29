import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from app.config.database import Base
from app.models.project import ProjectResponse

# --- ORM Models ---
from app.models.orm import PredictionLog, AuditLog

# --- Pydantic Schemas ---
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
    delay_level: str
    confidence: float
    derived_metrics: Dict[str, float]
    predicted_at: str

class DashboardOverview(BaseModel):
    total_projects: int
    delay_distribution: Dict[str, int]
    total_budget: float
    utilized_budget: float
    avg_completion_percentage: float
    high_priority_projects: List[ProjectResponse]
    department_summary: Dict[str, Dict[str, Any]]
