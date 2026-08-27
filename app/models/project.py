import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from app.config.database import Base

# --- ORM Model ---
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    project_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)

    budget = Column(Float, nullable=False)
    expenditure = Column(Float, default=0.0)

    planned_start_date = Column(String(20), nullable=False)
    planned_end_date = Column(String(20), nullable=False)
    actual_start_date = Column(String(20), nullable=True)
    actual_end_date = Column(String(20), nullable=True)

    planned_duration_days = Column(Integer, nullable=False)
    time_elapsed_days = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)

    status = Column(String(30), default="IN_PROGRESS")
    delay_level = Column(String(20), default="LOW")
    risk_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    progress_updates = relationship("ProgressUpdate", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    prediction_logs = relationship("PredictionLog", back_populates="project", cascade="all, delete-orphan")

# --- Pydantic Schemas ---
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
