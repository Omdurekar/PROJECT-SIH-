from typing import Dict, Any
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray, model_name: str = "Model") -> Dict[str, Any]:
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
    class_p, class_r, class_f1, _ = precision_recall_fscore_support(y_test, y_pred, average=None, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    high_delay_recall = class_r[2] if len(class_r) > 2 else 0.0

    metrics = {
        "model_name": model_name,
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "high_delay_recall": round(float(high_delay_recall), 4),
        "class_metrics": {
            "LOW": {"precision": round(float(class_p[0]), 4), "recall": round(float(class_r[0]), 4), "f1": round(float(class_f1[0]), 4)},
            "MEDIUM": {"precision": round(float(class_p[1]), 4), "recall": round(float(class_r[1]), 4), "f1": round(float(class_f1[1]), 4)},
            "HIGH": {"precision": round(float(class_p[2]), 4), "recall": round(float(class_r[2]), 4), "f1": round(float(class_f1[2]), 4)}
        },
        "confusion_matrix": cm.tolist()
    }
    return metrics
