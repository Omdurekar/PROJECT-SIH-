import uuid
import datetime
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config.database import SessionLocal, init_db
from app.models.orm import User, OTPVerification
from app.config.settings import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_otp_table():
    """Ensure clean OTP table state for API tests."""
    init_db()
    db = SessionLocal()
    db.query(OTPVerification).delete()
    db.commit()
    try:
        yield
    finally:
        db.query(OTPVerification).delete()
        db.commit()
        db.close()


def test_api_registration_creates_unverified_user_and_triggers_otp():
    """1. Registration creates unverified user and triggers OTP service email."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    payload = {
        "username": uname,
        "email": email,
        "password": "Password123!",
        "role": "Monitoring Officer"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        res = client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == uname
        assert data["email"] == email
        assert data["is_verified"] is False
        mock_send.assert_called_once()
        assert mock_send.call_args[0][0] == email


def test_api_verify_otp_success():
    """2. Verify OTP endpoint successfully verifies user."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    payload = {
        "username": uname,
        "email": email,
        "password": "Password123!"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        client.post("/api/v1/auth/register", json=payload)
        sent_otp = mock_send.call_args[0][1]

        verify_res = client.post("/api/v1/auth/verify-otp", json={"email": email, "otp_code": sent_otp})
        assert verify_res.status_code == 200
        assert verify_res.json()["is_verified"] is True
        assert verify_res.json()["email"] == email


def test_api_verify_otp_invalid_code():
    """3. Invalid OTP returns HTTP 400 error."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    payload = {
        "username": uname,
        "email": email,
        "password": "Password123!"
    }

    with patch("app.services.otp.send_otp_email"):
        client.post("/api/v1/auth/register", json=payload)

        verify_res = client.post("/api/v1/auth/verify-otp", json={"email": email, "otp_code": "000000"})
        assert verify_res.status_code == 400
        assert "Invalid OTP" in verify_res.json()["detail"]


def test_api_verify_otp_expired_code():
    """4. Expired OTP returns HTTP 400 error."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    payload = {
        "username": uname,
        "email": email,
        "password": "Password123!"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        client.post("/api/v1/auth/register", json=payload)
        sent_otp = mock_send.call_args[0][1]

        # Expire the record in DB
        db = SessionLocal()
        otp_rec = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        otp_rec.expires_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        db.commit()
        db.close()

        verify_res = client.post("/api/v1/auth/verify-otp", json={"email": email, "otp_code": sent_otp})
        assert verify_res.status_code == 400
        assert "expired" in verify_res.json()["detail"].lower()


def test_api_resend_otp_success_and_cooldown():
    """5 & 6. Resend OTP works and cooldown is enforced via API."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    payload = {
        "username": uname,
        "email": email,
        "password": "Password123!"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        client.post("/api/v1/auth/register", json=payload)

        # Immediate resend attempt should fail with 429
        resend_cooldown = client.post("/api/v1/auth/resend-otp", json={"email": email})
        assert resend_cooldown.status_code == 429
        assert "cooldown active" in resend_cooldown.json()["detail"].lower()

        # Age the last_sent_at past cooldown period
        db = SessionLocal()
        otp_rec = db.query(OTPVerification).filter(OTPVerification.email == email).first()
        otp_rec.last_sent_at = datetime.datetime.utcnow() - datetime.timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS + 5)
        db.commit()
        db.close()

        # Resend after cooldown should succeed
        resend_ok = client.post("/api/v1/auth/resend-otp", json={"email": email})
        assert resend_ok.status_code == 200
        assert resend_ok.json()["email"] == email


def test_api_unverified_and_verified_user_login():
    """7 & 8. Unverified user login is blocked (403), verified user login succeeds (200 + JWT)."""
    uname = f"user_{uuid.uuid4().hex[:6]}"
    email = f"{uname}@example.com"
    reg_payload = {
        "username": uname,
        "email": email,
        "password": "Password123!"
    }
    login_payload = {
        "username": uname,
        "password": "Password123!"
    }

    with patch("app.services.otp.send_otp_email") as mock_send:
        client.post("/api/v1/auth/register", json=reg_payload)
        sent_otp = mock_send.call_args[0][1]

        # 7. Unverified user login rejected
        login_unverified = client.post("/api/v1/auth/login", json=login_payload)
        assert login_unverified.status_code == 403
        assert "verification required" in login_unverified.json()["detail"].lower()

        # Verify OTP
        client.post("/api/v1/auth/verify-otp", json={"email": email, "otp_code": sent_otp})

        # 8. Verified user login succeeds
        login_verified = client.post("/api/v1/auth/login", json=login_payload)
        assert login_verified.status_code == 200
        assert "access_token" in login_verified.json()
        assert login_verified.json()["user"]["username"] == uname
        assert login_verified.json()["user"]["is_verified"] is True
