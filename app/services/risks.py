from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.schemas import RiskCreate, RiskUpdate, RiskResponse
from app.database import risks as db_risks
from app.database import projects as db_projects
from app.database import audit as db_audit

def create_risk_service(db: Session, risk_in: RiskCreate, username: str = "System") -> RiskResponse:
    project = db_projects.get_project_by_id(db, risk_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {risk_in.project_id} not found."
        )

    risk = db_risks.create_risk(db, risk_in)

    # Adjust project risk_score
    if risk.severity == "CRITICAL":
        project.risk_score = min(10.0, project.risk_score + 3.0)
    elif risk.severity == "HIGH":
        project.risk_score = min(10.0, project.risk_score + 2.0)
    elif risk.severity == "MEDIUM":
        project.risk_score = min(10.0, project.risk_score + 1.0)
    db.commit()

    db_audit.create_audit_entry(
        db,
        action="RISK_CREATE",
        entity_type="Risk",
        entity_id=str(risk.id),
        username=username,
        details=f"Logged {risk.severity} risk '{risk.title}' for project {project.project_code}"
    )

    return RiskResponse.model_validate(risk)

def list_risks_service(db: Session, project_id: Optional[int] = None) -> List[RiskResponse]:
    if project_id:
        risks = db_risks.get_risks_by_project(db, project_id)
    else:
        risks = db_risks.list_all_risks(db)
    return [RiskResponse.model_validate(r) for r in risks]

def update_risk_service(
    db: Session,
    risk_id: int,
    risk_in: RiskUpdate,
    username: str = "System"
) -> RiskResponse:
    risk = db_risks.update_risk(db, risk_id, risk_in)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk with ID {risk_id} not found."
        )

    db_audit.create_audit_entry(
        db,
        action="RISK_UPDATE",
        entity_type="Risk",
        entity_id=str(risk_id),
        username=username,
        details=f"Updated risk {risk_id} to status {risk.status}"
    )

    return RiskResponse.model_validate(risk)
