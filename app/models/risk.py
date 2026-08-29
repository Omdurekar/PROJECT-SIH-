import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app.config.database import Base

# --- ORM Model ---
from app.models.orm import Risk

# --- Pydantic Schemas ---
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
