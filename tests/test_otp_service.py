import datetime
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.config.database import SessionLocal, init_db
from app.models.orm import User, OTPVerification
from app.services.otp import request_otp_service, verify_otp_service
from app.utils.email import EmailDeliveryError
from app.config.settings import settings


@pytest.fixture(scope="function")
def db():
    """Provides a fresh database session for testing."""
    init_db()
    session = SessionLocal()
    session.query(OTPVerification).delete()
    session.commit()
    try:
        yield session
    finally:
        session.query(OTPVerification).delete()
        session.commit()
        session.close()


def test_1_successful_otp_generation_and_db_creation(db):
    """1. Successful OTP generation and database creation."""
    email = "test_gen@example.com"
    with patch("app.services.otp.send_otp_email") as mock_send:
        res = request_otp_service(db, email)
        assert res["email"] == email
        assert res["message"] == "OTP sent successfully to email."

        otp_record = (
            db.query(OTPVerification)
            .filter(OTPVerification.email == email, OTPVerification.is_used == False)
            .first()
        )
        assert otp_record is not None
        assert otp_record.attempts == 0
        assert otp_record.is_invalidated is False
        assert len(otp_record.hashed_otp) > 0
        assert otp_record.hashed_otp != mock_send.call_args[0][1]


def test_2_otp_email_sending(db):
    """2. OTP email sending."""
    email = "test_send@example.com"
    with patch("app.services.otp.send_otp_email") as mock_send:
        request_otp_service(db, email)
        mock_send.assert_called_once()
        sent_email, sent_otp = mock_send.call_args[0]
        assert sent_email == email
        assert len(sent_otp) == 6
        assert sent_otp.isdigit()


def test_3_otp_verification_success(db):
    """3. OTP verification success."""
    email = "test_verify@example.com"
    with patch("app.services.otp.send_otp_email") as mock_send:
        request_otp_service(db, email)
        sent_otp = mock_send.call_args[0][1]

        res = verify_otp_service(db, email, sent_otp)
        assert res["message"] == "OTP verified successfully."
        assert res["email"] == email

        otp_record = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        assert otp_record.is_used is True


def test_4_incorrect_otp_increments_attempts(db):
    """4. Incorrect OTP increments attempts."""
    email = "test_inc@example.com"
    with patch("app.services.otp.send_otp_email"):
        request_otp_service(db, email)

        with pytest.raises(HTTPException) as exc_info:
            verify_otp_service(db, email, "000000")
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid OTP."

        otp_record = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        assert otp_record.attempts == 1
        assert otp_record.is_invalidated is False


def test_5_maximum_attempts_invalidates_otp(db):
    """5. Maximum attempts invalidates the OTP."""
    email = "test_max@example.com"
    with patch("app.services.otp.send_otp_email"):
        request_otp_service(db, email)

        for i in range(settings.OTP_MAX_ATTEMPTS - 1):
            with pytest.raises(HTTPException):
                verify_otp_service(db, email, "000000")

        with pytest.raises(HTTPException) as exc_info:
            verify_otp_service(db, email, "000000")
        assert exc_info.value.status_code == 400
        assert "Maximum OTP verification attempts exceeded" in exc_info.value.detail

        otp_record = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        assert otp_record.attempts == settings.OTP_MAX_ATTEMPTS
        assert otp_record.is_invalidated is True


def test_6_expired_otp_is_rejected(db):
    """6. Expired OTP is rejected."""
    email = "test_expired@example.com"
    with patch("app.services.otp.send_otp_email") as mock_send:
        request_otp_service(db, email)
        sent_otp = mock_send.call_args[0][1]

        otp_record = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        otp_record.expires_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        db.commit()

        with pytest.raises(HTTPException) as exc_info:
            verify_otp_service(db, email, sent_otp)
        assert exc_info.value.status_code == 400
        assert "OTP has expired" in exc_info.value.detail


def test_7_resend_cooldown_is_enforced(db):
    """7. Resend cooldown is enforced."""
    email = "test_cooldown@example.com"
    with patch("app.services.otp.send_otp_email"):
        request_otp_service(db, email)

        with pytest.raises(HTTPException) as exc_info:
            request_otp_service(db, email)
        assert exc_info.value.status_code == 429
        assert "Resend cooldown active" in exc_info.value.detail


def test_8_resend_invalidates_previous_otp(db):
    """8. Resend invalidates the previous OTP."""
    email = "test_resend@example.com"
    with patch("app.services.otp.send_otp_email"):
        request_otp_service(db, email)
        first_otp = db.query(OTPVerification).filter(OTPVerification.email == email).first()

        first_otp.last_sent_at = datetime.datetime.utcnow() - datetime.timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS + 5)
        db.commit()

        request_otp_service(db, email)

        db.refresh(first_otp)
        assert first_otp.is_invalidated is True

        active_otps = (
            db.query(OTPVerification)
            .filter(
                OTPVerification.email == email,
                OTPVerification.is_used == False,
                OTPVerification.is_invalidated == False
            )
            .all()
        )
        assert len(active_otps) == 1


def test_9_successful_verification_sets_user_is_verified(db):
    """9. Successful verification sets User.is_verified = True."""
    email = "unverified_user@example.com"
    username = "unverified_user"

    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        user = User(
            username=username,
            email=email,
            hashed_password="somepasswordhash",
            is_verified=False
        )
        db.add(user)
        db.commit()
    else:
        existing_user.is_verified = False
        db.commit()

    with patch("app.services.otp.send_otp_email") as mock_send:
        request_otp_service(db, email)
        sent_otp = mock_send.call_args[0][1]

        res = verify_otp_service(db, email, sent_otp)
        assert res["is_verified"] is True

        user_in_db = db.query(User).filter(User.email == email).first()
        assert user_in_db.is_verified is True


def test_10_no_active_otp_is_rejected(db):
    """10. No active OTP is rejected."""
    with pytest.raises(HTTPException) as exc_info:
        verify_otp_service(db, "nobody_active@example.com", "123456")
    assert exc_info.value.status_code == 404
    assert "No active OTP found" in exc_info.value.detail


def test_11_email_delivery_failure_handled_correctly(db):
    """11. Email delivery failure is handled correctly."""
    email = "delivery_fail@example.com"
    with patch("app.services.otp.send_otp_email", side_effect=EmailDeliveryError("SMTP Connection failed")):
        with pytest.raises(HTTPException) as exc_info:
            request_otp_service(db, email)
        assert exc_info.value.status_code == 500
        assert "Failed to send OTP email" in exc_info.value.detail

        active_otp = (
            db.query(OTPVerification)
            .filter(OTPVerification.email == email)
            .first()
        )
        assert active_otp is None
