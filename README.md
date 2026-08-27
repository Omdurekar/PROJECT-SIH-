# SIH26103 — Integrated Project Monitoring Platform

## 📌 Overview

The **Integrated Project Monitoring Platform** is an enterprise-grade backend system developed for **SIH26103**. It provides government officials, project managers, and monitoring officers with a centralized data-driven system to track infrastructure and public project progress, manage risks, detect schedule/budget anomalies, and prioritize projects requiring urgent intervention.

The platform integrates a **FastAPI backend**, an **encapsulated database abstraction layer**, a dedicated **business service layer**, and a **Machine Learning pipeline** that automatically classifies project delay risk levels:

* 🟢 **LOW DELAY**: Project is executing within nominal progress and schedule parameters.
* 🟡 **MEDIUM DELAY**: Project exhibits minor schedule/budget slippage requiring close monitoring.
* 🔴 **HIGH DELAY**: Project has critical delays, milestone bottlenecks, or high risk scores requiring immediate intervention.

---

# 🎯 Key Objectives

* **Centralized Data Aggregation**: Consolidates multi-department project tracking data into a unified platform.
* **Milestone & Progress Management**: Tracks granular phase completions, expenditure utilization, and completion percentages.
* **ML-Driven Delay Prediction**: Classifies project delay severity using multi-feature predictive models (Random Forest, XGBoost, Decision Tree).
* **High-Priority Risk Identification**: Automatically flags projects with negative progress variance or critical operational risks.
* **Audit Trail & Governance**: Records every critical operational change (progress updates, risk escalations, project modifications) for transparency and accountability.
* **Modular & Scalable Backend**: Implements clean layer separation (API Router ➔ Service Layer ➔ Database Layer ➔ Storage).

---

# 🏗️ Modular Architecture Layout

The repository follows a clean **feature-oriented modular architecture**, separating API endpoint handlers, business logic, database operations, ORM schemas, and machine learning scripts into distinct compartments:

```text
c:\Users\Abhay Kinkar\PROJECT-SIH-\
│
├── app/                        # Main FastAPI Application Compartment
│   ├── __init__.py
│   ├── main.py                 # Application entry point, CORS, startup events
│   ├── api.py                  # Consolidated FastAPI endpoint handlers & request validation
│   │
│   ├── config/                 # System Settings & Database Connection
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy engine, session maker, DB dependency
│   │   └── settings.py         # App environment variables & JWT configuration
│   │
│   ├── models/                 # Database ORM Entities & Pydantic Data Schemas
│   │   ├── __init__.py         # Re-exports models & schemas
│   │   ├── user.py             # User ORM model, UserCreate, UserLogin, Token
│   │   ├── project.py          # Project ORM model, ProjectCreate, ProjectUpdate, ProjectResponse
│   │   ├── milestone.py        # Milestone ORM model & schemas
│   │   ├── progress.py         # ProgressUpdate ORM model & schemas
│   │   ├── risk.py             # Risk ORM model & schemas
│   │   └── prediction.py       # PredictionLog, AuditLog, Prediction schemas & Dashboard models
│   │
│   ├── database/               # Encapsulated Data Access Layer (CRUD)
│   │   ├── __init__.py
│   │   ├── users.py            # User queries & creation
│   │   ├── projects.py         # Project CRUD queries & stats aggregation
│   │   ├── milestones.py       # Milestone queries & status updates
│   │   ├── progress.py         # Progress log insertions & history queries
│   │   ├── risks.py            # Risk tracking queries
│   │   ├── predictions.py      # ML prediction log persistence
│   │   └── audit.py            # Audit log recording & retrieval
│   │
│   ├── services/               # Core Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth.py             # User registration & password/token authentication
│   │   ├── projects.py         # Project lifecycle & audit logging
│   │   ├── milestones.py       # Milestone management service
│   │   ├── progress.py         # Progress tracking & project status auto-updates
│   │   ├── predictions.py      # ML model inference & derived feature pipeline integration
│   │   ├── risks.py            # Risk assessment & project risk score updating
│   │   └── dashboard.py        # Monitoring metrics, budget utilization & high-priority project aggregation
│   │
│   └── utils/                  # Utility Functions & Helpers
│       ├── __init__.py
│       ├── auth.py             # JWT token creation/decoding, bcrypt password hashing
│       └── helpers.py          # Derived metric formulas & date calculation utilities
│
├── ml/                         # Machine Learning Pipeline
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── generate_dataset.py # Synthetic historical project dataset generator
│   ├── preprocessing.py        # Data cleaning, scaling (StandardScaler), & label encoding
│   ├── feature_engineering.py  # Domain-specific feature calculation engine
│   ├── train.py                # Candidate model trainer (Random Forest, XGBoost, Decision Tree, Logistic Regression)
│   ├── evaluate.py             # Evaluation metrics (Accuracy, F1, Precision, Recall, Confusion Matrix)
│   └── saved_model/
│       └── model_bundle.joblib # Serialized best model, scaler & feature definitions
│
├── tests/                      # Automated Test Suite
│   ├── __init__.py
│   └── test_api.py             # Pytest suite covering all API routes & ML inference
│
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation & developer guide
```

