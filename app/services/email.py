import smtplib
from email.message import EmailMessage

from app.config import get_settings

settings = get_settings()


def send_verification_email(
    recipient: str,
    username: str,
    verification_token: str,
) -> None:
    verification_url = (
        f"{settings.app_base_url}/api/auth/verify-email" f"?token={verification_token}"
    )

    message = EmailMessage()
    message["Subject"] = "Verify your email"
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message.set_content(
        f"Hello {username},\n\n"
        "Please verify your email address by opening this link:\n"
        f"{verification_url}\n\n"
        "If you did not create this account, ignore this email."
    )

    if settings.smtp_use_tls:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=10,
        ) as smtp:
            smtp.starttls()
            if settings.smtp_username:
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )
            smtp.send_message(message)
    else:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=10,
        ) as smtp:
            if settings.smtp_username:
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )
            smtp.send_message(message)
