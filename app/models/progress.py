import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from app.config.database import Base

# --- ORM Model ---
class ProgressUpdate(Base):
    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reported_by = Column(String(100), nullable=False)
    completion_percentage = Column(Float, nullable=False)
    expenditure = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="progress_updates")

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
