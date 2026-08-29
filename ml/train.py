import os
import sys
import joblib
import pandas as pd
import numpy as np

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from ml.data.generate_dataset import generate_project_dataset
from ml.preprocessing import MLPreprocessor
from ml.evaluate import evaluate_model

def train_and_select_best_model(data_path: str = "ml/data/projects_dataset.csv", save_dir: str = "ml/saved_model"):
    # 1. Load or Generate Dataset
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Generating dataset...")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df = generate_project_dataset(1500)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    print(f"Loaded dataset with {len(df)} samples.")

    # 2. Preprocess Data
    preprocessor = MLPreprocessor()
    X_scaled, y_labels = preprocessor.fit_transform(df)

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_labels, test_size=0.2, random_state=42, stratify=y_labels
    )

    # 3. Define Candidate Models
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=8, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
    }

    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=6, eval_metric="mlogloss", random_state=42)
    else:
        models["Gradient Boosting"] = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)

    # 4. Train & Evaluate Candidates
    evaluation_results = []
    best_score = -1.0
    best_model_name = None
    best_model = None

    print("\n--- Model Evaluation Results ---")
    for name, model in models.items():
        model.fit(X_train, y_train)
        metrics = evaluate_model(model, X_test, y_test, model_name=name)
        evaluation_results.append(metrics)

        # Composite score prioritizing High Delay recall and F1 score
        composite_score = metrics["f1_score"] * 0.5 + metrics["high_delay_recall"] * 0.5
        print(f"[{name}] Accuracy: {metrics['accuracy']:.4f} | F1-Score: {metrics['f1_score']:.4f} | High Delay Recall: {metrics['high_delay_recall']:.4f}")

        if composite_score > best_score:
            best_score = composite_score
            best_model_name = name
            best_model = model

    print(f"\nBest Model Selected: {best_model_name} (Composite Score: {best_score:.4f})")

    # 5. Save Artifacts
    os.makedirs(save_dir, exist_ok=True)
    model_bundle = {
        "model_name": best_model_name,
        "model": best_model,
        "scaler": preprocessor.scaler,
        "feature_columns": preprocessor.feature_columns,
        "target_mapping": {"LOW": 0, "MEDIUM": 1, "HIGH": 2},
        "reverse_target_mapping": {0: "LOW", 1: "MEDIUM", 2: "HIGH"},
        "evaluation_results": evaluation_results
    }

    bundle_path = os.path.join(save_dir, "model_bundle.joblib")
    joblib.dump(model_bundle, bundle_path)
    print(f"Saved model bundle successfully to {bundle_path}")

    return model_bundle

if __name__ == "__main__":
    train_and_select_best_model()
