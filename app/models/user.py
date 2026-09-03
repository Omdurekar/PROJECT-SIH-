import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

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
    is_verified: bool = False
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., pattern=r"^\d{6}$", description="6-digit numeric OTP")

class OTPResendRequest(BaseModel):
    email: EmailStr

class OTPResponse(BaseModel):
    message: str
    email: str
    is_verified: Optional[bool] = None
