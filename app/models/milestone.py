import datetime
from typing import Optional
from pydantic import BaseModel
<<<<<<< HEAD
=======
from app.config.database import Base

# --- ORM Model ---
>>>>>>> origin/main
from app.models.orm import Milestone

# --- Pydantic Schemas ---
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
