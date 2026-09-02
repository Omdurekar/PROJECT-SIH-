# REST API Documentation — SIH26103 Monitoring Platform

Welcome to the **REST API Reference Specification** for the SIH26103 Integrated Project Monitoring Platform.

All endpoints are hosted under prefix `/api/v1` (and directly mounted at root `/` for convenience).
Interactive Swagger UI / OpenAPI documentation is accessible at `http://127.0.0.1:8000/docs`.

---

## 📌 Table of Contents

1. [Authentication (`/register`, `/login`)](#1-authentication)
2. [Monitored Projects API (`/projects`)](#2-monitored-projects-api)
3. [Historical Projects Dataset API (`/project/{name}`, `/projects/top-risk`, `/projects/dataset/search`)](#3-historical-projects-dataset-api)
4. [Machine Learning Predictions (`/predict`)](#4-machine-learning-predictions)
5. [Machine Learning Model Analytics & Explainability (`/ml/models`, `/ml/explainability/shap`)](#5-machine-learning-model-analytics--explainability)
6. [Milestones & Progress Tracking (`/milestones`, `/progress`)](#6-milestones--progress-tracking)
7. [Risk Management & Dashboard (`/risks`, `/dashboard/overview`)](#7-risk-management--dashboard)
8. [Governance & Audit Trail (`/audit-logs`)](#8-governance--audit-trail)

---

## 🔐 1. Authentication

### `POST /api/v1/register`
Registers a new user account with role-based access control.

* **Status Code**: `201 Created`
* **Request Payload**:
```json
{
  "username": "officer_rajesh",
  "email": "rajesh@monitoring.gov.in",
  "password": "SecurePassword123",
  "role": "Monitoring Officer",
  "department": "Ministry of Railways"
}
```
* **Response Payload**:
```json
{
  "id": 1,
  "username": "officer_rajesh",
  "email": "rajesh@monitoring.gov.in",
  "role": "Monitoring Officer",
  "department": "Ministry of Railways",
  "created_at": "2026-08-30T02:00:00"
}
```

---

### `POST /api/v1/login`
Authenticates credentials and returns a Bearer JWT access token.

* **Status Code**: `200 OK`
* **Request Payload**:
```json
{
  "username": "officer_rajesh",
  "password": "SecurePassword123"
}
```
* **Response Payload**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "officer_rajesh",
    "email": "rajesh@monitoring.gov.in",
    "role": "Monitoring Officer",
    "department": "Ministry of Railways",
    "created_at": "2026-08-30T02:00:00"
  }
}
```

---

## 📁 2. Monitored Projects API

### `POST /api/v1/projects`
Registers a new monitored project.

* **Status Code**: `201 Created`
* **Request Payload**:
```json
{
  "project_code": "PRJ-9001",
  "name": "Delhi-Mumbai Dedicated Freight Corridor Phase 2",
  "department": "Ministry of Railways",
  "project_type": "Transportation",
  "location": "Gujarat Section",
  "budget": 2400.0,
  "planned_start_date": "2024-01-01",
  "planned_end_date": "2027-12-31",
  "planned_duration_days": 1461
}
```

---

### `GET /api/v1/projects`
Lists all active monitored projects.

* **Parameters**:
  - `skip` (int, default `0`): Pagination offset.
  - `limit` (int, default `100`): Maximum records.
  - `department` (string, optional): Filter by department.
  - `delay_level` (string, optional): Filter by delay severity (`LOW`, `MEDIUM`, `HIGH`).

---

### `GET /api/v1/projects/{project_id}`
Retrieves complete details for a specific project by primary key ID.

---

### `PUT /api/v1/projects/{project_id}`
Updates details of an existing project.

---

### `DELETE /api/v1/projects/{project_id}`
Deletes a project and records an audit log entry.

---

## 📊 3. Historical Projects Dataset API

### `GET /api/v1/project/{project_name}` or `GET /api/v1/projects/by-name/{project_name}`
Retrieves historical project records matching a specific project name (supports substring and case-insensitive lookup).

* **Method**: `GET`
* **Path Parameter**: `project_name` (string) — Name or partial name of project (e.g. `BELONIA`, `MEHKAR TO AJISPUR`).
* **Response Payload**: Array of matching project objects:
```json
[
  {
    "id": 2,
    "global_project_id": "9515cef5760c496b",
    "project_name_clean": "BELONIA",
    "report_date": "2024-04-30",
    "project_status": "Ongoing",
    "sector_clean": "General",
    "agency_clean": "Unknown Agency",
    "state_clean": "Unknown State",
    "cost_original": 18.6,
    "cost_anticipated": 6.0,
    "cost_revised": null,
    "cost_overrun_amount_calc": -12.6,
    "cost_overrun_percent_clean": -67.74,
    "time_overrun_months_calc": 1.0,
    "total_planned_duration_months": 47.0,
    "project_age_months": 47.0,
    "remaining_schedule_months": -67.74,
    "physical_progress_clean": 1.0,
    "time_overrun_prediction": 1,
    "time_overrun_probability": 0.5198,
    "cost_overrun_prediction": 1,
    "cost_overrun_probability": 0.8979,
    "risk_class_prediction": 2,
    "risk_class_probability": 0.9755,
    "risk_class_0_probability": 0.0084,
    "risk_class_1_probability": 0.0160,
    "risk_class_2_probability": 0.9755,
    "created_at": "2026-08-30T02:00:00"
  }
]
```

---

### `GET /api/v1/projects/by-id/{global_project_id}`
Retrieves a project record directly by unique `global_project_id`.

* **Method**: `GET`
* **Path Parameter**: `global_project_id` (string, e.g. `fdb6143bd65654ce`)

---

### `GET /api/v1/projects/top-risk`
Retrieves top high-risk ongoing projects requiring priority intervention.

* **Method**: `GET`
* **Query Parameter**: `limit` (int, default `10`, range `1–100`)
* **Response Payload**:
```json
[
  {
    "id": 1,
    "global_project_id": "fdb6143bd65654ce",
    "project_name_clean": "MLD PHASE II STP 114 MLD AND PHASE III S",
    "report_date": "2024-04-30",
    "project_status": "Ongoing",
    "predicted_risk_class": 2,
    "predicted_risk_probability": 0.9764,
    "cost_original": 10.0,
    "cost_anticipated": 3.0,
    "time_overrun_months_calc": -7.0,
    "analysis_details": { ... },
    "created_at": "2026-08-30T02:00:00"
  }
]
```

---

### `GET /api/v1/projects/dataset/search`
Filters dataset projects across multi-criteria attributes.

* **Method**: `GET`
* **Query Parameters**:
  - `search` (string, optional): Text query for name, agency, or ID.
  - `sector` (string, optional): Filter by sector (`General`, `Transportation`, `Power`).
  - `state` (string, optional): Filter by state.
  - `status` (string, optional): Filter by project status (`Ongoing`, `Delayed`, `Completed`).
  - `skip` (int, default `0`)
  - `limit` (int, default `100`)

---

## 🤖 4. Machine Learning Predictions

### `POST /api/v1/predict`
Submits real-time project metrics to the Machine Learning pipeline and returns predicted delay category, confidence score, and derived metrics.

* **Method**: `POST`
* **Request Payload**:
```json
{
  "budget": 2400.0,
  "expenditure": 1800.0,
  "planned_duration_days": 1461,
  "time_elapsed_days": 1100,
  "completion_percentage": 42.0,
  "total_milestones": 25,
  "completed_milestones": 8,
  "delayed_milestones": 9,
  "pending_milestones": 8,
  "risk_score": 7.8,
  "project_id": 1
}
```
* **Response Payload**:
```json
{
  "project_id": 1,
  "delay_level": "HIGH",
  "confidence": 0.985,
  "derived_metrics": {
    "schedule_variance_days": 361.0,
    "budget_variance": 600.0,
    "time_elapsed_pct": 75.29,
    "progress_variance": -33.29,
    "milestone_delay_ratio": 0.36,
    "milestone_completion_ratio": 0.32,
    "expenditure_pct": 75.0,
    "remaining_duration_days": 361.0
  },
  "predicted_at": "2026-08-30T02:00:00"
}
```

---

## 📈 5. Machine Learning Model Analytics & Explainability

### `GET /api/v1/ml/models`
Lists evaluation summaries and performance metrics for all candidate trained ML models (Random Forest, XGBoost, KNN, Logistic Regression).

* **Method**: `GET`
* **Response Payload**: Array of model evaluation objects:
```json
[
  {
    "id": 1,
    "model_key": "random_forest_risk_classification",
    "model_name": "Random Forest Multiclass Risk Classifier",
    "task": "classification",
    "target": "target_risk_class",
    "target_definition": "Multiclass target representing overall project implementation risk level (0=Low, 1=Medium, 2=High).",
    "dataset_info": {
      "train_sample_count": 6627,
      "test_sample_count": 1103,
      "train_period": "2012-2019",
      "test_period": "2022-2025"
    },
    "best_model_parameters": {
      "n_estimators": 200,
      "max_depth": 12,
      "class_weight": "balanced"
    },
    "test_performance": {
      "accuracy": 0.892,
      "precision": 0.884,
      "recall": 0.879,
      "f1": 0.881,
      "roc_auc": 0.941
    },
    "cross_validation_results": { ... },
    "leakage_audit": {
      "status": "PASSED",
      "training_test_leakage": false,
      "future_features_used": false
    },
    "top_feature_importance": [ ... ],
    "created_at": "2026-08-30T02:00:00"
  }
]
```

---

### `GET /api/v1/ml/models/{model_key}`
Retrieves full evaluation report, hyperparameters, cross-validation metrics, confusion matrix, and leakage audit for a specific model key.

* **Method**: `GET`
* **Path Parameter**: `model_key` (string, e.g., `random_forest_risk_classification`, `knn_cost_overrun`, `logistic_regression_time_overrun`)

---

### `GET /api/v1/ml/explainability/shap`
Retrieves consolidated SHAP (SHapley Additive exPlanations) feature importance values across models for transparent AI explainability.

* **Method**: `GET`
* **Response Payload**:
```json
{
  "time_overrun": {
    "model_name": "Random Forest Time Overrun Classifier",
    "top_feature": "time_overrun_months_calc",
    "features": [
      {
        "feature": "time_overrun_months_calc",
        "mean_abs_shap": 0.016035,
        "direction": "Higher values decrease risk (-)"
      },
      {
        "feature": "remaining_schedule_months",
        "mean_abs_shap": 0.015146,
        "direction": "Higher values decrease risk (-)"
      }
    ]
  },
  "cost_overrun": { ... },
  "risk_class": { ... }
}
```

---

## 🎯 6. Milestones & Progress Tracking

### `POST /api/v1/milestones`
Registers a deliverable milestone for a project.

### `GET /api/v1/projects/{project_id}/milestones`
Lists all milestones associated with a project.

### `POST /api/v1/progress`
Records a new progress snapshot (completion percentage & expenditure), triggering auto-recalculation of project metrics and status.

### `GET /api/v1/projects/{project_id}/progress`
Retrieves historical time-series progress log entries for a project.

---

## ⚠️ 7. Risk Management & Dashboard

### `GET /api/v1/risks`
Lists risks logged across all projects or for a specific `project_id`.

### `POST /api/v1/risks`
Logs an operational or regulatory risk for a project.

### `GET /api/v1/dashboard/overview`
Aggregates high-level executive metrics across all departments:
```json
{
  "total_projects": 150,
  "delay_distribution": {
    "LOW": 95,
    "MEDIUM": 38,
    "HIGH": 17
  },
  "total_budget": 45200.0,
  "utilized_budget": 28400.0,
  "avg_completion_percentage": 61.4,
  "high_priority_projects": [ ... ],
  "department_summary": { ... }
}
```

---

## 🔐 8. Governance & Audit Trail

### `GET /api/v1/audit-logs`
Retrieves system audit logs recorded for compliance, governance, and traceability.

* **Query Parameters**: `skip` (int), `limit` (int)
* **Response Payload**:
```json
[
  {
    "id": 1,
    "username": "officer_rajesh",
    "action": "PROJECT_CREATE",
    "entity_type": "Project",
    "entity_id": "1",
    "details": "Created project PRJ-9001: Delhi-Mumbai Dedicated Freight Corridor Phase 2",
    "timestamp": "2026-08-30T02:00:00"
  }
]
```
