from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database import model_analytics as db_model_analytics
from app.models.orm import TopRiskProject, ModelSummary

def get_top_risk_projects_service(db: Session, limit: int = 10) -> List[TopRiskProject]:
    """
    Retrieve highest-risk ongoing projects.
    """
    return db_model_analytics.get_top_risk_projects(db, limit=limit)

def list_model_summaries_service(db: Session) -> List[ModelSummary]:
    """
    List all ML model evaluation summaries.
    """
    return db_model_analytics.get_model_summaries(db)

def get_model_summary_service(db: Session, model_key: str) -> ModelSummary:
    """
    Retrieve full performance, hyperparameters, and diagnostic report for a given model.
    """
    model = db_model_analytics.get_model_summary_by_key(db, model_key=model_key)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ML model summary for key '{model_key}' not found."
        )
    return model

def get_shap_explainability_service(db: Session) -> Dict[str, Any]:
    """
    Retrieve consolidated SHAP feature importance explainability breakdown.
    """
    shap_summary = db_model_analytics.get_model_summary_by_key(db, model_key="shap_frontend_summary")
    if shap_summary and shap_summary.shap_summary:
        return shap_summary.shap_summary
    return db_model_analytics.get_shap_summary_consolidated(db)
