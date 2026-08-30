import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(30), default="Monitoring Officer") # Admin, Project Manager, Monitoring Officer, Department Official, Viewer
    department = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

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

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    delay_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    features_snapshot = Column(JSON, nullable=True)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="prediction_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class DatasetProject(Base):
    __tablename__ = "dataset_projects"

    id = Column(Integer, primary_key=True, index=True)
    global_project_id = Column(String(100), unique=True, index=True, nullable=False)
    project_name_clean = Column(String(255), index=True, nullable=False)
    report_date = Column(String(50), nullable=True)
    project_status = Column(String(50), nullable=True)
    sector_clean = Column(String(100), nullable=True)
    agency_clean = Column(String(150), nullable=True)
    state_clean = Column(String(100), nullable=True)

    cost_original = Column(Float, nullable=True)
    cost_anticipated = Column(Float, nullable=True)
    cost_revised = Column(Float, nullable=True)
    cost_overrun_amount_calc = Column(Float, nullable=True)
    cost_overrun_percent_clean = Column(Float, nullable=True)

    time_overrun_months_calc = Column(Float, nullable=True)
    total_planned_duration_months = Column(Float, nullable=True)
    project_age_months = Column(Float, nullable=True)
    remaining_schedule_months = Column(Float, nullable=True)
    physical_progress_clean = Column(Float, nullable=True)

    time_overrun_prediction = Column(Integer, nullable=True)
    time_overrun_probability = Column(Float, nullable=True)
    cost_overrun_prediction = Column(Integer, nullable=True)
    cost_overrun_probability = Column(Float, nullable=True)
    risk_class_prediction = Column(Integer, nullable=True)
    risk_class_probability = Column(Float, nullable=True)
    risk_class_0_probability = Column(Float, nullable=True)
    risk_class_1_probability = Column(Float, nullable=True)
    risk_class_2_probability = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TopRiskProject(Base):
    __tablename__ = "top_risk_projects"

    id = Column(Integer, primary_key=True, index=True)
    global_project_id = Column(String(100), index=True, nullable=False)
    project_name_clean = Column(String(255), index=True, nullable=False)
    report_date = Column(String(50), nullable=True)
    project_status = Column(String(50), nullable=True)

    predicted_risk_class = Column(Integer, nullable=False)
    predicted_risk_probability = Column(Float, nullable=False)
    cost_original = Column(Float, nullable=True)
    cost_anticipated = Column(Float, nullable=True)
    time_overrun_months_calc = Column(Float, nullable=True)

    analysis_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ModelSummary(Base):
    __tablename__ = "model_summaries"

    id = Column(Integer, primary_key=True, index=True)
    model_key = Column(String(100), unique=True, index=True, nullable=False)
    model_name = Column(String(150), nullable=False)
    task = Column(String(100), nullable=False)
    target = Column(String(100), nullable=False)
    target_definition = Column(Text, nullable=True)

    dataset_info = Column(JSON, nullable=True)
    best_model_parameters = Column(JSON, nullable=True)
    test_performance = Column(JSON, nullable=True)
    cross_validation_results = Column(JSON, nullable=True)
    leakage_audit = Column(JSON, nullable=True)
    top_feature_importance = Column(JSON, nullable=True)
    shap_summary = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), index=True, nullable=False)
    hashed_otp = Column(String(255), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_sent_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    is_invalidated = Column(Boolean, default=False, nullable=False)

