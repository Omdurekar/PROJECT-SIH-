import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Custom exception raised when email delivery via SMTP fails."""
    pass


def send_otp_email(recipient_email: str, otp: str) -> None:
    """
    Sends a 6-digit OTP to the recipient's email address via SMTP for registration verification.

    Args:
        recipient_email (str): The target recipient's email address.
        otp (str): The plaintext 6-digit OTP string.

    Raises:
        ValueError: If recipient_email or otp is missing.
        EmailDeliveryError: If SMTP connection, authentication, or transmission fails.
    """
    if not recipient_email or not otp:
        raise ValueError("Recipient email and OTP must be provided.")

    sender_email = settings.EMAIL_USERNAME
    expire_minutes = settings.OTP_EXPIRE_MINUTES

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Registration Verification OTP"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    text_body = (
        f"Hello,\n\n"
        f"Your OTP for account registration and email verification is: {otp}\n\n"
        f"This OTP expires after {expire_minutes} minute(s). "
        f"Please do not share this code with anyone.\n\n"
        f"If you did not request this, please ignore this email.\n"
    )

    html_body = f"""
    <html>
      <body>
        <h2>Registration Verification Code</h2>
        <p>Your OTP for account registration and email verification is:</p>
        <h1 style="font-size: 28px; letter-spacing: 4px; color: #2b6cb0;">{otp}</h1>
        <p>This OTP expires after <strong>{expire_minutes} minute(s)</strong>.</p>
        <p>If you did not request this verification code, please ignore this email.</p>
      </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        smtp_host = settings.EMAIL_HOST
        smtp_port = int(settings.EMAIL_PORT)

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        logger.error(f"Failed to send OTP email to {recipient_email}: {type(exc).__name__}")
        raise EmailDeliveryError("Failed to send OTP email due to SMTP server error.") from None
