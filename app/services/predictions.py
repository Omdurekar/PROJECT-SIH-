import os
import joblib
import datetime
import numpy as np
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.config.settings import settings
from app.models.schemas import PredictionRequest, PredictionResponse
from app.utils.helpers import derive_project_metrics
from app.database import predictions as db_predictions
from app.database import projects as db_projects
from ml.feature_engineering import engineer_features, FEATURE_COLUMNS
import pandas as pd

_model_bundle = None

def get_ml_bundle():
    global _model_bundle
    if _model_bundle is None:
        model_path = settings.ML_MODEL_PATH
        if not os.path.exists(model_path):
            from ml.train import train_and_select_best_model
            _model_bundle = train_and_select_best_model()
        else:
            _model_bundle = joblib.load(model_path)
    return _model_bundle

def predict_project_delay_service(db: Session, request: PredictionRequest) -> PredictionResponse:
    bundle = get_ml_bundle()
    model = bundle["model"]
    scaler = bundle["scaler"]
    reverse_mapping = bundle["reverse_target_mapping"]

    # Build input dictionary
    input_dict = {
        "budget": request.budget,
        "expenditure": request.expenditure,
        "planned_duration_days": request.planned_duration_days,
        "time_elapsed_days": request.time_elapsed_days,
        "completion_percentage": request.completion_percentage,
        "total_milestones": request.total_milestones,
        "completed_milestones": request.completed_milestones,
        "delayed_milestones": request.delayed_milestones,
        "pending_milestones": request.pending_milestones,
        "risk_score": request.risk_score
    }

    # Derive engineered features
    df_single = pd.DataFrame([input_dict])
    df_engineered = engineer_features(df_single)
    X_features = df_engineered[FEATURE_COLUMNS].fillna(0.0)
    X_scaled = scaler.transform(X_features)

    # ML Inference
    pred_class_idx = model.predict(X_scaled)[0]
    delay_level = reverse_mapping.get(int(pred_class_idx), "MEDIUM")

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_scaled)[0]
        confidence = float(np.max(probabilities))
    else:
        confidence = 0.90

    derived_metrics = derive_project_metrics(
        budget=request.budget,
        expenditure=request.expenditure,
        planned_duration=request.planned_duration_days,
        time_elapsed=request.time_elapsed_days,
        completion_pct=request.completion_percentage,
        total_milestones=request.total_milestones,
        completed_milestones=request.completed_milestones,
        delayed_milestones=request.delayed_milestones,
        risk_score=request.risk_score
    )

    # Save to database log
    db_predictions.log_prediction(
        db=db,
        project_id=request.project_id,
        delay_level=delay_level,
        confidence=round(confidence, 4),
        features_snapshot=input_dict
    )

    # Update project delay level if project_id exists
    if request.project_id:
        project = db_projects.get_project_by_id(db, request.project_id)
        if project:
            project.delay_level = delay_level
            db.commit()

    return PredictionResponse(
        project_id=request.project_id,
        delay_level=delay_level,
        confidence=round(confidence, 4),
        derived_metrics=derived_metrics,
        predicted_at=datetime.datetime.utcnow().isoformat()
    )
