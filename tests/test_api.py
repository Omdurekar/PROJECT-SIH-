import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

from unittest.mock import patch

def test_user_registration_and_login():
    uname = f"officer_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@monitoring.gov.in"
    reg_data = {
        "username": uname,
        "email": email,
        "password": "SecurePassword123",
        "role": "Monitoring Officer",
        "department": "Ministry of Railways"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        response = client.post("/api/v1/auth/register", json=reg_data)
        assert response.status_code == 201
        assert response.json()["username"] == uname
        assert response.json()["is_verified"] is False

        login_data = {
            "username": uname,
            "password": "SecurePassword123"
        }
        # Unverified user login must be rejected
        unverified_res = client.post("/api/v1/auth/login", json=login_data)
        assert unverified_res.status_code == 403
        assert "verification required" in unverified_res.json()["detail"].lower()

        # Extract generated OTP from mock call args and verify via API
        otp_code = mock_send.call_args[0][1]
        verify_res = client.post("/api/v1/auth/verify-otp", json={"email": email, "otp_code": otp_code})
        assert verify_res.status_code == 200
        assert verify_res.json()["is_verified"] is True

        # Verified user login must succeed
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()



def test_project_lifecycle():
    code = f"PRJ-{uuid.uuid4().hex[:6].upper()}"
    proj_data = {
        "project_code": code,
        "name": "High-Speed Rail Corridor Test Project",
        "department": "Ministry of Railways",
        "project_type": "Transportation",
        "location": "Mumbai-Ahmedabad",
        "budget": 1200.0,
        "planned_start_date": "2024-01-01",
        "planned_end_date": "2026-12-31",
        "planned_duration_days": 1095
    }
    # Create Project
    res = client.post("/projects", json=proj_data)
    assert res.status_code == 201
    project_id = res.json()["id"]

    # List Projects
    res = client.get("/projects")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # Get Single Project
    res = client.get(f"/projects/{project_id}")
    assert res.status_code == 200
    assert res.json()["project_code"] == code

    # Add Milestone
    milestone_data = {
        "project_id": project_id,
        "name": "Land Acquisition Phase 1",
        "target_date": "2024-06-30",
        "status": "COMPLETED",
        "completion_percentage": 100.0
    }
    res = client.post("/milestones", json=milestone_data)
    assert res.status_code == 201

    # Record Progress
    prog_data = {
        "project_id": project_id,
        "completion_percentage": 45.0,
        "expenditure": 480.0,
        "reported_by": "Test Officer",
        "remarks": "On schedule"
    }
    res = client.post("/progress", json=prog_data)
    assert res.status_code == 201

    # Log Risk
    risk_data = {
        "project_id": project_id,
        "title": "Right of Way clearance delay",
        "severity": "HIGH",
        "category": "Regulatory",
        "mitigation_plan": "Expedite state liaison"
    }
    res = client.post("/risks", json=risk_data)
    assert res.status_code == 201

def test_ml_prediction_endpoint():
    # Low delay test payload
    low_payload = {
        "budget": 500.0,
        "expenditure": 200.0,
        "planned_duration_days": 365,
        "time_elapsed_days": 150,
        "completion_percentage": 50.0,
        "total_milestones": 10,
        "completed_milestones": 5,
        "delayed_milestones": 0,
        "pending_milestones": 5,
        "risk_score": 1.5
    }
    res = client.post("/predict", json=low_payload)
    assert res.status_code == 200
    data = res.json()
    assert "delay_level" in data
    assert data["delay_level"] in ["LOW", "MEDIUM", "HIGH"]

    # High delay test payload
    high_payload = {
        "budget": 1000.0,
        "expenditure": 900.0,
        "planned_duration_days": 365,
        "time_elapsed_days": 400,
        "completion_percentage": 30.0,
        "total_milestones": 20,
        "completed_milestones": 5,
        "delayed_milestones": 12,
        "pending_milestones": 3,
        "risk_score": 8.5
    }
    res = client.post("/predict", json=high_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["delay_level"] in ["MEDIUM", "HIGH"]

def test_dashboard_overview():
    res = client.get("/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert "total_projects" in data
    assert "delay_distribution" in data
    assert "utilized_budget" in data

def test_audit_logs():
    res = client.get("/audit-logs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_dataset_project_retrieval():
    # Test GET /project/{project_name}
    res = client.get("/project/BELONIA")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "BELONIA" in data[0]["project_name_clean"]

    # Test GET /projects/by-name/{project_name}
    res_by_name = client.get("/projects/by-name/BELONIA")
    assert res_by_name.status_code == 200
    assert len(res_by_name.json()) >= 1

    # Test GET /projects/by-id/{global_project_id}
    global_id = data[0]["global_project_id"]
    res_by_id = client.get(f"/projects/by-id/{global_id}")
    assert res_by_id.status_code == 200
    assert res_by_id.json()["global_project_id"] == global_id

def test_top_risk_projects_retrieval():
    res = client.get("/projects/top-risk")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_ml_model_summaries():
    res = client.get("/ml/models")
    assert res.status_code == 200
    models = res.json()
    assert isinstance(models, list)
    assert len(models) >= 1

    model_key = models[0]["model_key"]
    res_single = client.get(f"/ml/models/{model_key}")
    assert res_single.status_code == 200
    assert res_single.json()["model_key"] == model_key

def test_shap_explainability():
    res = client.get("/ml/explainability/shap")
    assert res.status_code == 200
    assert isinstance(res.json(), dict)
