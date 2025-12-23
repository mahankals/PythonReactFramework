"""
Email tasks for async email sending via Celery.

Usage:
    from app.tasks.email import send_password_reset_email

    # Send password reset email asynchronously
    send_password_reset_email.delay(
        to_email="user@example.com",
        username="john",
        reset_token="abc123..."
    )
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.tasks.celery_app import celery_app
from app.config import settings


def _send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP settings from config.

    Returns True if successful, raises exception otherwise.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email

    # Plain text fallback
    if text_content:
        msg.attach(MIMEText(text_content, "plain"))

    # HTML content
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

    return True


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(
    self,
    to_email: str,
    username: str,
    reset_token: str
) -> dict:
    """
    Send password reset email to user.

    Args:
        to_email: Recipient email address
        username: User's display name
        reset_token: Password reset token

    Returns:
        dict with task status
    """
    reset_url = f"{settings.app_url}/reset-password?token={reset_token}"
    expire_minutes = settings.password_reset_expire_minutes

    subject = f"Reset your {settings.app_name} password"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #007bff;
                color: white !important;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            <p>Hello {username},</p>
            <p>We received a request to reset your password for your {settings.app_name} account.</p>
            <p>Click the button below to reset your password:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            <p><strong>This link will expire in {expire_minutes} minutes.</strong></p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
            <div class="footer">
                <p>This is an automated message from {settings.app_name}.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Password Reset Request

    Hello {username},

    We received a request to reset your password for your {settings.app_name} account.

    Click the link below to reset your password:
    {reset_url}

    This link will expire in {expire_minutes} minutes.

    If you didn't request a password reset, you can safely ignore this email.

    This is an automated message from {settings.app_name}.
    """

    try:
        _send_email(to_email, subject, html_content, text_content)
        return {
            "status": "sent",
            "to_email": to_email,
            "task_id": self.request.id
        }
    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(
    self,
    to_email: str,
    username: str
) -> dict:
    """
    Send welcome email to newly registered user.

    Args:
        to_email: Recipient email address
        username: User's display name

    Returns:
        dict with task status
    """
    login_url = f"{settings.app_url}/login"

    subject = f"Welcome to {settings.app_name}!"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #28a745;
                color: white !important;
                text-decoration: none;
                border-radius: 4px;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to {settings.app_name}!</h2>
            <p>Hello {username},</p>
            <p>Thank you for creating an account with us. We're excited to have you on board!</p>
            <p>Your account is now active and ready to use.</p>
            <a href="{login_url}" class="button">Login to Your Account</a>
            <div class="footer">
                <p>This is an automated message from {settings.app_name}.</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_content = f"""
    Welcome to {settings.app_name}!

    Hello {username},

    Thank you for creating an account with us. We're excited to have you on board!

    Your account is now active and ready to use.

    Login here: {login_url}

    This is an automated message from {settings.app_name}.
    """

    try:
        _send_email(to_email, subject, html_content, text_content)
        return {
            "status": "sent",
            "to_email": to_email,
            "task_id": self.request.id
        }
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_generic_email(
    self,
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> dict:
    """
    Send a generic email with custom content.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body content
        text_content: Optional plain text fallback

    Returns:
        dict with task status
    """
    try:
        _send_email(to_email, subject, html_content, text_content)
        return {
            "status": "sent",
            "to_email": to_email,
            "task_id": self.request.id
        }
    except Exception as exc:
        raise self.retry(exc=exc)
