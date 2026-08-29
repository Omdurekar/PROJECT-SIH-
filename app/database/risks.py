from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.orm import Risk
from app.models.schemas import RiskCreate, RiskUpdate

def create_risk(db: Session, risk_in: RiskCreate) -> Risk:
    db_risk = Risk(
        project_id=risk_in.project_id,
        title=risk_in.title,
        description=risk_in.description,
        category=risk_in.category or "Operational",
        severity=risk_in.severity or "MEDIUM",
        status="OPEN",
        mitigation_plan=risk_in.mitigation_plan
    )
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk

def get_risks_by_project(db: Session, project_id: int) -> List[Risk]:
    return db.query(Risk).filter(Risk.project_id == project_id).all()

def list_all_risks(db: Session, skip: int = 0, limit: int = 100) -> List[Risk]:
    return db.query(Risk).order_by(Risk.id.desc()).offset(skip).limit(limit).all()

def update_risk(db: Session, risk_id: int, risk_in: RiskUpdate) -> Optional[Risk]:
    db_risk = db.query(Risk).filter(Risk.id == risk_id).first()
    if not db_risk:
        return None

    update_data = risk_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_risk, field, value)

    db.commit()
    db.refresh(db_risk)
    return db_risk
