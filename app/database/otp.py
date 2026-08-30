import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.orm import OTPVerification

def create_otp_record(
    db: Session,
    email: str,
    hashed_otp: str,
    expires_at: datetime.datetime,
    last_sent_at: Optional[datetime.datetime] = None
) -> OTPVerification:
    now = datetime.datetime.utcnow()
    db_otp = OTPVerification(
        email=email,
        hashed_otp=hashed_otp,
        attempts=0,
        created_at=now,
        expires_at=expires_at,
        last_sent_at=last_sent_at or now,
        is_used=False,
        is_invalidated=False
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def get_latest_active_otp(db: Session, email: str) -> Optional[OTPVerification]:
    return (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.is_used == False,
            OTPVerification.is_invalidated == False
        )
        .order_by(OTPVerification.created_at.desc(), OTPVerification.id.desc())
        .first()
    )

def invalidate_existing_otps(db: Session, email: str) -> int:
    count = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.is_used == False,
            OTPVerification.is_invalidated == False
        )
        .update({OTPVerification.is_invalidated: True}, synchronize_session=False)
    )
    db.commit()
    return count

def increment_attempts(db: Session, otp_record: OTPVerification) -> OTPVerification:
    otp_record.attempts += 1
    db.commit()
    db.refresh(otp_record)
    return otp_record

def mark_otp_as_used(db: Session, otp_record: OTPVerification) -> OTPVerification:
    otp_record.is_used = True
    db.commit()
    db.refresh(otp_record)
    return otp_record

def get_otp_by_id(db: Session, otp_id: int) -> Optional[OTPVerification]:
    return db.query(OTPVerification).filter(OTPVerification.id == otp_id).first()
