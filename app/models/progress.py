import datetime
from typing import Optional
from pydantic import BaseModel, Field
<<<<<<< HEAD
=======
from app.config.database import Base

# --- ORM Model ---
>>>>>>> origin/main
from app.models.orm import ProgressUpdate

# --- Pydantic Schemas ---
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
