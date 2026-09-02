import pytest
from app.utils.otp import generate_otp, hash_otp, verify_otp


def test_generate_otp_format():
    """Test that generated OTPs are always 6 numeric digits."""
    for _ in range(100):
        otp = generate_otp()
        assert isinstance(otp, str)
        assert len(otp) == 6
        assert otp.isdigit()


def test_hash_otp_does_not_return_plaintext():
    """Test that hash_otp does not return the plaintext OTP."""
    otp = "123456"
    hashed = hash_otp(otp)
    assert hashed != otp
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_verify_otp_correct():
    """Test that verify_otp returns True for matching plaintext OTP and hash."""
    otp = "654321"
    hashed = hash_otp(otp)
    assert verify_otp(otp, hashed) is True


def test_verify_otp_incorrect():
    """Test that verify_otp returns False for wrong OTP."""
    otp = "123456"
    hashed = hash_otp(otp)
    assert verify_otp("654321", hashed) is False


def test_verify_otp_invalid_inputs():
    """Test verify_otp behavior on empty or invalid inputs."""
    hashed = hash_otp("123456")
    assert verify_otp("", hashed) is False
    assert verify_otp("123456", "") is False
    assert verify_otp("", "") is False
