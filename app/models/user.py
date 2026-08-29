import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from pydantic import BaseModel, EmailStr
from app.config.database import Base

# --- ORM Model ---
from app.models.orm import User

# --- Pydantic Schemas ---
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
