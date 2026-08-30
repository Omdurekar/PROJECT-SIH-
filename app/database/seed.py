import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import json
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.config.database import engine, Base, SessionLocal
from app.models.orm import DatasetProject, TopRiskProject, ModelSummary

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "temporary_data")

def clean_val(val):
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    return str(val)

def seed_dataset_projects(db: Session):
    csv_path = os.path.join(DATA_DIR, "random_forest_final_dataset.csv")
    if not os.path.exists(csv_path):
        print(f"Skipping dataset_projects seed: '{csv_path}' not found.")
        return

    print(f"Seeding dataset_projects from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Clear existing entries
    db.query(DatasetProject).delete()
    db.commit()

    records = []
    for _, row in df.iterrows():
        records.append(
            DatasetProject(
                global_project_id=str(row.get("global_project_id")),
                project_name_clean=str(row.get("project_name_clean", "")),
                report_date=clean_val(row.get("report_date")),
                project_status=clean_val(row.get("project_status")),
                sector_clean=clean_val(row.get("sector_clean")),
                agency_clean=clean_val(row.get("agency_clean")),
                state_clean=clean_val(row.get("state_clean")),
                cost_original=clean_val(row.get("cost_original")),
                cost_anticipated=clean_val(row.get("cost_anticipated")),
                cost_revised=clean_val(row.get("cost_revised")),
                cost_overrun_amount_calc=clean_val(row.get("cost_overrun_amount_calc")),
                cost_overrun_percent_clean=clean_val(row.get("cost_overrun_percent_clean")),
                time_overrun_months_calc=clean_val(row.get("time_overrun_months_calc")),
                total_planned_duration_months=clean_val(row.get("total_planned_duration_months")),
                project_age_months=clean_val(row.get("project_age_months")),
                remaining_schedule_months=clean_val(row.get("remaining_schedule_months")),
                physical_progress_clean=clean_val(row.get("physical_progress_clean")),
                time_overrun_prediction=clean_val(row.get("time_overrun_prediction")),
                time_overrun_probability=clean_val(row.get("time_overrun_probability")),
                cost_overrun_prediction=clean_val(row.get("cost_overrun_prediction")),
                cost_overrun_probability=clean_val(row.get("cost_overrun_probability")),
                risk_class_prediction=clean_val(row.get("risk_class_prediction")),
                risk_class_probability=clean_val(row.get("risk_class_probability")),
                risk_class_0_probability=clean_val(row.get("risk_class_0_probability")),
                risk_class_1_probability=clean_val(row.get("risk_class_1_probability")),
                risk_class_2_probability=clean_val(row.get("risk_class_2_probability")),
            )
        )

    db.bulk_save_objects(records)
    db.commit()
    print(f"Successfully seeded {len(records)} projects into 'dataset_projects'.")


def seed_top_risk_projects(db: Session):
    ongoing_csv = os.path.join(DATA_DIR, "random_forest_top_3_ongoing_risk_projects.csv")
    complete_csv = os.path.join(DATA_DIR, "random_forest_top_3_complete_project_analysis.csv")

    if not os.path.exists(ongoing_csv):
        print(f"Skipping top_risk_projects seed: '{ongoing_csv}' not found.")
        return

    print(f"Seeding top_risk_projects from {ongoing_csv}...")
    df_ongoing = pd.read_csv(ongoing_csv)
    df_complete = pd.read_csv(complete_csv) if os.path.exists(complete_csv) else pd.DataFrame()

    db.query(TopRiskProject).delete()
    db.commit()

    records = []
    for _, row in df_ongoing.iterrows():
        g_id = str(row.get("global_project_id"))
        
        # Extract full analysis details if present in complete_csv
        analysis_details = {}
        if not df_complete.empty:
            match = df_complete[df_complete["global_project_id"] == g_id]
            if not match.empty:
                analysis_details = json.loads(match.iloc[0].to_json())

        records.append(
            TopRiskProject(
                global_project_id=g_id,
                project_name_clean=str(row.get("project_name_clean", "")),
                report_date=clean_val(row.get("report_date")),
                project_status=clean_val(row.get("project_status")),
                predicted_risk_class=int(row.get("predicted_risk_class", 2)),
                predicted_risk_probability=float(row.get("predicted_risk_probability", 0.0)),
                cost_original=clean_val(analysis_details.get("cost_original")),
                cost_anticipated=clean_val(analysis_details.get("cost_anticipated")),
                time_overrun_months_calc=clean_val(analysis_details.get("time_overrun_months_calc")),
                analysis_details=analysis_details
            )
        )

    db.bulk_save_objects(records)
    db.commit()
    print(f"Successfully seeded {len(records)} projects into 'top_risk_projects'.")


def seed_model_summaries(db: Session):
    if not os.path.exists(DATA_DIR):
        print(f"Skipping model_summaries seed: '{DATA_DIR}' directory not found.")
        return

    print(f"Seeding model_summaries from JSON files in {DATA_DIR}...")
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    db.query(ModelSummary).delete()
    db.commit()

    records = []
    for fname in json_files:
        fpath = os.path.join(DATA_DIR, fname)
        model_key = fname.replace(".json", "").replace("_summary", "")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if fname == "shap_frontend_summary.json":
            # Master SHAP summary
            records.append(
                ModelSummary(
                    model_key="shap_frontend_summary",
                    model_name="SHAP Consolidated Frontend Summary",
                    task="explainability",
                    target="all_targets",
                    target_definition="Global SHAP feature importance breakdowns across time overrun, cost overrun, and risk class classification models.",
                    shap_summary=data
                )
            )
        else:
            records.append(
                ModelSummary(
                    model_key=model_key,
                    model_name=data.get("model_name", model_key),
                    task=data.get("task", "classification"),
                    target=data.get("target", "unknown"),
                    target_definition=data.get("target_definition"),
                    dataset_info=data.get("dataset_info"),
                    best_model_parameters=data.get("best_model_parameters"),
                    test_performance=data.get("test_performance"),
                    cross_validation_results=data.get("cross_validation_results"),
                    leakage_audit=data.get("leakage_audit"),
                    top_feature_importance=data.get("top_feature_importance"),
                    shap_summary=data.get("features") if "features" in data else data
                )
            )

    db.bulk_save_objects(records)
    db.commit()
    print(f"Successfully seeded {len(records)} entries into 'model_summaries'.")


def run_seed():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_dataset_projects(db)
        seed_top_risk_projects(db)
        seed_model_summaries(db)
        print("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
