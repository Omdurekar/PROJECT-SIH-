import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app.config.database import Base

# --- ORM Model ---
class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    target_date = Column(String(20), nullable=False)
    status = Column(String(30), default="PENDING")
    completion_percentage = Column(Float, default=0.0)
    is_delayed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="milestones")

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