---

# 🔗 Backend Request Flow & Layer Separation

```text
    ┌───────────────────────────┐
    │  HTTP Request (Client)    │
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │        app/api.py         │  <--- Validates Input Schemas (Pydantic)
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │       app/services/       │  <--- Business Rules, ML Model Call, Logic
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │       app/database/       │  <--- Abstract Data Access Layer (SQLAlchemy CRUD)
    └─────────────┬─────────────┘
                  │
                  ▼
    ┌───────────────────────────┐
    │   Database / SQLite / PG  │  <--- Database Layer
    └───────────────────────────┘
```

### Layer Responsibilities:

1. **API Router (`app/api.py`)**: Receives HTTP requests, validates payload format using Pydantic schemas, delegates business operations to services, and returns HTTP responses with proper status codes.
2. **Services (`app/services/`)**: Implements application logic, orchestrates feature engineering and ML prediction calls, updates project metrics, triggers audit logs, and enforces domain rules.
3. **Database Layer (`app/database/`)**: Contains pure database queries. Separates ORM operations from business logic to enable database backend switching (e.g. SQLite ➔ PostgreSQL / MongoDB) without altering API endpoints or services.
4. **Models (`app/models/`)**: Structured into separate domain files (`user.py`, `project.py`, `milestone.py`, `progress.py`, `risk.py`, `prediction.py`) defining SQLAlchemy ORM tables and Pydantic schemas.

---

# 🤖 Machine Learning Engine, Tasks & Feature Engineering

The platform's ML Engine provides a multi-task predictive analytics pipeline combining **Classification**, **Regression**, and **Explainable AI (SHAP Analysis)**.

---

## 🎯 Prediction Tasks & Target Metrics

| Task | Type | Description / Output Format |
| :--- | :--- | :--- |
| **Time Overrun Prediction** | **Regression** | Predicts estimated schedule delay in days ($\Delta t$). |
| **Time Overrun Risk** | **Classification** | Classifies schedule delay severity (🟢 LOW, 🟡 MEDIUM, 🔴 HIGH). |
| **Cost Overrun Prediction** | **Regression** | Predicts projected financial budget overrun in ₹ Crores ($\Delta C$). |
| **Cost Overrun Risk** | **Classification** | Classifies financial budget overrun severity (🟢 LOW, 🟡 MEDIUM, 🔴 HIGH). |
| **Overall Implementation Risk** | **Classification** | Overall project execution status & health grade (🟢 LOW, 🟡 MEDIUM, 🔴 HIGH). |
| **Composite Risk Score** | **Score (0–100)** | Quantitative composite project risk score calculated on a 0 to 100 scale. |

---

## 📐 Derived Feature Formulas

The feature engineering pipeline derives 8 key domain metrics used as inputs for both regression and classification algorithms:

| Feature Name | Mathematical Formula | Purpose / Significance |
| :--- | :--- | :--- |
| **Time Elapsed %** | $\left( \frac{\text{Time Elapsed Days}}{\text{Planned Duration Days}} \right) \times 100$ | Relative schedule consumption rate |
| **Schedule Variance (Days)** | $\text{Planned Duration Days} - \text{Time Elapsed Days}$ | Days remaining before planned deadline |
| **Budget Variance** | $\text{Budget} - \text{Expenditure}$ | Financial margin remaining in Crores |
| **Progress Variance (%)** | $\text{Completion \%} - \text{Time Elapsed \%}$ | Discrepancy between actual vs. expected progress |
| **Milestone Delay Ratio** | $\frac{\text{Delayed Milestones}}{\text{Total Milestones}}$ | Ratio of blocked/overdue deliverables |
| **Milestone Completion Ratio** | $\frac{\text{Completed Milestones}}{\text{Total Milestones}}$ | Deliverable completion rate |
| **Expenditure %** | $\left( \frac{\text{Expenditure}}{\text{Budget}} \right) \times 100$ | Financial budget utilization rate |
| **Remaining Duration (Days)** | $\max(0, \text{Planned Duration Days} - \text{Time Elapsed Days})$ | Remaining project execution timeframe |

---

## 🧪 Candidate Models Suite

The framework trains and evaluates candidate models across classification and regression tasks using cross-validation:

### 1. Classification Models (Risk Levels & Health Category)
* **Random Forest Classifier**: Ensemble decision tree model capturing non-linear interactions.
* **XGBoost / Gradient Boosting**: Boosted decision trees optimized for tabular classification.
* **K-Nearest Neighbors (KNN) Classifier**: Distance-based instance learning for project similarity profiling.
* **Logistic Regression**: Linear baseline probabilistic model.
* **Decision Tree Classifier**: Interpretable baseline decision rules.

