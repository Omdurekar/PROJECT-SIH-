from unittest.mock import patch, MagicMock
import pytest
from app.utils.email import send_otp_email, EmailDeliveryError
from app.config.settings import settings


def test_send_otp_email_success():
    """Verify SMTP connection, TLS, login, email contents, OTP inclusion, and connection closure on success."""
    with patch("smtplib.SMTP") as mock_smtp_class:
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        recipient = "testuser@example.com"
        otp = "987654"

        send_otp_email(recipient, otp)

        # 1. Verify SMTP connection uses configured host and port
        mock_smtp_class.assert_called_once_with(
            settings.EMAIL_HOST, int(settings.EMAIL_PORT), timeout=10
        )

        # 2. Verify STARTTLS is called
        mock_server.starttls.assert_called_once()

        # 3. Verify Login uses configured credentials
        mock_server.login.assert_called_once_with(
            settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD
        )

        # 4. Verify email construction & send_message call
        mock_server.send_message.assert_called_once()
        sent_msg = mock_server.send_message.call_args[0][0]

        assert sent_msg["To"] == recipient
        assert sent_msg["From"] == settings.EMAIL_USERNAME
        assert "Registration Verification" in sent_msg["Subject"]

        # 5. Verify OTP and expiration period are in body
        payload = sent_msg.get_payload()
        combined_body = "".join([part.get_payload() for part in payload])
        assert otp in combined_body
        assert "registration" in combined_body.lower()
        assert str(settings.OTP_EXPIRE_MINUTES) in combined_body

        # 6. Verify SMTP connection close (__exit__ called by context manager)
        mock_smtp_class.return_value.__exit__.assert_called_once()


def test_send_otp_email_smtp_failure_handling():
    """Verify SMTP exceptions are handled cleanly without exposing credentials or internal traces."""
    with patch("smtplib.SMTP") as mock_smtp_class:
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("SecretCredentialError: login failed")
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        with pytest.raises(EmailDeliveryError) as exc_info:
            send_otp_email("user@example.com", "123456")

        err_text = str(exc_info.value)
        # Ensure password and internal error details are redacted
        assert settings.EMAIL_PASSWORD not in err_text
        assert "SecretCredentialError" not in err_text
        assert "Failed to send OTP email" in err_text


def test_send_otp_email_missing_parameters():
    """Verify ValueError is raised if recipient email or OTP is empty."""
    with pytest.raises(ValueError):
        send_otp_email("", "123456")

    with pytest.raises(ValueError):
        send_otp_email("user@example.com", "")
