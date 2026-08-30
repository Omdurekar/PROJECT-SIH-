from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.orm import TopRiskProject, ModelSummary

def get_top_risk_projects(db: Session, limit: int = 10) -> List[TopRiskProject]:
    """
    Retrieve top risk projects ordered by predicted risk probability.
    """
    return db.query(TopRiskProject).order_by(
        TopRiskProject.predicted_risk_probability.desc()
    ).limit(limit).all()

def get_model_summaries(db: Session) -> List[ModelSummary]:
    """
    List all ML model summaries stored in database.
    """
    return db.query(ModelSummary).order_by(ModelSummary.task, ModelSummary.model_name).all()

def get_model_summary_by_key(db: Session, model_key: str) -> Optional[ModelSummary]:
    """
    Retrieve model summary by unique model_key.
    """
    return db.query(ModelSummary).filter(ModelSummary.model_key == model_key).first()

def get_shap_summary_consolidated(db: Session) -> Dict[str, Any]:
    """
    Retrieve SHAP summaries from stored model analytics.
    """
    summaries = db.query(ModelSummary).filter(ModelSummary.shap_summary.isnot(None)).all()
    result = {}
    for summary in summaries:
        if summary.shap_summary:
            result[summary.model_key] = summary.shap_summary
    return result