### 2. Regression Models (Cost & Time Overrun Numerical Predictions)
* **Random Forest Regressor**: Predicts continuous schedule delay days ($\Delta t$) and cost overrun ($\Delta C$).
* **XGBoost Regressor**: Gradient boosting regression for numerical overrun estimation.
* **K-Nearest Neighbors (KNN) Regressor**: Distance-based numerical prediction based on historical project clusters.
* **Ridge / Linear Regression**: Linear baseline continuous prediction.

---

## 🔍 Explainable AI (SHAP Analysis)

To ensure predictions are transparent and explainable for government authorities rather than acting as a black box:
* **SHAP (SHapley Additive exPlanations)** values are calculated for both global feature importance and local instance predictions.
* **Global Importance Summary Plots**: Ranks which features (e.g. *Progress Variance*, *Milestone Delay Ratio*, *Risk Score*) contribute most to project delays.
* **Local Waterfall & Force Plots**: Explains *why* a specific project was classified as **HIGH Risk** or predicted to have a 120-day time overrun by breaking down the positive/negative contribution of each metric.

---

# 🚀 REST API Reference Specification

All endpoints are hosted with prefix `/api/v1` (and directly at root `/` for convenience). Interactive Swagger UI documentation is available at `http://127.0.0.1:8000/docs`.

### 🔐 1. Authentication

#### `POST /register`
Creates a new system user with role-based access.
```json
// Request Body
{
  "username": "officer_rajesh",
  "email": "rajesh@monitoring.gov.in",
  "password": "SecurePassword123",
  "role": "Monitoring Officer",
  "department": "Ministry of Railways"
}
```

#### `POST /login`
Authenticates credentials and returns a JWT Bearer token.
```json
// Request Body
{
  "username": "officer_rajesh",
  "password": "SecurePassword123"
}
```

---

### 📁 2. Project Management

#### `POST /projects`
Registers a new project in the platform.
```json
// Request Body
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

#### `GET /projects`
Lists all monitored projects. Supports optional query parameters `department` and `delay_level`.

#### `GET /projects/{project_id}`
Retrieves complete details for a specific project.

#### `PUT /projects/{project_id}`
Updates editable project details (budget, status, name).

#### `DELETE /projects/{project_id}`
Deletes a project record and logs an audit trail entry.

---

### 🎯 3. Milestone & Progress Management

#### `POST /milestones`
Creates a target milestone for a project.
```json
// Request Body
{
  "project_id": 1,
  "name": "Land Acquisition & Environmental Clearance",
  "target_date": "2024-09-30",
  "status": "COMPLETED",
  "completion_percentage": 100.0
}
```

#### `POST /progress`
Records a progress update and automatically recalculates overall completion percentage and status.
```json
// Request Body
{
  "project_id": 1,
  "completion_percentage": 62.5,
  "expenditure": 1350.0,
  "reported_by": "Officer Rajesh",
  "remarks": "Track alignment 60% complete, signaling setup in progress."
}
```

---

### 🤖 4. Machine Learning Delay Prediction

#### `POST /predict`
Submits real-time project metrics to the trained ML model and returns predicted delay category, confidence score, and feature metrics.
```json
// Request Body
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

```json
// Response Payload
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
  "predicted_at": "2026-08-27T14:35:00"
}
```

---

### ⚠️ 5. Risk Management & Dashboard Overview

#### `POST /risks`
Logs an operational or regulatory risk for a project.

#### `GET /dashboard/overview`
Aggregates high-level project monitoring statistics across departments:
```json
// Response Payload
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

# 🛠️ Setup & Execution Guide

### 1. Prerequisites
* **Python 3.10+**

### 2. Environment Setup
Clone the repository and install the dependencies:
```bash
git clone https://github.com/Omdurekar/PROJECT-SIH-.git
cd PROJECT-SIH-

python -m pip install -r requirements.txt
```

### 3. Generate Machine Learning Model
Train candidate models on synthetic historical dataset and save the optimal model bundle:
```bash
python ml/train.py
```
*Output*: Generates dataset at `ml/data/projects_dataset.csv` and serializes best model to `ml/saved_model/model_bundle.joblib`.

### 4. Run FastAPI Backend Server
Launch the application server with live reload:
```bash
python app/main.py
```
Alternatively using Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open **`http://127.0.0.1:8000/docs`** in your browser to access the interactive OpenAPI / Swagger UI documentation.

---

# 🧪 Automated Testing

Run the automated test suite covering API routes, authentication, project lifecycle, and ML prediction integration:

```bash
python -m pytest tests/test_api.py -v
```

---

# 🔐 Audit Logging & Governance

Every critical operation performed on the platform is automatically recorded in the `audit_logs` table via `app/database/audit.py`. This ensures full operational governance, allowing supervisors to track:
* User registrations and authentication events
* Project creation, status updates, and deletions
* Progress reports and completion updates
* Risk score escalations and mitigation assignments