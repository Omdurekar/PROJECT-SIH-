import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config.settings import settings
from app.database import otp as db_otp
from app.database import users as db_users
from app.database import audit as db_audit
from app.utils.otp import generate_otp, hash_otp, verify_otp
from app.utils.email import send_otp_email, EmailDeliveryError


def request_otp_service(db: Session, email: str) -> dict:
    """
    Generates, hashes, stores, and sends a new OTP for registration email verification.
    Enforces resend cooldown and invalidates previous OTPs.
    """
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is required."
        )

    # 1. Check existing active OTP for resend cooldown
    active_otp = db_otp.get_latest_active_otp(db, email)
    if active_otp:
        now = datetime.datetime.utcnow()
        elapsed = (now - active_otp.last_sent_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Resend cooldown active. Please wait before requesting another OTP."
            )

    # 2. Invalidate previous active OTPs for this email
    db_otp.invalidate_existing_otps(db, email)

    # 3. Generate plaintext OTP and calculate hash + expiry
    plaintext_otp = generate_otp()
    hashed_otp = hash_otp(plaintext_otp)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    # 4. Create OTP database record
    otp_record = db_otp.create_otp_record(
        db=db,
        email=email,
        hashed_otp=hashed_otp,
        expires_at=expires_at,
        last_sent_at=datetime.datetime.utcnow()
    )

    # 5. Send OTP via email; rollback record if delivery fails
    try:
        send_otp_email(email, plaintext_otp)
    except Exception:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please try again later."
        )

    # 6. Log audit event
    db_audit.create_audit_entry(
        db,
        action="OTP_REQUESTED",
        entity_type="OTP",
        entity_id=email,
        details=f"OTP generated and sent to {email}"
    )

    return {
        "message": "OTP sent successfully to email.",
        "email": email
    }


def verify_otp_service(db: Session, email: str, otp: str) -> dict:
    """
    Verifies a submitted plaintext OTP against the latest active OTP for an email address.
    Checks expiration, attempt limits, marks OTP as used, and updates User.is_verified.
    """
    if not email or not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and OTP are required."
        )

    # 1. Retrieve latest active OTP
    active_otp = db_otp.get_latest_active_otp(db, email)
    if not active_otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active OTP found for this email."
        )

    now = datetime.datetime.utcnow()

    # 2. Check whether OTP has expired
    if now > active_otp.expires_at:
        active_otp.is_invalidated = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired."
        )

    # 3. Check attempt limit prior to verification
    if active_otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        active_otp.is_invalidated = True
        db.commit()
        db_audit.create_audit_entry(
            db,
            action="OTP_MAX_ATTEMPTS_EXCEEDED",
            entity_type="OTP",
            entity_id=email,
            details="Maximum OTP verification attempts exceeded"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum OTP verification attempts exceeded."
        )

    # 4. Verify OTP cryptography
    is_valid = verify_otp(otp, active_otp.hashed_otp)
    if not is_valid:
        db_otp.increment_attempts(db, active_otp)
        if active_otp.attempts >= settings.OTP_MAX_ATTEMPTS:
            active_otp.is_invalidated = True
            db.commit()
            db_audit.create_audit_entry(
                db,
                action="OTP_MAX_ATTEMPTS_EXCEEDED",
                entity_type="OTP",
                entity_id=email,
                details="Maximum OTP verification attempts exceeded"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum OTP verification attempts exceeded."
            )
        else:
            db_audit.create_audit_entry(
                db,
                action="OTP_VERIFICATION_FAILED",
                entity_type="OTP",
                entity_id=email,
                details="Incorrect OTP attempt"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP."
            )

    # 5. On successful OTP verification
    db_otp.mark_otp_as_used(db, active_otp)

    # Update corresponding user is_verified status if user exists
    user = db_users.get_user_by_email(db, email)
    if user:
        user.is_verified = True
        db.commit()
        db.refresh(user)

    db_audit.create_audit_entry(
        db,
        action="OTP_VERIFICATION_SUCCESS",
        entity_type="OTP",
        entity_id=email,
        details=f"OTP successfully verified for {email}"
    )

    return {
        "message": "OTP verified successfully.",
        "email": email,
        "is_verified": True if user else False
    }
