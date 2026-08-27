import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from app.config.database import Base
from app.models.project import ProjectResponse

# --- ORM Models ---
class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    delay_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    features_snapshot = Column(JSON, nullable=True)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="prediction_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

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
