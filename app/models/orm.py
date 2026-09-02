import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="Monitoring Officer") # Admin, Project Manager, Monitoring Officer, Department Official, Viewer
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    project_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)

    budget = Column(Float, nullable=False)  # Crores INR
    expenditure = Column(Float, default=0.0)

    planned_start_date = Column(String(20), nullable=False)
    planned_end_date = Column(String(20), nullable=False)
    actual_start_date = Column(String(20), nullable=True)
    actual_end_date = Column(String(20), nullable=True)

    planned_duration_days = Column(Integer, nullable=False)
    time_elapsed_days = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)

    status = Column(String(30), default="IN_PROGRESS")  # NOT_STARTED, IN_PROGRESS, COMPLETED, SUSPENDED
    delay_level = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH
    risk_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    progress_updates = relationship("ProgressUpdate", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    prediction_logs = relationship("PredictionLog", back_populates="project", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    target_date = Column(String(20), nullable=False)
    status = Column(String(30), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, DELAYED
    completion_percentage = Column(Float, default=0.0)
    is_delayed = Column(Integer, default=0)  # 0 or 1
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="milestones")


class ProgressUpdate(Base):
    __tablename__ = "progress_updates"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reported_by = Column(String(100), nullable=False)
    completion_percentage = Column(Float, nullable=False)
    expenditure = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="progress_updates")


class Risk(Base):
    __tablename__ = "risks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="Operational") # Financial, Operational, Regulatory, Environmental, Schedule
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), default="OPEN") # OPEN, MITIGATED, CLOSED
    mitigation_plan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="risks")


class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    delay_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    features_snapshot = Column(JSON, nullable=True)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="prediction_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
