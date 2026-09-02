import datetime
from typing import Optional
from pydantic import BaseModel, Field
<<<<<<< HEAD
=======
from app.config.database import Base

# --- ORM Model ---
>>>>>>> origin/main
from app.models.orm import Project

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
