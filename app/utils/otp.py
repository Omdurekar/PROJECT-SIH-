import secrets
from app.utils.auth import hash_password, verify_password


def generate_otp() -> str:
    """
    Generate a cryptographically secure 6-digit numeric OTP as a string.
    Ensures exact 6 digits with leading zero padding if applicable.
    """
    number = secrets.randbelow(1_000_000)
    return f"{number:06d}"


def hash_otp(otp: str) -> str:
    """
    Hashes an OTP before storage using the project's existing password hashing mechanism.
    Never returns the plaintext OTP.
    """
    return hash_password(otp)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """
    Verifies an entered plaintext OTP against a stored OTP hash.
    Returns True if it matches, False otherwise.
    """
    if not plain_otp or not hashed_otp:
        return False
    return verify_password(plain_otp, hashed_otp)
