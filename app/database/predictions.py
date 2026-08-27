from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.orm import PredictionLog

def log_prediction(
    db: Session,
    project_id: Optional[int],
    delay_level: str,
    confidence: float,
    features_snapshot: Dict[str, Any]
) -> PredictionLog:
    db_log = PredictionLog(
        project_id=project_id,
        delay_level=delay_level,
        confidence=confidence,
        features_snapshot=features_snapshot
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
